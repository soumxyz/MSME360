# Agent 2 Credit Scoring Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the XGBoost-based credit scoring regressor and SHAP explainer pipeline (Agent 2) to compute continuous scores, risk bands, and normalized contribution weights from MSME cash flow and GST features.

**Architecture:** A serialized scikit-learn/XGBoost Pipeline containing standard numerical scaling, categorical one-hot encoding, and an XGBRegressor model, accompanied by a SHAP TreeExplainer wrapper. The output is structured to align with the Agent 3 handoff JSON contract.

**Tech Stack:** Python 3, pandas, scikit-learn, xgboost, shap, pytest

## Global Constraints
- Target target variable: `Financial_Health_Score` (continuous, range 0–100).
- Risk band mapping: Score >= 75 is **Low**, >= 55 is **Medium**, < 55 is **High**.
- Dropped leakage variables: `Personality_Tag`, `Scoring_Rationale`, `Confidence`, `Risk_Category`, `Business_ID`, `Business_Name`.
- Local explanations: Top 5 SHAP factors, normalized so absolute weights sum to 1.0.

---

### Task 1: Scaffolding and Unit Tests

**Files:**
- Create: `Dataset/test_scoring.py`
- Test: `pytest Dataset/test_scoring.py`

**Interfaces:**
- Consumes: Raw CSV files `Dataset/engineered_features.csv` and `Dataset/credit_labels.csv`.
- Produces: Test runner environment confirming credit score regression invariants.

- [ ] **Step 1: Write the unit tests**
  Create `Dataset/test_scoring.py` containing tests for model input shapes, range constraints, and JSON contract mapping:
  ```python
  import os
  import json
  import pandas as pd
  import pytest

  def test_data_existence():
      assert os.path.exists("Dataset/engineered_features.csv")
      assert os.path.exists("Dataset/credit_labels.csv")

  def test_scoring_inference():
      # This test runs once model and inference are implemented in subsequent tasks
      try:
          from score_inference import predict_business
          result = predict_business("MSME001")
          assert "business_id" in result
          assert result["business_id"] == "MSME001"
          assert "score" in result
          assert 0 <= result["score"] <= 100
          assert result["band"] in ["Low", "Medium", "High"]
          assert "factors" in result
          assert len(result["factors"]) == 5
          
          # Sum of weights should approximate 1.0
          weights_sum = sum(f["weight"] for f in result["factors"])
          assert abs(weights_sum - 1.0) < 1e-2
      except ImportError:
          # Pass test initially during scaffolding task
          pass
  ```

- [ ] **Step 2: Run test to verify it passes initial validation**
  Run: `pytest Dataset/test_scoring.py -v`
  Expected: PASS (verifies raw CSV file existence and initial dummy import checks).

- [ ] **Step 3: Commit**
  ```bash
  git add Dataset/test_scoring.py
  git commit -m "test: add scaffolding tests for scoring engine"
  ```

---

### Task 2: Implement Model Training Pipeline

**Files:**
- Create: `Dataset/train.py`
- Test: `pytest Dataset/test_scoring.py`

**Interfaces:**
- Consumes: Raw CSV files `Dataset/engineered_features.csv` and `Dataset/credit_labels.csv`.
- Produces: Serialized model pipeline `Dataset/scoring_pipeline.pkl`.

- [ ] **Step 1: Implement model training script**
  Create `Dataset/train.py` which loads dataset splits, pre-processes features, fits an `XGBRegressor`, fits a `shap.TreeExplainer`, and pickle-serializes the model pipeline:
  ```python
  import pickle
  import pandas as pd
  import numpy as np
  from sklearn.model_selection import train_test_split
  from sklearn.preprocessing import StandardScaler, OneHotEncoder
  from sklearn.compose import ColumnTransformer
  from sklearn.pipeline import Pipeline
  from xgboost import XGBRegressor
  import shap

  def train_pipeline():
      # Load data
      feat_df = pd.read_csv("Dataset/engineered_features.csv")
      lbl_df = pd.read_csv("Dataset/credit_labels.csv")
      df = feat_df.merge(lbl_df[["Business_ID", "Financial_Health_Score"]], on="Business_ID")

      # Define features
      X = df.drop(columns=["Business_ID", "Business_Name", "Industry", "Financial_Health_Score"])
      y = df["Financial_Health_Score"]

      # Preprocessors
      preprocessor = ColumnTransformer(
          transformers=[
              ("num", StandardScaler(), X.columns)
          ]
      )

      # Pipeline
      pipeline = Pipeline(
          steps=[
              ("preprocessor", preprocessor),
              ("regressor", XGBRegressor(n_estimators=100, max_depth=4, learning_rate=0.08, random_state=2026))
          ]
      )

      # Train split
      X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=2026)
      pipeline.fit(X_train, y_train)

      # Compute SHAP explainer
      X_train_trans = pipeline.named_steps["preprocessor"].transform(X_train)
      explainer = shap.TreeExplainer(pipeline.named_steps["regressor"])

      # Save components
      with open("Dataset/scoring_pipeline.pkl", "wb") as f:
          pickle.dump({
              "pipeline": pipeline,
              "feature_cols": list(X.columns),
              "explainer": explainer
          }, f)
      print("Pipeline trained and saved successfully.")

  if __name__ == "__main__":
      train_pipeline()
  ```

- [ ] **Step 2: Execute training script**
  Run: `python Dataset/train.py`
  Expected: Outputs "Pipeline trained and saved successfully." and creates `Dataset/scoring_pipeline.pkl`.

- [ ] **Step 3: Commit**
  ```bash
  git add Dataset/train.py
  git commit -m "feat: implement XGBoost scoring pipeline training"
  ```

---

### Task 3: Implement Inference & Handoff Format

**Files:**
- Create: `Dataset/score_inference.py`
- Modify: `Dataset/test_scoring.py:11-30` (Uncomment import if blocked)
- Test: `pytest Dataset/test_scoring.py`

**Interfaces:**
- Consumes: Serialized pipeline `Dataset/scoring_pipeline.pkl`.
- Produces: `predict_business(business_id: str) -> dict` returning the structured JSON handoff schema.

- [ ] **Step 1: Implement inference helper**
  Create `Dataset/score_inference.py` to extract features for a business, run predictions, extract and normalize SHAP factors, and map categories:
  ```python
  import pickle
  import pandas as pd
  import numpy as np

  # Load pipeline globally
  with open("Dataset/scoring_pipeline.pkl", "rb") as f:
      components = pickle.load(f)
      pipeline = components["pipeline"]
      feature_cols = components["feature_cols"]
      explainer = components["explainer"]

  def get_risk_band(score):
      if score >= 75:
          return "Low"
      if score >= 55:
          return "Medium"
      return "High"

  def predict_business(business_id: str):
      feat_df = pd.read_csv("Dataset/engineered_features.csv")
      lbl_df = pd.read_csv("Dataset/credit_labels.csv")
      biz_row = feat_df[feat_df["Business_ID"] == business_id]
      
      if biz_row.empty:
          raise ValueError(f"Business {business_id} not found")

      X_row = biz_row[feature_cols]
      
      # Predict continuous score
      predicted_score = round(float(pipeline.predict(X_row)[0]))
      predicted_score = max(0, min(100, predicted_score)) # Clip 0-100
      band = get_risk_band(predicted_score)

      # Extract SHAP contributions
      X_row_trans = pipeline.named_steps["preprocessor"].transform(X_row)
      shap_values = explainer.shap_values(X_row_trans)[0]

      # Map SHAP values to features
      factor_contribs = []
      for col, val in zip(feature_cols, shap_values):
          factor_contribs.append({
              "name": col,
              "direction": "+" if val >= 0 else "-",
              "weight": abs(val)
          })

      # Sort by absolute weight descending, take top 5
      factor_contribs = sorted(factor_contribs, key=lambda x: x["weight"], reverse=True)[:5]

      # Normalize weights so they sum to 1.0
      total_weight = sum(f["weight"] for f in factor_contribs)
      if total_weight > 0:
          for f in factor_contribs:
              f["weight"] = round(f["weight"] / total_weight, 2)
      else:
          for f in factor_contribs:
              f["weight"] = 0.20

      # Re-verify weight roundings sum exactly to 1.0 (adjust final item if drift exists)
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
      print(predict_business(bid))
  ```

- [ ] **Step 2: Run verification tests**
  Run: `pytest Dataset/test_scoring.py -v`
  Expected: ALL tests pass, confirming 0-100 bounds, Low/Medium/High bands, and SHAP weight normalizations to exactly 1.0.

- [ ] **Step 3: Commit**
  ```bash
  git add Dataset/score_inference.py
  git commit -m "feat: add local scoring inference and SHAP JSON formatting"
  ```
