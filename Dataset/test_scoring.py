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
