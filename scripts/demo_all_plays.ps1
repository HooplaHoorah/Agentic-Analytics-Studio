# Agentic Analytics Studio - Complete Demo Script
# Demonstrates all 4 hero plays end-to-end

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Agentic Analytics Studio - Full Demo" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$API_BASE = "http://localhost:8000"

# Check if API is running
Write-Host "[1/5] Checking API status..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$API_BASE/health" -Method Get
    Write-Host "✓ API is online" -ForegroundColor Green
    Write-Host "  - LLM Provider: $($health.llm_provider)" -ForegroundColor Gray
    Write-Host "  - Salesforce Mode: $($health.salesforce_mode)" -ForegroundColor Gray
}
catch {
    Write-Host "✗ API is offline. Please start the backend:" -ForegroundColor Red
    Write-Host "  uvicorn aas.api:app --reload" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# List available plays
Write-Host "[2/5] Fetching available plays..." -ForegroundColor Yellow
$plays = Invoke-RestMethod -Uri "$API_BASE/plays" -Method Get
Write-Host "✓ Found $($plays.plays.Count) plays:" -ForegroundColor Green
foreach ($play in $plays.plays) {
    if ($play -is [string]) {
        Write-Host "  - $play" -ForegroundColor Gray
    }
    else {
        Write-Host "  - $($play.id): $($play.label)" -ForegroundColor Gray
    }
}

Write-Host ""

# Function to run a play and display results
function Run-Play {
    param(
        [string]$PlayId,
        [string]$PlayName
    )
    
    Write-Host "----------------------------------------" -ForegroundColor Cyan
    Write-Host "Running: $PlayName" -ForegroundColor Cyan
    Write-Host "----------------------------------------" -ForegroundColor Cyan
    
    try {
        $result = Invoke-RestMethod -Uri "$API_BASE/run/$PlayId" -Method Post -ContentType "application/json" -Body "{}"
        
        Write-Host "✓ Analysis complete" -ForegroundColor Green
        Write-Host ""
        
        if ($result.analysis) {
            Write-Host "📊 Analysis Summary:" -ForegroundColor Yellow
            Write-Host "  $($result.analysis.summary)" -ForegroundColor White
            Write-Host ""
        }
        
        if ($result.actions -and $result.actions.Count -gt 0) {
            Write-Host "🎯 Recommended Actions: $($result.actions.Count)" -ForegroundColor Yellow
            Write-Host ""
            
            $topActions = $result.actions | Select-Object -First 3
            foreach ($action in $topActions) {
                Write-Host "  [$($action.priority.ToUpper())] $($action.title)" -ForegroundColor $(
                    if ($action.priority -eq "high") { "Red" }
                    elseif ($action.priority -eq "medium") { "Yellow" }
                    else { "Green" }
                )
                Write-Host "  Impact Score: $($action.impact_score)" -ForegroundColor Gray
                if ($action.reasoning) {
                    $reasoning = $action.reasoning.Substring(0, [Math]::Min(100, $action.reasoning.Length))
                    Write-Host "  Rationale: $reasoning..." -ForegroundColor Gray
                }
                Write-Host ""
            }
            
            if ($result.actions.Count -gt 3) {
                Write-Host "  ... and $($result.actions.Count - 3) more actions" -ForegroundColor Gray
                Write-Host ""
            }
        }
        else {
            Write-Host "ℹ No actions recommended" -ForegroundColor Gray
            Write-Host ""
        }
        
        return $result
        
    }
    catch {
        Write-Host "✗ Failed to run $PlayName" -ForegroundColor Red
        Write-Host "  Error: $_" -ForegroundColor Red
        Write-Host ""
        return $null
    }
}

# Run all plays
Write-Host "[3/5] Running all hero plays..." -ForegroundColor Yellow
Write-Host ""

$results = @{}

# Pipeline Leakage
$results["pipeline"] = Run-Play -PlayId "pipeline" -PlayName "💰 Pipeline Leakage"

# Churn Rescue
$results["churn"] = Run-Play -PlayId "churn" -PlayName "🛟 Churn Rescue"

# Spend Anomaly
$results["spend"] = Run-Play -PlayId "spend" -PlayName "📊 Spend Anomaly"

# Revenue Forecasting
$results["revenue"] = Run-Play -PlayId "revenue" -PlayName "📈 Revenue Forecasting"

# Display impact summary
Write-Host "[4/5] Fetching impact analytics..." -ForegroundColor Yellow
try {
    $impact = Invoke-RestMethod -Uri "$API_BASE/api/impact/summary" -Method Get
    
    Write-Host "✓ Impact Dashboard:" -ForegroundColor Green
    Write-Host ""
    Write-Host "  💰 Total Estimated Value: `$$($impact.estimated_value.ToString('N0'))" -ForegroundColor Cyan
    Write-Host "  ✅ Actions Approved: $($impact.total_approved) / $($impact.total_actions)" -ForegroundColor Cyan
    Write-Host "  🔄 Pipeline Runs: $($impact.total_runs)" -ForegroundColor Cyan
    
    if ($impact.top_plays -and $impact.top_plays.Count -gt 0) {
        Write-Host "  🏆 Top Play: $($impact.top_plays[0].play) (Impact: $($impact.top_plays[0].total_impact))" -ForegroundColor Cyan
    }
    
    Write-Host ""
}
catch {
    Write-Host "⚠ Could not fetch impact analytics" -ForegroundColor Yellow
    Write-Host ""
}

# Save results
Write-Host "[5/5] Saving results..." -ForegroundColor Yellow
$outputDir = "demo_outputs"
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir | Out-Null
}

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$outputFile = "$outputDir/demo_results_$timestamp.json"

$demoResults = @{
    timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    plays_run = $results.Keys.Count
    results   = $results
    impact    = $impact
}

$demoResults | ConvertTo-Json -Depth 10 | Out-File -FilePath $outputFile -Encoding UTF8

Write-Host "✓ Results saved to: $outputFile" -ForegroundColor Green
Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Demo Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Summary:" -ForegroundColor Yellow
Write-Host "  - Plays executed: $($results.Keys.Count)" -ForegroundColor White
Write-Host "  - Total actions generated: $(($results.Values | Where-Object { $_ -ne $null } | ForEach-Object { $_.actions.Count } | Measure-Object -Sum).Sum)" -ForegroundColor White
Write-Host "  - Results saved: $outputFile" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Open http://localhost:5173 to view in UI" -ForegroundColor White
Write-Host "  2. Click 'Try Demo' for guided tour" -ForegroundColor White
Write-Host "  3. Click '📊 Impact' to view analytics dashboard" -ForegroundColor White
Write-Host "  4. Export impact report with '📥 Export Report'" -ForegroundColor White
Write-Host ""
