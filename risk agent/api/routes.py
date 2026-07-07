"""API routes for Risk Intelligence Agent.

This module defines the REST API endpoints for credit risk evaluation.

**Validates Requirements**: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7, 16.7
"""

from fastapi import APIRouter, HTTPException, Header, Depends
from typing import Optional
import asyncio
import uuid
from datetime import datetime

from agents.risk_intelligence_agent.schemas import MSMEInput, AssessmentReport
from agents.risk_intelligence_agent.workflow import evaluate_msme


router = APIRouter()


async def verify_token(authorization: Optional[str] = Header(None)) -> str:
    """Verify Bearer token in Authorization header.
    
    Args:
        authorization: Authorization header value
        
    Returns:
        Validated token string
        
    Raises:
        HTTPException: If token is missing or invalid
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Missing Authorization header"
        )
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid Authorization header format. Expected: Bearer <token>"
        )
    
    token = authorization.split(" ")[1]
    
    # TODO: Implement actual token validation logic
    # For now, accept any non-empty token
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )
    
    return token


@router.post("/evaluate", response_model=AssessmentReport)
async def evaluate_credit_risk(
    msme_input: MSMEInput,
    token: str = Depends(verify_token)
) -> AssessmentReport:
    """Evaluate MSME credit risk.
    
    This endpoint accepts MSME data and returns a comprehensive risk assessment
    including ML prediction, policy compliance, fraud detection, and explainability.
    
    Args:
        msme_input: MSME application data
        token: Validated authentication token (from header)
        
    Returns:
        AssessmentReport with complete risk assessment
        
    Raises:
        HTTPException 400: Invalid request data
        HTTPException 401: Authentication failed
        HTTPException 500: Internal server error
        HTTPException 504: Request timeout (>10 seconds)
    """
    try:
        # Set 10-second timeout for workflow execution
        result = await asyncio.wait_for(
            evaluate_msme(msme_input),
            timeout=10.0
        )
        
        return result
        
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail={
                "error": "evaluation timeout",
                "limit_seconds": 10,
                "message": "Risk assessment exceeded maximum execution time"
            }
        )
        
    except ValueError as e:
        # Validation or workflow errors
        error_id = str(uuid.uuid4())
        raise HTTPException(
            status_code=400,
            detail={
                "error_id": error_id,
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        # Internal server errors
        error_id = str(uuid.uuid4())
        print(f"Internal error {error_id}: {str(e)}")  # Log for tracking
        
        raise HTTPException(
            status_code=500,
            detail={
                "error_id": error_id,
                "message": "Internal server error during risk assessment",
                "timestamp": datetime.now().isoformat()
            }
        )


@router.get("/health")
async def health_check():
    """Health check endpoint.
    
    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "service": "risk-intelligence-agent",
        "version": "v1",
        "timestamp": datetime.now().isoformat()
    }


@router.get("/")
async def root():
    """Root endpoint with API information.
    
    Returns:
        API information
    """
    return {
        "service": "Risk Intelligence Agent",
        "version": "v1",
        "endpoints": {
            "evaluate": "POST /api/v1/evaluate",
            "health": "GET /api/v1/health"
        },
        "documentation": "/docs"
    }
