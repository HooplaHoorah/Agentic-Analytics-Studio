\
$ErrorActionPreference = "Stop"
function Find-RepoRoot {
  $starts = @((Resolve-Path $PSScriptRoot).Path, (Get-Location).Path)
  foreach ($s in $starts) {
    $p = $s
    while ($true) {
      if (Test-Path (Join-Path $p "aas") -and Test-Path (Join-Path $p "requirements.txt")) { return $p }
      $parent = Split-Path $p -Parent
      if ($parent -eq $p) { break }
      $p = $parent
    }
  }
  throw "Could not locate repo root."
}
$ROOT = Find-RepoRoot
Set-Location $ROOT
if (-not (Test-Path ".venv")) { python -m venv .venv }
.\\.venv\\Scripts\\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install playwright slack_sdk tableauserverclient
python -m playwright install chromium
Write-Host "Setup complete."
