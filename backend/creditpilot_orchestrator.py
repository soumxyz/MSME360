"""
CreditPilot AI Orchestrator
============================
Your AI Credit Officer with 20 years of experience.

This module orchestrates three AI specialists:
1. Financial Intelligence Agent (Agent 1) - Validates data quality
2. Risk Intelligence Agent (Agent 2) - Assesses credit risk
3. CreditPilot Copilot (Agent 3) - Provides conversational interface

Architecture:
    Document Upload
         ↓
    Financial Agent (validates & cleans)
         ↓
    Risk Agent (scores & analyzes)
         ↓
    CreditPilot AI (synthesizes & explains)
         ↓
    Credit Officer
"""

import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel

from agent1_intake import check_compliance_rules
from agent3_copilot import call_llm


class CreditPilotAnalysis(BaseModel):
    """Complete credit analysis from CreditPilot AI"""
    request_id: str
    business_id: str
    timestamp: str
    
    # Stage 1: Financial Agent Results
    financial_validation: Dict[str, Any]
    
    # Stage 2: Risk Agent Results
    risk_assessment: Dict[str, Any]
    
    # Stage 3: Final Synthesis
    summary: Dict[str, Any]
    recommendation: Dict[str, Any]
    agent_insights: Dict[str, Any]
    
    # Conversational context for Copilot
    conversational_context: str


class CreditPilotOrchestrator:
    """
    Senior Credit Manager AI that orchestrates specialist agents.
    
    Think of this as a team leader with three specialists:
    - Financial Intelligence Agent
    - Risk & Compliance Agent  
    - Conversational AI Assistant
    """
    
    def __init__(self):
        self.request_counter = 0
    
    async def analyze_msme(
        self,
        business_id: str,
        bank_csv_bytes: bytes,
        gst_csv_bytes: Optional[bytes],
        msme_input_data: Dict[str, Any]
    ) -> CreditPilotAnalysis:
        """
        Complete MSME credit analysis orchestrating all three agents.
        
        Flow:
        1. Financial Agent validates documents
        2. Risk Agent performs credit assessment
        3. CreditPilot synthesizes insights with attribution
        """
        self.request_counter += 1
        request_id = f"CPAL-{datetime.now().strftime('%Y%m%d')}-{self.request_counter:04d}"
        
        # =====================================================================
        # STAGE 1: Financial Intelligence Agent
        # =====================================================================
        print(f"[CreditPilot {request_id}] Stage 1: Financial Intelligence Agent")
        
        financial_verdict, financial_checks = check_compliance_rules(
            bank_csv_bytes, 
            gst_csv_bytes
        )
        
        financial_validation = {
            "agent": "Financial Intelligence Agent",
            "status": financial_verdict,  # GREEN, YELLOW, RED
            "checks": financial_checks,
            "findings": self._extract_financial_findings(financial_checks, financial_verdict)
        }
        
        # If RED status, stop here and return early rejection
        if financial_verdict == "RED":
            return CreditPilotAnalysis(
                request_id=request_id,
                business_id=business_id,
                timestamp=datetime.now().isoformat(),
                financial_validation=financial_validation,
                risk_assessment={
                    "agent": "Risk Intelligence Agent",
                    "status": "NOT_RUN",
                    "reason": "Financial validation failed"
                },
                summary={
                    "decision": "REJECT",
                    "reason": "Failed financial validation checks",
                    "confidence": 0.99
                },
                recommendation={
                    "action": "REJECT",
                    "loan_amount": 0,
                    "reasoning": "Critical data quality issues detected by Financial Intelligence Agent"
                },
                agent_insights={
                    "financial_agent": financial_validation,
                    "risk_agent": {"status": "NOT_RUN"}
                },
                conversational_context=self._build_rejection_context(financial_validation)
            )
        
        # =====================================================================
        # STAGE 2: Risk Intelligence Agent
        # =====================================================================
        print(f"[CreditPilot {request_id}] Stage 2: Risk Intelligence Agent")
        
        # Import here to avoid circular dependency
        from agents.risk_intelligence_agent.workflow import evaluate_msme
        from agents.risk_intelligence_agent.schemas import MSMEInput
        
        # Convert dict to Pydantic model
        msme_input = MSMEInput(**msme_input_data)
        
        # Run risk assessment
        risk_report = await evaluate_msme(msme_input)
        
        # Convert to dict
        if hasattr(risk_report, "model_dump"):
            risk_dict = risk_report.model_dump()
        elif hasattr(risk_report, "dict"):
            risk_dict = risk_report.dict()
        else:
            risk_dict = risk_report
        
        risk_assessment = {
            "agent": "Risk Intelligence Agent",
            "status": "COMPLETED",
            "score": risk_dict.get("eligibility_score", 70),
            "risk_category": risk_dict.get("risk_category", "Medium"),
            "confidence": risk_dict.get("confidence", 0.85),
            "findings": self._extract_risk_findings(risk_dict),
            "fraud_flags": risk_dict.get("fraud_flags", {}),
            "policy_violations": risk_dict.get("policy_violations", []),
            "full_report": risk_dict,
        }
        
        # =====================================================================
        # STAGE 3: CreditPilot Synthesis
        # =====================================================================
        print(f"[CreditPilot {request_id}] Stage 3: Synthesizing insights")
        
        summary, recommendation, agent_insights = self._synthesize_analysis(
            financial_validation,
            risk_assessment,
            business_id,
            msme_input_data,
        )
        
        conversational_context = self._build_conversational_context(
            business_id,
            financial_validation,
            risk_assessment,
            summary,
            recommendation
        )
        
        return CreditPilotAnalysis(
            request_id=request_id,
            business_id=business_id,
            timestamp=datetime.now().isoformat(),
            financial_validation=financial_validation,
            risk_assessment=risk_assessment,
            summary=summary,
            recommendation=recommendation,
            agent_insights=agent_insights,
            conversational_context=conversational_context
        )
    
    def _extract_financial_findings(self, checks: List[Dict], verdict: str) -> List[str]:
        """Extract key findings from Financial Agent checks"""
        findings = []
        
        for check in checks:
            if check.get("status") == "pass":
                findings.append(f"✓ {check['name']}: {check.get('message', 'Passed')}")
            elif check.get("status") == "warn":
                findings.append(f"⚠ {check['name']}: {check.get('message', 'Warning')}")
            else:
                findings.append(f"✗ {check['name']}: {check.get('message', 'Failed')}")
        
        return findings
    
    def _extract_risk_findings(self, risk_dict: Dict) -> List[str]:
        """Extract key findings from Risk Agent assessment"""
        findings = []
        
        score = risk_dict.get("eligibility_score", 70)
        risk_cat = risk_dict.get("risk_category", "Medium")
        
        findings.append(f"Credit Score: {score}/100 ({risk_cat} Risk)")
        
        # Extract from financial health if available
        fin_health = risk_dict.get("financial_health", {})
        if fin_health:
            findings.append(f"Financial Health: {fin_health.get('overall_score', 'N/A')}/100")
        
        # Policy violations
        violations = risk_dict.get("policy_violations", [])
        if violations:
            findings.append(f"Policy Violations: {len(violations)} detected")
        else:
            findings.append("✓ No policy violations detected")
        
        # Fraud flags
        fraud_flags = risk_dict.get("fraud_flags", {})
        flagged = sum(1 for v in fraud_flags.values() if v)
        if flagged > 0:
            findings.append(f"⚠ Fraud Flags: {flagged} raised")
        else:
            findings.append("✓ No fraud indicators detected")
        
        return findings
    
    def _synthesize_analysis(
        self,
        financial: Dict,
        risk: Dict,
        business_id: str,
        msme_input_data: Optional[Dict[str, Any]] = None,
    ) -> tuple:
        """Synthesize insights from both agents into final recommendation"""

        score = risk["score"]
        risk_category = risk["risk_category"]
        confidence = risk["confidence"]

        # Determine decision
        msme_input_data = msme_input_data or {}
        if financial["status"] == "RED":
            decision = "REJECT"
            loan_amount = 0
        elif score >= 75:
            decision = "APPROVE"
            loan_amount = self._calculate_loan_amount(risk, score, msme_input_data)
        elif score >= 55:
            decision = "CONDITIONAL_APPROVAL"
            loan_amount = self._calculate_loan_amount(risk, score, msme_input_data) * 0.8
        else:
            decision = "REJECT"
            loan_amount = 0
        
        summary = {
            "business_id": business_id,
            "financial_health_score": score,
            "risk_category": risk_category,
            "confidence": confidence,
            "decision": decision
        }
        
        recommendation = {
            "action": decision,
            "requested_loan": 2000000,  # Default ₹20 lakh
            "recommended_loan": int(loan_amount),
            "reasoning": self._build_reasoning(financial, risk, decision, loan_amount),
            "conditions": self._build_conditions(financial, risk, decision)
        }
        
        agent_insights = {
            "financial_intelligence_agent": {
                "status": financial["status"],
                "key_findings": financial["findings"][:3]  # Top 3
            },
            "risk_intelligence_agent": {
                "score": score,
                "risk_category": risk_category,
                "key_findings": risk["findings"][:3]  # Top 3
            }
        }
        
        return summary, recommendation, agent_insights
    
    def _calculate_loan_amount(self, risk: Dict, score: int, msme_input_data: Optional[Dict] = None) -> float:
        """Calculate recommended loan amount from the applicant's actual monthly revenue.

        Priority order for the revenue signal:
          1. Mean of `gst_data.monthly_revenue` from the input (real GST filings, when present)
          2. `annual_turnover / 12` from GST data
          3. Mean of `account_aggregator_data.monthly_inflows` (bank inflow proxy)
          4. Report-level `financial_health.monthly_revenue` if the risk agent surfaces it
        Only if all four are absent do we fall back to a stated constant; that constant is
        no longer a headline number pretending to be derived.
        """
        monthly_revenue: Optional[float] = None

        def _mean(seq):
            vals = [float(v) for v in (seq or []) if v is not None]
            return sum(vals) / len(vals) if vals else None

        if msme_input_data:
            gst = msme_input_data.get("gst_data") or {}
            monthly_revenue = _mean(gst.get("monthly_revenue"))
            if monthly_revenue is None and gst.get("annual_turnover"):
                monthly_revenue = float(gst["annual_turnover"]) / 12
            if monthly_revenue is None:
                aa = msme_input_data.get("account_aggregator_data") or {}
                monthly_revenue = _mean(aa.get("monthly_inflows"))

        if monthly_revenue is None:
            fin_health = (risk.get("full_report") or {}).get("financial_health") or {}
            if fin_health.get("monthly_revenue"):
                monthly_revenue = float(fin_health["monthly_revenue"])

        # Last-resort fallback: signal via zero rather than a made-up ₹6L constant.
        if monthly_revenue is None or monthly_revenue <= 0:
            return 0.0

        base_amount = monthly_revenue * 3
        score_multiplier = score / 100
        recommended = base_amount * score_multiplier

        # Cap at ₹20 lakh max
        return min(recommended, 2000000)
    
    def _build_reasoning(
        self,
        financial: Dict,
        risk: Dict,
        decision: str,
        loan_amount: float
    ) -> str:
        """Build human-readable reasoning for recommendation"""
        
        if decision == "REJECT":
            return (
                "Based on analysis by Financial Intelligence Agent and Risk Intelligence Agent, "
                "this application does not meet minimum criteria for approval. "
                f"Financial validation status: {financial['status']}. "
                "Recommend rejection or request additional documentation."
            )
        
        score = risk["score"]
        risk_cat = risk["risk_category"]
        
        if decision == "APPROVE":
            return (
                f"I analyzed the application using multiple AI specialists. "
                f"Financial Intelligence Agent found: {', '.join(financial['findings'][:2])}. "
                f"Risk Intelligence Agent found: {', '.join(risk['findings'][:2])}. "
                f"Based on repayment capacity and risk profile ({risk_cat}), "
                f"₹{loan_amount/100000:.1f} lakh is recommended while maintaining healthy cash flow."
            )
        
        # CONDITIONAL_APPROVAL
        return (
            f"Credit score of {score}/100 indicates {risk_cat} risk. "
            f"Conditional approval recommended for ₹{loan_amount/100000:.1f} lakh "
            "with additional monitoring or collateral requirements."
        )
    
    def _build_conditions(
        self,
        financial: Dict,
        risk: Dict,
        decision: str
    ) -> List[str]:
        """Build conditions for conditional approvals"""
        
        if decision != "CONDITIONAL_APPROVAL":
            return []
        
        conditions = []
        
        # Check for warnings in financial validation
        for check in financial.get("checks", []):
            if check.get("status") == "warn":
                conditions.append(f"Verify: {check['name']}")
        
        # Check for policy violations
        violations = risk.get("policy_violations", [])
        if violations:
            conditions.append("Address policy violations before final approval")
        
        # Check for fraud flags
        fraud_flags = risk.get("fraud_flags", {})
        if any(fraud_flags.values()):
            conditions.append("Manual review required due to fraud indicators")
        
        if not conditions:
            conditions.append("Standard monitoring protocols apply")
        
        return conditions
    
    def _build_conversational_context(
        self,
        business_id: str,
        financial: Dict,
        risk: Dict,
        summary: Dict,
        recommendation: Dict
    ) -> str:
        """Build context for CreditPilot conversational AI"""
        
        context = f"""
CreditPilot AI Analysis Context for {business_id}

FINANCIAL INTELLIGENCE AGENT FINDINGS:
Status: {financial['status']}
{chr(10).join(f'- {finding}' for finding in financial['findings'])}

RISK INTELLIGENCE AGENT FINDINGS:
Score: {risk['score']}/100
Risk Category: {risk['risk_category']}
Confidence: {risk['confidence']:.1%}
{chr(10).join(f'- {finding}' for finding in risk['findings'])}

FINAL RECOMMENDATION:
Decision: {recommendation['action']}
Requested: ₹{recommendation['requested_loan']/100000:.1f} lakh
Recommended: ₹{recommendation['recommended_loan']/100000:.1f} lakh
Reasoning: {recommendation['reasoning']}
"""
        
        return context.strip()
    
    def _build_rejection_context(self, financial: Dict) -> str:
        """Build context for rejected applications"""
        
        return f"""
CreditPilot AI Analysis - REJECTED

FINANCIAL INTELLIGENCE AGENT FINDINGS:
Status: {financial['status']} (FAILED)
{chr(10).join(f'- {finding}' for finding in financial['findings'])}

RECOMMENDATION:
This application failed financial validation checks and cannot proceed to risk assessment.
Request corrected documentation or reject the application.
"""


# Global orchestrator instance
orchestrator = CreditPilotOrchestrator()


def get_orchestrator() -> CreditPilotOrchestrator:
    """Get the global CreditPilot orchestrator instance"""
    return orchestrator
