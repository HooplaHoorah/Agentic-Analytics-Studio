# Revenue Forecasting Demo Scenario
# This script demonstrates the Revenue Forecasting play end-to-end

Write-Host "=== Agentic Analytics Studio - Revenue Forecasting Demo ===" -ForegroundColor Cyan
Write-Host ""

# Check if backend is running
Write-Host "[1/4] Checking backend status..." -ForegroundColor Yellow
try {
    $healthCheck = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -ErrorAction Stop
    Write-Host "✓ Backend is online (LLM Provider: $($healthCheck.llm_provider))" -ForegroundColor Green
}
catch {
    Write-Host "✗ Backend is offline. Please start it with: uvicorn aas.api:app --reload" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[2/4] Running Revenue Forecasting analysis..." -ForegroundColor Yellow

# Run the revenue forecasting play
$runPayload = @{
    params = @{
        target_revenue = 5000000  # $5M target
    }
} | ConvertTo-Json

try {
    $result = Invoke-RestMethod -Uri "http://localhost:8000/run/revenue" -Method Post -Body $runPayload -ContentType "application/json" -ErrorAction Stop
    
    Write-Host "✓ Analysis complete!" -ForegroundColor Green
    Write-Host ""
    
    # Display key metrics
    Write-Host "--- Revenue Forecast Summary ---" -ForegroundColor Cyan
    Write-Host "Target Revenue:      `$$($result.analysis.target_revenue.ToString('N0'))"
    Write-Host "Forecasted Revenue:  `$$($result.analysis.forecasted_revenue.ToString('N0'))"
    Write-Host "Shortfall:           `$$($result.analysis.shortfall.ToString('N0')) ($($result.analysis.shortfall_pct.ToString('N1'))%)"
    Write-Host "Win Rate:            $($result.analysis.win_rate.ToString('P1'))"
    Write-Host "Avg Deal Velocity:   $($result.analysis.avg_deal_velocity_days.ToString('N0')) days"
    Write-Host "Open Deals:          $($result.analysis.open_deals)"
    Write-Host ""
    
    # Display recommended actions
    Write-Host "--- Recommended Actions ($($result.actions.Count)) ---" -ForegroundColor Cyan
    foreach ($action in $result.actions) {
        Write-Host ""
        Write-Host "[$($action.priority.ToUpper())] $($action.title)" -ForegroundColor $(if ($action.priority -eq "high") { "Red" } else { "Yellow" })
        Write-Host "  Type: $($action.type)"
        Write-Host "  Impact Score: $($action.impact_score)"
        Write-Host "  Description: $($action.description)"
        if ($action.rationale) {
            Write-Host "  AI Rationale: $($action.rationale)" -ForegroundColor Magenta
        }
    }
    
    Write-Host ""
    Write-Host "[3/4] Saving run results..." -ForegroundColor Yellow
    $result | ConvertTo-Json -Depth 10 | Out-File -FilePath "revenue_forecast_run.json" -Encoding UTF8
    Write-Host "✓ Results saved to revenue_forecast_run.json" -ForegroundColor Green
    
}
catch {
    Write-Host "✗ Failed to run revenue forecasting: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[4/4] Demo scenario complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Open the web UI at http://localhost:5173"
Write-Host "  2. Select 'Revenue Forecasting' from the play dropdown"
Write-Host "  3. Click 'Run Pipeline Audit' to see the analysis"
Write-Host "  4. Review and approve recommended actions"
Write-Host ""
Write-Host "To approve actions programmatically:" -ForegroundColor Cyan
Write-Host '  $approvePayload = @{ actions = $result.actions; approver = "demo-user" } | ConvertTo-Json -Depth 10'
Write-Host '  Invoke-RestMethod -Uri "http://localhost:8000/approve" -Method Post -Body $approvePayload -ContentType "application/json"'
Write-Host ""
