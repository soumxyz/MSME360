import pickle
import os
import pandas as pd
import numpy as np

# Resolve local paths relative to the current file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PIPELINE_PATH = os.path.join(BASE_DIR, "scoring_pipeline.pkl")

# Load pipeline globally
with open(PIPELINE_PATH, "rb") as f:
    components = pickle.load(f)
    pipeline = components["pipeline"]
    feature_cols = components["feature_cols"]
    explainer = components["explainer"]

# 5 New Indian MSME Profiles
NEW_INDIAN_MSMES = [
    {
        "Business_Name": "Surat Silk Sarees (Surat, Gujarat)",
        "Industry": "Grocery Store",  # Map to closest dataset categories
        "Average_Monthly_Revenue": 850000.0,
        "Average_Monthly_Expense": 680000.0,
        "Expense_Ratio": 0.80,
        "Cash_Buffer_Days": 28.0,
        "Average_Balance": 420000.0,
        "Minimum_Balance": 150000.0,
        "Maximum_Balance": 980000.0,
        "Income_Volatility": 0.10,
        "Revenue_Growth": 0.15,
        "GST_Regularity_Score": 1.0,
        "Bounce_Count": 0.0,
        "Monthly_Savings_Rate": 0.20,
        "EMI_Ratio": 0.0,
        "Credit_Frequency": 45.0,
        "Debit_Frequency": 62.0,
        "Cash_Deposit_Ratio": 0.15,
        "Digital_Payment_Ratio": 0.85,
        "Business_Stability_Index": 0.88,
        "Growth_Index": 0.65,
        "Liquidity_Score": 0.82
    },
    {
        "Business_Name": "Royal Hyderabadi Biryani (Hyderabad, Telangana)",
        "Industry": "Restaurant",
        "Average_Monthly_Revenue": 1200000.0,
        "Average_Monthly_Expense": 1020000.0,
        "Expense_Ratio": 0.85,
        "Cash_Buffer_Days": 12.0,
        "Average_Balance": 250000.0,
        "Minimum_Balance": 20000.0,
        "Maximum_Balance": 580000.0,
        "Income_Volatility": 0.22,
        "Revenue_Growth": -0.05,
        "GST_Regularity_Score": 0.83,
        "Bounce_Count": 1.0,
        "Monthly_Savings_Rate": 0.15,
        "EMI_Ratio": 0.05,
        "Credit_Frequency": 80.0,
        "Debit_Frequency": 110.0,
        "Cash_Deposit_Ratio": 0.45,
        "Digital_Payment_Ratio": 0.55,
        "Business_Stability_Index": 0.72,
        "Growth_Index": 0.12,
        "Liquidity_Score": 0.68
    },
    {
        "Business_Name": "Kerala Spices Emporium (Kochi, Kerala)",
        "Industry": "Grocery Store",
        "Average_Monthly_Revenue": 550000.0,
        "Average_Monthly_Expense": 460000.0,
        "Expense_Ratio": 0.83,
        "Cash_Buffer_Days": 24.0,
        "Average_Balance": 310000.0,
        "Minimum_Balance": 85000.0,
        "Maximum_Balance": 720000.0,
        "Income_Volatility": 0.18,
        "Revenue_Growth": 0.08,
        "GST_Regularity_Score": 1.0,
        "Bounce_Count": 0.0,
        "Monthly_Savings_Rate": 0.17,
        "EMI_Ratio": 0.0,
        "Credit_Frequency": 38.0,
        "Debit_Frequency": 45.0,
        "Cash_Deposit_Ratio": 0.25,
        "Digital_Payment_Ratio": 0.75,
        "Business_Stability_Index": 0.80,
        "Growth_Index": 0.45,
        "Liquidity_Score": 0.77
    },
    {
        "Business_Name": "Chennai Metal Components (Chennai, Tamil Nadu)",
        "Industry": "Medical Shop",
        "Average_Monthly_Revenue": 450000.0,
        "Average_Monthly_Expense": 495000.0,
        "Expense_Ratio": 1.10,
        "Cash_Buffer_Days": -2.0,
        "Average_Balance": -15000.0,
        "Minimum_Balance": -60000.0,
        "Maximum_Balance": 120000.0,
        "Income_Volatility": 0.25,
        "Revenue_Growth": -0.18,
        "GST_Regularity_Score": 0.58,
        "Bounce_Count": 4.0,
        "Monthly_Savings_Rate": -0.10,
        "EMI_Ratio": 0.18,
        "Credit_Frequency": 14.0,
        "Debit_Frequency": 32.0,
        "Cash_Deposit_Ratio": 0.10,
        "Digital_Payment_Ratio": 0.90,
        "Business_Stability_Index": 0.45,
        "Growth_Index": -0.55,
        "Liquidity_Score": 0.38
    },
    {
        "Business_Name": "Mumbai Cutting Chai (Mumbai, Maharashtra)",
        "Industry": "Restaurant",
        "Average_Monthly_Revenue": 300000.0,
        "Average_Monthly_Expense": 230000.0,
        "Expense_Ratio": 0.76,
        "Cash_Buffer_Days": 16.0,
        "Average_Balance": 120000.0,
        "Minimum_Balance": 35000.0,
        "Maximum_Balance": 280000.0,
        "Income_Volatility": 0.08,
        "Revenue_Growth": 0.12,
        "GST_Regularity_Score": 0.92,
        "Bounce_Count": 0.0,
        "Monthly_Savings_Rate": 0.23,
        "EMI_Ratio": 0.0,
        "Credit_Frequency": 120.0,
        "Debit_Frequency": 180.0,
        "Cash_Deposit_Ratio": 0.05,
        "Digital_Payment_Ratio": 0.95,
        "Business_Stability_Index": 0.85,
        "Growth_Index": 0.52,
        "Liquidity_Score": 0.78
    }
]

def evaluate_new_msmes():
    df = pd.DataFrame(NEW_INDIAN_MSMES)
    X = df[feature_cols]
    
    # Predict score using XGBoost Pipeline
    scores = pipeline.predict(X)
    
    # Transform and explain using SHAP TreeExplainer
    X_trans = pipeline.named_steps["preprocessor"].transform(X)
    shap_values = explainer.shap_values(X_trans)
    
    print("\n" + "="*80)
    print(" EVALUATION REPORT: SCORING ON ADDITIONAL INDIAN MSME RECORDS")
    print("="*80 + "\n")
    
    for idx, row in df.iterrows():
        score = max(0, min(100, round(float(scores[idx]))))
        name = row["Business_Name"]
        
        # Risk band mapping
        if score >= 75:
            band = "LOW RISK (Green)"
        elif score >= 55:
            band = "MEDIUM RISK (Yellow)"
        else:
            band = "HIGH RISK (Red)"
            
        print(f"Business: {name}")
        print(f"Credit Health Score: {score}/100 -> Risk Band: {band}")
        
        # Map SHAP factors
        contribs = []
        for col_idx, col in enumerate(feature_cols):
            shap_val = shap_values[idx, col_idx]
            contribs.append((col, shap_val))
            
        # Top 3 positive factors
        pos_contribs = sorted([c for c in contribs if c[1] > 0], key=lambda x: x[1], reverse=True)[:3]
        # Top 3 negative factors
        neg_contribs = sorted([c for c in contribs if c[1] < 0], key=lambda x: x[1])[:3]
        
        print("   [+] Top Positive Drivers:")
        for factor, weight in pos_contribs:
            print(f"      * {factor.replace('_', ' ')} (Contribution: +{weight:.2f})")
            
        print("   [-] Top Negative Drivers:")
        for factor, weight in neg_contribs:
            print(f"      * {factor.replace('_', ' ')} (Contribution: {weight:.2f})")
            
        print("-" * 80 + "\n")

if __name__ == "__main__":
    evaluate_new_msmes()
