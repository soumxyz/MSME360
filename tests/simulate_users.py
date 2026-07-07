import os
import sys
import json
import asyncio
import time
import argparse
import random
from datetime import datetime

# We will import httpx to perform concurrent HTTP requests
try:
    import httpx
except ImportError:
    print("[ERROR] httpx is required for simulation. Please make sure it is installed.")
    sys.exit(1)

BASE_URL = "http://localhost:8000"

# Mock MSME payload template for applicants
MOCK_PAYLOAD = {
    "gstin": "29ABCDE1234F1Z5",
    "pan": "ABCDE1234F",
    "business_registration_date": "2020-01-15",
    "gst_data": {
        "gstin": "29ABCDE1234F1Z5",
        "monthly_revenue": [150000.0] * 12,
        "filing_history": [True] * 12,
        "annual_turnover": 1800000.0
    },
    "upi_transactions": [
        {"amount": 1000.0, "timestamp": "2025-07-01T12:00:00", "counterparty": "Test Payer"}
    ],
    "account_aggregator_data": {
        "month_end_balances": [75000.0] * 6,
        "monthly_inflows": [150000.0] * 6,
        "monthly_outflows": [120000.0] * 6,
        "statement_start_date": "2025-01-01",
        "statement_end_date": "2025-06-30"
    }
}

class LoadTester:
    def __init__(self, concurrency, total_requests):
        self.concurrency = concurrency
        self.total_requests = total_requests
        self.completed = 0
        self.results = []
        self.start_time = 0
        
    async def run_request(self, client, user_type):
        req_id = self.completed
        self.completed += 1
        
        # Decide what endpoint to hit based on user type
        start = time.time()
        status_code = 0
        endpoint = ""
        
        try:
            if user_type == "applicant":
                # Connect alternate data & evaluate
                endpoint = "/api/v1/evaluate"
                # Randomize PAN/GSTIN slightly to prevent unique key clashes
                payload = dict(MOCK_PAYLOAD)
                letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                digits = "0123456789"
                rand_pan_letters = "".join(random.choice(letters) for _ in range(5))
                rand_pan_digits = "".join(random.choice(digits) for _ in range(4))
                rand_pan_last = random.choice(letters)
                
                payload["pan"] = f"{rand_pan_letters}{rand_pan_digits}{rand_pan_last}"
                payload["gstin"] = f"27{payload['pan']}1Z5"
                payload["gst_data"]["gstin"] = payload["gstin"]
                
                # In main.py we expect gstin/pan at root, let's also pass msme_id
                payload["msme_id"] = f"MSME_SIM_{random.randint(1000, 9999)}"
                
                response = await client.post(f"{BASE_URL}{endpoint}", json=payload, timeout=20.0)
                status_code = response.status_code
                if status_code == 422:
                    print("Validation Error 422 Response:", response.text)
                
            elif user_type == "officer_portfolio":
                endpoint = "/api/portfolio"
                response = await client.get(f"{BASE_URL}{endpoint}", timeout=10.0)
                status_code = response.status_code
                
            elif user_type == "officer_copilot":
                endpoint = "/api/copilot"
                payload = {
                    "business_id": f"MSME00{random.randint(1, 7)}",
                    "message": random.choice([
                        "Explain the risk band of this business",
                        "Is the monthly revenue stable?",
                        "What is the suggested maximum loan exposure?"
                    ])
                }
                response = await client.post(f"{BASE_URL}{endpoint}", json=payload, timeout=15.0)
                status_code = response.status_code
                
            else: # officer_details
                biz_id = f"MSME00{random.randint(1, 7)}"
                endpoint = f"/api/business/{biz_id}"
                response = await client.get(f"{BASE_URL}{endpoint}", timeout=10.0)
                status_code = response.status_code
                
            latency = time.time() - start
            self.results.append({
                "req_id": req_id,
                "endpoint": endpoint,
                "user_type": user_type,
                "status_code": status_code,
                "latency": latency,
                "success": status_code in [200, 201]
            })
            
        except Exception as e:
            latency = time.time() - start
            self.results.append({
                "req_id": req_id,
                "endpoint": endpoint,
                "user_type": user_type,
                "status_code": 500,
                "latency": latency,
                "success": False,
                "error": str(e)
            })

    async def worker(self, client, queue):
        while True:
            try:
                user_type = queue.get_nowait()
            except asyncio.QueueEmpty:
                break
                
            await self.run_request(client, user_type)
            queue.task_done()

    async def run(self):
        print(f"Starting load test on server {BASE_URL}...")
        print(f"Concurrency: {self.concurrency}")
        print(f"Total Requests: {self.total_requests}")
        
        # Populate queue with randomized request profiles
        queue = asyncio.Queue()
        user_types = ["applicant", "officer_portfolio", "officer_copilot", "officer_details"]
        
        # We assign weights: 15% applicants, 25% portfolios, 20% copilots, 40% details
        weights = [0.15, 0.25, 0.20, 0.40]
        
        for _ in range(self.total_requests):
            u_type = random.choices(user_types, weights=weights)[0]
            await queue.put(u_type)
            
        self.start_time = time.time()
        
        # Create client and launch workers
        limits = httpx.Limits(max_keepalive_connections=self.concurrency, max_connections=self.concurrency * 2)
        async with httpx.AsyncClient(limits=limits) as client:
            workers = [asyncio.create_task(self.worker(client, queue)) for _ in range(self.concurrency)]
            await queue.join()
            
            # Cancel workers
            for w in workers:
                w.cancel()
                
        total_time = time.time() - self.start_time
        self.print_report(total_time)

    def print_report(self, total_time):
        successes = [r for r in self.results if r["success"]]
        failures = [r for r in self.results if not r["success"]]
        
        latencies = [r["latency"] for r in self.results]
        avg_latency = sum(latencies) / len(latencies) if latencies else 0
        min_latency = min(latencies) if latencies else 0
        max_latency = max(latencies) if latencies else 0
        
        # Sort for p95
        latencies.sort()
        p95_idx = int(len(latencies) * 0.95)
        p95_latency = latencies[p95_idx] if latencies else 0
        
        rps = len(self.results) / total_time if total_time > 0 else 0
        
        print("\n" + "="*80)
        print("CONCURRENT USER SIMULATOR / STRESS TEST REPORT")
        print("="*80)
        print(f"Duration: {total_time:.2f} seconds")
        print(f"Requests completed: {len(self.results)}")
        print(f"Successful: {len(successes)} ({(len(successes)/len(self.results))*100:.1f}%)")
        print(f"Failed: {len(failures)}")
        print(f"Requests Per Second (RPS): {rps:.2f}")
        print("\nLatency Metrics:")
        print(f"   - Minimum: {min_latency:.3f}s")
        print(f"   - Average: {avg_latency:.3f}s")
        print(f"   - 95th Percentile: {p95_latency:.3f}s")
        print(f"   - Maximum: {max_latency:.3f}s")
        
        # Grouped by endpoint
        endpoints = {}
        for r in self.results:
            ep = r["endpoint"]
            if ep not in endpoints:
                endpoints[ep] = []
            endpoints[ep].append(r)
            
        print("\nEndpoint Breakdown:")
        for ep, reqs in endpoints.items():
            ep_latencies = [r["latency"] for r in reqs]
            ep_avg = sum(ep_latencies) / len(ep_latencies)
            ep_success = len([r for r in reqs if r["success"]])
            print(f"   * {ep:<30} | Req: {len(reqs):<3} | Success: {ep_success/len(reqs)*100:>5.1f}% | Avg Latency: {ep_avg:.3f}s")
            
        print("="*80 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stress test backend with simulated users.")
    parser.add_argument("--concurrency", type=int, default=10, help="Number of concurrent virtual users (workers)")
    parser.add_argument("--requests", type=int, default=100, help="Total number of requests to execute")
    args = parser.parse_args()
    
    asyncio.run(LoadTester(args.concurrency, args.requests).run())
