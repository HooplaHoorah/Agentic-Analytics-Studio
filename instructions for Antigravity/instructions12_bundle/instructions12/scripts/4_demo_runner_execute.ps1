$ErrorActionPreference = "Stop"
function Find-RepoRoot {
  $starts = @((Resolve-Path $PSScriptRoot).Path, (Get-Location).Path)
  foreach ($s in $starts) {
    $p = $s
    while ($true) {
      if ((Test-Path (Join-Path $p "aas")) -and (Test-Path (Join-Path $p "requirements.txt"))) { return $p }
      $parent = Split-Path $p -Parent
      if ($parent -eq $p) { break }
      $p = $parent
    }
  }
  throw "Could not locate repo root."
}
$ROOT = Find-RepoRoot
Set-Location $ROOT
python "instructions for Antigravity\instructions12_bundle\instructions12\tools\demo_runner.py" --mode execute
Write-Host "`nSend back: instructions12/out/demo_report.md"
