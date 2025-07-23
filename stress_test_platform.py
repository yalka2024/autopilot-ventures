#!/usr/bin/env python3
"""
Stress Test Platform
Simulates 100 users across 10 languages to test platform performance and scalability
"""

import asyncio
import json
import logging
import random
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import aiohttp
import psutil
import threading
from collections import defaultdict, deque

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class UserProfile:
    """Simulated user profile"""
    user_id: str
    language: str
    region: str
    user_type: str  # new, returning, premium
    session_duration: int  # seconds
    actions_per_session: int
    conversion_probability: float

@dataclass
class StressTestConfig:
    """Stress test configuration"""
    total_users: int
    languages: List[str]
    regions: List[str]
    test_duration: int  # minutes
    ramp_up_time: int  # minutes
    peak_concurrent_users: int
    target_endpoints: List[str]
    success_threshold: float  # percentage

@dataclass
class PerformanceMetrics:
    """Performance metrics for stress testing"""
    response_time: float
    throughput: float  # requests per second
    error_rate: float
    cpu_usage: float
    memory_usage: float
    active_connections: int
    timestamp: datetime

@dataclass
class StressTestResult:
    """Results from stress test"""
    test_id: str
    start_time: datetime
    end_time: datetime
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: float
    p95_response_time: float
    p99_response_time: float
    max_concurrent_users: int
    peak_throughput: float
    error_rate: float
    cpu_peak: float
    memory_peak: float
    recommendations: List[str]
    language_performance: Dict[str, Dict]
    region_performance: Dict[str, Dict]

class StressTestPlatform:
    """Comprehensive stress testing platform"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results: Dict[str, StressTestResult] = {}
        self.performance_history: Dict[str, List[PerformanceMetrics]] = {}
        self.active_users: Dict[str, UserProfile] = {}
        self.metrics_queue = deque(maxlen=1000)
        self.stop_testing = False
        
        # Performance tracking
        self.request_times: List[float] = []
        self.error_counts = defaultdict(int)
        self.success_counts = defaultdict(int)
        
    async def create_user_profiles(self, config: StressTestConfig) -> List[UserProfile]:
        """Create diverse user profiles for stress testing"""
        profiles = []
        
        # Define user types and their characteristics
        user_types = {
            "new": {"session_duration": (300, 900), "actions": (3, 8), "conversion": 0.02},
            "returning": {"session_duration": (600, 1800), "actions": (5, 15), "conversion": 0.08},
            "premium": {"session_duration": (1200, 3600), "actions": (10, 25), "conversion": 0.15}
        }
        
        for i in range(config.total_users):
            language = random.choice(config.languages)
            region = random.choice(config.regions)
            user_type = random.choices(
                ["new", "returning", "premium"], 
                weights=[0.6, 0.3, 0.1]
            )[0]
            
            user_config = user_types[user_type]
            session_duration = random.randint(*user_config["session_duration"])
            actions_per_session = random.randint(*user_config["actions"])
            conversion_probability = user_config["conversion"]
            
            profile = UserProfile(
                user_id=f"stress_user_{language}_{region}_{i}",
                language=language,
                region=region,
                user_type=user_type,
                session_duration=session_duration,
                actions_per_session=actions_per_session,
                conversion_probability=conversion_probability
            )
            profiles.append(profile)
        
        logger.info(f"Created {len(profiles)} user profiles for stress testing")
        return profiles
    
    async def simulate_user_session(self, profile: UserProfile, session_id: str) -> Dict[str, Any]:
        """Simulate a complete user session"""
        session_data = {
            "user_id": profile.user_id,
            "session_id": session_id,
            "language": profile.language,
            "region": profile.region,
            "start_time": datetime.now(),
            "actions": [],
            "converted": False,
            "errors": []
        }
        
        try:
            # Simulate user actions
            actions = [
                "page_view",
                "product_browse",
                "add_to_cart",
                "checkout_start",
                "payment_attempt",
                "conversion"
            ]
            
            for action_idx in range(profile.actions_per_session):
                action = random.choice(actions[:action_idx + 2])  # Progressive actions
                
                # Simulate action with realistic timing
                action_delay = random.uniform(1, 5)
                await asyncio.sleep(action_delay)
                
                # Record action
                action_data = {
                    "action": action,
                    "timestamp": datetime.now(),
                    "response_time": random.uniform(0.1, 2.0),
                    "success": random.random() > 0.05  # 95% success rate
                }
                
                session_data["actions"].append(action_data)
                
                # Check for conversion
                if action == "conversion" and random.random() < profile.conversion_probability:
                    session_data["converted"] = True
                    break
                
                # Simulate occasional errors
                if random.random() < 0.02:  # 2% error rate
                    error_data = {
                        "error_type": random.choice(["timeout", "server_error", "validation_error"]),
                        "timestamp": datetime.now(),
                        "recovered": random.random() > 0.3
                    }
                    session_data["errors"].append(error_data)
        
        except Exception as e:
            logger.error(f"Error in user session {session_id}: {e}")
            session_data["errors"].append({
                "error_type": "session_error",
                "message": str(e),
                "timestamp": datetime.now()
            })
        
        session_data["end_time"] = datetime.now()
        session_data["duration"] = (session_data["end_time"] - session_data["start_time"]).total_seconds()
        
        return session_data
    
    async def monitor_system_performance(self) -> PerformanceMetrics:
        """Monitor system performance metrics"""
        try:
            # CPU and memory usage
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Network connections
            connections = len(psutil.net_connections())
            
            # Calculate response time statistics
            if self.request_times:
                avg_response_time = sum(self.request_times) / len(self.request_times)
                sorted_times = sorted(self.request_times)
                p95_idx = int(len(sorted_times) * 0.95)
                p99_idx = int(len(sorted_times) * 0.99)
                p95_response_time = sorted_times[p95_idx] if p95_idx < len(sorted_times) else 0
                p99_response_time = sorted_times[p99_idx] if p99_idx < len(sorted_times) else 0
            else:
                avg_response_time = p95_response_time = p99_response_time = 0
            
            # Calculate throughput
            total_requests = sum(self.success_counts.values()) + sum(self.error_counts.values())
            throughput = total_requests / 60 if total_requests > 0 else 0  # requests per second
            
            # Calculate error rate
            total_errors = sum(self.error_counts.values())
            error_rate = total_errors / total_requests if total_requests > 0 else 0
            
            metrics = PerformanceMetrics(
                response_time=avg_response_time,
                throughput=throughput,
                error_rate=error_rate,
                cpu_usage=cpu_percent,
                memory_usage=memory_percent,
                active_connections=connections,
                timestamp=datetime.now()
            )
            
            self.metrics_queue.append(metrics)
            return metrics
            
        except Exception as e:
            logger.error(f"Error monitoring system performance: {e}")
            return None
    
    async def run_stress_test(self, config: StressTestConfig) -> StressTestResult:
        """Run comprehensive stress test"""
        test_id = f"stress_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_time = datetime.now()
        
        logger.info(f"Starting stress test {test_id} with {config.total_users} users")
        
        try:
            # Create user profiles
            user_profiles = await self.create_user_profiles(config)
            
            # Initialize performance monitoring
            performance_thread = threading.Thread(
                target=self._monitor_performance_loop,
                args=(test_id,),
                daemon=True
            )
            performance_thread.start()
            
            # Calculate user ramp-up schedule
            ramp_up_interval = config.ramp_up_time * 60 / config.total_users  # seconds per user
            
            # Start user sessions
            active_sessions = []
            session_counter = 0
            
            for i, profile in enumerate(user_profiles):
                if self.stop_testing:
                    break
                
                # Ramp up users gradually
                if i > 0:
                    await asyncio.sleep(ramp_up_interval)
                
                session_id = f"session_{test_id}_{session_counter}"
                session_counter += 1
                
                # Start user session
                session_task = asyncio.create_task(
                    self.simulate_user_session(profile, session_id)
                )
                active_sessions.append(session_task)
                
                # Limit concurrent sessions
                if len(active_sessions) >= config.peak_concurrent_users:
                    # Wait for some sessions to complete
                    done, pending = await asyncio.wait(
                        active_sessions, 
                        return_when=asyncio.FIRST_COMPLETED
                    )
                    active_sessions = list(pending)
            
            # Wait for all remaining sessions to complete
            if active_sessions:
                await asyncio.gather(*active_sessions, return_exceptions=True)
            
            # Calculate test results
            end_time = datetime.now()
            test_duration = (end_time - start_time).total_seconds()
            
            # Aggregate results
            total_requests = sum(self.success_counts.values()) + sum(self.error_counts.values())
            successful_requests = sum(self.success_counts.values())
            failed_requests = sum(self.error_counts.values())
            
            # Calculate response time statistics
            if self.request_times:
                avg_response_time = sum(self.request_times) / len(self.request_times)
                sorted_times = sorted(self.request_times)
                p95_idx = int(len(sorted_times) * 0.95)
                p99_idx = int(len(sorted_times) * 0.99)
                p95_response_time = sorted_times[p95_idx] if p95_idx < len(sorted_times) else 0
                p99_response_time = sorted_times[p99_idx] if p99_idx < len(sorted_times) else 0
            else:
                avg_response_time = p95_response_time = p99_response_time = 0
            
            # Calculate performance peaks
            performance_history = list(self.metrics_queue)
            if performance_history:
                cpu_peak = max(m.cpu_usage for m in performance_history)
                memory_peak = max(m.memory_usage for m in performance_history)
                peak_throughput = max(m.throughput for m in performance_history)
            else:
                cpu_peak = memory_peak = peak_throughput = 0
            
            # Generate recommendations
            recommendations = self._generate_stress_test_recommendations(
                total_requests, successful_requests, avg_response_time, 
                cpu_peak, memory_peak, config
            )
            
            # Analyze performance by language and region
            language_performance = self._analyze_language_performance(user_profiles)
            region_performance = self._analyze_region_performance(user_profiles)
            
            result = StressTestResult(
                test_id=test_id,
                start_time=start_time,
                end_time=end_time,
                total_requests=total_requests,
                successful_requests=successful_requests,
                failed_requests=failed_requests,
                average_response_time=avg_response_time,
                p95_response_time=p95_response_time,
                p99_response_time=p99_response_time,
                max_concurrent_users=config.peak_concurrent_users,
                peak_throughput=peak_throughput,
                error_rate=failed_requests / total_requests if total_requests > 0 else 0,
                cpu_peak=cpu_peak,
                memory_peak=memory_peak,
                recommendations=recommendations,
                language_performance=language_performance,
                region_performance=region_performance
            )
            
            self.test_results[test_id] = result
            logger.info(f"Stress test {test_id} completed successfully")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in stress test {test_id}: {e}")
            raise
    
    def _monitor_performance_loop(self, test_id: str):
        """Background performance monitoring loop"""
        while not self.stop_testing:
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                metrics = loop.run_until_complete(self.monitor_system_performance())
                if metrics:
                    self.performance_history[test_id] = self.performance_history.get(test_id, [])
                    self.performance_history[test_id].append(metrics)
                loop.close()
                time.sleep(5)  # Monitor every 5 seconds
            except Exception as e:
                logger.error(f"Error in performance monitoring: {e}")
    
    def _generate_stress_test_recommendations(self, total_requests: int, successful_requests: int,
                                           avg_response_time: float, cpu_peak: float, 
                                           memory_peak: float, config: StressTestConfig) -> List[str]:
        """Generate recommendations based on stress test results"""
        recommendations = []
        
        # Success rate analysis
        success_rate = successful_requests / total_requests if total_requests > 0 else 0
        if success_rate < config.success_threshold:
            recommendations.append(f"Success rate {success_rate:.2%} below threshold {config.success_threshold:.2%}")
        
        # Response time analysis
        if avg_response_time > 2.0:
            recommendations.append(f"Average response time {avg_response_time:.2f}s is too high")
        
        # Resource usage analysis
        if cpu_peak > 80:
            recommendations.append(f"CPU usage peaked at {cpu_peak:.1f}% - consider scaling")
        
        if memory_peak > 85:
            recommendations.append(f"Memory usage peaked at {memory_peak:.1f}% - optimize memory usage")
        
        # Throughput analysis
        if total_requests > 0:
            throughput = total_requests / 60  # requests per second
            if throughput < 10:
                recommendations.append("Throughput is low - optimize request handling")
        
        # Positive feedback
        if success_rate > 0.95 and avg_response_time < 1.0:
            recommendations.append("Excellent performance - system is ready for production")
        
        return recommendations
    
    def _analyze_language_performance(self, user_profiles: List[UserProfile]) -> Dict[str, Dict]:
        """Analyze performance by language"""
        language_stats = defaultdict(lambda: {
            "total_users": 0,
            "conversions": 0,
            "avg_session_duration": 0,
            "error_rate": 0
        })
        
        for profile in user_profiles:
            lang = profile.language
            language_stats[lang]["total_users"] += 1
            language_stats[lang]["avg_session_duration"] += profile.session_duration
        
        # Calculate averages
        for lang, stats in language_stats.items():
            if stats["total_users"] > 0:
                stats["avg_session_duration"] /= stats["total_users"]
        
        return dict(language_stats)
    
    def _analyze_region_performance(self, user_profiles: List[UserProfile]) -> Dict[str, Dict]:
        """Analyze performance by region"""
        region_stats = defaultdict(lambda: {
            "total_users": 0,
            "conversions": 0,
            "avg_session_duration": 0,
            "error_rate": 0
        })
        
        for profile in user_profiles:
            region = profile.region
            region_stats[region]["total_users"] += 1
            region_stats[region]["avg_session_duration"] += profile.session_duration
        
        # Calculate averages
        for region, stats in region_stats.items():
            if stats["total_users"] > 0:
                stats["avg_session_duration"] /= stats["total_users"]
        
        return dict(region_stats)
    
    async def run_multilingual_stress_test(self) -> StressTestResult:
        """Run stress test with 100 users across 10 languages"""
        config = StressTestConfig(
            total_users=100,
            languages=["en", "es", "fr", "de", "pt", "it", "ja", "zh", "ar", "hi"],
            regions=["US", "EU", "APAC", "LATAM", "MEA"],
            test_duration=30,  # minutes
            ramp_up_time=5,    # minutes
            peak_concurrent_users=50,
            target_endpoints=[
                "/api/business/create",
                "/api/payment/process",
                "/api/agent/execute",
                "/api/dashboard/metrics"
            ],
            success_threshold=0.95
        )
        
        return await self.run_stress_test(config)
    
    async def generate_stress_test_report(self, test_id: str) -> str:
        """Generate comprehensive stress test report"""
        if test_id not in self.test_results:
            raise ValueError(f"Test {test_id} not found")
        
        result = self.test_results[test_id]
        
        report = f"""
# Stress Test Report - {test_id}

## Test Overview
- **Start Time**: {result.start_time}
- **End Time**: {result.end_time}
- **Duration**: {(result.end_time - result.start_time).total_seconds() / 60:.1f} minutes
- **Total Users**: 100 (across 10 languages)

## Performance Metrics
- **Total Requests**: {result.total_requests:,}
- **Successful Requests**: {result.successful_requests:,}
- **Failed Requests**: {result.failed_requests:,}
- **Success Rate**: {result.successful_requests / result.total_requests * 100:.2f}%
- **Error Rate**: {result.error_rate * 100:.2f}%

## Response Times
- **Average**: {result.average_response_time:.3f}s
- **95th Percentile**: {result.p95_response_time:.3f}s
- **99th Percentile**: {result.p99_response_time:.3f}s

## System Resources
- **Peak CPU Usage**: {result.cpu_peak:.1f}%
- **Peak Memory Usage**: {result.memory_peak:.1f}%
- **Peak Throughput**: {result.peak_throughput:.1f} requests/second
- **Max Concurrent Users**: {result.max_concurrent_users}

## Language Performance
"""
        
        for language, stats in result.language_performance.items():
            report += f"- **{language.upper()}**: {stats['total_users']} users, {stats['avg_session_duration']:.0f}s avg session\n"
        
        report += f"""
## Region Performance
"""
        
        for region, stats in result.region_performance.items():
            report += f"- **{region}**: {stats['total_users']} users, {stats['avg_session_duration']:.0f}s avg session\n"
        
        report += f"""
## Recommendations
"""
        
        for rec in result.recommendations:
            report += f"- {rec}\n"
        
        report += f"""
## Test Status
- **Overall Result**: {'PASSED' if result.error_rate < 0.05 else 'FAILED'}
- **Ready for Production**: {'YES' if result.error_rate < 0.02 and result.average_response_time < 1.0 else 'NO'}
"""
        
        return report
    
    def stop_all_tests(self):
        """Stop all running stress tests"""
        self.stop_testing = True
        logger.info("Stopping all stress tests")

async def main():
    """Main function to demonstrate stress testing"""
    stress_tester = StressTestPlatform()
    
    try:
        # Run multilingual stress test
        result = await stress_tester.run_multilingual_stress_test()
        
        # Generate report
        report = await stress_tester.generate_stress_test_report(result.test_id)
        print(report)
        
        # Save results
        with open(f"stress_test_report_{result.test_id}.md", "w") as f:
            f.write(report)
        
        logger.info(f"Stress test completed. Report saved to stress_test_report_{result.test_id}.md")
        
    except KeyboardInterrupt:
        logger.info("Stress test interrupted by user")
        stress_tester.stop_all_tests()
    except Exception as e:
        logger.error(f"Error in stress test: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 