import os
import sys
import json
import urllib.request
import urllib.parse
import urllib.error
import time
import subprocess

def make_post_request(url, data_dict=None, is_json=True):
    try:
        if is_json:
            req_data = json.dumps(data_dict).encode('utf-8')
            content_type = 'application/json'
        else:
            req_data = urllib.parse.urlencode(data_dict).encode('utf-8')
            content_type = 'application/x-www-form-urlencoded'

        req = urllib.request.Request(url, data=req_data)
        req.add_header('Content-Type', content_type)
        
        with urllib.request.urlopen(req) as response:
            return response.getcode(), json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode('utf-8'))
    except Exception as e:
        return 500, {"error": str(e)}

def test_endpoints():
    print("========================================================================")
    print("STARTING HACKATHON MOCK GATEWAY END-TO-END TESTS")
    print("========================================================================")

    # 1. Start mock server locally in background
    cmd = [sys.executable, "-m", "uvicorn", "mock_server:app", "--host", "127.0.0.1", "--port", "8080"]
    server_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("[INFO] Launching FastAPI mock server in the background...")
    proc = subprocess.Popen(
        cmd, 
        cwd=server_dir,
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE
    )
    
    # Wait for server to boot
    time.sleep(2.0)
    
    try:
        # Base URL
        base_url = "http://127.0.0.1:8080"
        
        # Test 1: KYC verify (POST /api/v1/kyc/verify)
        print("\n--- Test 1: POST /api/v1/kyc/verify (Form Data) ---")
        kyc_url = f"{base_url}/api/v1/kyc/verify"
        kyc_payload = {
            "pan_number": "ABCDE1234F",
            "aadhaar_number": "123456789012",
            "udyam_number": "UDYAM-AS-01-0012345"
        }
        code, resp = make_post_request(kyc_url, kyc_payload, is_json=False)
        print(f"Status Code: {code}")
        print(f"Response: {json.dumps(resp, indent=2)}")
        assert code == 200, "KYC verify endpoint failed"
        assert resp["status"] == "VERIFIED", "Status should be VERIFIED"
        assert resp["kyc_data"]["pan"]["pan_number"] == "ABCDE1234F", "PAN mismatch"
        print("[PASS] KYC verification mocks successfully checked.")

        # Test 2: Connect Financial (POST /api/v1/financial/connect) - Success Mode
        print("\n--- Test 2: POST /api/v1/financial/connect (Success) ---")
        connect_url = f"{base_url}/api/v1/financial/connect"
        connect_payload = {
            "connect_gst": True,
            "connect_aa": True,
            "connect_upi": True,
            "connect_epfo": True
        }
        code, resp = make_post_request(connect_url, connect_payload, is_json=True)
        print(f"Status Code: {code}")
        print(f"Response: {json.dumps(resp, indent=2)}")
        assert code == 200, "Financial connect endpoint failed"
        assert resp["status"] == "CONNECTED", "Status should be CONNECTED"
        assert resp["sources"]["gst"]["connected"] is True, "GST should be connected"
        print("[PASS] Alternate-data connections successfully mocked.")

        # Test 3: Connect Financial (POST /api/v1/financial/connect) - Failure/Fallback Mode
        print("\n--- Test 3: POST /api/v1/financial/connect?simulate_failure=true ---")
        fail_url = f"{base_url}/api/v1/financial/connect?simulate_failure=true"
        code, resp = make_post_request(fail_url, connect_payload, is_json=True)
        print(f"Status Code: {code}")
        print(f"Response: {json.dumps(resp, indent=2)}")
        assert code == 200, "Financial connect failure simulation failed"
        assert resp["status"] == "FAILED", "Status should be FAILED to trigger fallback UI"
        assert resp["error_code"] == "CONSENT_TIMEOUT", "Error code should match timeout"
        print("[PASS] Fallback flow triggering condition successfully checked.")

        # Test 4: Credit Evaluate (POST /api/v1/credit-copilot/evaluate)
        print("\n--- Test 4: POST /api/v1/credit-copilot/evaluate ---")
        eval_url = f"{base_url}/api/v1/credit-copilot/evaluate"
        eval_payload = {
            "kyc_verification_result": "VERIFIED",
            "connected_financial_summary": resp  # pass the outputs in
        }
        code, resp = make_post_request(eval_url, eval_payload, is_json=True)
        print(f"Status Code: {code}")
        print(f"Response (abbreviated):")
        # Abbreviate credit memo markdown for display
        memo_abbrev = resp["credit_memo_markdown"][:150] + "..."
        resp_display = {**resp, "credit_memo_markdown": memo_abbrev}
        print(json.dumps(resp_display, indent=2))
        
        assert code == 200, "Credit Copilot evaluate endpoint failed"
        assert resp["status"] == "APPROVED", "Evaluation should result in APPROVED"
        assert resp["loan_recommendation"]["approved_amount_inr"] == 2500000.0, "Loan amount mismatch"
        assert resp["financial_health_card"]["health_score"] == 82, "Health score mismatch"
        print("[PASS] AI Credit Copilot evaluation payload successfully verified.")

        print("\n========================================================================")
        print("ALL HACKATHON MOCK GATEWAY ENDPOINTS VERIFIED SUCCESSFULLY!")
        print("========================================================================")

    except Exception as e:
        print(f"\n[FAIL] Test assertion failed: {e}")
        sys.exit(1)
    finally:
        # Stop background uvicorn server
        print("\n[INFO] Stopping background FastAPI mock server...")
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()

if __name__ == "__main__":
    test_endpoints()
