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
  python instructions21/scripts/patch_index_html_v21.py
  Write-Host "✅ v21 applied. Hard refresh the browser (Ctrl+Shift+R) before recording."
} finally {
  Pop-Location
}
