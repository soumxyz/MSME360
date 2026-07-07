import os
import sys
import json
import asyncio
import time
from datetime import datetime

# Add packages to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "risk agent"))

from agents.risk_intelligence_agent.workflow import evaluate_msme
from agents.risk_intelligence_agent.schemas import MSMEInput

async def evaluate_profile(profile):
    # Parse payload using MSMEInput
    try:
        msme_input = MSMEInput(**profile)
        start_time = time.time()
        report = await evaluate_msme(msme_input)
        elapsed = time.time() - start_time
        
        if hasattr(report, "model_dump"):
            report_dict = report.model_dump()
        elif hasattr(report, "dict"):
            report_dict = report.dict()
        else:
            report_dict = report
            
        return {
            "msme_id": profile["msme_id"],
            "success": True,
            "score": report_dict.get("eligibility_score") or report_dict.get("financial_health_score"),
            "risk_category": report_dict.get("risk_category"),
            "recommendation": report_dict.get("recommendation"),
            "latency_sec": elapsed,
            "error": None
        }
    except Exception as e:
        import traceback
        return {
            "msme_id": profile["msme_id"],
            "success": False,
            "score": None,
            "risk_category": None,
            "recommendation": None,
            "latency_sec": 0,
            "error": f"{type(e).__name__}: {str(e)}"
        }

async def main():
    print("Loading synthetic test cases...")
    json_path = os.path.join(os.path.dirname(__file__), "synthetic_msmes.json")
    if not os.path.exists(json_path):
        print(f"[FAIL] {json_path} does not exist. Run generate_test_cases.py first.")
        return

    with open(json_path, "r") as f:
        profiles = json.load(f)

    print(f"Loaded {len(profiles)} profiles. Running batch evaluation...")
    
    start_time = time.time()
    
    # Run in chunks to prevent thread pool exhaustion or rate limits
    chunk_size = 10
    results = []
    
    for i in range(0, len(profiles), chunk_size):
        chunk = profiles[i:i+chunk_size]
        print(f"   Evaluating chunk {i//chunk_size + 1}/{len(profiles)//chunk_size + 1}...")
        tasks = [evaluate_profile(p) for p in chunk]
        chunk_results = await asyncio.gather(*tasks)
        results.extend(chunk_results)
        
    total_elapsed = time.time() - start_time
    
    # Calculate stats
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    
    approvals = len([r for r in successful if r["recommendation"] == "APPROVE" or "APPROVE" in str(r["recommendation"]).upper()])
    rejections = len([r for r in successful if r["recommendation"] == "REJECT" or "REJECT" in str(r["recommendation"]).upper()])
    conditionals = len(successful) - approvals - rejections
    
    low_risk = len([r for r in successful if r["risk_category"] == "LOW" or "LOW" in str(r["risk_category"]).upper()])
    med_risk = len([r for r in successful if r["risk_category"] == "MEDIUM" or "MEDIUM" in str(r["risk_category"]).upper()])
    high_risk = len(successful) - low_risk - med_risk
    
    avg_score = sum(r["score"] for r in successful) / len(successful) if successful else 0
    avg_latency = sum(r["latency_sec"] for r in successful) / len(successful) if successful else 0
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_evaluated": len(profiles),
        "successful_evaluations": len(successful),
        "failed_evaluations": len(failed),
        "overall_success_rate": f"{(len(successful)/len(profiles))*100:.2f}%",
        "total_elapsed_seconds": round(total_elapsed, 2),
        "average_score": round(avg_score, 2),
        "average_latency_seconds": round(avg_latency, 3),
        "recommendation_distribution": {
            "APPROVE": approvals,
            "REJECT": rejections,
            "CONDITIONAL_APPROVAL": conditionals
        },
        "risk_category_distribution": {
            "LOW": low_risk,
            "MEDIUM": med_risk,
            "HIGH": high_risk
        },
        "failures": failed[:10],
        "detailed_results": results
    }
    
    report_path = os.path.join(os.path.dirname(__file__), "batch_evaluation_report.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
        
    print(f"\n========================================================")
    print(f"BATCH EVALUATION RESULTS")
    print(f"========================================================")
    print(f"Status: SUCCESS" if len(failed) == 0 else "Status: COMPLETED WITH FAILURES")
    print(f"Total Evaluated: {len(profiles)}")
    print(f"Success Rate: {(len(successful)/len(profiles))*100:.1f}%")
    print(f"Avg Score: {avg_score:.1f}/100")
    print(f"Avg Evaluation Latency: {avg_latency:.3f}s")
    print(f"\nRecommendations:")
    print(f"   - Approve: {approvals}")
    print(f"   - Conditional: {conditionals}")
    print(f"   - Reject: {rejections}")
    print(f"\nRisk Bands:")
    print(f"   - Low: {low_risk}")
    print(f"   - Medium: {med_risk}")
    print(f"   - High: {high_risk}")
    print(f"========================================================")
    print(f"Full report saved to 'tests/batch_evaluation_report.json'")

if __name__ == "__main__":
    asyncio.run(main())
