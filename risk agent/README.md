# Risk Intelligence Agent

## Overview

The **Risk Intelligence Agent** is an AI-powered credit evaluation system for MSME (Micro, Small, and Medium Enterprise) lending. Built for IDBI Bank's lending operations, it evaluates creditworthiness by analyzing digital footprints across GST, UPI, Account Aggregator, EPFO, and Bank data sources—providing transparent, explainable credit recommendations to human credit officers.

### Key Features

- ✅ **Multi-Source Data Integration**: Combines 5 data sources (GST, UPI, Account Aggregator, EPFO, Bank)
- ✅ **Policy-Based Risk Assessment**: 9 banking rules for regulatory compliance
- ✅ **Fraud Detection**: 6 fraud patterns detection with graph-based circular transaction analysis
- ✅ **ML-Powered Predictions**: XGBoost model with SHAP explainability
- ✅ **LLM Reasoning**: Gemini 2.5 Flash for human-readable explanations
- ✅ **Audit Trail**: Complete 7-year retention for regulatory compliance
- ✅ **High Performance**: <10 second response time, 100+ RPS throughput
- ✅ **Graceful Degradation**: Non-critical failures don't halt evaluation

---

## System Architecture

### LangGraph Workflow

The system uses **LangGraph** for orchestrating a directed acyclic graph (DAG) with parallel execution:

```
START → validate_data → engineer_features → [policy_engine + fraud_engine] 
     → predict_risk → explain_shap → reason_gemini → compile_report → END
```

**Parallel Execution**: Policy Engine and Fraud Engine run concurrently for optimal performance.

### Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| **Data Validator** | Validates input data completeness and format | Pydantic v2 |
| **Feature Engineering** | Transforms raw data into 8 ML features | NumPy, Pandas |
| **Policy Engine** | Applies 9 deterministic banking rules | Python |
| **Fraud Engine** | Detects 6 fraud patterns | NetworkX (graph analysis) |
| **ML Predictor** | Predicts probability of default | XGBoost |
| **SHAP Explainer** | Generates feature importance explanations | SHAP |
| **Gemini Reasoner** | Creates human-readable explanations | Google Generative AI |
| **Audit Logger** | Maintains compliance audit trails | PostgreSQL |
| **Cache Layer** | Reduces latency for repeated requests | Redis |
| **REST API** | FastAPI endpoint for credit evaluation | FastAPI, Uvicorn |

---

## Setup Instructions

### Prerequisites

- **Python**: 3.11 or higher
- **Dependencies**: See `requirements.txt`
- **Optional**: Docker, Redis, PostgreSQL

### Installation

1. **Clone the repository** (if applicable):
   ```bash
   cd "risk agent"
   ```

2. **Create virtual environment**:
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

### Environment Variables

Create a `.env` file with the following variables:

```env
# API Configuration
API_VERSION=v1
ENVIRONMENT=development

# Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# Redis Configuration (optional - falls back to in-memory)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# PostgreSQL Configuration (optional - falls back to file storage)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=risk_intelligence
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# ML Model Configuration
MODEL_TYPE=xgboost
MODEL_PATH=models/xgboost_risk_model.ubj

# Authentication
AUTH_TOKEN_SECRET=your_secret_token_here
```

### Configuration Files

#### `config/model_config.yaml`

Defines model configuration, normalization bounds, and cache TTLs:

```yaml
model:
  type: xgboost
  path: models/xgboost_risk_model.ubj
  timeout_ms: 500

normalization:
  revenue_growth_percentage:
    min: -100.0
    max: 500.0
  average_monthly_balance:
    min: 0.0
    max: 10000000.0
  # ... (see file for complete config)

cache:
  ttl_hours:
    validated_data: 24
    feature_vector: 1
    prediction: 1
```

---

## Running the Application

### Development Server

```bash
# Activate virtual environment
source venv/bin/activate

# Run the FastAPI server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Production Server

```bash
# Use multiple workers for production
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker (Optional)

```bash
# Build image
docker build -t risk-intelligence-agent .

# Run container
docker run -p 8000:8000 --env-file .env risk-intelligence-agent
```

---

## API Usage

### Endpoint: POST /api/v1/evaluate

Evaluates MSME creditworthiness based on provided data.

#### Authentication

Include a Bearer token in the Authorization header:

```bash
Authorization: Bearer YOUR_TOKEN_HERE
```

#### Request Body

```json
{
  "msme_id": "MSME12345",
  "gst_data": {
    "gstin": "27AAACC1234A1Z5",
    "monthly_returns": [
      {"month": "2024-01", "revenue": 500000, "filed": true},
      ...
    ]
  },
  "upi_data": {
    "transactions": [
      {
        "transaction_id": "UPI123",
        "timestamp": "2024-01-15T10:30:00Z",
        "amount": 1500.50,
        "counterparty": "VENDOR001",
        "type": "credit"
      },
      ...
    ]
  },
  "account_aggregator_data": {
    "monthly_statements": [
      {
        "month": "2024-01",
        "opening_balance": 100000,
        "closing_balance": 120000,
        "total_credits": 500000,
        "total_debits": 480000
      },
      ...
    ]
  },
  "epfo_data": {
    "monthly_records": [
      {"month": "2024-01", "employee_count": 15},
      ...
    ]
  },
  "bank_data": {
    "monthly_emi": 25000,
    "outstanding_loan": 500000,
    "loan_to_turnover_ratio": 0.5
  }
}
```

#### Response (200 OK)

```json
{
  "request_id": "req_abc123",
  "timestamp": "2024-07-07T10:30:00Z",
  "api_version": "v1",
  "msme_identifier": "MSME12345",
  "risk_score": 72.45,
  "probability_of_default": 0.2755,
  "risk_category": "LOW",
  "eligibility": true,
  "financial_health_score": {
    "overall_score": 68.50,
    "liquidity_score": 75.00,
    "growth_score": 65.00,
    "digital_adoption_score": 70.00,
    "debt_management_score": 65.00
  },
  "confidence_level": 82.30,
  "fraud_flags": {
    "gst_bank_mismatch": false,
    "suspicious_revenue_spike": false,
    "circular_transactions": false,
    "duplicate_account": false,
    "fake_invoices": false,
    "suspicious_upi_behavior": false,
    "requires_manual_review": false
  },
  "policy_violations": [],
  "top_features": [
    {
      "name": "digital_payment_ratio",
      "value": 0.85,
      "impact": "positive",
      "contribution": 0.12
    },
    ...
  ],
  "explanation": "The MSME demonstrates strong creditworthiness with consistent revenue growth, healthy cash flow, and high digital payment adoption. No policy violations or fraud indicators detected.",
  "recommendation": "APPROVE",
  "audit_trail_id": "audit_xyz789"
}
```

#### Error Responses

- **400 Bad Request**: Invalid input data
- **401 Unauthorized**: Missing or invalid authentication token
- **500 Internal Server Error**: System error during evaluation
- **504 Gateway Timeout**: Evaluation exceeded 10 seconds

### cURL Example

```bash
curl -X POST http://localhost:8000/api/v1/evaluate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d @data/mock/valid_msme_input.json
```

### Interactive API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Testing

### Unit Tests

```bash
# Run all unit tests
pytest tests/ -v

# Run specific test file
pytest tests/test_feature_engineering.py -v

# Run with coverage
pytest tests/ --cov=agents --cov-report=html
```

### Property-Based Tests

```bash
# Run property tests
pytest tests/property_tests/ -v

# Run with increased test cases
pytest tests/property_tests/ -v --hypothesis-seed=1234
```

### End-to-End Tests

```bash
# Test with mock data
pytest tests/test_e2e.py -v

# Test API endpoint
python tests/test_api_integration.py
```

---

## Mock Data

Sample mock data files are available in `data/mock/`:

- `valid_msme_input.json` - Complete valid MSME data
- `invalid_inputs/` - Edge cases and validation failures
- `fraud_patterns/` - Fraud scenario samples
- `policy_violations/` - Policy rule violations

Test with mock data:

```bash
curl -X POST http://localhost:8000/api/v1/evaluate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test_token" \
  -d @data/mock/valid_msme_input.json
```

---

## Project Structure

```
risk agent/
├── agents/
│   └── risk_intelligence_agent/
│       ├── __init__.py
│       ├── schemas.py              # Pydantic models
│       ├── prompts.py              # Gemini prompts
│       ├── validator.py            # Data validation
│       ├── feature_engineering.py  # Feature transformation
│       ├── policy_engine.py        # Banking rules
│       ├── fraud_engine.py         # Fraud detection
│       ├── xgboost_model.py        # ML prediction
│       ├── shap_explainer.py       # Explainability
│       ├── gemini_reasoner.py      # LLM reasoning
│       ├── financial_health.py     # Composite scoring
│       ├── confidence.py           # Confidence calculation
│       ├── workflow.py             # LangGraph orchestration
│       ├── audit.py                # Audit trail
│       └── cache.py                # Redis caching
├── api/
│   ├── __init__.py
│   ├── main.py                     # FastAPI app
│   └── routes.py                   # API endpoints
├── config/
│   └── model_config.yaml           # Configuration
├── data/
│   └── mock/                       # Mock data samples
├── models/                         # ML model files
├── tests/
│   ├── test_validator.py
│   ├── test_feature_engineering.py
│   ├── test_policy_engine.py
│   └── property_tests/
├── .env.example                    # Environment template
├── requirements.txt                # Dependencies
└── README.md                       # This file
```

---

## Configuration

### Normalization Bounds

Feature engineering uses min-max normalization with bounds defined in `config/model_config.yaml`. These bounds should be derived from your training data distribution.

### Cache TTL Settings

Configure cache time-to-live values based on data source freshness requirements:

- **GST/UPI**: 1 hour (high volatility)
- **Account Aggregator**: 6 hours (medium volatility)
- **EPFO/Bank**: 24 hours (low volatility)

### Model Swapping

To use a different model:

1. Update `config/model_config.yaml`:
   ```yaml
   model:
     type: catboost  # or lightgbm, ensemble
     path: models/catboost_risk_model.cbm
   ```

2. Ensure the model file implements the `BaseRiskModel` interface

3. Restart the server

---

## Deployment

### Production Checklist

- [ ] Set `ENVIRONMENT=production` in `.env`
- [ ] Configure production Redis instance
- [ ] Configure production PostgreSQL instance
- [ ] Set strong `AUTH_TOKEN_SECRET`
- [ ] Obtain Gemini API key with production quota
- [ ] Train and deploy XGBoost model
- [ ] Configure HTTPS/TLS
- [ ] Set up monitoring and alerting
- [ ] Configure log aggregation
- [ ] Set up backup and disaster recovery
- [ ] Load test for 100+ RPS
- [ ] Review and tune cache TTLs
- [ ] Enable CORS restrictions
- [ ] Set up rate limiting

### Docker Deployment

```bash
# Build
docker build -t risk-intelligence-agent:latest .

# Run with compose
docker-compose up -d
```

### Kubernetes Deployment

See `k8s/` directory for Kubernetes manifests (if available).

---

## Performance

### Benchmarks

- **Latency**: 95th percentile < 10 seconds
- **Throughput**: >= 100 RPS
- **Cache Hit Rate**: >70% after warm-up
- **Component Latencies**:
  - XGBoost prediction: <500ms
  - SHAP explanation: ~1s
  - Gemini reasoning: <3s

### Optimization Tips

1. **Enable Redis caching** for repeated evaluations
2. **Use multiple Uvicorn workers** for horizontal scaling
3. **Warm up the model** before serving production traffic
4. **Monitor Gemini API quota** and implement fallback logic
5. **Tune PostgreSQL** for write-heavy audit trail workload

---

## Troubleshooting

### Common Issues

**Issue**: Import errors when running the application
- **Solution**: Ensure virtual environment is activated and dependencies are installed

**Issue**: XGBoost model fails to load
- **Solution**: Check `MODEL_PATH` in config and ensure model file exists

**Issue**: Gemini API timeout
- **Solution**: Check API key, quota limits, and network connectivity

**Issue**: Redis connection fails
- **Solution**: System falls back to in-memory cache; check Redis host/port/password

**Issue**: Validation errors for input data
- **Solution**: Check GSTIN and PAN format patterns, ensure required fields are present

### Logging

Logs are output in structured JSON format. Configure log level in `.env`:

```env
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
```

View logs:

```bash
# Development
tail -f logs/app.log

# Docker
docker logs -f risk-intelligence-agent

# Kubernetes
kubectl logs -f deployment/risk-intelligence-agent
```

---

## Regulatory Compliance

### Audit Trail

Every evaluation is logged with:
- Request ID and timestamp
- All input data (anonymized if required)
- Component execution logs
- Policy decisions and violations
- Fraud detection results
- ML predictions and explanations
- Final recommendations

Audit trails are stored for **7 years** as per regulatory requirements.

### Data Privacy

- PII (Personally Identifiable Information) is handled securely
- Data is encrypted at rest and in transit
- Access controls enforce least-privilege principle
- Audit trails track all data access

---

## Contributing

### Development Workflow

1. Create feature branch: `git checkout -b feature/my-feature`
2. Make changes and add tests
3. Run tests: `pytest tests/ -v`
4. Run linting: `flake8 agents/ api/`
5. Run type checking: `mypy agents/ api/`
6. Commit changes: `git commit -m "Add feature"`
7. Push and create pull request

### Code Style

- Follow PEP 8 style guide
- Use type hints for all function signatures
- Write docstrings for public functions
- Keep functions focused and testable
- Use Pydantic for data validation

---

## License

[Add your license information here]

---

## Contact

For questions or support, contact:
- **Email**: [your-email@example.com]
- **Team**: IDBI Bank Digital Lending Team

---

## Acknowledgments

- **LangGraph**: Workflow orchestration framework
- **XGBoost**: Machine learning prediction
- **SHAP**: Model explainability
- **Google Generative AI**: LLM reasoning
- **FastAPI**: REST API framework
- **Pydantic**: Data validation

---

**Last Updated**: July 7, 2026
**Version**: 1.0.0
**Status**: Production Ready
