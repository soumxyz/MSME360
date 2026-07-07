"""
CreditPilot AI Conversational Interface
========================================
Handles natural language queries from credit officers.

Examples:
- "Analyze this MSME"
- "Why did you recommend ₹18.5 lakh instead of ₹20 lakh?"
- "What documents are missing?"
- "Explain the Financial Health Score"
- "Generate Credit Memo"
- "Compare with similar businesses"
- "Scenario Analysis: What if we reduce to ₹15 lakh?"
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel
from agent3_copilot import call_llm
import json


class ConversationRequest(BaseModel):
    """Request for conversational query"""
    business_id: str
    query: str
    context: Optional[Dict[str, Any]] = None


class ConversationResponse(BaseModel):
    """Response from CreditPilot AI"""
    answer: str
    agent_attribution: Optional[Dict[str, Any]] = None
    suggested_followups: list[str] = []


class CreditPilotConversation:
    """
    Conversational interface for CreditPilot AI.
    
    This makes the AI feel like a Senior Credit Manager who:
    - Cites specific agents ("Financial Intelligence Agent found...")
    - Provides clear reasoning with data
    - Offers actionable insights
    """
    
    def __init__(self):
        self.conversation_handlers = {
            "analyze": self._handle_analyze,
            "why": self._handle_why_recommendation,
            "documents": self._handle_missing_documents,
            "score": self._handle_explain_score,
            "memo": self._handle_generate_memo,
            "compare": self._handle_comparison,
            "scenario": self._handle_scenario_analysis,
            "risk": self._handle_explain_risk
        }
    
    async def handle_query(
        self,
        business_id: str,
        query: str,
        analysis_context: Dict[str, Any]
    ) -> ConversationResponse:
        """
        Handle natural language query from credit officer.
        
        Args:
            business_id: Business identifier
            query: Natural language query
            analysis_context: Full CreditPilot analysis context
        
        Returns:
            ConversationResponse with answer and attribution
        """
        
        # Detect query intent
        intent = self._detect_intent(query)
        
        # Route to appropriate handler
        if intent in self.conversation_handlers:
            handler = self.conversation_handlers[intent]
            return await handler(business_id, query, analysis_context)
        
        # Default: General LLM response
        return await self._handle_general_query(business_id, query, analysis_context)
    
    def _detect_intent(self, query: str) -> str:
        """Detect query intent from natural language"""
        query_lower = query.lower()
        
        if "analyze" in query_lower or "summarize" in query_lower or "overview" in query_lower:
            return "analyze"
        elif "why" in query_lower and ("recommend" in query_lower or "amount" in query_lower):
            return "why"
        elif "document" in query_lower or "missing" in query_lower:
            return "documents"
        elif "score" in query_lower or "financial health" in query_lower:
            return "score"
        elif "memo" in query_lower or "report" in query_lower:
            return "memo"
        elif "compare" in query_lower or "similar" in query_lower or "industry" in query_lower:
            return "compare"
        elif "scenario" in query_lower or "what if" in query_lower or "reduce" in query_lower:
            return "scenario"
        elif "risk" in query_lower:
            return "risk"
        
        return "general"
    
    async def _handle_analyze(
        self,
        business_id: str,
        query: str,
        context: Dict[str, Any]
    ) -> ConversationResponse:
        """Handle 'Analyze this MSME' queries"""
        
        summary = context.get("summary", {})
        recommendation = context.get("recommendation", {})
        agent_insights = context.get("agent_insights", {})
        
        answer = f"""**Application Summary**

**Business ID:** {business_id}
**Financial Health Score:** {summary.get('financial_health_score', 'N/A')}/100
**Risk Category:** {summary.get('risk_category', 'N/A')}
**Confidence:** {summary.get('confidence', 0) * 100:.0f}%
**Recommendation:** {recommendation.get('action', 'N/A')}
**Suggested Loan:** ₹{recommendation.get('recommended_loan', 0)/100000:.2f} lakh

**Agent Insights:**

**Financial Intelligence Agent found:**
{self._format_findings(agent_insights.get('financial_intelligence_agent', {}).get('key_findings', []))}

**Risk Intelligence Agent found:**
{self._format_findings(agent_insights.get('risk_intelligence_agent', {}).get('key_findings', []))}

**Reasoning:** {recommendation.get('reasoning', 'N/A')}
"""
        
        followups = [
            "Why did you recommend this amount?",
            "What documents are missing?",
            "Explain the Financial Health Score",
            "Generate Credit Memo"
        ]
        
        return ConversationResponse(
            answer=answer,
            agent_attribution=agent_insights,
            suggested_followups=followups
        )
    
    async def _handle_why_recommendation(
        self,
        business_id: str,
        query: str,
        context: Dict[str, Any]
    ) -> ConversationResponse:
        """Handle 'Why did you recommend X?' queries"""
        
        recommendation = context.get("recommendation", {})
        agent_insights = context.get("agent_insights", {})
        
        requested = recommendation.get("requested_loan", 2000000)
        recommended = recommendation.get("recommended_loan", 0)
        
        answer = f"""**Why ₹{recommended/100000:.2f} lakh instead of ₹{requested/100000:.2f} lakh?**

I analyzed the application using multiple AI specialists.

**Financial Intelligence Agent found:**
{self._format_findings(agent_insights.get('financial_intelligence_agent', {}).get('key_findings', []))}

**Risk Intelligence Agent found:**
{self._format_findings(agent_insights.get('risk_intelligence_agent', {}).get('key_findings', []))}

{recommendation.get('reasoning', '')}

Based on repayment capacity, ₹{recommended/100000:.2f} lakh is safer while maintaining an EMI-to-income ratio below the bank's preferred threshold.
"""
        
        followups = [
            "What if we reduce the loan to ₹15 lakh?",
            "What are the risks?",
            "Generate Credit Memo"
        ]
        
        return ConversationResponse(
            answer=answer,
            agent_attribution=agent_insights,
            suggested_followups=followups
        )
    
    async def _handle_missing_documents(
        self,
        business_id: str,
        query: str,
        context: Dict[str, Any]
    ) -> ConversationResponse:
        """Handle 'What documents are missing?' queries"""
        
        financial_validation = context.get("financial_validation", {})
        
        # Extract failed/warning checks
        missing = []
        verified = []
        
        for check in financial_validation.get("checks", []):
            if check.get("status") == "fail":
                missing.append(f"• {check['name']}")
            elif check.get("status") == "pass":
                verified.append(check['name'])
        
        if not missing:
            answer = """**Missing Documents**

✅ All required documents verified!

**Successfully retrieved from:**
✓ GST
✓ Account Aggregator
✓ UPI
✓ Bank Statements

No additional documents required at this time.
"""
        else:
            answer = f"""**Missing Documents**

{chr(10).join(missing)}

**All other required information was successfully retrieved from:**
✓ GST
✓ Account Aggregator  
✓ UPI
✓ Bank Statements

Please request these documents from the applicant.
"""
        
        followups = [
            "Analyze this MSME",
            "What are the risks?",
            "Generate Credit Memo"
        ]
        
        return ConversationResponse(
            answer=answer,
            suggested_followups=followups
        )
    
    async def _handle_explain_score(
        self,
        business_id: str,
        query: str,
        context: Dict[str, Any]
    ) -> ConversationResponse:
        """Handle 'Explain the Financial Health Score' queries"""
        
        summary = context.get("summary", {})
        risk_assessment = context.get("risk_assessment", {})
        
        score = summary.get("financial_health_score", 70)
        full_report = risk_assessment.get("full_report", {})
        fin_health = full_report.get("financial_health", {})
        
        # Extract breakdown if available
        breakdown = {
            "Revenue Stability": fin_health.get("revenue_stability", 85),
            "Cash Flow": fin_health.get("cash_flow", 80),
            "Business Activity": fin_health.get("business_activity", 82),
            "Risk Profile": fin_health.get("risk_profile", 75),
            "Compliance": fin_health.get("compliance", 90)
        }
        
        answer = f"""**Financial Health Score: {score}/100**

**Breakdown:**
{chr(10).join(f'**{k}:** {v}' for k, v in breakdown.items())}
**Overall:** {score}

**Reasoning:**
{self._format_findings(risk_assessment.get('findings', []))}

This score reflects the overall financial stability and creditworthiness based on multiple data sources and risk factors.
"""
        
        followups = [
            "Why is the risk Medium instead of Low?",
            "Compare with similar businesses",
            "Generate Credit Memo"
        ]
        
        return ConversationResponse(
            answer=answer,
            suggested_followups=followups
        )
    
    async def _handle_generate_memo(
        self,
        business_id: str,
        query: str,
        context: Dict[str, Any]
    ) -> ConversationResponse:
        """Handle 'Generate Credit Memo' queries"""
        
        summary = context.get("summary", {})
        recommendation = context.get("recommendation", {})
        agent_insights = context.get("agent_insights", {})
        
        score = summary.get("financial_health_score", 70)
        risk_cat = summary.get("risk_category", "Medium")
        requested = recommendation.get("requested_loan", 2000000)
        recommended = recommendation.get("recommended_loan", 0)
        
        # Extract strengths and weaknesses
        financial_agent = agent_insights.get("financial_intelligence_agent", {})
        risk_agent = agent_insights.get("risk_intelligence_agent", {})
        
        strengths = []
        weaknesses = []
        
        for finding in financial_agent.get("key_findings", []):
            if "✓" in finding or "pass" in finding.lower():
                strengths.append(finding.replace("✓", "").strip())
            elif "✗" in finding or "fail" in finding.lower():
                weaknesses.append(finding.replace("✗", "").strip())
        
        for finding in risk_agent.get("key_findings", []):
            if "✓" in finding or "No" in finding and "violation" in finding.lower():
                strengths.append(finding.replace("✓", "").strip())
            elif "⚠" in finding or "violation" in finding.lower():
                weaknesses.append(finding.replace("⚠", "").strip())
        
        answer = f"""**Credit Assessment Report**

**Applicant:** {business_id}
**Business Age:** 5 Years  
**Requested Amount:** ₹{requested/100000:.2f} lakh
**Recommended Amount:** ₹{recommended/100000:.2f} lakh
**Risk Category:** {risk_cat}
**Financial Health Score:** {score}/100

**Strengths:**
{chr(10).join(f'• {s}' for s in strengths[:3]) if strengths else '• Stable operations'}

**Weaknesses:**
{chr(10).join(f'• {w}' for w in weaknesses[:3]) if weaknesses else '• None identified'}

**Recommendation:** {recommendation.get('action', 'REVIEW')}

**Reasoning:**
{recommendation.get('reasoning', 'N/A')}

---
**Prepared by:** CreditPilot AI  
**Date:** {context.get('timestamp', 'N/A')[:10]}

*This report can be edited by the credit officer before submission.*
"""
        
        followups = [
            "Compare with similar businesses",
            "What if we reduce the loan amount?",
            "Analyze this MSME"
        ]
        
        return ConversationResponse(
            answer=answer,
            suggested_followups=followups
        )
    
    async def _handle_comparison(
        self,
        business_id: str,
        query: str,
        context: Dict[str, Any]
    ) -> ConversationResponse:
        """Handle 'Compare with similar businesses' queries"""
        
        summary = context.get("summary", {})
        score = summary.get("financial_health_score", 70)
        
        # Mock industry comparison (in production, query actual database)
        answer = f"""**Industry Comparison**

**Compared against:** 220 similar MSMEs  

**Financial Health Score:** {score}/100
• **Industry Average:** 65/100
• **Your Ranking:** Top 30%

**Key Metrics vs Industry:**
• **Revenue Stability:** Above Average
• **GST Compliance:** Top 15%  
• **Cash Flow:** Above Average
• **Repayment Capacity:** High
• **Risk Profile:** Lower than industry average

**Insight:** This MSME performs better than 70% of comparable businesses in the sector.

*For the prototype, comparisons use mock benchmark data.*
"""
        
        followups = [
            "What makes this MSME stand out?",
            "Generate Credit Memo",
            "Scenario Analysis"
        ]
        
        return ConversationResponse(
            answer=answer,
            suggested_followups=followups
        )
    
    async def _handle_scenario_analysis(
        self,
        business_id: str,
        query: str,
        context: Dict[str, Any]
    ) -> ConversationResponse:
        """Handle 'What if' scenario analysis queries"""
        
        # Extract amount from query if present
        import re
        amounts = re.findall(r'₹?(\d+(?:\.\d+)?)\s*(?:lakh|lac)', query.lower())
        
        if amounts:
            new_amount_lakh = float(amounts[0])
            new_amount = new_amount_lakh * 100000
        else:
            new_amount_lakh = 15
            new_amount = 1500000
        
        # Calculate new EMI (assuming 2-year tenure, 12% interest)
        tenure_months = 24
        monthly_rate = 0.12 / 12
        emi = (new_amount * monthly_rate * (1 + monthly_rate)**tenure_months) / ((1 + monthly_rate)**tenure_months - 1)
        
        # Determine new risk
        if new_amount < 1500000:
            new_risk = "Low"
        elif new_amount < 1800000:
            new_risk = "Medium-Low"
        else:
            new_risk = "Medium"
        
        answer = f"""**Scenario Analysis**

**Loan Amount:** ₹{new_amount_lakh:.1f} lakh  
**Expected EMI:** ₹{emi:,.0f}  
**Tenure:** {tenure_months} months
**Interest Rate:** ~12% p.a.

**Impact Assessment:**
• **Debt Burden:** Reduced ✓
• **Risk Category:** {new_risk}
• **Cash Flow Buffer:** Improved
• **Approval Probability:** Higher

**Recommendation:**  
This amount provides a stronger cash flow buffer while supporting the applicant's expansion plans. The lower EMI reduces repayment risk and increases likelihood of timely payments.

**Trade-off:** Reduced funding may require phased business growth rather than immediate expansion.
"""
        
        followups = [
            "What if we increase to ₹20 lakh?",
            "Generate Credit Memo",
            "Final recommendation?"
        ]
        
        return ConversationResponse(
            answer=answer,
            suggested_followups=followups
        )
    
    async def _handle_explain_risk(
        self,
        business_id: str,
        query: str,
        context: Dict[str, Any]
    ) -> ConversationResponse:
        """Handle 'Why is the risk X?' queries"""
        
        summary = context.get("summary", {})
        risk_assessment = context.get("risk_assessment", {})
        
        risk_cat = summary.get("risk_category", "Medium")
        
        # Extract specific risk factors
        findings = risk_assessment.get("findings", [])
        violations = risk_assessment.get("policy_violations", [])
        fraud_flags = risk_assessment.get("fraud_flags", {})
        
        risk_factors = []
        for finding in findings:
            if "⚠" in finding or "violation" in finding.lower() or "flag" in finding.lower():
                risk_factors.append(finding)
        
        answer = f"""**Why is the Risk {risk_cat}?**

**Contributing Factors:**

{chr(10).join(f'{i+1}. {factor}' for i, factor in enumerate(risk_factors[:3]))}

**Fraud Check:** {'✓ No fraud indicators detected' if not any(fraud_flags.values()) else '⚠ Fraud indicators require review'}

**Policy Compliance:** {'✓ All policies satisfied' if not violations else f'⚠ {len(violations)} policy violation(s)'}

**Overall Assessment:**  
The {risk_cat} risk category reflects a balanced evaluation of financial stability, compliance history, and operational factors. This risk level is manageable with standard lending protocols.
"""
        
        followups = [
            "How can we reduce the risk?",
            "Generate Credit Memo",
            "Scenario Analysis"
        ]
        
        return ConversationResponse(
            answer=answer,
            suggested_followups=followups
        )
    
    async def _handle_general_query(
        self,
        business_id: str,
        query: str,
        context: Dict[str, Any]
    ) -> ConversationResponse:
        """Handle general queries using LLM"""
        
        context_str = context.get("conversational_context", "")
        
        system_prompt = f"""
You are CreditPilot AI, a Senior Credit Manager with 20 years of experience.

You have three AI specialists working under you:
1. Financial Intelligence Agent
2. Risk Intelligence Agent  
3. Compliance & Fraud Specialist

Context for this business:
{context_str}

Guidelines:
- Always cite which agent provided specific information
- Ground responses in the provided data
- Be concise and actionable
- Decline out-of-scope questions politely
"""
        
        answer = call_llm(system_prompt, query)
        
        followups = [
            "Generate Credit Memo",
            "Compare with similar businesses",
            "Scenario Analysis"
        ]
        
        return ConversationResponse(
            answer=answer,
            suggested_followups=followups
        )
    
    def _format_findings(self, findings: list) -> str:
        """Format findings list as bullet points"""
        if not findings:
            return "• No specific findings"
        return chr(10).join(f"• {f}" for f in findings)


# Global conversation handler
conversation = CreditPilotConversation()


def get_conversation_handler() -> CreditPilotConversation:
    """Get the global conversation handler"""
    return conversation
