# MSME Credit Intelligence — Dataset Handoff

**From:** Adu (Data generation)
**To:** Agent 2 (Analyst / Scoring Engine) build owner
**Date:** 2026-07-07
**Project:** IDBI Innovate 2026, Track 3 — Financial Health Score
**Reference:** ADR-01 (MSME_C_1.MD)

---

## What this is

A fully synthesized, mathematically reconciled MSME dataset covering 425 businesses across 21 industries and 12 months of activity. Built to feed Agent 2 (feature engineering + XGBoost/LightGBM + SHAP) and, downstream, Agent 3 (Credit Copilot LLM). No real customer data. No PII risk.

Every file has been checked by an independent validator with 10 integrity tests. **All 10 pass. 0 failures.** See the "Verification" section at the end for how to re-run.

---

## File inventory

Location: `outputs/` (same folder as this doc)

| File | Rows | Size | Purpose |
|---|---|---|---|
| `businesses.csv` | 425 | 68 KB | Business profiles (industry, city, size, loan info) |
| `bank_transactions.csv` | 809,958 | 80 MB | Full 12-month bank statement per business |
| `gst_summary.csv` | 5,052 | 465 KB | Monthly GST filings per registered business |
| `engineered_features.csv` | 425 | 77 KB | 20 pre-computed features per business (**Agent 2's direct input**) |
| `credit_labels.csv` | 425 | 113 KB | Target variable + score rationale |
| `generate_msme_dataset.py` | — | 60 KB | Generator (for reproducing / adding data) |
| `validate_msme_dataset.py` | — | 15 KB | Validator (proves math still reconciles) |

**Join key across every file:** `Business_ID` (format `MSME001` .. `MSME425`).

---

## Data dictionaries

### 1. `businesses.csv` — 20 columns

| Column | Type | Meaning | Example |
|---|---|---|---|
| Business_ID | str | Primary key across all files | `MSME001` |
| Business_Name | str | Trade name | `Guwahati Kirana` |
| Owner_Name | str | Proprietor | `Ayesha Mehta` |
| Industry | str | One of 21 industries (see below) | `Grocery Store` |
| City | str | Indian city | `Ahmedabad` |
| State | str | Indian state | `Gujarat` |
| Business_Age_Years | int | Years in operation | `14` |
| Owner_Age | int | Proprietor age | `52` |
| Employee_Count | int | Full-time equivalents | `7` |
| Monthly_Operating_Days | int | 25–30 | `27` |
| Average_Daily_Customers | int | Footfall estimate | `52` |
| Annual_Turnover_INR | float | Estimated ₹ turnover | `7621739.42` |
| GST_Registered | Yes/No | GSTIN status | `Yes` |
| Existing_Loan | Yes/No | Any current loan | `No` |
| Existing_EMI_INR | float | Monthly EMI (0 if no loan) | `0.0` |
| Working_Capital_INR | float | Working capital cycle amount | `515803.24` |
| Credit_Limit_INR | float | Bank-sanctioned CC/OD limit | `700686.62` |
| Business_Category | str | Micro / Small / Medium (post-2020 turnover-based) | `Micro` |
| Personality_Tag | str | Internal driver of financial behavior (see "Personalities") | `service_based` |
| Opening_Balance_INR | float | Balance at start of 12-month window | `279202.13` |

**Industries (21):** Grocery Store, Pharmacy, Medical Shop, Restaurant, Cafe, Bakery, Textile Shop, Garment Store, Hardware Store, Electronics Shop, Furniture Manufacturer, Mobile Shop, Dairy, Agriculture Supply, Printing Press, Transport Service, Logistics Company, Hotel, Automobile Workshop, Construction Contractor, Manufacturing Unit.

**Personality tags (13):** very_stable, rapidly_growing, seasonal_festival, cash_heavy, digitally_driven, debt_stressed, high_emi, declining, recovery_phase, expansion_phase, inventory_intensive, service_based, manufacturing_based. These drive the underlying transaction patterns. **Do not train on this column** — it's a leaky feature by design. Drop it before modeling.

---

### 2. `bank_transactions.csv` — 10 columns

| Column | Type | Meaning |
|---|---|---|
| Transaction_ID | str | Unique, format `MSME001-T000001` |
| Business_ID | str | Foreign key |
| Date | ISO date | `2025-07-01` .. `2026-06-30` |
| Description | str | Realistic Indian bank-statement narration |
| Transaction_Type | Credit / Debit | Side of transaction |
| Payment_Mode | enum | UPI, NEFT, RTGS, IMPS, Cash Deposit, Cash Withdrawal, Cheque |
| Category | enum | Sales, Vendor Payment, Salary, Rent, Electricity, Internet, GST, Fuel, Raw Material, Office Supplies, Insurance, Maintenance, Loan EMI, Interest, Miscellaneous |
| Credit | float | ₹ inflow (0 if Debit row) |
| Debit | float | ₹ outflow (0 if Credit row) |
| Running_Balance | float | Reconciled balance after this row |

**Data window:** July 2025 → June 2026 (12 months). **Verified invariants:** running balance = opening_balance + Σ(credit − debit), row-by-row, per business, drift < ₹0.02.

---

### 3. `gst_summary.csv` — 12 columns

One row per registered business per month. Only businesses with `GST_Registered = "Yes"` appear here.

| Column | Meaning |
|---|---|
| Business_ID | Foreign key |
| Month | `YYYY-MM` |
| Sales | Gross sales (matches Σ of Sales-category credits in bank txn for that month, drift < ₹0.5) |
| Taxable_Sales | Sales / (1 + gst_slab) |
| GST_Paid | ₹ paid via challan |
| GST_Liability | max(0, Output_Tax − ITC) — must equal GST_Paid |
| Return_Filing_Date | Actual filing date |
| Filed_On_Time | Yes/No (No iff Late_Days > 0) |
| Late_Days | Days past due (GSTR-3B due = 20th of next month) |
| Input_Tax_Credit | ITC claimed |
| Output_Tax | Sales − Taxable_Sales |
| Refund | ₹ (usually 0) |

**GST slabs used per industry:** 5% (grocery/dairy/restaurant/agri/transport/bakery), 12% (pharmacy/medical/garment/hotel/printing), 18% (hardware/electronics/mobile/furniture/logistics/auto/construction/manufacturing).

---

### 4. `engineered_features.csv` — 23 columns (20 features + 3 IDs) — **THIS IS AGENT 2's INPUT**

| Column | Meaning | Range / notes |
|---|---|---|
| Business_ID | Foreign key | |
| Business_Name | For display | drop before training |
| Industry | For display | one-hot encode if using as feature |
| Average_Monthly_Revenue | Mean over 12 months | ₹ |
| Average_Monthly_Expense | Mean over 12 months | ₹ |
| Expense_Ratio | Avg_Expense / Avg_Revenue | typically 0.75–1.10; > 1 means burning cash |
| Cash_Buffer_Days | Avg_Balance / (Avg_Expense / 30) | Negative = OD-dependent |
| Average_Balance | Mean of all transaction Running_Balances | ₹ |
| Minimum_Balance | Lowest running balance in 12 months | Negative allowed only for distressed personalities |
| Maximum_Balance | Peak running balance | ₹ |
| Income_Volatility | std(monthly revenue) / mean | 0.03–0.35 typical |
| Revenue_Growth | (last-3-mo avg − first-3-mo avg) / first-3-mo avg | −0.30 to +0.60 typical |
| GST_Regularity_Score | Fraction of months filed on time | 0.0–1.0 (0.5 for unregistered) |
| Bounce_Count | Cheque bounces in 12 months | 0–6 typical |
| Monthly_Savings_Rate | (Revenue − Expense) / Revenue | Negative for cash-burn businesses |
| EMI_Ratio | EMI / Avg_Monthly_Revenue | 0 if no loan; > 0.20 is high risk |
| Credit_Frequency | Avg # credit txns per month | 60–140 |
| Debit_Frequency | Avg # debit txns per month | 30–60 |
| Cash_Deposit_Ratio | Cash deposits / total credits | Higher for grocery, dairy |
| Digital_Payment_Ratio | UPI+NEFT+RTGS+IMPS / all txns | Higher for cafe, mobile shop |
| Business_Stability_Index | Composite (0–1); low vol + positive savings + positive growth | 0.4–0.9 |
| Growth_Index | Clipped revenue growth | −1 to +1 |
| Liquidity_Score | Composite (0–1) of cash buffer days + min balance | 0.0–1.0 |

---

### 5. `credit_labels.csv` — 10 columns — **THIS IS THE TARGET**

| Column | Meaning |
|---|---|
| Business_ID | Foreign key |
| Business_Name | For display |
| Financial_Health_Score | **0–100 continuous target** (for regressor) |
| Risk_Category | **Low / Medium / High (for classifier)**; bands are Score >= 75 / >= 55 / < 55 |
| Confidence | 0.55–0.98; inverse of income volatility, boosted by GST regularity |
| Recommended_Loan_Amount | ₹; multiple of Avg_Monthly_Revenue, scaled by risk |
| Recommended_Tenure_Months | 12 / 18 / 24 / 36 / 48 / 60 |
| Recommended_Interest_Band | Text range e.g. `10.5% - 12.5%` |
| Approval_Decision | Approve / Conditional Approval / Reject |
| Scoring_Rationale | Human-readable factor breakdown (**leaky — drop before training**) |

---

## Class balance (portfolio distribution)

- Approve (Low risk): 173 (40.7%)
- Conditional Approval (Medium risk): 166 (39.1%)
- Reject (High risk): 86 (20.2%)

Score distribution: min 24.7, mean 70.4, max 100.0. Suitable for stratified 70/15/15 train/val/test split.

---

## How to load in pandas

```python
import pandas as pd

biz = pd.read_csv("businesses.csv")
tx  = pd.read_csv("bank_transactions.csv", parse_dates=["Date"])
gst = pd.read_csv("gst_summary.csv")
feat = pd.read_csv("engineered_features.csv")
lbl = pd.read_csv("credit_labels.csv")

# For training — join features + labels
df = feat.merge(lbl[["Business_ID", "Financial_Health_Score", "Risk_Category"]],
                on="Business_ID")

# Drop leaky/display columns before modeling
X = df.drop(columns=["Business_ID", "Business_Name",
                     "Financial_Health_Score", "Risk_Category"])
X = pd.get_dummies(X, columns=["Industry"])  # one-hot encode
y_reg = df["Financial_Health_Score"]         # for regressor
y_cls = df["Risk_Category"]                  # for classifier
```

**Warning columns to drop before training** (leakage risk):
- `Personality_Tag` in businesses.csv (drives the ground truth)
- `Scoring_Rationale` in credit_labels.csv (literally the scoring formula)
- `Confidence` in credit_labels.csv (derived from same features)

---

## The JSON contract Agent 2 must produce (Agent 3 depends on this)

From ADR-01. **Do not change the schema without coordinating with Agent 3 owner.**

```json
{
  "business_id": "MSME042",
  "score": 78,
  "band": "Low",
  "factors": [
    {"name": "Income_Volatility", "direction": "+", "weight": 0.24},
    {"name": "EMI_Ratio",          "direction": "-", "weight": 0.18},
    {"name": "GST_Regularity",     "direction": "+", "weight": 0.15},
    {"name": "Cash_Buffer_Days",   "direction": "+", "weight": 0.12},
    {"name": "Bounce_Count",       "direction": "-", "weight": 0.10}
  ]
}
```

- `score`: 0–100 integer (round the regressor output)
- `band`: exactly one of `"Low"`, `"Medium"`, `"High"`
- `factors`: top 5 SHAP-ranked features, ordered by absolute contribution, weights sum ≈ 1.0
- `direction`: `"+"` if the feature pushed the score up, `"-"` if it pushed it down

---

## How to regenerate (if you need more/different data)

```bash
# Same 425 businesses, deterministic — reproduces this exact dataset
python3 generate_msme_dataset.py --count 425 --seed 20260707

# Additional batch (say a 100-row holdout set with a different seed)
python3 generate_msme_dataset.py --count 100 --start-id 500 --seed 42 --suffix _holdout

# Append to existing files instead of overwriting
python3 generate_msme_dataset.py --count 100 --start-id 500 --seed 42 --append
```

CLI flags:
- `--count N` — how many businesses (default 25)
- `--start-id N` — starting numeric suffix (default 1 → `MSME001`)
- `--seed N` — RNG seed (default 20260707)
- `--suffix _tag` — appends to every filename e.g. `businesses_tag.csv`
- `--append` — append rows to existing files instead of overwriting

Full 425-business run takes ~40 seconds.

---

## Verification — how to prove the data is clean

Run the validator. It runs 10 integrity checks and prints PASS/FAIL for each:

```bash
python3 validate_msme_dataset.py
```

Expected output ends with:

```
[PASS] 01_schema
[PASS] 02_balance_reconciliation
[PASS] 03_delta_consistency
[PASS] 04_gst_vs_revenue
[PASS] 05_negative_balance_policy
[PASS] 06_date_sequential
[PASS] 07_valid_enums
[PASS] 08_cross_file_ids
[PASS] 09_label_consistency
[PASS] 10_gst_filing_flags
TOTAL FAILURES: 0
```

**What each check enforces:**

1. Schema — all required columns present, no empty values in critical fields
2. Balance reconciliation — Running_Balance = opening + Σ(credit − debit) row-by-row
3. Delta consistency — every row's balance delta = credit − debit
4. GST vs revenue — GST.Sales matches Σ of Sales-category credits per month
5. Negative balance policy — negative balances only appear for distressed personalities, capped at −0.75× working capital
6. Date sequential — transactions ordered by date within each business
7. Valid enums — Category, Payment_Mode, Transaction_Type all from allowed sets
8. Cross-file IDs — every Business_ID in transactions/gst/features/labels exists in businesses.csv
9. Label consistency — Risk_Category matches score band; no High-risk Approvals or Low-risk Rejects
10. GST filing flags — Filed_On_Time and Late_Days agree; filing date matches due-date arithmetic

If the validator ever prints anything other than "TOTAL FAILURES: 0", **do not train on the data.** Fix the generator, re-run, re-validate.

---

## Known limitations — read before pitching

1. **Labels are rule-derived, not real repayment outcomes.** A well-tuned XGBoost will hit >95% accuracy on this dataset because the target is a deterministic function of the features. This is fine for a demo (SHAP will produce clean, sensible explanations) but do not claim the model has predictive power over real defaults. If a judge asks: "the score is a rules-based aggregation of financial health indicators — the model demonstrates that the features are learnable and the explanations are interpretable, not that it beats a bank's underwriter." That framing is accurate and defensible.

2. **Vendor names cycle from a fixed pool of ~20.** Not visible in features (aggregate stats only) but visible in `bank_transactions.csv` if someone opens it. Don't dwell on the transaction file during the demo.

3. **All GST-registered businesses file monthly (GSTR-3B).** Real MSMEs below ₹5 Cr turnover often use QRMP (quarterly). Not a modeling issue, is an accuracy-of-mock issue.

4. **No festival-week concentration.** Diwali would spike sales 3–4× in one week; our model applies a smoother monthly multiplier.

5. **Sales tickets are smoother than real POS data.** Real data has a heavier long tail.

6. **Opening balances trend generous.** Some micro businesses start with ₹3L+ cash — real micro units often don't.

None of these break the model or the demo. All of these are honest answers if asked.

---

## What Agent 2 owner is expected to deliver back

Per ADR-01 build sequence step 3:

- Feature-engineering script that reads `engineered_features.csv` (features already computed here, so this may be a passthrough or additional derivations)
- Trained XGBoost or LightGBM model (regressor for score, classifier for band — or both, choose one primary)
- SHAP explainer instance
- **The JSON contract above, produced per business_id on demand**
- Model artifacts (pickle) + a `predict(features_dict) → json` function ready to be wrapped by the FastAPI endpoint

---

## Contact

For questions on the data, the generator, or the validator: reach out to Adu.
For questions on the JSON contract: coordinate with the Agent 3 owner before changing it.
