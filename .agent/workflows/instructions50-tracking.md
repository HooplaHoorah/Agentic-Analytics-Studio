---
description: Instructions 50 - 20% Score Improvement Roadmap Tracking
---

# Instructions 50 Implementation Tracker

**Goal:** Drive ~20% aggregate score improvement across Innovation, Technical Execution, Impact, and User Experience.

**Timeline:** 10-day sprint (Days 1-10)

**Last Updated:** 2026-01-02

---

## Current State Audit (Completed 2026-01-02)

### ✅ Already Implemented
- **Multi-Play Architecture**: 3 plays (pipeline, churn, spend) registered in `AGENTS` dict
- **Database Integration**: Postgres schema with runs, actions, executions, opportunities
- **LLM Provider Abstraction**: OpenAI, Ollama, and rule-based fallback in `base.py`
- **Salesforce Client**: Stub implementation with credential gating in `salesforce_client.py`
- **Tableau Integration**: JWT auth + view embedding via Connected App
- **Slack Integration**: Basic notification client
- **Impact Scoring**: Actions have priority field (1=high, 2=medium, 3=low)
- **API Endpoints**: `/run/{play}`, `/approve`, `/context/actions`, `/tableau/jwt`
- **Frontend**: Basic web UI with play selector, Tableau embed, action approval

### 🟡 Partially Implemented
- **Modular Play API**: Plays inherit from `AgentPlay` base class but no formal registry/config system
- **Impact Analytics**: Priority scoring exists but no aggregate ROI dashboard
- **Error Handling**: Some try/catch blocks but not comprehensive
- **Documentation**: README exists but needs update for latest features

### ❌ Missing / Not Started
- **Revenue Forecasting Play**: Not implemented
- **Onboarding Tour**: No guided tour or first-run experience
- **Exportable Reports**: No PDF/CSV export endpoint
- **Automated Testing**: No unit tests or CI/CD
- **Interactive Slack Actions**: Plain text only, no Block Kit
- **Architecture Diagram**: Not in docs/
- **Accessibility**: No ARIA labels or a11y considerations

---

## Epic Breakdown & Ticket Tracking

### 🔴 HIGH-IMPACT (Priority 1)

#### Epic 1: Extend Hero Plays with Revenue Forecasting
**Owner:** Antigravity  
**Status:** ✅ Complete  
**Target:** Days 1-3  
**DoD:** 
- [x] New `revenue_forecasting.py` agent implemented
- [x] Play registered in `AGENTS` dict
- [x] API route `/run/revenue` functional
- [x] Sample dataset in `aas/sample_data/revenue_forecast_data.csv`
- [x] UI hook for Revenue Forecasting play
- [x] At least 1 scripted scenario for judges

**Tickets:**
- [x] **RF-1**: Create `revenue_forecasting.py` agent skeleton (inherit from `AgentPlay`)
- [x] **RF-2**: Implement `load_data()` to read sample revenue/pipeline data
- [x] **RF-3**: Implement `analyze()` to calculate velocity, forecast shortfalls
- [x] **RF-4**: Implement `recommend_actions()` to suggest budget reallocation, outreach
- [x] **RF-5**: Add sample dataset `revenue_forecast_data.csv` with historical deal data
- [x] **RF-6**: Register play in `api.py` AGENTS dict
- [x] **RF-7**: Update frontend play selector to include "revenue" option
- [x] **RF-8**: Create demo scenario script `scripts/demo_revenue_forecasting.ps1`

---

#### Epic 2: Modular Play API & Registry
**Owner:** Antigravity  
**Status:** 🟡 Partially Implemented  
**Target:** Days 2-3  
**DoD:**
- [ ] Play registry pattern (config-driven or decorator-based)
- [ ] Clear interface documentation in `docs/play_api.md`
- [ ] Example third-party play template
- [ ] Plays can be added with minimal code changes

**Tickets:**
- [ ] **MPA-1**: Design play registry interface (JSON config or Python decorator)
- [ ] **MPA-2**: Refactor `AGENTS` dict to use registry pattern
- [ ] **MPA-3**: Create `docs/play_api.md` with interface spec and examples
- [ ] **MPA-4**: Create `aas/agents/template_play.py` as third-party template
- [ ] **MPA-5**: Add validation for play registration (required methods, schema)

---

#### Epic 3: Improved User Onboarding & Guided Tour
**Owner:** Antigravity  
**Status:** 🔴 Not Started  
**Target:** Days 4-5 (parallel with Epic 1)  
**DoD:**
- [ ] Interactive first-run tour using library (e.g., intro.js or shepherd.js)
- [ ] Unified styling pass (consistent colors, typography, spacing)
- [ ] "Try a demo scenario" entry point
- [ ] Tooltips explaining mock vs. live modes

**Tickets:**
- [ ] **UX-1**: Install and integrate tour library (intro.js or shepherd.js)
- [ ] **UX-2**: Define tour steps (connect data → run audit → approve actions)
- [ ] **UX-3**: Add first-run detection (localStorage flag)
- [ ] **UX-4**: Unified CSS pass: standardize color palette, fonts, spacing
- [ ] **UX-5**: Add "Demo Mode" banner/button for quick scenario launch
- [ ] **UX-6**: Add tooltips for Salesforce/LLM mode indicators
- [ ] **UX-7**: Responsive design fixes for mobile/tablet

---

#### Epic 4: Enhanced Impact Analytics & Reporting
**Owner:** Antigravity  
**Status:** 🟡 Partially Implemented  
**Target:** Days 5-6  
**DoD:**
- [ ] Aggregate ROI dashboard showing cumulative impact
- [ ] `/reports/impact` endpoint for PDF/CSV export
- [ ] Download button in UI
- [ ] Mock savings data if no real executions

**Tickets:**
- [ ] **IA-1**: Create `/analytics/roi` endpoint to aggregate impact scores
- [ ] **IA-2**: Query DB for approved/executed actions, sum impact estimates
- [ ] **IA-3**: Create frontend dashboard component for ROI metrics
- [ ] **IA-4**: Implement `/reports/impact` endpoint (PDF generation with reportlab)
- [ ] **IA-5**: Implement CSV export option
- [ ] **IA-6**: Add "Download Report" button to UI
- [ ] **IA-7**: Seed mock savings data for demo purposes

---

#### Epic 5: Optional Salesforce Integration Framework
**Owner:** Antigravity  
**Status:** 🟡 Partially Implemented  
**Target:** Days 6-7  
**DoD:**
- [ ] Credential gate with graceful fallback (already mostly done)
- [ ] Service abstraction with clear methods
- [ ] Unit tests for stub and real modes
- [ ] Configuration guide in README

**Tickets:**
- [ ] **SF-1**: Review and harden `salesforce_client.py` credential gating
- [ ] **SF-2**: Add descriptive UI tooltips when in stub mode
- [ ] **SF-3**: Create unit tests for `create_task()` in both modes
- [ ] **SF-4**: Update `.env.example` with Salesforce credential instructions
- [ ] **SF-5**: Update README with Salesforce setup guide
- [ ] **SF-6**: Add error handling for API failures with user-friendly messages

---

### 🟡 MEDIUM-IMPACT (Priority 2)

#### Epic 6: Expand LLM Provider Support
**Owner:** Antigravity  
**Status:** 🟡 Partially Implemented  
**Target:** Days 3-4  
**DoD:**
- [ ] Anthropic/Claude provider stub
- [ ] Google Gemini provider stub
- [ ] Centralized prompt library (JSON/YAML)
- [ ] Environment variable `LLM_PROVIDER` supports new options

**Tickets:**
- [ ] **LLM-1**: Create `aas/llm/providers/anthropic.py` stub
- [ ] **LLM-2**: Create `aas/llm/providers/gemini.py` stub
- [ ] **LLM-3**: Refactor `generate_rationale()` to use provider factory
- [ ] **LLM-4**: Create `aas/llm/prompts.yaml` for centralized prompts
- [ ] **LLM-5**: Update `.env.example` with new provider options

---

#### Epic 7: Automated Testing & CI Enhancements
**Owner:** Antigravity  
**Status:** 🔴 Not Started  
**Target:** Days 7-8  
**DoD:**
- [ ] Unit tests for key API endpoints
- [ ] Integration tests for stub vs. real modes
- [ ] Pre-commit hooks (black, flake8)
- [ ] GitHub Actions workflow
- [ ] Coverage badge in README

**Tickets:**
- [ ] **TEST-1**: Create `tests/test_api.py` with tests for `/run/{play}`
- [ ] **TEST-2**: Create `tests/test_agents.py` for agent logic
- [ ] **TEST-3**: Create `tests/test_services.py` for Salesforce/Slack/Tableau
- [ ] **TEST-4**: Set up pre-commit hooks config
- [ ] **TEST-5**: Create `.github/workflows/ci.yml` for automated testing
- [ ] **TEST-6**: Generate coverage report and add badge to README

---

#### Epic 8: Data Seeding & Sample Scenarios
**Owner:** Antigravity  
**Status:** 🟡 Partially Implemented  
**Target:** Days 4-5  
**DoD:**
- [ ] Expanded sample datasets for all plays
- [ ] Scenario scripts for realistic business flows
- [ ] Easy judge testing experience

**Tickets:**
- [ ] **DATA-1**: Create `aas/data/churn_rescue_data.csv`
- [ ] **DATA-2**: Create `aas/data/spend_anomaly_data.csv`
- [ ] **DATA-3**: Create `scripts/seed_all_plays.py` to load all datasets
- [ ] **DATA-4**: Create `scripts/demo_scenarios.ps1` with 3-5 scenarios
- [ ] **DATA-5**: Document scenarios in `README_DEMO.md`

---

### 🟢 LOW-IMPACT (Priority 3)

#### Epic 9: Documentation & Outreach
**Owner:** Antigravity  
**Status:** 🟡 Partially Implemented  
**Target:** Days 8-9  
**DoD:**
- [ ] README overhaul reflecting final features
- [ ] Architecture diagram in `docs/`
- [ ] Call for contributors section

**Tickets:**
- [ ] **DOC-1**: Update README with all implemented features
- [ ] **DOC-2**: Create architecture diagram (data flow: Tableau → Postgres → LLM → Slack/SF)
- [ ] **DOC-3**: Add FAQ section to README
- [ ] **DOC-4**: Add "Contributing" section with PR guidelines
- [ ] **DOC-5**: Create `docs/architecture.md` with detailed system design

---

#### Epic 10: Slack UX Enhancements
**Owner:** Antigravity  
**Status:** 🔴 Not Started  
**Target:** Days 7-8  
**DoD:**
- [ ] Interactive Slack Block Kit messages
- [ ] Approve/Decline buttons in Slack
- [ ] Notification preferences toggle

**Tickets:**
- [ ] **SLACK-1**: Refactor `slack_client.py` to use Block Kit
- [ ] **SLACK-2**: Add interactive buttons for approve/decline
- [ ] **SLACK-3**: Create webhook handler for Slack button actions
- [ ] **SLACK-4**: Add notification toggle in `.env` or UI
- [ ] **SLACK-5**: Add email notification option (SMTP)

---

#### Epic 11: Polish & Stability
**Owner:** Antigravity  
**Status:** 🟡 Partially Implemented  
**Target:** Days 9-10  
**DoD:**
- [ ] Comprehensive error handling across API and frontend
- [ ] Performance tuning for slow endpoints
- [ ] Caching for repeated requests

**Tickets:**
- [ ] **POLISH-1**: Audit all API endpoints for unhandled exceptions
- [ ] **POLISH-2**: Add user-friendly error messages to frontend
- [ ] **POLISH-3**: Profile `/run/{play}` endpoint for performance
- [ ] **POLISH-4**: Implement caching for Tableau metadata fetches
- [ ] **POLISH-5**: Add request logging middleware
- [ ] **POLISH-6**: Final QA pass across all features

---

## Implementation Timeline

### Days 1-2: Foundation & Revenue Forecasting
- [ ] Complete Epic 1 (Revenue Forecasting) - Tickets RF-1 through RF-8
- [ ] Start Epic 5 (Salesforce Framework) - Tickets SF-1 through SF-3

### Days 3-4: Modular API & LLM Expansion
- [ ] Complete Epic 2 (Modular Play API) - Tickets MPA-1 through MPA-5
- [ ] Complete Epic 6 (LLM Providers) - Tickets LLM-1 through LLM-5
- [ ] Start Epic 3 (Onboarding) - Tickets UX-1 through UX-3

### Days 5-6: Impact Analytics & UX
- [ ] Complete Epic 3 (Onboarding) - Tickets UX-4 through UX-7
- [ ] Complete Epic 4 (Impact Analytics) - Tickets IA-1 through IA-7
- [ ] Complete Epic 5 (Salesforce) - Tickets SF-4 through SF-6

### Days 7-8: Testing & Data
- [ ] Complete Epic 7 (Testing) - Tickets TEST-1 through TEST-6
- [ ] Complete Epic 8 (Data Seeding) - Tickets DATA-1 through DATA-5
- [ ] Complete Epic 10 (Slack UX) - Tickets SLACK-1 through SLACK-5

### Days 9-10: Documentation & Final Polish
- [ ] Complete Epic 9 (Documentation) - Tickets DOC-1 through DOC-5
- [ ] Complete Epic 11 (Polish) - Tickets POLISH-1 through POLISH-6
- [ ] Final QA and submission prep

---

## Success Metrics

### Innovation & Creativity (Target: +5%)
- [ ] Revenue Forecasting play demonstrates extensibility
- [ ] Modular play API shows platform thinking
- [ ] Multi-LLM support shows forward-thinking architecture

### Technical Execution (Target: +5%)
- [ ] Automated tests with >70% coverage
- [ ] Clean error handling across all endpoints
- [ ] Performance optimizations measurable

### Potential Impact (Target: +5%)
- [ ] ROI dashboard quantifies business value
- [ ] Exportable reports provide tangible artifacts
- [ ] Sample scenarios demonstrate real-world applicability

### User Experience (Target: +5%)
- [ ] Guided tour reduces time-to-value
- [ ] Unified styling creates premium feel
- [ ] Responsive design works across devices

---

## Notes & Decisions

**2026-01-02:** Initial tracking document created. Starting with Epic 1 (Revenue Forecasting) as highest ROI/lowest dependency item.

**Next Actions:**
1. Begin RF-1: Create revenue_forecasting.py agent skeleton
2. Parallel track: Start UX-1 for onboarding tour (can work independently)
3. Review current Salesforce client for hardening opportunities
