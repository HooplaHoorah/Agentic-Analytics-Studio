# Netlify GitHub Auto-Deploy Setup Guide

## Step-by-Step Instructions

### 1. Access Netlify Dashboard
- Go to: https://app.netlify.com
- Log in if needed
- Find your site: **agentic-analytics-studio**

### 2. Navigate to Build Settings
- Click on your site
- Go to: **Site configuration** → **Build & deploy**
- Look for: **Continuous Deployment** section

### 3. Link to Git Repository
- Click: **Link site to Git** (or **Link repository** if site is already linked)
- Choose: **GitHub**
- Authorize Netlify to access your GitHub account if prompted
- Select repository: **HooplaHoorah/Agentic-Analytics-Studio**

### 4. Configure Build Settings
Set the following:

**Branch to deploy:**
```
feat/pipeline-risk-and-execution
```
(Or use `main` if you want to deploy from main branch)

**Build command:**
```
(leave empty)
```
The site is static HTML/JS, no build step needed.

**Publish directory:**
```
web
```
This is where your `index.html` and `app.js` files are located.

### 5. Advanced Settings (Optional)
If you need environment variables for the frontend:
- Scroll to **Environment variables**
- Add any needed variables (though for this app, secrets are backend-only)

### 6. Save and Deploy
- Click **Save** or **Deploy site**
- Netlify will immediately trigger a deploy from the selected branch
- Future pushes to `feat/pipeline-risk-and-execution` will auto-deploy

### 7. Verify Auto-Deploy Works
After setup:
1. Make a small change to `web/index.html` (e.g., add a comment)
2. Commit and push to GitHub
3. Watch Netlify dashboard - should see new deploy start automatically
4. Deploy should complete in ~30-60 seconds

## Current Repository Info
- **GitHub Repo**: https://github.com/HooplaHoorah/Agentic-Analytics-Studio
- **Current Branch**: feat/pipeline-risk-and-execution
- **Latest Commit**: Includes the new `<tableau-viz>` web component implementation

## What This Enables
Once connected:
- ✅ Every `git push` triggers automatic deployment
- ✅ No manual drag-and-drop needed
- ✅ Deploy previews for pull requests (optional)
- ✅ Rollback capability in Netlify UI
- ✅ Deploy logs and build history

## Troubleshooting
If auto-deploy doesn't work:
1. Check **Deploys** tab in Netlify - look for errors
2. Verify the publish directory is set to `web`
3. Ensure the branch name matches exactly
4. Check GitHub webhook is active (Settings → Webhooks in GitHub repo)
