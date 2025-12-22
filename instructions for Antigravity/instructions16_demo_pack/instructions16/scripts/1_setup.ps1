\
$ErrorActionPreference = "Stop"
Write-Host "== Instructions16 setup =="

python -m pip install --upgrade pip
python -m pip install -r ..\requirements.txt

# Optional helpers for evidence screenshots (safe if already installed)
python -m pip install playwright python-dotenv
try { python -m playwright install chromium } catch { Write-Host "Playwright chromium install skipped/failed (ok)." }

Write-Host "Setup complete."
