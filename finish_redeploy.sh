#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/opt/aas"
SERVICE="aas"
AAS_USER="aas"
AAS_GROUP="aas"

say() { echo -e "\n==> $*"; }

say "Ensuring OS deps"
command -v python3 >/dev/null 2>&1 || (apt-get update && apt-get install -y python3)
python3 -c "import venv" 2>/dev/null || (apt-get update && apt-get install -y python3-venv)

say "Ensuring service user/group exist: ${AAS_USER}:${AAS_GROUP}"
getent group "${AAS_GROUP}" >/dev/null 2>&1 || groupadd --system "${AAS_GROUP}"
id -u "${AAS_USER}" >/dev/null 2>&1 || useradd --system --create-home --gid "${AAS_GROUP}" --shell /usr/sbin/nologin "${AAS_USER}"

say "Fixing ownership"
chown -R "${AAS_USER}:${AAS_GROUP}" "${APP_DIR}"

say "Creating venv + installing requirements"
sudo -u "${AAS_USER}" bash -lc "cd '${APP_DIR}' && python3 -m venv .venv"
sudo -u "${AAS_USER}" bash -lc "cd '${APP_DIR}' && . .venv/bin/activate && pip install -U pip && pip install -r requirements.txt"

say "Installing/refreshing systemd unit: /etc/systemd/system/${SERVICE}.service"
cat > "/etc/systemd/system/${SERVICE}.service" <<EOF
[Unit]
Description=Agentic Analytics Studio API
After=network.target

[Service]
User=${AAS_USER}
Group=${AAS_GROUP}
WorkingDirectory=${APP_DIR}
EnvironmentFile=/etc/aas/aas.env
ExecStart=${APP_DIR}/.venv/bin/uvicorn aas.api:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
RestartSec=2

[Install]
WantedBy=multi-user.target
EOF

say "Starting service"
systemctl daemon-reload
systemctl enable "${SERVICE}" >/dev/null 2>&1 || true
systemctl restart "${SERVICE}"

say "Done."
(systemctl status "${SERVICE}" --no-pager -l | sed -n '1,25p') || true
