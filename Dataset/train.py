import pickle
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from xgboost import XGBRegressor
import shap

def train_pipeline():
    # Load data
    feat_df = pd.read_csv("Dataset/engineered_features.csv")
    lbl_df = pd.read_csv("Dataset/credit_labels.csv")
    df = feat_df.merge(lbl_df[["Business_ID", "Financial_Health_Score"]], on="Business_ID")

    # Define features (Drop leaky/meta columns)
    X = df.drop(columns=["Business_ID", "Business_Name", "Industry", "Financial_Health_Score"])
    y = df["Financial_Health_Score"]

    # Preprocessor (numerical scaling)
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), X.columns)
        ]
    )

    # Pipeline definition
    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("regressor", XGBRegressor(n_estimators=100, max_depth=4, learning_rate=0.08, random_state=2026))
        ]
    )

    # Stratified-style random split (since continuous target, standard train_test_split is used)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=2026)
    pipeline.fit(X_train, y_train)

    # Evaluate validation metrics
    train_preds = pipeline.predict(X_train)
    test_preds = pipeline.predict(X_test)
    train_mae = np.mean(np.abs(train_preds - y_train))
    test_mae = np.mean(np.abs(test_preds - y_test))
    print(f"Train MAE: {train_mae:.4f}")
    print(f"Test MAE: {test_mae:.4f}")

    # Compute SHAP explainer
    X_train_trans = pipeline.named_steps["preprocessor"].transform(X_train)
    explainer = shap.TreeExplainer(pipeline.named_steps["regressor"])

    # Save serialized pipeline components
    with open("Dataset/scoring_pipeline.pkl", "wb") as f:
        pickle.dump({
            "pipeline": pipeline,
            "feature_cols": list(X.columns),
            "explainer": explainer
        }, f)
    print("Pipeline trained and saved successfully.")

if __name__ == "__main__":
    train_pipeline()
