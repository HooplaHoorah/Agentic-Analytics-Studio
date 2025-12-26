# INSTRUCTIONS30 Implementation Status

## Completed Steps

### ✅ Step 1: Backend Verification
- Verified `/api/tableau/jwt` returns valid JSON with `token` and `vizUrl`
- Confirmed `vizUrl` contains `/views/` and points to `AAS_Live_Data`

### ✅ Step 2: Frontend Implementation
- Added `ensureTableauEmbeddingApi()` helper to dynamically load Tableau API
- Added `renderTableauCloudViz()` to create `<tableau-viz>` web component
- Updated `loadTableauView()` to use new cloud renderer
- Removed static import of Tableau API (now loaded dynamically)

### ✅ Step 3: Remove iframe DOM Access
- Verified no `contentWindow` or `contentDocument` references exist in `app.js`
- Updated event listeners to use string literals instead of `TableauEventType` enum

### ✅ Step 4: Deployment
- Committed changes to Git
- Pushed to GitHub (triggers Netlify auto-build)
- Created standalone test page at `/test-tableau.html` for isolated verification

## Next Steps

### Pending: Step 5 - Verification
Once Netlify build completes (~2-3 minutes), verify:
1. Visit `https://agentic-analytics-studio.netlify.app/test-tableau.html`
2. Check console for step-by-step logs
3. Verify viz loads without X-Frame-Options errors
4. Test main app at `/?tableau=cloud`

### Pending: Step 6 - Tighten Allowlist
After successful verification, update Tableau Connected App allowlist from `*` to:
- `https://agentic-analytics-studio.netlify.app`
- `http://localhost:5173` (dev only)

## Files Modified
- `web/app.js` - Implemented dynamic API loading and web component rendering
- `web/test-tableau.html` - Created standalone test page

## Known Issues
- Browser subagent hit rate limit (429) during verification
- Will need manual verification via test page once Netlify build completes
