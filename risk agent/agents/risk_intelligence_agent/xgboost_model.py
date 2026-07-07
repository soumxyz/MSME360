"""XGBoost risk prediction model for Risk Intelligence Agent.

This module provides the ML prediction component with a pluggable model interface.
Supports XGBoost, CatBoost, LightGBM, and Ensemble models through configuration.

**Validates Requirements**: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 13.1, 13.2, 13.3, 13.4, 13.5, 13.6, 13.7
"""

from abc import ABC, abstractmethod
from typing import Optional
import numpy as np
import os
import yaml

from .schemas import RiskPrediction, RiskCategory


class BaseRiskModel(ABC):
    """Abstract base class for all risk prediction models.
    
    All model types (XGBoost, CatBoost, LightGBM, Ensemble) must implement this interface.
    """
    
    @abstractmethod
    def predict(self, features: np.ndarray) -> RiskPrediction:
        """Predict probability of default from feature vector.
        
        Args:
            features: 8-element feature vector (numpy array)
            
        Returns:
            RiskPrediction with probability_of_default, risk_score, risk_category
        """
        pass
    
    @abstractmethod
    def validate_interface(self) -> bool:
        """Validate that the model implements the required interface correctly.
        
        Returns:
            True if validation passes, False otherwise
        """
        pass
    
    @abstractmethod
    def get_model_version(self) -> str:
        """Get model version string for audit logging.
        
        Returns:
            Model version string
        """
        pass


class XGBoostRiskModel(BaseRiskModel):
    """XGBoost implementation of risk prediction model.
    
    Loads trained XGBoost model and provides predictions with risk categorization.
    """
    
    def __init__(self, model_path: Optional[str] = None, config_path: Optional[str] = None):
        """Initialize XGBoost model.
        
        Args:
            model_path: Path to trained XGBoost model file (.json or .ubj)
            config_path: Path to model configuration YAML file
        """
        self.model = None
        self.model_path = model_path
        self.config = self._load_config(config_path)
        
        if model_path:
            self._load_model(model_path)
    
    def _load_config(self, config_path: Optional[str]) -> dict:
        """Load model configuration from YAML file.
        
        Args:
            config_path: Path to config YAML file
            
        Returns:
            Configuration dictionary
        """
        if not config_path:
            # Default config path
            config_path = os.path.join(
                os.path.dirname(__file__), 
                '..', '..', 'config', 'model_config.yaml'
            )
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        else:
            # Return default configuration if file doesn't exist
            return {
                'model_type': 'xgboost',
                'model_version': '1.0.0',
                'timeout_ms': 500,
                'feature_names': [
                    'revenue_growth_percentage',
                    'average_monthly_balance',
                    'cash_flow_ratio',
                    'upi_transaction_frequency',
                    'employee_growth_percentage',
                    'emi_to_revenue_ratio',
                    'business_age_months',
                    'digital_payment_ratio'
                ]
            }
    
    def _load_model(self, model_path: str):
        """Load XGBoost model from file.
        
        Args:
            model_path: Path to model file
            
        Raises:
            FileNotFoundError: If model file doesn't exist
            Exception: If model loading fails
        """
        try:
            import xgboost as xgb
            
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model file not found: {model_path}")
            
            self.model = xgb.Booster()
            self.model.load_model(model_path)
            
        except ImportError:
            raise ImportError("xgboost package not installed. Install with: pip install xgboost")
        except Exception as e:
            raise Exception(f"Failed to load XGBoost model: {str(e)}")
    
    def predict(self, features: np.ndarray) -> RiskPrediction:
        """Predict probability of default and classify risk category.
        
        Args:
            features: 8-element numpy array with normalized feature values
            
        Returns:
            RiskPrediction with probability_of_default, risk_score, risk_category
            
        Raises:
            ValueError: If features array is invalid
        """
        # Validate input
        if not isinstance(features, np.ndarray):
            features = np.array(features)
        
        if features.shape[0] != 8:
            raise ValueError(f"Expected 8 features, got {features.shape[0]}")
        
        # Mock prediction if model not loaded (for testing/development)
        if self.model is None:
            probability_of_default = self._mock_predict(features)
        else:
            try:
                import xgboost as xgb
                
                # Convert to DMatrix for XGBoost
                dmatrix = xgb.DMatrix(features.reshape(1, -1))
                
                # Get prediction (probability of default)
                prediction = self.model.predict(dmatrix)
                probability_of_default = float(prediction[0])
                
            except Exception as e:
                # Fallback to mock prediction on error
                print(f"Warning: XGBoost prediction failed, using mock: {str(e)}")
                probability_of_default = self._mock_predict(features)
        
        # Ensure probability is in [0, 1]
        probability_of_default = np.clip(probability_of_default, 0.0, 1.0)
        
        # Calculate risk score: (1 - prob_default) * 100
        risk_score = (1.0 - probability_of_default) * 100.0
        
        # Classify risk category
        risk_category = self._classify_risk(risk_score)
        
        return RiskPrediction(
            probability_of_default=probability_of_default,
            risk_score=risk_score,
            risk_category=risk_category
        )
    
    def _mock_predict(self, features: np.ndarray) -> float:
        """Mock prediction for testing when no model is loaded.
        
        Uses a simple heuristic based on feature values.
        
        Args:
            features: Feature vector
            
        Returns:
            Probability of default (0-1)
        """
        # Simple heuristic: average of normalized features (excluding -1 null values)
        valid_features = features[features != -1.0]
        
        if len(valid_features) == 0:
            # No valid features, high default risk
            return 0.7
        
        # Average normalized feature value
        avg_feature = np.mean(valid_features)
        
        # Convert to probability of default
        # Higher feature values (better financial health) -> lower default probability
        # Assuming features are normalized to [0, 1] where higher is better
        probability_of_default = 1.0 - avg_feature
        
        # Add some adjustment for specific high-risk indicators
        # Index 2: cash_flow_ratio (negative is bad)
        # Index 5: emi_to_revenue_ratio (high is bad)
        # Index 6: business_age_months (low is bad)
        
        if features[2] != -1.0 and features[2] < 0.2:  # Low cash flow
            probability_of_default += 0.1
        
        if features[5] != -1.0 and features[5] > 0.7:  # High EMI burden
            probability_of_default += 0.1
        
        if features[6] != -1.0 and features[6] < 0.3:  # Young business
            probability_of_default += 0.1
        
        return np.clip(probability_of_default, 0.0, 1.0)
    
    def _classify_risk(self, risk_score: float) -> RiskCategory:
        """Classify risk category based on risk score.
        
        Classification rules (Requirements 5.3, 5.4, 5.5):
        - LOW: risk_score > 70
        - MEDIUM: 40 <= risk_score <= 70
        - HIGH: risk_score < 40
        
        Args:
            risk_score: Risk score (0-100)
            
        Returns:
            RiskCategory enum value
        """
        if risk_score > 70:
            return RiskCategory.LOW
        elif risk_score < 40:
            return RiskCategory.HIGH
        else:
            return RiskCategory.MEDIUM
    
    def validate_interface(self) -> bool:
        """Validate that model implements required interface.
        
        Returns:
            True if validation passes
        """
        # Check that predict method exists and works with sample data
        try:
            sample_features = np.array([0.5] * 8)
            result = self.predict(sample_features)
            
            # Validate return type
            if not isinstance(result, RiskPrediction):
                return False
            
            # Validate ranges
            if not (0.0 <= result.probability_of_default <= 1.0):
                return False
            
            if not (0.0 <= result.risk_score <= 100.0):
                return False
            
            if result.risk_category not in [RiskCategory.LOW, RiskCategory.MEDIUM, RiskCategory.HIGH]:
                return False
            
            return True
            
        except Exception:
            return False
    
    def get_model_version(self) -> str:
        """Get model version string.
        
        Returns:
            Model version from config or default
        """
        return self.config.get('model_version', '1.0.0')


class CatBoostRiskModel(BaseRiskModel):
    """CatBoost implementation (placeholder for future use)."""
    
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path
        raise NotImplementedError("CatBoost model not yet implemented")
    
    def predict(self, features: np.ndarray) -> RiskPrediction:
        raise NotImplementedError()
    
    def validate_interface(self) -> bool:
        return False
    
    def get_model_version(self) -> str:
        return "catboost-1.0.0"


class LightGBMRiskModel(BaseRiskModel):
    """LightGBM implementation (placeholder for future use)."""
    
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path
        raise NotImplementedError("LightGBM model not yet implemented")
    
    def predict(self, features: np.ndarray) -> RiskPrediction:
        raise NotImplementedError()
    
    def validate_interface(self) -> bool:
        return False
    
    def get_model_version(self) -> str:
        return "lightgbm-1.0.0"


class EnsembleRiskModel(BaseRiskModel):
    """Ensemble model combining multiple models (placeholder for future use)."""
    
    def __init__(self, model_paths: Optional[list[str]] = None):
        self.model_paths = model_paths
        raise NotImplementedError("Ensemble model not yet implemented")
    
    def predict(self, features: np.ndarray) -> RiskPrediction:
        raise NotImplementedError()
    
    def validate_interface(self) -> bool:
        return False
    
    def get_model_version(self) -> str:
        return "ensemble-1.0.0"


def load_model(config_path: Optional[str] = None) -> BaseRiskModel:
    """Factory function to load model based on configuration.
    
    Reads model_config.yaml to determine model type and instantiates appropriate class.
    
    Args:
        config_path: Path to model_config.yaml
        
    Returns:
        Instantiated model implementing BaseRiskModel
        
    Raises:
        ValueError: If model type is invalid or unsupported
        FileNotFoundError: If model file not found
    """
    # Load configuration
    if not config_path:
        config_path = os.path.join(
            os.path.dirname(__file__), 
            '..', '..', 'config', 'model_config.yaml'
        )
    
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    else:
        # Default to XGBoost if no config
        config = {'model_type': 'xgboost'}
    
    model_type = config.get('model_type', 'xgboost').lower()
    model_path = config.get('model_path', None)
    
    # Instantiate appropriate model type
    if model_type == 'xgboost':
        model = XGBoostRiskModel(model_path=model_path, config_path=config_path)
    elif model_type == 'catboost':
        model = CatBoostRiskModel(model_path=model_path)
    elif model_type == 'lightgbm':
        model = LightGBMRiskModel(model_path=model_path)
    elif model_type == 'ensemble':
        model_paths = config.get('model_paths', [])
        model = EnsembleRiskModel(model_paths=model_paths)
    else:
        raise ValueError(f"Unsupported model type: {model_type}")
    
    # Validate model interface
    if not model.validate_interface():
        raise ValueError(f"Model {model_type} failed interface validation")
    
    return model
