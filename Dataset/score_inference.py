import pickle
import os
import pandas as pd
import numpy as np

# Resolve local paths relative to the current file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PIPELINE_PATH = os.path.join(BASE_DIR, "scoring_pipeline.pkl")
FEATURES_PATH = os.path.join(BASE_DIR, "engineered_features.csv")
LABELS_PATH = os.path.join(BASE_DIR, "credit_labels.csv")

# Load pipeline globally
with open(PIPELINE_PATH, "rb") as f:
    components = pickle.load(f)
    pipeline = components["pipeline"]
    feature_cols = components["feature_cols"]
    explainer = components["explainer"]

# Map of feature columns to human-readable labels and dynamic detail generators
FEATURE_METADATA = {
    "Average_Monthly_Revenue": {
        "label": "Average Monthly Revenue",
        "detail": lambda val: f"Maintains average monthly revenue of ₹{val:,.0f}."
    },
    "Average_Monthly_Expense": {
        "label": "Average Monthly Expenses",
        "detail": lambda val: f"Incurs average monthly expenses of ₹{val:,.0f}."
    },
    "Expense_Ratio": {
        "label": "Expense-to-income ratio",
        "detail": lambda val: f"Expenses run at {val * 100:.1f}% of monthly income."
    },
    "Cash_Buffer_Days": {
        "label": "Cash buffer",
        "detail": lambda val: f"Average balance covers {val:.0f} days of operating expenses."
    },
    "Average_Balance": {
        "label": "Average balance",
        "detail": lambda val: f"Maintains an average bank balance of ₹{val:,.0f}."
    },
    "Minimum_Balance": {
        "label": "Minimum balance",
        "detail": lambda val: f"Minimum balance dipped to ₹{val:,.0f} in the last 12 months."
    },
    "Maximum_Balance": {
        "label": "Maximum balance",
        "detail": lambda val: f"Peak monthly balance reached ₹{val:,.0f}."
    },
    "Income_Volatility": {
        "label": "Income volatility",
        "detail": lambda val: f"Monthly income varies ±{val * 100:.0f}% around its mean."
    },
    "Revenue_Growth": {
        "label": "Revenue growth",
        "detail": lambda val: f"Revenue grew {val * 100:+.1f}% comparing the last quarter to the first." if val >= 0 else f"Revenue declined {abs(val) * 100:.1f}% comparing the last quarter to the first."
    },
    "GST_Regularity_Score": {
        "label": "GST filing regularity",
        "detail": lambda val: f"GST returns filed on time in {val * 12:.0f} of 12 months." if val <= 1.0 else f"GST filings verified."
    },
    "Bounce_Count": {
        "label": "Cheque bounces",
        "detail": lambda val: f"{val:.0f} cheque bounces in the last 12 months."
    },
    "Monthly_Savings_Rate": {
        "label": "Savings rate",
        "detail": lambda val: f"Business retains {val * 100:.1f}% of revenue each month." if val >= 0 else f"Business runs at a monthly cash deficit of {abs(val) * 100:.1f}%."
    },
    "EMI_Ratio": {
        "label": "EMI burden",
        "detail": lambda val: f"Existing EMIs consume {val * 100:.1f}% of monthly revenue." if val > 0 else "No existing EMIs obligations found."
    },
    "Credit_Frequency": {
        "label": "Credit transactions",
        "detail": lambda val: f"Averages {val:.0f} credit transactions per month."
    },
    "Debit_Frequency": {
        "label": "Debit transactions",
        "detail": lambda val: f"Averages {val:.0f} debit transactions per month."
    },
    "Cash_Deposit_Ratio": {
        "label": "Cash deposit share",
        "detail": lambda val: f"Cash deposits represent {val * 100:.1f}% of total inflows."
    },
    "Digital_Payment_Ratio": {
        "label": "Digital payments share",
        "detail": lambda val: f"{val * 100:.1f}% of transactions are digital (UPI/NEFT/RTGS/IMPS)."
    },
    "Business_Stability_Index": {
        "label": "Stability index",
        "detail": lambda val: f"Composite stability rating of {val:.2f} on a 0–1 scale."
    },
    "Growth_Index": {
        "label": "Growth index",
        "detail": lambda val: f"Revenue growth score of {val:+.2f} on a -1 to +1 scale."
    },
    "Liquidity_Score": {
        "label": "Liquidity",
        "detail": lambda val: f"Composite liquidity index of {val:.2f} on a 0–1 scale."
    }
}

def get_risk_band(score):
    if score >= 75:
        return "Low"
    if score >= 55:
        return "Medium"
    return "High"

# Features are static for the process lifetime — load once, not per prediction
_FEAT_DF = pd.read_csv(FEATURES_PATH)

def predict_business(business_id: str):
    biz_row = _FEAT_DF[_FEAT_DF["Business_ID"] == business_id]
    
    if biz_row.empty:
        raise ValueError(f"Business {business_id} not found")

    X_row = biz_row[feature_cols]
    
    # Predict continuous score (round and clip 0-100)
    raw_pred = pipeline.predict(X_row)[0]
    predicted_score = round(float(raw_pred))
    predicted_score = max(0, min(100, predicted_score))
    band = get_risk_band(predicted_score)

    # Compute SHAP contributions
    X_row_trans = pipeline.named_steps["preprocessor"].transform(X_row)
    shap_values = explainer.shap_values(X_row_trans)[0]

    # Map SHAP values to features
    factor_contribs = []
    for col, val in zip(feature_cols, shap_values):
        val_float = float(val)
        actual_val = float(X_row[col].values[0])
        
        # Look up metadata
        meta = FEATURE_METADATA.get(col, {
            "label": col.replace("_", " "),
            "detail": lambda v: f"Metric value is {v:.2f}."
        })

        factor_contribs.append({
            "name": col,
            "label": meta["label"],
            "direction": "+" if val_float >= 0 else "-",
            "weight": abs(val_float),
            "detail": meta["detail"](actual_val)
        })

    # Sort by absolute weight descending, select top 5
    factor_contribs = sorted(factor_contribs, key=lambda x: x["weight"], reverse=True)[:5]

    # Normalize weights so they sum to 1.0
    total_weight = sum(f["weight"] for f in factor_contribs)
    if total_weight > 0:
        for f in factor_contribs:
            f["weight"] = round(f["weight"] / total_weight, 2)
    else:
        for f in factor_contribs:
            f["weight"] = 0.20

    # Ensure weights sum exactly to 1.0 by adjusting the first item
    diff = round(1.0 - sum(f["weight"] for f in factor_contribs), 2)
    if diff != 0:
        factor_contribs[0]["weight"] = round(factor_contribs[0]["weight"] + diff, 2)

    return {
        "business_id": business_id,
        "score": predicted_score,
        "band": band,
        "factors": factor_contribs
    }

if __name__ == "__main__":
    import sys
    bid = sys.argv[1] if len(sys.argv) > 1 else "MSME001"
    try:
        print(predict_business(bid))
    except Exception as e:
        print(f"Error: {e}")
