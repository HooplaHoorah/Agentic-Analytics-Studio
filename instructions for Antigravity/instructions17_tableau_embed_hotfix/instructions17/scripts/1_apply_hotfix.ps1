$ErrorActionPreference = "Stop"

function Find-RepoRoot {
  param([string]$start)
  $p = Resolve-Path $start
  while ($true) {
    if (Test-Path (Join-Path $p "aas\api.py")) { return $p }
    $parent = Split-Path $p -Parent
    if ($parent -eq $p) { throw "Could not find repo root (missing aas\api.py) starting from: $start" }
    $p = $parent
  }
}

$repo = Find-RepoRoot (Get-Location).Path
Write-Host "Repo root: $repo"

Push-Location $repo
try {
  python instructions17/scripts/patch_backend.py
  python instructions17/scripts/patch_frontend.py
  Write-Host "✅ Instructions17 hotfix applied."
  Write-Host ""
  Write-Host "Next:"
  Write-Host "  1) Restart backend"
  Write-Host "  2) Open http://127.0.0.1:8000/tableau/views and confirm embed_url is present"
  Write-Host "  3) Reload demo UI"
} finally {
  Pop-Location
}
