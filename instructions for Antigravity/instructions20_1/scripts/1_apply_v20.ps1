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
  python instructions20/scripts/patch_index_html_v20.py
  Write-Host "✅ v20 applied. Hard refresh the browser and run the demo via http://localhost (not file://)."
} finally {
  Pop-Location
}
