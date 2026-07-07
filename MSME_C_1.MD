# ADR-01: MSME Credit Intelligence Workspace — Architecture for IDBI Innovate 2026 (Track 3)

**Status:** Accepted (final build plan)
**Date:** 2026-07-07
**Deciders:** Adu / build team

## Context

Track 3 (Financial Health Score) asks for a data-driven methodology to assess the financial health of MSMEs / individuals who lack traditional credit documents (New-to-Credit, New-to-Bank). IDBI provides sandbox banking APIs and synthetic transaction data to shortlisted teams post-registration; nothing is public yet. The exact event format (single build weekend vs. multi-week program — Eventopia lists June 9–Aug 21, "hybrid, 73 days") is unconfirmed, so this plan assumes the tighter constraint: a short, hackathon-style build window, with the understanding it can be stretched if the real format is longer.

Three architectural options were evaluated before settling on this one.

## Decision

Build a lean **3-agent MSME Credit Intelligence Workspace**: an Intake & Verification Agent, an Analyst (Scoring) Agent, and a Credit Copilot Agent — grounded on two mockable alternative-data sources (bank statement + GST summary), with SHAP-based explainability and human-in-the-loop approval at every decision point.

## Options Considered

### Option A: Single-pipeline Financial Health Score (no agents)

| Dimension | Assessment |
|---|---|
| Complexity | Low |
| Cost | Minimal compute, fastest build |
| Scalability | Fine for a demo |
| Team familiarity | High — standard ML pipeline |

**Pros:** Fastest to build, lowest execution risk, still solves the stated problem.
**Cons:** Indistinguishable from what most other teams will submit — a dashboard with a score. Weak differentiation.

### Option B: Full 6-Agent Workspace (GST, Banking, UPI, Financial Health orchestrator, Risk & Fraud, Copilot)

| Dimension | Assessment |
|---|---|
| Complexity | High |
| Cost | High — four+ data ecosystems to mock, a fraud model with no labeled data |
| Scalability | Good on paper |
| Team familiarity | Low for UPI/AA/EPFO integration and fraud detection specifically |

**Pros:** Most impressive-sounding architecture; strong narrative.
**Cons:** Not realistically deliverable in a short window. The fraud/risk agent has no real signal without labeled fraud data — it would be faked, and sophisticated judges catch that under direct questioning. Most build hours go into faking four data sources instead of improving the one thing being judged: is the score any good.

### Option C: Lean 3-Agent Workspace (chosen)

| Dimension | Assessment |
|---|---|
| Complexity | Medium |
| Cost | Moderate — two data sources, one ML model, one grounded LLM call |
| Scalability | Good — clean separation of concerns |
| Team familiarity | Medium-high |

**Pros:** Genuinely differentiated from Option A (a real, inspectable agent handoff), realistically buildable, explainable by design, leaves UPI/AA/EPFO as an honest roadmap slide instead of a fake integration.
**Cons:** Still requires two believable mock datasets, not one. The Copilot needs strict grounding discipline (structured JSON in, no raw-data access) to avoid hallucinating answers.

## Trade-off Analysis

Option C sits at the point of maximum credible differentiation per hour of build time available. Option A is safest but forgettable. Option B is most impressive on a slide but has the highest collapse risk — one pointed question about the fraud agent or the UPI pipeline exposes it as unbuilt. Option C's defining detail is the structured-JSON handoff between the Analyst and Copilot agents: it's the one part of the architecture a judge can ask about and get a real, verifiable answer to, rather than a hand-wave.

## Consequences

- Easier: the demo narrative, technical Q&A defense, and the explainability requirement that credit-scoring judges specifically look for.
- Harder: two mock data formats (bank statement + GST) must both look plausible, not one.
- To revisit: if the real IDBI Innovate format turns out to be the longer multi-week program suggested by the Eventopia listing, Option B becomes more feasible and worth reconsidering. This is a live open question, not resolved by this plan — confirm the actual format once registered.

---

## End-to-End Architecture

```
                         MSME Applicant
                               │
                     Uploads bank statement + GST summary
                               │
                               ▼
                ┌───────────────────────────────┐
                │  AGENT 1 — Intake & Verify     │
                │  (rule-based, no ML)           │
                │  - checks date range coverage  │
                │  - checks required columns     │
                │  - checks GST/bank consistency │
                └───────────────┬───────────────┘
                                │
                  Readiness flag + cleaned data
                                │
                                ▼
                ┌───────────────────────────────┐
                │  AGENT 2 — Analyst             │
                │  (feature engineering + model) │
                │  - income volatility           │
                │  - expense/income ratio        │
                │  - cash buffer days            │
                │  - bounced payment count       │
                │  - revenue trend               │
                │  - GST turnover growth         │
                │  - GST filing regularity       │
                │  → XGBoost / LightGBM          │
                │  → SHAP explanation            │
                └───────────────┬───────────────┘
                                │
              Structured JSON: {score, band, factors}
                                │
                                ▼
                ┌───────────────────────────────┐
                │  AGENT 3 — Credit Copilot      │
                │  (LLM, grounded on JSON only)  │
                │  - explains the score          │
                │  - answers banker questions    │
                │  - drafts credit memo          │
                │  - recommends loan amount      │
                └───────────────┬───────────────┘
                                │
                                ▼
                   Credit Officer Dashboard
              (score card + chat + audit log view)
                                │
                                ▼
                Human Decision (approve / reject / request more info)
                                │
                                ▼
                      Logged to Audit Trail
              (every score, every Copilot answer, timestamped)
```

## Component Detail

**Agent 1 — Intake & Verification**
Input: raw uploaded bank statement CSV + GST summary CSV.
Logic: plain Python validation — minimum 6 months coverage, required columns present, no internal contradictions in GST turnover figures month to month.
Output: readiness flag (green/yellow/red) + a list of missing/flagged items, passed forward only if not red.
Build effort: ~half a day. No model required.

**Agent 2 — Analyst (Scoring Engine)**
Input: verified bank + GST data.
Logic: feature engineering (7 features listed above) → XGBoost/LightGBM classifier or regressor → SHAP values ranked by contribution.
Output: `{ "score": 0-100, "band": "Low|Medium|High", "factors": [{"name": "...", "direction": "+/-", "weight": ...}] }`.
Build effort: the largest single chunk of time — this is the real product.

**Agent 3 — Credit Copilot**
Input: Agent 2's JSON only — never raw transaction data directly, which is what keeps it from inventing numbers.
Logic: one LLM call (OpenAI or Gemini API) with a system prompt constraining it to answer strictly from the supplied JSON and cite specific factors.
Output: natural-language answers, a draftable credit memo, a suggested loan amount/range.
Build effort: fast once Agent 2's output format is stable — this is a prompt-engineering task, not a model-training one.

**Audit Trail**
Every score computation and every Copilot exchange gets a timestamped row in SQLite: what was asked, what data was used, what was answered. This is what makes "human-in-the-loop, fully auditable" true rather than a slide claim.

## Tech Stack

- **Data / features:** Python, pandas, numpy
- **Model:** XGBoost or LightGBM, scikit-learn for splitting/evaluation
- **Explainability:** SHAP
- **Copilot:** OpenAI or Gemini API, single grounded call — no LangGraph/CrewAI orchestration needed for 3 agents at this scale
- **Backend:** FastAPI (serves Agent 1 + 2 + 3 as endpoints)
- **Frontend:** Streamlit (upload, score card, trend chart, chat interface)
- **Storage:** SQLite (mock data + audit log)
- **Deployment:** local for demo, or Streamlit Community Cloud / Render if a live link is wanted

## Build Sequence (phase-based, compress or stretch to actual event length)

1. Build synthetic bank statement + GST generators (believable, varied across 10-15 sample businesses spanning healthy/risky/ambiguous).
2. Build Agent 1 (validation rules).
3. Build Agent 2: features → model → SHAP → structured JSON output. Validate scores make sense across the sample businesses.
4. Build Agent 3: grounded Copilot call against Agent 2's JSON, test for hallucination (ask it something not in the JSON — it should decline, not invent).
5. Build Streamlit dashboard wiring all three agents together, plus the audit log view.
6. Full run-through on all sample businesses, fix anything that looks wrong end to end.
7. Pitch prep: lead with the NTC/NTB problem, walk one business through Agent 1 → 2 → 3 live, name the roadmap (UPI/AA/EPFO) honestly as future work, not built work.

## Action Items

1. [ ] Confirm actual IDBI Innovate 2026 format/timeline before finalizing phase durations.
2. [ ] Build synthetic bank + GST data generator.
3. [ ] Implement Agent 1 (Intake & Verification).
4. [ ] Implement Agent 2 (Analyst: features, model, SHAP, JSON output).
5. [ ] Implement Agent 3 (Credit Copilot, grounded prompt).
6. [ ] Build Streamlit dashboard + SQLite audit log.
7. [ ] Validate against 10-15 sample businesses.
8. [ ] Prepare pitch script and live demo path.
