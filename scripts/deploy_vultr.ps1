
$ErrorActionPreference = "Stop"
$TargetHost = $env:TARGET_HOST
# The target host should be provided via the TARGET_HOST environment variable
# rather than hard‑coding an IP address. This avoids committing
# sensitive server addresses into source control. Example:
#   $env:TARGET_HOST = "root@your.server.com"
if (-not $TargetHost) {
    throw "TARGET_HOST environment variable must be set to your deployment server, e.g. 'root@hostname'"
}

Write-Host "Deploying to Vultr..."

# 1. Upload Code (Comprehensive)
Write-Host "Syncing directory structure..."
ssh $TargetHost "mkdir -p /opt/aas/aas/agents /opt/aas/aas/models /opt/aas/aas/services"

$FilesToDeploy = @(
    "aas/db.py",
    "aas/api.py",
    "aas/executor.py",
    "aas/models/action.py",
    "aas/models/play.py",
    "aas/agents/base.py",
    "aas/agents/pipeline_leakage.py",
    "aas/agents/churn_rescue.py",
    "aas/agents/spend_anomaly.py",
    "aas/services/salesforce_client.py",
    "aas/services/tableau_client.py",
    "aas/services/slack_client.py",
    "requirements.txt"
)

foreach ($file in $FilesToDeploy) {
    Write-Host "Mirroring $file..."
    Get-Content -Raw $file | ssh $TargetHost "cat > /opt/aas/$file"
}

# 2. Configure Environment (Secrets)
Write-Host "Configuring secrets in /etc/aas/aas.env..."
# Try to read local .env file
$EnvFile = "$PSScriptRoot/../.env"
if (Test-Path $EnvFile) {
    Write-Host "Reading secrets from .env..."
    $EnvLines = Get-Content $EnvFile
    foreach ($line in $EnvLines) {
        if ($line -match "^([^#=]+)=(.*)$") {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            # Remove quotes if present
            $value = $value -replace '^"|"$', ''
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
        }
    }
}

# Verify Critical Vars
$RequiredVars = @("DATABASE_URL", "TABLEAU_TOKEN_SECRET", "SLACK_BOT_TOKEN", "OPENAI_API_KEY")
foreach ($var in $RequiredVars) {
    if (-not (Get-Item "Env:\$var" -ErrorAction SilentlyContinue)) {
        Write-Warning "Missing variable: $var (Script may fail on server if needed)"
    }
}

$EnvContent = @"
DATABASE_URL="$($env:DATABASE_URL)"
TABLEAU_SERVER_URL="$($env:TABLEAU_SERVER_URL)"
TABLEAU_SITE_ID="$($env:TABLEAU_SITE_ID)"
TABLEAU_TOKEN_NAME="$($env:TABLEAU_TOKEN_NAME)"
TABLEAU_TOKEN_SECRET="$($env:TABLEAU_TOKEN_SECRET)"
TABLEAU_CONNECTED_APP_CLIENT_ID="$($env:TABLEAU_CONNECTED_APP_CLIENT_ID)"
TABLEAU_CONNECTED_APP_SECRET_ID="$($env:TABLEAU_CONNECTED_APP_SECRET_ID)"
TABLEAU_CONNECTED_APP_SECRET_VALUE="$($env:TABLEAU_CONNECTED_APP_SECRET_VALUE)"
TABLEAU_CONNECTED_APP_USERNAME="$($env:TABLEAU_CONNECTED_APP_USERNAME)"
SLACK_BOT_TOKEN="$($env:SLACK_BOT_TOKEN)"
TABLEAU_VIZ_URL_CLOUD="$($env:TABLEAU_VIZ_URL_CLOUD)"
TABLEAU_VIZ_URL_PIPELINE="$($env:TABLEAU_VIZ_URL_PIPELINE)"
TABLEAU_VIZ_URL_CHURN="$($env:TABLEAU_VIZ_URL_CHURN)"
TABLEAU_VIZ_URL_SPEND="$($env:TABLEAU_VIZ_URL_SPEND)"

# AI / LLM Configuration
LLM_PROVIDER="$($env:LLM_PROVIDER)"
OPENAI_API_KEY="$($env:OPENAI_API_KEY)"
OLLAMA_BASE_URL="$($env:OLLAMA_BASE_URL)"
OLLAMA_MODEL="$($env:OLLAMA_MODEL)"

# Salesforce Configuration
SF_USERNAME="$($env:SF_USERNAME)"
SF_PASSWORD="$($env:SF_PASSWORD)"
SF_SECURITY_TOKEN="$($env:SF_SECURITY_TOKEN)"
SF_DOMAIN="$($env:SF_DOMAIN)"
"@

# Write env file safely (using specific echo to avoid pipe issues with special chars if any, but simplistic here)
# Using base64 to avoid quoting hell
$Bytes = [System.Text.Encoding]::UTF8.GetBytes($EnvContent)
$B64 = [Convert]::ToBase64String($Bytes)
ssh $TargetHost "mkdir -p /etc/aas && echo '$B64' | base64 -d > /etc/aas/aas.env && chmod 600 /etc/aas/aas.env"

# 3. Update Service
Write-Host "Updating systemd service..."
$ServiceContent = @"
[Unit]
Description=Agentic Analytics Studio API
After=network.target

[Service]
User=aas
Group=aas
WorkingDirectory=/opt/aas
EnvironmentFile=/etc/aas/aas.env
ExecStart=/opt/aas/.venv/bin/uvicorn aas.api:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always

[Install]
WantedBy=multi-user.target
"@

$BytesSvc = [System.Text.Encoding]::UTF8.GetBytes($ServiceContent)
$B64Svc = [Convert]::ToBase64String($BytesSvc)
ssh $TargetHost "echo '$B64Svc' | base64 -d > /etc/systemd/system/aas.service"

# 4. Install Dependencies & Restart
Write-Host "Installing dependencies and restarting service..."
ssh $TargetHost "su - aas -c 'cd /opt/aas && . .venv/bin/activate && pip install -U pip && pip install -r requirements.txt' && systemctl daemon-reload && systemctl restart aas"

Write-Host "Deployment Complete!"
