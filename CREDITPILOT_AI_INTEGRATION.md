# CreditPilot AI - Complete Integration Guide

## 🎯 Overview

**CreditPilot AI** is your AI Credit Officer with 20 years of experience, orchestrating three specialist agents to provide comprehensive MSME credit evaluation.

### **The Innovation**

Unlike simple chatbots, CreditPilot AI acts as a **team leader** managing AI specialists:

```
Financial Intelligence Agent
         │
         ▼
Risk & Compliance Agent
         │
         ▼
    CreditPilot AI
         │
         ▼
   Credit Officer
```

The Credit Officer interacts with **one intelligent assistant** while specialist agents work behind the scenes.

---

## 🏗️ Architecture

### **Three-Agent System**

#### **Agent 1: Financial Intelligence Agent**
- **Location:** `backend/agent1_intake.py`
- **Purpose:** Validates data quality and compliance
- **Checks:**
  - Bank statement completeness
  - GST filing consistency
  - Data format validation
  - Coverage requirements (180+ days)
  - Balance reconciliation
- **Output:** GREEN/YELLOW/RED status with findings

#### **Agent 2: Risk Intelligence Agent**
- **Location:** `risk agent/agents/risk_intelligence_agent/`
- **Purpose:** Comprehensive credit risk assessment
- **Features:**
  - 8 ML features engineering
  - XGBoost prediction model
  - 9 policy rules engine
  - 6 fraud detection patterns
  - SHAP explainability
  - Financial health scoring
- **Output:** Credit score, risk category, fraud flags, recommendations

#### **Agent 3: CreditPilot Copilot**
- **Location:** `backend/agent3_copilot.py` + `creditpilot_conversation.py`
- **Purpose:** Conversational interface with LLM reasoning
- **Features:**
  - Groq LLM integration
  - Natural language understanding
  - Agent attribution ("Financial Intelligence Agent found...")
  - Scenario analysis
  - Credit memo generation
- **Output:** Human-readable explanations with context

### **Orchestrator**

**Location:** `backend/creditpilot_orchestrator.py`

The orchestrator coordinates all three agents in sequence:

1. **Stage 1:** Financial Agent validates documents
2. **Stage 2:** Risk Agent performs assessment (only if Stage 1 passes)
3. **Stage 3:** CreditPilot synthesizes insights with attribution

---

## 🚀 API Endpoints

### **1. Unified Analysis Endpoint**

```http
POST /api/creditpilot/analyze
```

**Purpose:** Run complete analysis orchestrating all three agents

**Request:**
```
FormData:
- business_id: string
- bank_file: file (CSV)
- gst_file: file (CSV, optional)
- msme_data: JSON string (MSMEInput schema)
```

**Response:**
```json
{
  "request_id": "CPAL-20260707-0001",
  "business_id": "MSME001",
  "timestamp": "2026-07-07T21:30:00",
  
  "financial_validation": {
    "agent": "Financial Intelligence Agent",
    "status": "GREEN",
    "findings": [
      "✓ Bank statement coverage: 364 days",
      "✓ GST compliance: 12/12 filings on time",
      "✓ Balance reconciliation: Passed"
    ]
  },
  
  "risk_assessment": {
    "agent": "Risk Intelligence Agent",
    "status": "COMPLETED",
    "score": 85,
    "risk_category": "Low",
    "confidence": 0.94,
    "findings": [
      "Credit Score: 85/100 (Low Risk)",
      "Financial Health: 89/100",
      "✓ No policy violations detected",
      "✓ No fraud indicators detected"
    ],
    "fraud_flags": {},
    "policy_violations": []
  },
  
  "summary": {
    "business_id": "MSME001",
    "financial_health_score": 85,
    "risk_category": "Low",
    "confidence": 0.94,
    "decision": "APPROVE"
  },
  
  "recommendation": {
    "action": "APPROVE",
    "requested_loan": 2000000,
    "recommended_loan": 1850000,
    "reasoning": "Financial Intelligence Agent found: GST turnover increased 18%, average monthly revenue ₹6.2 lakh, healthy cash flow. Risk Intelligence Agent found: No existing loans, seasonal cash flow stable, no fraud detected. Based on repayment capacity, ₹18.5 lakh is recommended while maintaining EMI-to-income ratio below threshold.",
    "conditions": []
  },
  
  "agent_insights": {
    "financial_intelligence_agent": {
      "status": "GREEN",
      "key_findings": [...]
    },
    "risk_intelligence_agent": {
      "score": 85,
      "risk_category": "Low",
      "key_findings": [...]
    }
  },
  
  "conversational_context": "..."
}
```

### **2. Conversational Interface**

```http
POST /api/creditpilot/chat
```

**Purpose:** Natural language queries with agent attribution

**Request:**
```json
{
  "business_id": "MSME001",
  "query": "Why did you recommend ₹18.5 lakh instead of ₹20 lakh?",
  "context": { } // Optional, loaded from DB if omitted
}
```

**Response:**
```json
{
  "answer": "**Why ₹18.5 lakh instead of ₹20 lakh?**\n\nI analyzed the application using multiple AI specialists.\n\n**Financial Intelligence Agent found:**\n• GST turnover increased by 18%\n• Average monthly revenue ₹6.2 lakh\n• Healthy cash flow\n\n**Risk Intelligence Agent found:**\n• No existing loans\n• Seasonal cash flow stable\n• No fraud detected\n\nBased on repayment capacity, ₹18.5 lakh is safer while maintaining an EMI-to-income ratio below the bank's preferred threshold.",
  
  "agent_attribution": {
    "financial_intelligence_agent": {...},
    "risk_intelligence_agent": {...}
  },
  
  "suggested_followups": [
    "What if we reduce the loan to ₹15 lakh?",
    "What are the risks?",
    "Generate Credit Memo"
  ]
}
```

### **3. Status Check**

```http
GET /api/creditpilot/status/{business_id}
```

**Response:**
```json
{
  "business_id": "MSME001",
  "analyzed": true,
  "timestamp": "2026-07-07T21:30:00",
  "score": 85,
  "risk_category": "Low",
  "recommendation": "APPROVE",
  "request_id": "CPAL-20260707-0001"
}
```

---

## 💬 Conversational Features

### **Supported Queries**

| Query Type | Example | Response |
|------------|---------|----------|
| **Analysis** | "Analyze this MSME" | Complete summary with scores and recommendations |
| **Why Recommendation** | "Why ₹18.5 lakh instead of ₹20 lakh?" | Reasoning with agent attribution |
| **Documents** | "What documents are missing?" | Document checklist |
| **Score Explanation** | "Explain the Financial Health Score" | Score breakdown with components |
| **Credit Memo** | "Generate Credit Memo" | Formal assessment report |
| **Comparison** | "Compare with similar businesses" | Industry benchmarking |
| **Scenario Analysis** | "What if we reduce to ₹15 lakh?" | Impact assessment |
| **Risk Explanation** | "Why is the Risk Medium?" | Risk factor breakdown |

### **Agent Attribution Examples**

Every answer clearly cites which agent provided the information:

```
✅ Good (CreditPilot AI):
"Financial Intelligence Agent found:
 • GST turnover increased by 18%
 
 Risk Intelligence Agent found:
 • Existing machinery loan
 • No fraud detected"

❌ Bad (Generic Chatbot):
"The MSME has good revenue growth and no fraud."
```

---

## 🎨 Frontend Integration

### **Chat Interface Component**

```tsx
// Example React component
function CreditPilotChat({ businessId }) {
  const [messages, setMessages] = useState([]);
  const [query, setQuery] = useState("");
  
  const sendQuery = async () => {
    const response = await fetch('/api/creditpilot/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ business_id: businessId, query })
    });
    
    const data = await response.json();
    
    setMessages([...messages, {
      query,
      answer: data.answer,
      agent_attribution: data.agent_attribution,
      followups: data.suggested_followups
    }]);
  };
  
  return (
    <div className="creditpilot-chat">
      <div className="messages">
        {messages.map(msg => (
          <div key={msg.query}>
            <div className="query">{msg.query}</div>
            <div className="answer">{msg.answer}</div>
            <div className="followups">
              {msg.followups.map(f => (
                <button onClick={() => setQuery(f)}>{f}</button>
              ))}
            </div>
          </div>
        ))}
      </div>
      
      <input
        value={query}
        onChange={e => setQuery(e.target.value)}
        placeholder="Ask CreditPilot AI anything..."
      />
      <button onClick={sendQuery}>Send</button>
    </div>
  );
}
```

---

## 📊 Testing

### **Run Test Script**

```bash
cd backend
python test_creditpilot.py
```

This demonstrates:
- Complete workflow orchestration
- All 8 conversational query types
- Agent attribution examples
- API endpoint documentation

### **Manual Testing with cURL**

```bash
# 1. Analyze MSME (requires actual CSV files)
curl -X POST http://localhost:8001/api/creditpilot/analyze \
  -F "business_id=MSME001" \
  -F "bank_file=@bank_transactions.csv" \
  -F "gst_file=@gst_summary.csv" \
  -F 'msme_data={"msme_id":"MSME001",...}'

# 2. Ask CreditPilot
curl -X POST http://localhost:8001/api/creditpilot/chat \
  -H "Content-Type: application/json" \
  -d '{
    "business_id": "MSME001",
    "query": "Analyze this MSME"
  }'

# 3. Check status
curl http://localhost:8001/api/creditpilot/status/MSME001
```

---

## 🎯 Hackathon Presentation Points

### **What Makes This Unique?**

1. **Not Just a Chatbot**
   - CreditPilot AI is a **Senior Credit Manager** with AI specialists
   - Clear agent attribution shows where insights come from
   - Banks want transparency, not black-box AI

2. **Multi-Agent Orchestration**
   - Three specialists working together
   - Sequential workflow with validation gates
   - Graceful degradation (if one fails, others don't run)

3. **Conversational Decision Support**
   - Natural language queries
   - Scenario analysis ("What if we reduce to ₹15 lakh?")
   - Industry comparison
   - Credit memo generation

4. **Production-Ready**
   - Complete audit trail
   - Error handling and validation
   - Compliance-focused design
   - API documentation with OpenAPI/Swagger

### **Live Demo Flow**

1. **Upload Documents** → Show Financial Agent validation
2. **View Analysis** → Show Risk Agent assessment with scores
3. **Ask Questions** → Demonstrate conversational interface
4. **Generate Memo** → Show final credit report

---

## 🚀 Current Status

### **✅ Completed**

- ✅ Financial Intelligence Agent (Agent 1)
- ✅ Risk Intelligence Agent (Agent 2)
- ✅ CreditPilot Copilot (Agent 3)
- ✅ Orchestrator (connects all 3 agents)
- ✅ Conversational interface (8 query types)
- ✅ API endpoints (/analyze, /chat, /status)
- ✅ Agent attribution system
- ✅ Test suite and documentation
- ✅ Backend running on port 8001
- ✅ Frontend running on port 5175

### **🎯 Ready For**

- ✅ Hackathon presentation
- ✅ Live demonstration
- ✅ API testing
- ✅ Frontend integration

---

## 📝 Files Created

| File | Purpose |
|------|---------|
| `backend/creditpilot_orchestrator.py` | Orchestrates all 3 agents |
| `backend/creditpilot_conversation.py` | Handles conversational queries |
| `backend/main.py` (updated) | Added CreditPilot endpoints |
| `backend/test_creditpilot.py` | Test suite and demo |
| `CREDITPILOT_AI_INTEGRATION.md` | This documentation |

---

## 🎉 Your Competitive Advantage

Most teams will build:
- A scoring model ✓ (You have this)
- A chatbot ✓ (You have this)
- A dashboard ✓ (You have this)

**You're building:**
- A **Senior Credit Manager AI** that coordinates specialists
- **Agent attribution** for transparency
- **Scenario analysis** for decision support
- **Multi-agent orchestration** (FenRock-inspired architecture)

**This is the story that wins hackathons!** 🏆

---

**Ready to run:** Both frontend and backend servers are live!

- **Frontend:** http://localhost:5175/
- **Backend:** http://localhost:8001/
- **API Docs:** http://localhost:8001/docs

**Test it now with the demo script or start integrating with your frontend!** 🚀
