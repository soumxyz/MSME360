# Design Spec — Agent 2 Credit Scoring Engine (ML Pipeline)

**Date:** 2026-07-07  
**Status:** Draft (Pending User Review)  
**Author:** AI Coding Assistant  

---

## 1. Objectives & Success Criteria
- **Goal**: Train a predictive regression model on transactional and GST features to determine credit readiness for NTC (New-to-Credit) MSMEs.
- **Model Output**: continuous score (0-100), risk band classification, and top 5 explanatory SHAP feature weights.
- **Success Criteria**: 
  - Zero data leakage (leakage variables dropped).
  - Validation Mean Absolute Error (MAE) < 5.0.
  - Explanations match the Hand-off JSON contract.

---

## 2. Dataset Schema & Engineering
- **Inputs**: Join `Dataset/engineered_features.csv` and `Dataset/credit_labels.csv` on `Business_ID`.
- **Target**: `Financial_Health_Score` (continuous rating).
- **Dropped Features (Leakage Risk)**:
  - `Personality_Tag`
  - `Scoring_Rationale`
  - `Confidence`
  - `Risk_Category`
  - `Business_ID`
  - `Business_Name`
- **Features to Keep**: `Average_Monthly_Revenue`, `Average_Monthly_Expense`, `Expense_Ratio`, `Cash_Buffer_Days`, `Average_Balance`, `Minimum_Balance`, `Maximum_Balance`, `Income_Volatility`, `Revenue_Growth`, `GST_Regularity_Score`, `Bounce_Count`, `Monthly_Savings_Rate`, `EMI_Ratio`, `Credit_Frequency`, `Debit_Frequency`, `Cash_Deposit_Ratio`, `Digital_Payment_Ratio`, `Business_Stability_Index`, `Growth_Index`, `Liquidity_Score`, and `Industry` (One-hot encoded).

---

## 3. Modeling Pipeline
- **Validation Splitting**: Stratified random split (70% train, 15% val, 15% test).
- **Preprocessing (Fitted on Train only)**:
  - Nominal categorical column: `OneHotEncoder` on `Industry`.
  - Numerical columns: `StandardScaler` on all numeric metrics.
  - Imputation: `SimpleImputer(strategy='median')` for robustness.
- **Model**: `XGBRegressor` with early stopping on the validation set. 
- **Explainability**: Fit a `shap.TreeExplainer` on the trained XGBoost model. Extract the top 5 absolute values for local predictions, normalize weights so they sum to 1.0, and map positive/negative signs.

---

## 4. Integration & Handoff
- Save the full pipeline as a pickle file `scoring_pipeline.pkl`.
- Include a test script `score_inference.py` that takes a business profile from the dataset, runs inference, and prints the exact JSON contract payload:
```json
{
  "business_id": "MSME042",
  "score": 78,
  "band": "Low",
  "factors": [
    {"name": "Income_Volatility", "label": "Income Volatility", "direction": "+", "weight": 0.24, "detail": "..."}
  ]
}
```
