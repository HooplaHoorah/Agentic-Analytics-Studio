# Netlify GitHub Connection - Updated Navigation Guide

## Current Netlify UI (2024/2025)

The Netlify UI has changed. Here's where to find the Git connection settings:

### Method 1: Via Site Settings (Most Common)
1. Go to https://app.netlify.com
2. Click on your site: **agentic-analytics-studio**
3. Look for **"Site settings"** button (usually top right or in tabs)
4. In the left sidebar, look for:
   - **"Build & deploy"** OR
   - **"Continuous deployment"** OR
   - **"Git"**
5. Click on it
6. Look for a section called **"Build settings"** or **"Repository"**
7. You should see either:
   - "Link repository" button (if not connected)
   - Current repository info (if already connected)

### Method 2: Via Deploys Tab
1. Go to https://app.netlify.com
2. Click on your site: **agentic-analytics-studio**
3. Click the **"Deploys"** tab at the top
4. Look for **"Deploy settings"** button or link
5. This should show you the current deployment configuration
6. Look for **"Link to repository"** or **"Configure builds"**

### Method 3: Direct URL
Try this direct link (replace YOUR_SITE_ID):
```
https://app.netlify.com/sites/agentic-analytics-studio/settings/deploys
```

### What You're Looking For
You need to find a section that shows:
- **Repository**: (currently might show "None" or "Manual deploys")
- **Branch**: (what branch to deploy from)
- **Build command**: (command to run before deploy)
- **Publish directory**: (which folder contains the site)

### If Site Is Already Linked to Git
If you see repository info already shown:
1. Click **"Edit settings"** or similar
2. Verify these settings:
   - Repository: HooplaHoorah/Agentic-Analytics-Studio
   - Branch: feat/pipeline-risk-and-execution (or main)
   - Build command: (empty)
   - Publish directory: web

### If You Need to Link for First Time
1. Click **"Link repository"** or **"Connect to Git"**
2. Choose **GitHub**
3. Authorize Netlify (if prompted)
4. Select: **HooplaHoorah/Agentic-Analytics-Studio**
5. Configure:
   - Branch to deploy: `feat/pipeline-risk-and-execution`
   - Build command: (leave empty)
   - Publish directory: `web`
6. Click **Save** or **Deploy site**

## Alternative: Check Current Deployment Method
Your site might already be set up for Git deploys. To check:

1. Go to the **Deploys** tab
2. Look at recent deploys
3. If they say "Published from Git" → already connected ✅
4. If they say "Published manually" → need to connect

## Screenshot Guide
If you can share a screenshot of your Netlify dashboard, I can point you to exactly where to click!

Common UI layouts:
- **Tabs at top**: Overview | Deploys | Plugins | Functions | Site settings
- **Or sidebar**: Overview, Deploys, Site configuration, Domain settings, etc.

## After Connecting
Once connected, test it:
```bash
# Make a small change
echo "<!-- test -->" >> web/index.html

# Commit and push
git add web/index.html
git commit -m "test: verify netlify auto-deploy"
git push origin feat/pipeline-risk-and-execution

# Watch Netlify Deploys tab - should see new deploy start automatically
```
