
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

# Load .env into process env for child processes
if (Test-Path ".env") {
  Get-Content ".env" | ForEach-Object {
    $line = $_.Trim()
    if ($line.StartsWith("#") -or [string]::IsNullOrWhiteSpace($line)) { return }
    if ($line -notmatch "=") { return }
    $parts = $line.Split("=", 2)
    $k = $parts[0].Trim()
    $v = $parts[1].Trim()
    if ($v.StartsWith('"') -and $v.EndsWith('"')) { $v = $v.Trim('"') }
    if ($v.StartsWith("'") -and $v.EndsWith("'")) { $v = $v.Trim("'") }
    [Environment]::SetEnvironmentVariable($k, $v)
  }
}

if (Test-Path ".venv\\Scripts\\Activate.ps1") {
  .\\.venv\\Scripts\\Activate.ps1
}

python "instructions for Antigravity\instructions13_bundle\instructions13\tools\walkthrough.py"

Write-Host "`nSend back: instructions13/out/walkthrough_report.md"
