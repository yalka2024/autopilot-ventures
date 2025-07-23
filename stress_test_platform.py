#!/usr/bin/env python3
"""
Platform Stress Test
Test platform performance under load
"""

import asyncio
import aiohttp
import time
import json
from datetime import datetime
from typing import List, Dict, Any
import statistics

class PlatformStressTest:
    """Stress test the platform with concurrent requests"""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.results = []
        
    async def single_request(self, session: aiohttp.ClientSession, endpoint: str, test_name: str) -> Dict[str, Any]:
        """Make a single request and measure performance"""
        start_time = time.time()
        try:
            async with session.get(f"{self.base_url}{endpoint}") as response:
                response_time = time.time() - start_time
                data = await response.json() if response.status == 200 else None
                
                return {
                    "test_name": test_name,
                    "endpoint": endpoint,
                    "status_code": response.status,
                    "response_time": response_time,
                    "success": response.status == 200,
                    "data": data
                }
        except Exception as e:
            response_time = time.time() - start_time
            return {
                "test_name": test_name,
                "endpoint": endpoint,
                "status_code": None,
                "response_time": response_time,
                "success": False,
                "error": str(e)
            }
    
    async def concurrent_requests(self, endpoint: str, test_name: str, num_requests: int = 10) -> List[Dict[str, Any]]:
        """Make concurrent requests to test load handling"""
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.single_request(session, endpoint, f"{test_name}_{i+1}")
                for i in range(num_requests)
            ]
            return await asyncio.gather(*tasks)
    
    async def run_stress_test(self, concurrent_users: int = 10, requests_per_user: int = 5):
        """Run comprehensive stress test"""
        print(f"🔥 STRESS TESTING PLATFORM")
        print(f"Concurrent Users: {concurrent_users}")
        print(f"Requests per User: {requests_per_user}")
        print(f"Total Requests: {concurrent_users * requests_per_user}")
        print("=" * 60)
        
        # Test endpoints
        endpoints = [
            ("/health", "Health Check"),
            ("/real_autonomous_status", "Autonomous Status"),
            ("/phase1_status", "Phase 1 Status"),
            ("/stripe_status", "Stripe Status"),
            ("/real_businesses", "Business List"),
            ("/real_customers", "Customer List")
        ]
        
        all_results = []
        
        for endpoint, test_name in endpoints:
            print(f"\n🔍 Testing: {test_name}")
            print(f"Endpoint: {endpoint}")
            
            # Run concurrent requests
            results = await self.concurrent_requests(
                endpoint, 
                test_name, 
                concurrent_users * requests_per_user
            )
            
            all_results.extend(results)
            
            # Calculate metrics for this endpoint
            response_times = [r["response_time"] for r in results if r["success"]]
            success_count = sum(1 for r in results if r["success"])
            
            if response_times:
                print(f"   ✅ Success Rate: {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%)")
                print(f"   ⏱️  Avg Response Time: {statistics.mean(response_times):.3f}s")
                print(f"   📊 Min Response Time: {min(response_times):.3f}s")
                print(f"   📊 Max Response Time: {max(response_times):.3f}s")
                print(f"   📊 Median Response Time: {statistics.median(response_times):.3f}s")
            else:
                print(f"   ❌ All requests failed")
        
        # Overall performance analysis
        print("\n" + "=" * 60)
        print("📊 STRESS TEST RESULTS")
        print("=" * 60)
        
        total_requests = len(all_results)
        successful_requests = sum(1 for r in all_results if r["success"])
        all_response_times = [r["response_time"] for r in all_results if r["success"]]
        
        print(f"Total Requests: {total_requests}")
        print(f"Successful Requests: {successful_requests}")
        print(f"Overall Success Rate: {successful_requests/total_requests*100:.1f}%")
        
        if all_response_times:
            print(f"Overall Avg Response Time: {statistics.mean(all_response_times):.3f}s")
            print(f"Overall Min Response Time: {min(all_response_times):.3f}s")
            print(f"Overall Max Response Time: {max(all_response_times):.3f}s")
            print(f"Overall Median Response Time: {statistics.median(all_response_times):.3f}s")
            
            # Performance rating
            avg_time = statistics.mean(all_response_times)
            success_rate = successful_requests / total_requests
            
            if avg_time < 0.5 and success_rate > 0.95:
                performance_rating = "EXCELLENT"
            elif avg_time < 1.0 and success_rate > 0.90:
                performance_rating = "GOOD"
            elif avg_time < 2.0 and success_rate > 0.80:
                performance_rating = "ACCEPTABLE"
            else:
                performance_rating = "NEEDS IMPROVEMENT"
            
            print(f"\n🏆 Performance Rating: {performance_rating}")
        
        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"stress_test_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "test_config": {
                    "concurrent_users": concurrent_users,
                    "requests_per_user": requests_per_user,
                    "total_requests": total_requests
                },
                "results": all_results,
                "summary": {
                    "total_requests": total_requests,
                    "successful_requests": successful_requests,
                    "success_rate": successful_requests / total_requests,
                    "avg_response_time": statistics.mean(all_response_times) if all_response_times else 0,
                    "min_response_time": min(all_response_times) if all_response_times else 0,
                    "max_response_time": max(all_response_times) if all_response_times else 0,
                    "median_response_time": statistics.median(all_response_times) if all_response_times else 0
                }
            }, f, indent=2)
        
        print(f"\n💾 Detailed results saved to: {filename}")
        
        return {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "success_rate": successful_requests / total_requests,
            "avg_response_time": statistics.mean(all_response_times) if all_response_times else 0
        }

async def main():
    """Main execution function"""
    stress_test = PlatformStressTest()
    
    # Run stress test with different load levels
    load_levels = [
        (5, 3),   # 5 users, 3 requests each = 15 total
        (10, 5),  # 10 users, 5 requests each = 50 total
        (20, 3),  # 20 users, 3 requests each = 60 total
    ]
    
    print("🚀 PLATFORM STRESS TESTING")
    print("Testing different load levels...")
    
    for concurrent_users, requests_per_user in load_levels:
        print(f"\n{'='*20} LOAD LEVEL: {concurrent_users} users x {requests_per_user} requests {'='*20}")
        await stress_test.run_stress_test(concurrent_users, requests_per_user)
        await asyncio.sleep(2)  # Brief pause between tests

if __name__ == "__main__":
    asyncio.run(main()) 