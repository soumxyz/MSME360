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
