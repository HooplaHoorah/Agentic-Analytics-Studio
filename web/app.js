import { TableauEventType } from 'https://public.tableau.com/javascripts/api/tableau.embedding.3.latest.min.js';

// Use localhost API when developing locally; use Netlify proxy in production.
const API_BASE = (location.hostname === 'localhost' || location.hostname === '127.0.0.1')
    ? 'http://127.0.0.1:8000'
    : '/api';

// Config
// ?tableau=cloud -> attempts Connected App (JWT) + API view listing
// ?tableau=public -> defaults to public URL (safe demo)
const TABLEAU_MODE = new URLSearchParams(window.location.search).get('tableau') || 'public';

// Fallback/Default Public URL
const TABLEAU_PUBLIC_DEFAULT_URL = "https://public.tableau.com/views/Superstore_24/Overview?:showVizHome=no&:embed=true";


// State
let pendingActions = [];
let runMetadata = null;
let currentViz = null;

// UI Elements
const actionsList = document.getElementById('actions-list');
const runBtn = document.getElementById('run-pipeline-btn');
const approveAllBtn = document.getElementById('approve-all-btn');
const actionCountBadge = document.getElementById('action-count');
const vizContainer = document.getElementById('tableau-viz');


// --- 1. Init & Status ---

async function checkStatus() {
    try {
        const res = await fetch(`${API_BASE}/health`);
        if (res.ok) {
            document.getElementById('api-status').textContent = 'API: ONLINE';
        }
    } catch (e) {
        document.getElementById('api-status').textContent = 'API: OFFLINE';
        document.getElementById('api-status').classList.replace('status-online', 'status-offline');
    }
}


// --- 2. Tableau Rendering (Web Component) ---

async function getTableauToken() {
    try {
        const resp = await fetch(`${API_BASE}/tableau/jwt`);
        if (!resp.ok) return null;
        const data = await resp.json();
        return data.token;
    } catch (e) {
        console.warn("Failed to fetch Tableau token", e);
        return null;
    }
}

async function loadTableauView() {
    let url = TABLEAU_PUBLIC_DEFAULT_URL;
    let token = null;

    if (TABLEAU_MODE === 'cloud') {
        // Fetch views from backend
        try {
            const res = await fetch(`${API_BASE}/tableau/views`);
            const data = await res.json();
            if (data.status === 'success' && data.views && data.views.length > 0) {
                // Use the first view or find one named 'Overview'
                const match = data.views.find(v => v.name.toLowerCase().includes('overview')) || data.views[0];
                url = match.embed_url;

                // Fetch JWT
                token = await getTableauToken();
            } else {
                console.warn("Tableau Cloud mode requested but no views returned. Falling back to Public.");
            }
        } catch (e) {
            console.error("Error initializing Tableau Cloud view", e);
        }
    }

    renderTableauViz(url, token);
}

function renderTableauViz(src, token = null) {
    vizContainer.innerHTML = ''; // Clear placeholder or old iframe

    const viz = document.createElement('tableau-viz');
    viz.id = 'aasViz';
    viz.src = src;
    viz.toolbar = 'hidden';
    viz.hideTabs = true;

    // Style it to fill container
    viz.style.width = '100%';
    viz.style.height = '100%';

    if (token) {
        viz.token = token;
        console.log("Using JWT for Tableau authentication");
    }

    // Add detailed event listener for bi-directional context
    viz.addEventListener(TableauEventType.FirstInteractive, () => {
        console.log("Tableau Viz Loaded & Interactive");
        viz.addEventListener(TableauEventType.MarkSelectionChanged, onMarkSelectionChanged);
    });

    vizContainer.appendChild(viz);
    currentViz = viz;
}

async function refreshViz() {
    if (currentViz) {
        try {
            console.log("Refreshing Tableau Viz...");
            await currentViz.refreshDataAsync();
        } catch (e) {
            console.warn("Viz refresh failed (possibly public or not ready), reloading src.", e);
            // Fallback: simple reload
            const src = currentViz.src;
            currentViz.src = '';
            currentViz.src = src;
        }
    }
}


// --- 3. Bi-Directional Context (Selection -> Actions) ---

function safeGetField(marks, fieldName) {
    // Helper to dig into the complexity of Tableau Marks API
    if (!marks || !marks.data || !marks.data.length) return null;
    try {
        const dataTable = marks.data[0];
        // dataTable.data is array of rows
        // dataTable.columns is metadata
        // We look for column index
        const colIdx = dataTable.columns.findIndex(c => c.fieldName === fieldName);
        if (colIdx === -1) return null;

        return dataTable.data[0][colIdx].value;
    } catch (e) {
        return null;
    }
}

async function onMarkSelectionChanged(e) {
    try {
        const marks = await e.detail.getMarksAsync();
        if (marks.data.length === 0) {
            // Cleared selection -> Reset actions to pending
            fetchContextActions();
            return;
        }

        // Try standard fields
        const region = safeGetField(marks, 'Region');
        const owner = safeGetField(marks, 'Owner');
        const stage = safeGetField(marks, 'Stage');

        console.log("Context selected:", { region, owner, stage });
        fetchContextActions({ region, owner, stage });

    } catch (err) {
        console.error("Error handling mark selection", err);
    }
}

async function fetchContextActions(filters = {}) {
    const params = new URLSearchParams();
    if (filters.region) params.set('region', filters.region);
    if (filters.owner) params.set('owner', filters.owner);
    if (filters.stage) params.set('stage', filters.stage);

    try {
        const resp = await fetch(`${API_BASE}/context/actions?${params.toString()}`);
        const data = await resp.json();
        renderActions(data.actions || [], data.filters);
    } catch (e) {
        console.error("Failed to fetch context actions", e);
    }
}


// --- 4. Action Panel Logic ---

function renderActions(actions, activeFilters = null) {
    pendingActions = actions; // Update local state
    actionsList.innerHTML = '';
    actionCountBadge.textContent = `${actions.length} PENDING`;

    // Render Context Badge if filters active
    if (activeFilters && (activeFilters.region || activeFilters.owner || activeFilters.stage)) {
        const hints = [];
        if (activeFilters.region) hints.push(`Region: ${activeFilters.region}`);
        if (activeFilters.owner) hints.push(`Owner: ${activeFilters.owner}`);
        if (activeFilters.stage) hints.push(`Stage: ${activeFilters.stage}`);

        const badge = document.createElement('div');
        badge.className = 'context-filter-badge';
        badge.style.background = 'rgba(76, 141, 255, 0.15)';
        badge.style.border = '1px solid rgba(76, 141, 255, 0.3)';
        badge.style.borderRadius = '8px';
        badge.style.padding = '8px 12px';
        badge.style.marginBottom = '12px';
        badge.style.fontSize = '0.85rem';
        badge.style.color = '#fff';
        badge.innerHTML = `<strong>Active Context:</strong> ${hints.join(' · ')}`;
        actionsList.appendChild(badge);
    }

    if (actions.length === 0) {
        const msg = document.createElement('div');
        msg.className = 'empty-state';
        msg.textContent = 'No pending actions for this context.';
        actionsList.appendChild(msg);
        return;
    }

    actions.forEach((action, index) => {
        const card = document.createElement('div');
        card.className = 'action-card';
        card.style.animationDelay = `${index * 0.05}s`;

        const typeClass = action.type === 'slack_message' ? 'type-slack' : 'type-sf';
        const typeLabel = action.type === 'slack_message' ? 'Slack' : 'Salesforce';

        card.innerHTML = `
            <div class="action-type ${typeClass}">${typeLabel}</div>
            <div class="action-title">${action.title || 'Action'}</div>
            <div class="action-desc">${action.description}</div>
            <div style="display:flex; gap: 0.5rem; margin-top: 1rem;">
                <button class="btn btn-outline ignore-btn" data-index="${index}" style="flex:1; padding: 0.4rem; font-size: 0.75rem;">Ignore</button>
                <button class="btn btn-primary approve-single" data-index="${index}" style="flex:1; padding: 0.4rem; font-size: 0.75rem;">Approve</button>
            </div>
        `;
        actionsList.appendChild(card);
    });

    // Wire buttons
    actionsList.querySelectorAll('.approve-single').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const idx = e.target.dataset.index;
            approveActions([pendingActions[idx]]);
        });
    });
}

runBtn.addEventListener('click', async () => {
    runBtn.disabled = true;
    runBtn.textContent = 'Analyzing...';

    try {
        const response = await fetch(`${API_BASE}/run/pipeline`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ params: {} })
        });
        const data = await response.json();

        // Update runs metadata
        runMetadata = { run_id: data.run_id };

        // Render actions
        renderActions(data.actions || []);

        // Refresh viz (to see the "new" run data ideally)
        setTimeout(refreshViz, 1000);

    } catch (error) {
        alert('Failed to run analysis. Check API.');
        console.error(error);
    } finally {
        runBtn.disabled = false;
        runBtn.textContent = 'Run Pipeline Audit';
    }
});

async function approveActions(actions) {
    if (actions.length === 0) return;

    try {
        const response = await fetch(`${API_BASE}/approve`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                actions: actions,
                approver: 'antigravity-ui',
                run_id: runMetadata?.run_id
            })
        });

        const result = await response.json();
        console.log("Approvals processed:", result);

        // Remove approved from view
        pendingActions = pendingActions.filter(a => !actions.includes(a));
        renderActions(pendingActions);

        // Refresh viz (to show "fixed" state)
        setTimeout(refreshViz, 1000);

    } catch (e) {
        console.error("Approval failed", e);
        alert("Approval failed");
    }
}

approveAllBtn.addEventListener('click', () => {
    approveActions(pendingActions);
});


// Start
checkStatus();
loadTableauView();
setInterval(checkStatus, 15000);