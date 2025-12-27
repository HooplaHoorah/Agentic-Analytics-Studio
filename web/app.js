// Tableau Embedding API is now loaded dynamically via ensureTableauEmbeddingApi()

// Use localhost API when developing locally; use Netlify proxy in production.
const API_BASE = (location.hostname === 'localhost' || location.hostname === '127.0.0.1')
    ? 'http://127.0.0.1:8000'
    : '/api';

// Config
// ?tableau=cloud  -> Connected App (JWT) embed (LIVE data dashboard)
// ?tableau=public -> Tableau Public fallback (safe demo)
const TABLEAU_MODE = new URLSearchParams(window.location.search).get('tableau') || 'cloud';

// Fallback/Default Public URL
const TABLEAU_PUBLIC_DEFAULT_URL = "https://public.tableau.com/views/Superstore_24/Overview?:showVizHome=no&:embed=true";


// --- New Helpers from INSTRUCTIONS30 ---

async function ensureTableauEmbeddingApi() {
    if (window.customElements?.get("tableau-viz")) return;

    await new Promise((resolve, reject) => {
        const s = document.createElement("script");
        s.type = "module";
        s.src = "https://public.tableau.com/javascripts/api/tableau.embedding.3.latest.min.js";
        s.onload = resolve;
        s.onerror = reject;
        document.head.appendChild(s);
    });
}

async function renderTableauCloudViz(containerEl) {
    await ensureTableauEmbeddingApi();

    const r = await fetch(`${API_BASE}/tableau/jwt`);
    if (!r.ok) throw new Error(`JWT endpoint failed: ${r.status}`);
    const { token, vizUrl } = await r.json();

    if (!vizUrl || !vizUrl.includes("/views/")) {
        throw new Error(`Invalid vizUrl returned (missing /views/): ${vizUrl}`);
    }

    // Clear container
    containerEl.innerHTML = "";

    // Create web component
    const viz = document.createElement("tableau-viz");
    viz.id = "aasViz";
    // Attributes must be set before appending or before src is set for best reliability
    viz.setAttribute("toolbar", "bottom");
    viz.setAttribute("hide-tabs", "");

    // Style it to fill container
    viz.style.width = '100%';
    viz.style.height = '100%';

    containerEl.appendChild(viz);

    // Apply src + token
    viz.src = vizUrl;
    viz.token = token;

    // Add event listener for bi-directional context
    // Note: Using string 'firstinteractive' instead of TableauEventType for dynamic loading safety
    viz.addEventListener('firstinteractive', () => {
        console.log("Tableau Cloud Viz Loaded & Interactive");
        viz.addEventListener('markselectionchanged', onMarkSelectionChanged);
    });

    return viz;
}

// --- End Helpers ---


// State
let pendingActions = [];
let runMetadata = null;
let currentViz = null;
let lastFilters = {};
let currentPlay = 'pipeline';

// UI Elements
const actionsList = document.getElementById('actions-list');
const runBtn = document.getElementById('run-pipeline-btn');
const approveAllBtn = document.getElementById('approve-all-btn');
const clearActionsBtn = document.getElementById('clear-actions');
const actionCountBadge = document.getElementById('action-count');
const vizContainer = document.getElementById('tableau-viz');
const playSelect = document.getElementById('play-select');


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
        const resp = await fetch(`${API_BASE}/tableau/jwt?play=${currentPlay}`);
        if (!resp.ok) return null;
        const data = await resp.json();
        return data.token;
    } catch (e) {
        console.warn("Failed to fetch Tableau token", e);
        return null;
    }
}

async function renderTableauCloudViz(containerEl) {
    await ensureTableauEmbeddingApi();

    const r = await fetch(`${API_BASE}/tableau/jwt?play=${currentPlay}`);
    if (!r.ok) throw new Error(`JWT endpoint failed: ${r.status}`);
    const { token, vizUrl } = await r.json();

    if (!vizUrl || !vizUrl.includes("/views/")) {
        throw new Error(`Invalid vizUrl returned (missing /views/): ${vizUrl}`);
    }

    // Clear container
    containerEl.innerHTML = "";

    // Create web component
    const viz = document.createElement("tableau-viz");
    viz.id = "aasViz";
    // Attributes must be set before appending or before src is set for best reliability
    viz.setAttribute("toolbar", "hidden");
    viz.setAttribute("hide-tabs", "");

    // Style it to fill container
    viz.style.width = '100%';
    viz.style.height = '100%';

    containerEl.appendChild(viz);

    // Apply src + token
    viz.src = vizUrl;
    viz.token = token;

    // Add event listener for bi-directional context
    // Note: Using string 'firstinteractive' instead of TableauEventType for dynamic loading safety
    viz.addEventListener('firstinteractive', () => {
        console.log("Tableau Cloud Viz Loaded & Interactive");
        viz.addEventListener('markselectionchanged', onMarkSelectionChanged);
    });

    return viz;
}

async function loadTableauView() {
    if (TABLEAU_MODE === 'cloud') {
        try {
            currentViz = await renderTableauCloudViz(vizContainer);
        } catch (e) {
            console.error("Error initializing Tableau Cloud view", e);
            // Fallback to public if cloud fails
            renderTableauViz(TABLEAU_PUBLIC_DEFAULT_URL);
        }
    } else {
        renderTableauViz(TABLEAU_PUBLIC_DEFAULT_URL);
    }
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
    viz.addEventListener('firstinteractive', () => {
        console.log("Tableau Viz Loaded & Interactive");
        viz.addEventListener('markselectionchanged', onMarkSelectionChanged);
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
    // Helper to dig into the complexity of Tableau Marks API.
    // This uses a flexible match because Tableau sometimes namespaces field names.
    if (!marks || !marks.data || !marks.data.length) return null;
    const want = String(fieldName || '').toLowerCase();

    // Collect values across all returned mark rows/tables.
    // If the selection is aggregated but still has a single dimension value
    // (e.g., Segment = Enterprise), we return it. If multiple values exist,
    // we return null to avoid sending ambiguous filters.
    try {
        for (const dataTable of (marks.data || [])) {
            const cols = dataTable.columns || [];

            // 1) exact (case-insensitive)
            let colIdx = cols.findIndex(c => String(c.fieldName || '').toLowerCase() === want);

            // 2) partial (case-insensitive) -- BUT skip if it looks like a measure/age
            if (colIdx === -1) {
                colIdx = cols.findIndex(c => {
                    const fname = String(c.fieldName || '').toLowerCase();
                    return fname.includes(want) && !fname.includes('age') && !fname.includes('days');
                });
            }

            if (colIdx === -1) continue;

            const values = [];
            for (const row of (dataTable.data || [])) {
                const v = row?.[colIdx]?.value;
                if (v !== undefined && v !== null && v !== '') values.push(v);
            }

            const uniq = Array.from(new Set(values.map(v => String(v))));
            if (uniq.length === 1) return uniq[0];
        }
        return null;
    } catch (e) {
        return null;
    }
}

async function onMarkSelectionChanged(e) {
    try {
        const marks = await e.detail.getMarksAsync();
        if (marks.data.length === 0) {
            // Cleared selection -> Reset actions to pending
            lastFilters = {};
            fetchContextActions();
            return;
        }

        // Try standard fields (exact field-name matches only)
        const segment = safeGetField(marks, 'Segment');
        const region = safeGetField(marks, 'Region');
        const owner = safeGetField(marks, 'Owner');
        const stage = safeGetField(marks, 'Stage');

        // Ignore selections that only include measures (e.g., 'Stage Age Days')
        if (!segment && !region && !owner && !stage) {
            console.log('Selection contained no supported dimension fields; ignoring.');
            return;
        }

        console.log('Context selected:', { segment, region, owner, stage });
        fetchContextActions({ segment, region, owner, stage });

    } catch (err) {
        console.error("Error handling mark selection", err);
    }
}

async function fetchContextActions(filters = {}) {
    lastFilters = { ...filters };
    const params = new URLSearchParams();
    params.set('play', currentPlay);
    if (filters.region) params.set('region', filters.region);
    if (filters.owner) params.set('owner', filters.owner);
    if (filters.stage) params.set('stage', filters.stage);
    if (filters.segment) params.set('segment', filters.segment);
    if (filters.segment) params.set('segment', filters.segment);

    try {
        const resp = await fetch(`${API_BASE}/context/actions?${params.toString()}`);
        const data = await resp.json();
        const actions = data.actions || [];
        renderActions(actions, data.filters);
        return actions;
    } catch (e) {
        console.error("Failed to fetch context actions", e);
        return null;
    }
}



// --- 4. Action Panel Logic ---

function renderActions(actions, activeFilters = null) {
    pendingActions = actions; // Update local state
    actionsList.innerHTML = '';
    actionCountBadge.textContent = `${actions.length} PENDING`;

    // Render Context Badge if filters active
    if (activeFilters && (activeFilters.region || activeFilters.owner || activeFilters.stage || activeFilters.segment)) {
        const hints = [];
        if (activeFilters.region) hints.push(`Region: ${activeFilters.region}`);
        if (activeFilters.owner) hints.push(`Owner: ${activeFilters.owner}`);
        if (activeFilters.stage) hints.push(`Stage: ${activeFilters.stage}`);
        if (activeFilters.segment) hints.push(`Segment: ${activeFilters.segment}`);

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

        // Make the entire card clickable: open the embed_url (if available) in a new tab.
        // Ignore clicks on buttons to prevent interference with approve/ignore actions.
        const embedUrl = (action.metadata && action.metadata.embed_url) || action.embed_url;
        if (embedUrl) {
            card.style.cursor = 'pointer';
            card.addEventListener('click', (ev) => {
                // If a button inside the card was clicked, do nothing.
                if (ev.target.closest('button')) return;
                window.open(embedUrl, '_blank');
            });
        }
    });

    // Wire buttons
    actionsList.querySelectorAll('.approve-single').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const idx = e.target.dataset.index;
            approveActions([pendingActions[idx]]);
        });
    });

    actionsList.querySelectorAll('.ignore-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const idx = Number(e.target.dataset.index);
            pendingActions = pendingActions.filter((_, i) => i !== idx);
            renderActions(pendingActions, lastFilters);
        });
    });
}

runBtn.addEventListener('click', async () => {
    runBtn.disabled = true;
    runBtn.textContent = 'Analyzing...';

    try {
        const response = await fetch(`${API_BASE}/run/${currentPlay}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ params: {} })
        });
        const data = await response.json();

        // Update runs metadata
        runMetadata = { run_id: data.run_id };

        // Render actions from DB (source of truth for action_id/status)
        await fetchContextActions();
        lastFilters = {};

        // Refresh viz (to see the "new" run data ideally)
        setTimeout(refreshViz, 1000);

    } catch (error) {
        alert('Failed to run analysis. Check API.');
        console.error(error);
    } finally {
        runBtn.disabled = false;
        const playLabel = playSelect ? playSelect.options[playSelect.selectedIndex].text : 'Pipeline Audit';
        runBtn.textContent = `Run ${playLabel}`;
    }
});

if (playSelect) {
    playSelect.addEventListener('change', async (e) => {
        currentPlay = e.target.value;
        const playLabel = playSelect.options[playSelect.selectedIndex].text;
        runBtn.textContent = `Run ${playLabel}`;

        // Reload Tableau View for the new play
        await loadTableauView();

        // Reset Actions
        lastFilters = {};
        fetchContextActions();
    });
}

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

        // Refresh actions from DB (source of truth)
        try {
            await fetchContextActions();
        } catch (e) {
            // Fallback: remove approved from local view
            pendingActions = pendingActions.filter(a => !actions.includes(a));
            renderActions(pendingActions, lastFilters);
        }

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

if (clearActionsBtn) {
    clearActionsBtn.addEventListener('click', async () => {
        try {
            // Clear any Tableau selection if supported by the component
            if (currentViz?.clearSelectedMarksAsync) await currentViz.clearSelectedMarksAsync();
        } catch (e) {
            console.warn('Failed to clear Tableau selection', e);
        }
        lastFilters = {};
        fetchContextActions();
    });
}


// Start
checkStatus();
loadTableauView();
setInterval(checkStatus, 15000);
fetchContextActions();
