# Demo Scripts & Sample Data

This directory contains demo scripts and sample datasets for all hero plays in Agentic Analytics Studio.

---

## 📁 Sample Data

Located in `aas/sample_data/`:

| File | Play | Records | Description |
|------|------|---------|-------------|
| `pipeline_leakage_data.csv` | Pipeline Leakage | 50 | Opportunities with stages, amounts, risk indicators |
| `churn_rescue_data.csv` | Churn Rescue | 50 | Customers with MRR, NPS, usage trends, health scores |
| `spend_anomaly_data.csv` | Spend Anomaly | 50 | Transactions with normal and anomalous patterns |
| `revenue_forecast_data.csv` | Revenue Forecasting | 40 | Historical deals for forecasting analysis |

All datasets contain realistic values designed to trigger agent recommendations.

---

## 🎬 Demo Scripts

### Complete Demo (All Plays)
**File:** `demo_all_plays.ps1`  
**Platform:** PowerShell (Windows/Linux/macOS)

Runs all 4 hero plays sequentially and displays results.

```powershell
# Ensure backend is running first
uvicorn aas.api:app --reload

# In another terminal:
.\scripts\demo_all_plays.ps1
```

**Output:**
- Checks API health
- Lists available plays
- Runs each play and displays top 3 actions
- Fetches impact analytics
- Saves results to `demo_outputs/demo_results_TIMESTAMP.json`

### Individual Play Demos

#### Revenue Forecasting
**File:** `demo_revenue_forecasting.ps1`

```powershell
.\scripts\demo_revenue_forecasting.ps1
```

Demonstrates revenue forecasting with detailed output and impact scoring.

---

## 🚀 Quick Start

### 1. Start the Backend
```bash
# Terminal 1
uvicorn aas.api:app --reload --port 8000
```

### 2. Run Demo Script
```powershell
# Terminal 2 (PowerShell)
.\scripts\demo_all_plays.ps1
```

### 3. View Results
- **Console**: See color-coded output with actions and impact scores
- **File**: Check `demo_outputs/demo_results_*.json` for full results
- **UI**: Open http://localhost:5173 and click "Try Demo"

---

## 📊 Expected Output

### Pipeline Leakage
- **Findings**: 5-10 at-risk deals
- **Actions**: Follow-up tasks, deal reviews, pipeline health checks
- **Impact**: $500K-$1.5M in recovered revenue

### Churn Rescue
- **Findings**: 8-12 at-risk customers
- **Actions**: Retention outreach, health check calls, upgrade offers
- **Impact**: $200K-$500K in retained MRR

### Spend Anomaly
- **Findings**: 3-5 anomalous transactions
- **Actions**: Budget holds, approval reviews, vendor audits
- **Impact**: $100K-$300K in cost avoidance

### Revenue Forecasting
- **Findings**: Revenue shortfall vs. target
- **Actions**: Budget reallocation, targeted outreach, process improvements
- **Impact**: $800K-$1.2M in pipeline acceleration

---

## 🧪 Testing Individual Plays

### Via API (curl)
```bash
# Pipeline Leakage
curl -X POST http://localhost:8000/run/pipeline

# Churn Rescue
curl -X POST http://localhost:8000/run/churn

# Spend Anomaly
curl -X POST http://localhost:8000/run/spend

# Revenue Forecasting
curl -X POST http://localhost:8000/run/revenue
```

### Via Python
```python
import requests

response = requests.post("http://localhost:8000/run/pipeline")
result = response.json()

print(f"Actions: {len(result['actions'])}")
for action in result['actions'][:3]:
    print(f"  - {action['title']} (Impact: {action['impact_score']})")
```

---

## 📝 Customizing Sample Data

### Modifying Datasets
1. Edit CSV files in `aas/sample_data/`
2. Ensure column names match agent expectations
3. Add realistic values that trigger recommendations

### Adding New Datasets
1. Create new CSV in `aas/sample_data/`
2. Update agent's `load_data()` method to reference it
3. Add entry to this README

---

## 🎯 Demo Scenarios

### Scenario 1: Executive Dashboard Review
**Goal:** Show aggregate impact across all plays

```powershell
# Run all plays
.\scripts\demo_all_plays.ps1

# Then in UI:
# 1. Click "📊 Impact"
# 2. Review $3.25M estimated value
# 3. Click "📥 Export Report"
```

### Scenario 2: Sales Team Pipeline Review
**Goal:** Focus on pipeline leakage

```powershell
# In UI:
# 1. Select "Pipeline Leakage" from dropdown
# 2. Click "Run Pipeline Audit"
# 3. Review at-risk deals
# 4. Approve top 3 actions
# 5. Check Salesforce for created tasks (if live mode)
```

### Scenario 3: Customer Success Review
**Goal:** Identify churn risks

```powershell
# In UI:
# 1. Select "Churn Rescue"
# 2. Run audit
# 3. Review customers by health score
# 4. Approve retention campaigns
```

---

## 🔧 Troubleshooting

### "API is offline"
**Solution:** Start the backend first
```bash
uvicorn aas.api:app --reload
```

### "No actions recommended"
**Solution:** Check sample data is loaded correctly
```bash
ls aas/sample_data/
# Should show all 4 CSV files
```

### "Import error"
**Solution:** Ensure dependencies are installed
```bash
pip install -r requirements.txt
```

### PowerShell execution policy error
**Solution:** Allow script execution
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 📈 Impact Metrics

After running demos, view aggregate impact:

```bash
# Get impact summary
curl http://localhost:8000/api/impact/summary

# Export CSV report
curl http://localhost:8000/api/impact/export?format=csv > impact_report.csv
```

---

## 🎓 For Judges

### Quick Evaluation (5 minutes)
1. Run `.\scripts\demo_all_plays.ps1`
2. Review console output
3. Check `demo_outputs/` for saved results
4. Open UI at http://localhost:5173
5. Click "Try Demo" for guided tour

### Deep Dive (15 minutes)
1. Run each play individually via UI
2. Review action rationales (AI-generated)
3. Approve actions to see Salesforce preview
4. View Impact Dashboard
5. Export impact report
6. Review sample data files

---

**Last Updated:** 2026-01-02  
**Version:** 1.0
