const API_BASE = 'http://127.0.0.1:8000';

// State
let pendingActions = [];
let runMetadata = null;

// UI Elements
const actionsList = document.getElementById('actions-list');
const runBtn = document.getElementById('run-pipeline-btn');
const approveAllBtn = document.getElementById('approve-all-btn');
const actionCountBadge = document.getElementById('action-count');

// Init
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

// Logic: Run Play
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
        renderActions(data.actions || []);
        runMetadata = { run_id: data.run_id, play: data.play };

        // Handle visual context from agent
        if (data.visual_context) {
            console.log('Agent visual context:', data.visual_context);
            // We could use this to filter or highlight the viz
            loadTableauView(data.visual_context.view_name);
        }

        console.log('Analysis Complete:', data);

    } catch (error) {
        console.error('Error running play:', error);
        alert('Failed to run analysis. Is the server running?');
    } finally {
        runBtn.disabled = false;
        runBtn.textContent = 'Run Pipeline Audit';
    }
});

async function loadTableauView(preferredName = null) {
    const vizContainer = document.getElementById('tableau-viz');

    try {
        const res = await fetch(`${API_BASE}/tableau/views`);
        const data = await res.json();

        if (data.status === 'success' && data.views.length > 0) {
            let view = data.views[0];
            if (preferredName) {
                view = data.views.find(v => v.name.toLowerCase().includes(preferredName.toLowerCase())) || view;
            }
            vizContainer.innerHTML = `<iframe src="${view.embed_url}" style="width:100%; height:100%; border:none;" allowfullscreen></iframe>`;
            console.log(`Loaded Tableau view: ${view.name}`);
        } else {
            // Demo Fallback (Tableau Public - Superstore is the most stable sample)
            const demoUrl = "https://public.tableau.com/views/Superstore_24/Overview?:showVizHome=no&:embed=true";
            vizContainer.innerHTML = `<iframe src="${demoUrl}" style="width:100%; height:100%; border:none;" allowfullscreen></iframe>`;
            console.warn('Tableau not configured. Loading Superstore demo view.');
        }
    } catch (e) {
        console.error('Failed to load Tableau views:', e);
        vizContainer.innerHTML = '<div class="error-state">Failed to connect to Tableau Service.</div>';
    }
}

function renderActions(actions) {
    pendingActions = actions;
    actionsList.innerHTML = '';
    actionCountBadge.textContent = `${actions.length} PENDING`;

    if (actions.length === 0) {
        actionsList.innerHTML = '<div class="empty-state">No actions recommended.</div>';
        return;
    }

    actions.forEach((action, index) => {
        const card = document.createElement('div');
        card.className = 'action-card';
        card.style.animationDelay = `${index * 0.1}s`;

        const typeClass = action.type === 'slack_message' ? 'type-slack' : 'type-sf';
        const typeLabel = action.type === 'slack_message' ? 'Slack' : 'Salesforce';

        card.innerHTML = `
      <div class="action-type ${typeClass}">${typeLabel}</div>
      <div class="action-title">${action.title || 'New Action'}</div>
      <div class="action-desc">${action.description}</div>
      <div class="action-context" style="font-size: 0.7rem; color: var(--accent-primary); margin-top: 0.5rem; display: flex; align-items: center; gap: 0.25rem;">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
        View context in Tableau
      </div>
      <div style="display:flex; gap: 0.5rem; margin-top: 1rem;">
        <button class="btn btn-outline" style="flex:1; padding: 0.4rem; font-size: 0.75rem;">Ignore</button>
        <button class="btn btn-primary approve-single" data-index="${index}" style="flex:1; padding: 0.4rem; font-size: 0.75rem;">Approve</button>
      </div>
    `;
        actionsList.appendChild(card);
    });

    // Single approval listeners
    document.querySelectorAll('.approve-single').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const idx = e.target.dataset.index;
            approveActions([pendingActions[idx]]);
        });
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
                approver: 'antigravity-studio-ui',
                run_id: runMetadata?.run_id
            })
        });

        const result = await response.json();
        alert(`Successfully executed ${result.executed_count} actions!`);

        // Update UI (simple refresh for demo)
        if (actions.length === pendingActions.length) {
            renderActions([]);
        } else {
            // Remove approved item from state
            pendingActions = pendingActions.filter(a => !actions.includes(a));
            renderActions(pendingActions);
        }

    } catch (error) {
        console.error('Error approving actions:', error);
        alert('Approval failed.');
    }
}

approveAllBtn.addEventListener('click', () => approveActions(pendingActions));

// Start
checkStatus();
loadTableauView();
setInterval(checkStatus, 10000);
