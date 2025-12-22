$ErrorActionPreference = "Stop"
Write-Host "== Launching AAS demo =="

# Load repo root .env into this process
$repoRoot = (python "instructions for Antigravity\instructions16_demo_pack\instructions16\tools\find_repo_root.py").Trim()
$envPath = Join-Path $repoRoot ".env"
if (Test-Path $envPath) {
  Get-Content $envPath | ForEach-Object {
    $line = $_.Trim()
    if ($line.StartsWith("#") -or [string]::IsNullOrWhiteSpace($line)) { return }
    if ($line -notmatch "=") { return }
    $parts = $line.Split("=", 2)
    $k = $parts[0].Trim()
    $v = $parts[1].Trim().Trim('"').Trim("'")
    [Environment]::SetEnvironmentVariable($k, $v)
  }
}
else {
  Write-Host "WARNING: .env not found in repo root. Real Mode may fail."
}

python "instructions for Antigravity\instructions16_demo_pack\instructions16\tools\launcher.py"
