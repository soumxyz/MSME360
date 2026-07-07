"""Test Risk Intelligence Agent with GitHub Dataset.

This script runs validated dataset records through the complete Risk Agent
workflow to verify all components work properly.
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.risk_intelligence_agent.workflow import create_risk_assessment_workflow
from agents.risk_intelligence_agent.schemas import MSMEInput, AssessmentReport


TEST_DATA_DIR = Path("/Users/utkarshsinha/Desktop/MSME360/risk agent/data/test_results")


async def test_single_business(workflow_app, business_file: Path) -> dict:
    """Test a single business through the Risk Agent workflow."""
    
    print(f"\n{'='*70}")
    print(f"Testing: {business_file.name}")
    print(f"{'='*70}")
    
    try:
        # Load validated data
        with open(business_file, 'r') as f:
            data = json.load(f)
        
        print(f"✅ Loaded data for {data.get('gstin', 'UNKNOWN')}")
        
        # Parse with Pydantic
        msme_input = MSMEInput(**data)
        print(f"✅ Pydantic validation passed")
        
        # Run through workflow
        print(f"🔄 Running through Risk Agent workflow...")
        
        result = await workflow_app.ainvoke({
            "msme_input": msme_input,
            "request_id": f"test_{business_file.stem}_{int(datetime.now().timestamp())}"
        })
        
        # Check if assessment report was generated
        if "assessment_report" in result:
            report = result["assessment_report"]
            print(f"\n✅ Assessment Complete!")
            print(f"   Risk Score: {report.risk_score:.2f}")
            print(f"   Risk Category: {report.risk_category}")
            print(f"   Recommendation: {report.recommendation}")
            print(f"   Eligibility: {report.eligibility}")
            print(f"   Confidence: {report.confidence_level:.2f}")
            
            # Check for fraud flags
            if report.fraud_flags:
                print(f"\n⚠️  Fraud Flags: {len(report.fraud_flags)}")
                for flag in report.fraud_flags:
                    if flag.status:
                        print(f"      - {flag.flag_name}: {flag.description}")
            
            # Check for policy violations
            if report.policy_violations:
                print(f"\n⚠️  Policy Violations: {len(report.policy_violations)}")
                for violation in report.policy_violations[:3]:
                    print(f"      - {violation}")
            
            # Save result
            result_file = TEST_DATA_DIR / f"result_{business_file.stem}.json"
            with open(result_file, 'w') as f:
                json.dump(json.loads(report.model_dump_json()), f, indent=2)
            print(f"\n💾 Saved result: {result_file.name}")
            
            return {
                "business_id": business_file.stem,
                "success": True,
                "risk_score": report.risk_score,
                "risk_category": report.risk_category,
                "recommendation": report.recommendation,
                "error": None
            }
        else:
            print(f"\n❌ No assessment report in result")
            print(f"   Result keys: {result.keys()}")
            return {
                "business_id": business_file.stem,
                "success": False,
                "error": "No assessment report generated"
            }
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "business_id": business_file.stem,
            "success": False,
            "error": str(e)
        }


async def run_tests(count: int = 5):
    """Run tests on multiple businesses."""
    
    print("\n")
    print("="*70)
    print("RISK INTELLIGENCE AGENT - DATASET TESTING")
    print("="*70)
    print()
    
    # Create workflow
    print("🔧 Initializing Risk Agent workflow...")
    try:
        workflow_app = create_risk_assessment_workflow()
        print("✅ Workflow initialized")
    except Exception as e:
        print(f"❌ Failed to initialize workflow: {e}")
        return
    
    # Get validated test files
    test_files = sorted(TEST_DATA_DIR.glob("validated_MSME*.json"))[:count]
    
    if not test_files:
        print(f"\n❌ No validated test files found in {TEST_DATA_DIR}")
        print("   Run test_dataset_with_risk_agent.py first")
        return
    
    print(f"\n📊 Found {len(test_files)} validated test files")
    print(f"   Testing first {count} businesses...")
    
    # Run tests
    results = []
    for i, test_file in enumerate(test_files, 1):
        print(f"\n[{i}/{len(test_files)}]")
        result = await test_single_business(workflow_app, test_file)
        results.append(result)
    
    # Summary
    print("\n")
    print("="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    success_count = sum(1 for r in results if r['success'])
    fail_count = len(results) - success_count
    
    print(f"\n✅ Successful: {success_count}/{len(results)}")
    print(f"❌ Failed: {fail_count}/{len(results)}")
    
    if success_count > 0:
        print("\n📊 Risk Assessment Results:")
        print(f"{'Business':<20} {'Risk Score':<12} {'Category':<10} {'Recommendation':<25}")
        print("-" * 70)
        for r in results:
            if r['success']:
                business_id = r['business_id'].replace('validated_', '')
                print(f"{business_id:<20} {r['risk_score']:<12.2f} {r['risk_category']:<10} {r['recommendation']:<25}")
    
    if fail_count > 0:
        print("\n❌ Failed Tests:")
        for r in results:
            if not r['success']:
                print(f"   - {r['business_id']}: {r['error']}")
    
    print("\n" + "="*70)
    print("✅ TESTING COMPLETE")
    print("="*70)
    print()


def main():
    """Main entry point."""
    asyncio.run(run_tests(count=5))


if __name__ == "__main__":
    main()
