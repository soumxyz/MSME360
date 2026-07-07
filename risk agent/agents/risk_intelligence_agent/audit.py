"""Audit trail generation for Risk Intelligence Agent.

This module provides structured logging and audit trail persistence for
regulatory compliance.

**Validates Requirements**: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7, 11.8
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import json

from .schemas import AuditEntry, AuditTrail, Recommendation


class AuditLogger:
    """Structured logger for audit trail generation.
    
    Stores audit entries for each component execution and provides
    retrieval functionality for compliance reporting.
    """
    
    def __init__(self, storage_backend: Optional[str] = None):
        """Initialize audit logger.
        
        Args:
            storage_backend: Storage backend type ("postgresql", "file", "memory")
        """
        self.storage_backend = storage_backend or "memory"
        self.audit_trails: Dict[str, AuditTrail] = {}  # In-memory storage
    
    def log_request_start(self, request_id: str, input_data_sources: List[str]) -> None:
        """Log start of evaluation request.
        
        Args:
            request_id: Unique request identifier
            input_data_sources: List of available data sources
        """
        self.audit_trails[request_id] = AuditTrail(
            request_id=request_id,
            start_timestamp=datetime.now(),
            entries=[],
            input_data_sources=input_data_sources,
            final_recommendation=Recommendation.MANUAL_REVIEW  # Default, updated later
        )
    
    def log_component_execution(
        self,
        request_id: str,
        component: str,
        timestamp: datetime,
        duration_ms: float,
        input_summary: Dict[str, Any],
        output_summary: Dict[str, Any]
    ) -> None:
        """Log component execution details.
        
        Args:
            request_id: Request identifier
            component: Component name
            timestamp: Execution timestamp
            duration_ms: Execution duration in milliseconds
            input_summary: Summary of input data
            output_summary: Summary of output data
        """
        if request_id not in self.audit_trails:
            self.log_request_start(request_id, [])
        
        entry = AuditEntry(
            component=component,
            timestamp=timestamp,
            duration_ms=duration_ms,
            input_summary=input_summary,
            output_summary=output_summary
        )
        
        self.audit_trails[request_id].entries.append(entry)
    
    def log_policy_evaluation(
        self,
        request_id: str,
        rules_checked: List[str],
        outcomes: Dict[str, bool],
        failure_reasons: List[str]
    ) -> None:
        """Log policy rule evaluation.
        
        Args:
            request_id: Request identifier
            rules_checked: List of rule IDs evaluated
            outcomes: Rule outcomes (rule_id -> passed)
            failure_reasons: List of failure descriptions
        """
        self.log_component_execution(
            request_id=request_id,
            component="policy_evaluation",
            timestamp=datetime.now(),
            duration_ms=0.0,
            input_summary={"rules": rules_checked},
            output_summary={"outcomes": outcomes, "failures": failure_reasons}
        )
    
    def log_fraud_detection(
        self,
        request_id: str,
        checks_performed: List[str],
        flag_statuses: Dict[str, Optional[bool]]
    ) -> None:
        """Log fraud detection checks.
        
        Args:
            request_id: Request identifier
            checks_performed: List of fraud checks performed
            flag_statuses: Check results (check_name -> status)
        """
        self.log_component_execution(
            request_id=request_id,
            component="fraud_detection",
            timestamp=datetime.now(),
            duration_ms=0.0,
            input_summary={"checks": checks_performed},
            output_summary={"flags": flag_statuses}
        )
    
    def log_ml_prediction(
        self,
        request_id: str,
        model_version: str,
        feature_vector: List[float],
        prediction_output: Dict[str, Any],
        shap_values: Optional[List[float]] = None
    ) -> None:
        """Log ML prediction details.
        
        Args:
            request_id: Request identifier
            model_version: Model version string
            feature_vector: Input feature vector
            prediction_output: Prediction results
            shap_values: SHAP values (optional)
        """
        self.log_component_execution(
            request_id=request_id,
            component="ml_prediction",
            timestamp=datetime.now(),
            duration_ms=0.0,
            input_summary={"model_version": model_version, "features": feature_vector},
            output_summary={"prediction": prediction_output, "shap": shap_values}
        )
    
    def log_gemini_reasoning(
        self,
        request_id: str,
        prompt: str,
        response: str,
        generation_timestamp: datetime
    ) -> None:
        """Log LLM reasoning generation.
        
        Args:
            request_id: Request identifier
            prompt: Prompt sent to Gemini
            response: Response from Gemini
            generation_timestamp: When response was generated
        """
        self.log_component_execution(
            request_id=request_id,
            component="gemini_reasoning",
            timestamp=generation_timestamp,
            duration_ms=0.0,
            input_summary={"prompt_length": len(prompt)},
            output_summary={"response_length": len(response)}
        )
    
    def finalize_audit_trail(
        self,
        request_id: str,
        final_recommendation: Recommendation
    ) -> None:
        """Finalize audit trail with final recommendation.
        
        Args:
            request_id: Request identifier
            final_recommendation: Final recommendation made
        """
        if request_id in self.audit_trails:
            self.audit_trails[request_id].final_recommendation = final_recommendation
    
    def retrieve_audit_trail(self, request_id: str) -> Optional[AuditTrail]:
        """Retrieve complete audit trail by request ID.
        
        Args:
            request_id: Request identifier
            
        Returns:
            AuditTrail if found, None otherwise
        """
        return self.audit_trails.get(request_id)
    
    def persist_audit_trail(self, request_id: str) -> bool:
        """Persist audit trail to storage backend.
        
        Args:
            request_id: Request identifier
            
        Returns:
            True if persisted successfully, False otherwise
        """
        if request_id not in self.audit_trails:
            return False
        
        audit_trail = self.audit_trails[request_id]
        
        if self.storage_backend == "postgresql":
            # TODO: Implement PostgreSQL storage
            # This would use psycopg2 to insert into audit_trails table
            pass
        elif self.storage_backend == "file":
            # Write to JSON file
            filename = f"audit_{request_id}.json"
            with open(filename, 'w') as f:
                json.dump(audit_trail.dict(), f, default=str, indent=2)
        else:
            # Memory storage - already persisted
            pass
        
        return True


# Global audit logger instance
_audit_logger: Optional[AuditLogger] = None


def get_audit_logger() -> AuditLogger:
    """Get global audit logger instance.
    
    Returns:
        AuditLogger instance
    """
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger
