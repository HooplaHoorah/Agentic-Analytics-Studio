
$ErrorActionPreference = "Stop"
$TargetHost = "root@66.135.1.215"

Write-Host "Deploying to Vultr..."

# 1. Upload Code
Write-Host "Uploading aas/db.py..."
Get-Content -Raw "aas/db.py" | ssh $TargetHost "cat > /opt/aas/aas/db.py"

Write-Host "Uploading aas/api.py..."
Get-Content -Raw "aas/api.py" | ssh $TargetHost "cat > /opt/aas/aas/api.py"

Write-Host "Uploading requirements.txt..."
Get-Content -Raw "requirements.txt" | ssh $TargetHost "cat > /opt/aas/requirements.txt"

# 2. Configure Environment (Secrets)
Write-Host "Configuring secrets in /etc/aas/aas.env..."
$EnvContent = @"
DATABASE_URL="postgresql://vultradmin:AVNS_1Z4yRiK79Yz3CDRzoFH@vultr-prod-38e84cab-c270-41d6-abee-23155df25ebd-vultr-prod-795c.vultrdb.com:16751/defaultdb"
TABLEAU_SERVER_URL="https://10ax.online.tableau.com"
TABLEAU_SITE_ID="agenticanalyticsstudio"
TABLEAU_TOKEN_NAME="aas_backend"
TABLEAU_TOKEN_SECRET="MYH8mqkASDCib/1+JsFCuw==:MZrOsK1z1LxovjNpP5GY9VAO6k3GNIrW"
TABLEAU_CONNECTED_APP_CLIENT_ID="842b6911-a5f5-4555-a3a5-8e344e656e18"
TABLEAU_CONNECTED_APP_SECRET_ID="ce7f5e90-4e90-4a12-8f78-71309404ca14"
TABLEAU_CONNECTED_APP_SECRET_VALUE="oJw/+UBTRDfkkv6AYquSyYLPZEntizwQWQxqGkeWmgE="
TABLEAU_CONNECTED_APP_USERNAME="hooplahoorah@gmail.com"
SLACK_BOT_TOKEN="xoxb-10168181986657-10162823619317-uqtFSrPzTzX9KX3BJeqdOVNw"
TABLEAU_VIZ_URL_CLOUD="https://10ax.online.tableau.com/t/agenticanalyticsstudio/views/AAS_Live_Data/Sheet1?:showVizHome=no&:embed=yes"
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
