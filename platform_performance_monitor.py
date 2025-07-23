#!/usr/bin/env python3
"""
Platform Performance Monitor
Comprehensive monitoring and testing script for AutoPilot Ventures platform
"""

import asyncio
import time
import requests
import json
import os
from datetime import datetime
from typing import Dict, List, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class PlatformPerformanceMonitor:
    """Comprehensive platform performance monitoring"""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.results = {}
        self.start_time = time.time()
        
    async def check_health_endpoint(self) -> Dict[str, Any]:
        """Check platform health endpoint"""
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/health", timeout=10)
            response_time = time.time() - start_time
            
            return {
                "status": "success" if response.status_code == 200 else "error",
                "response_time": response_time,
                "status_code": response.status_code,
                "data": response.json() if response.status_code == 200 else None
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "response_time": None,
                "status_code": None
            }
    
    async def check_autonomous_status(self) -> Dict[str, Any]:
        """Check autonomous system status"""
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/real_autonomous_status", timeout=10)
            response_time = time.time() - start_time
            
            return {
                "status": "success" if response.status_code == 200 else "error",
                "response_time": response_time,
                "status_code": response.status_code,
                "data": response.json() if response.status_code == 200 else None
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "response_time": None,
                "status_code": None
            }
    
    async def check_phase1_status(self) -> Dict[str, Any]:
        """Check Phase 1 autonomous learning system status"""
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/phase1_status", timeout=10)
            response_time = time.time() - start_time
            
            return {
                "status": "success" if response.status_code == 200 else "error",
                "response_time": response_time,
                "status_code": response.status_code,
                "data": response.json() if response.status_code == 200 else None
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "response_time": None,
                "status_code": None
            }
    
    async def check_stripe_status(self) -> Dict[str, Any]:
        """Check Stripe payment system status"""
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/stripe_status", timeout=10)
            response_time = time.time() - start_time
            
            return {
                "status": "success" if response.status_code == 200 else "error",
                "response_time": response_time,
                "status_code": response.status_code,
                "data": response.json() if response.status_code == 200 else None
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "response_time": None,
                "status_code": None
            }
    
    async def check_real_businesses(self) -> Dict[str, Any]:
        """Check real businesses created by AI"""
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/real_businesses", timeout=10)
            response_time = time.time() - start_time
            
            return {
                "status": "success" if response.status_code == 200 else "error",
                "response_time": response_time,
                "status_code": response.status_code,
                "data": response.json() if response.status_code == 200 else None
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "response_time": None,
                "status_code": None
            }
    
    async def check_real_customers(self) -> Dict[str, Any]:
        """Check real customers acquired by AI"""
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/real_customers", timeout=10)
            response_time = time.time() - start_time
            
            return {
                "status": "success" if response.status_code == 200 else "error",
                "response_time": response_time,
                "status_code": response.status_code,
                "data": response.json() if response.status_code == 200 else None
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "response_time": None,
                "status_code": None
            }
    
    async def test_business_creation(self) -> Dict[str, Any]:
        """Test business creation performance"""
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/create_business",
                params={
                    "name": f"Test Business {datetime.now().strftime('%H%M%S')}",
                    "description": "Performance test business",
                    "niche": "technology",
                    "language": "en"
                },
                timeout=30
            )
            response_time = time.time() - start_time
            
            return {
                "status": "success" if response.status_code == 200 else "error",
                "response_time": response_time,
                "status_code": response.status_code,
                "data": response.json() if response.status_code == 200 else None
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "response_time": None,
                "status_code": None
            }
    
    async def test_autonomous_workflow(self) -> Dict[str, Any]:
        """Test autonomous workflow execution"""
        try:
            start_time = time.time()
            response = requests.post(f"{self.base_url}/start_autonomous_workflow", timeout=30)
            response_time = time.time() - start_time
            
            return {
                "status": "success" if response.status_code == 200 else "error",
                "response_time": response_time,
                "status_code": response.status_code,
                "data": response.json() if response.status_code == 200 else None
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "response_time": None,
                "status_code": None
            }
    
    async def check_environment_variables(self) -> Dict[str, Any]:
        """Check critical environment variables"""
        required_vars = [
            'OPENAI_SECRET_KEY',
            'STRIPE_SECRET_KEY', 
            'STRIPE_PUBLISHABLE_KEY'
        ]
        
        results = {}
        for var in required_vars:
            value = os.getenv(var)
            results[var] = {
                "present": value is not None,
                "length": len(value) if value else 0,
                "starts_with_sk": value.startswith('sk_') if value else False
            }
        
        return {
            "status": "success",
            "variables": results,
            "all_present": all(results[var]["present"] for var in required_vars)
        }
    
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive platform performance test"""
        print("🚀 Starting Comprehensive Platform Performance Test")
        print("=" * 60)
        
        # Test all endpoints and systems
        tests = [
            ("Health Check", self.check_health_endpoint),
            ("Autonomous Status", self.check_autonomous_status),
            ("Phase 1 Status", self.check_phase1_status),
            ("Stripe Status", self.check_stripe_status),
            ("Real Businesses", self.check_real_businesses),
            ("Real Customers", self.check_real_customers),
            ("Environment Variables", self.check_environment_variables),
            ("Business Creation Test", self.test_business_creation),
            ("Autonomous Workflow Test", self.test_autonomous_workflow)
        ]
        
        results = {}
        for test_name, test_func in tests:
            print(f"🔍 Testing: {test_name}")
            try:
                result = await test_func()
                results[test_name] = result
                
                if result["status"] == "success":
                    print(f"   ✅ {test_name}: SUCCESS")
                    if "response_time" in result and result["response_time"]:
                        print(f"   ⏱️  Response time: {result['response_time']:.3f}s")
                else:
                    print(f"   ❌ {test_name}: FAILED")
                    if "error" in result:
                        print(f"   🔍 Error: {result['error']}")
            except Exception as e:
                print(f"   💥 {test_name}: EXCEPTION - {str(e)}")
                results[test_name] = {"status": "exception", "error": str(e)}
        
        # Calculate overall performance metrics
        total_time = time.time() - self.start_time
        successful_tests = sum(1 for r in results.values() if r.get("status") == "success")
        total_tests = len(results)
        
        # Performance summary
        performance_summary = {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": (successful_tests / total_tests) * 100 if total_tests > 0 else 0,
            "total_execution_time": total_time,
            "average_response_time": self._calculate_average_response_time(results),
            "critical_systems_operational": self._check_critical_systems(results)
        }
        
        print("\n" + "=" * 60)
        print("📊 PERFORMANCE SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Success Rate: {performance_summary['success_rate']:.1f}%")
        print(f"Total Execution Time: {total_time:.2f}s")
        print(f"Average Response Time: {performance_summary['average_response_time']:.3f}s")
        print(f"Critical Systems: {'✅ OPERATIONAL' if performance_summary['critical_systems_operational'] else '❌ ISSUES DETECTED'}")
        
        return {
            "timestamp": datetime.now().isoformat(),
            "performance_summary": performance_summary,
            "detailed_results": results
        }
    
    def _calculate_average_response_time(self, results: Dict) -> float:
        """Calculate average response time from test results"""
        response_times = []
        for result in results.values():
            if result.get("response_time"):
                response_times.append(result["response_time"])
        
        return sum(response_times) / len(response_times) if response_times else 0
    
    def _check_critical_systems(self, results: Dict) -> bool:
        """Check if critical systems are operational"""
        critical_tests = [
            "Health Check",
            "Autonomous Status", 
            "Environment Variables"
        ]
        
        return all(
            results.get(test, {}).get("status") == "success"
            for test in critical_tests
        )
    
    def save_results(self, filename: str = None):
        """Save test results to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"platform_performance_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"💾 Results saved to: {filename}")

async def main():
    """Main execution function"""
    monitor = PlatformPerformanceMonitor()
    
    # Run comprehensive test
    results = await monitor.run_comprehensive_test()
    monitor.results = results
    
    # Save results
    monitor.save_results()
    
    # Print final status
    if results["performance_summary"]["critical_systems_operational"]:
        print("\n🎉 PLATFORM PERFORMANCE: EXCELLENT")
        print("🚀 All critical systems are operational!")
    else:
        print("\n⚠️ PLATFORM PERFORMANCE: ISSUES DETECTED")
        print("🔧 Some critical systems need attention")

if __name__ == "__main__":
    asyncio.run(main()) 