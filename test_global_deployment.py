#!/usr/bin/env python3
"""
Global Deployment Test Script for AutoPilot Ventures
Tests business creation in Arabic and Japanese with comprehensive validation
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
import requests
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GlobalDeploymentTester:
    """Comprehensive global deployment tester."""
    
    def __init__(self):
        self.base_url = os.getenv('DEPLOYMENT_URL', 'http://localhost:5000')
        self.test_results = {}
        self.languages = {
            'ar': 'Arabic',
            'ja': 'Japanese',
            'en': 'English',
            'es': 'Spanish',
            'zh': 'Chinese'
        }
        
        # Test business configurations
        self.test_businesses = {
            'ar': {
                'name': 'منصة الذكاء الاصطناعي للإنتاجية',
                'description': 'منصة ذكية لإدارة المهام والمشاريع باستخدام الذكاء الاصطناعي',
                'niche': 'أدوات الإنتاجية الذكية',
                'target_audience': 'الشركات الناشئة والمؤسسات الصغيرة'
            },
            'ja': {
                'name': 'AI生産性プラットフォーム',
                'description': 'AIを活用したタスク管理とプロジェクト管理プラットフォーム',
                'niche': 'AI生産性ツール',
                'target_audience': 'スタートアップと中小企業'
            },
            'en': {
                'name': 'AI Productivity Platform',
                'description': 'AI-powered task and project management platform',
                'niche': 'AI Productivity Tools',
                'target_audience': 'Startups and small businesses'
            }
        }

    async def test_health_endpoint(self) -> Dict[str, Any]:
        """Test health endpoint."""
        logger.info("Testing health endpoint...")
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                logger.info("Health check passed")
                return {
                    'success': True,
                    'status_code': response.status_code,
                    'data': data,
                    'response_time': response.elapsed.total_seconds()
                }
            else:
                logger.error(f"Health check failed: {response.status_code}")
                return {
                    'success': False,
                    'status_code': response.status_code,
                    'error': response.text
                }
                
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def test_webhook_endpoint(self) -> Dict[str, Any]:
        """Test webhook endpoint."""
        logger.info("Testing webhook endpoint...")
        
        try:
            # Test webhook health
            response = requests.get(f"{self.base_url}/webhook/health", timeout=10)
            
            if response.status_code == 200:
                logger.info("Webhook health check passed")
                return {
                    'success': True,
                    'status_code': response.status_code,
                    'data': response.json()
                }
            else:
                logger.error(f"Webhook health check failed: {response.status_code}")
                return {
                    'success': False,
                    'status_code': response.status_code,
                    'error': response.text
                }
                
        except Exception as e:
            logger.error(f"Webhook test error: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def test_business_creation(self, language: str) -> Dict[str, Any]:
        """Test business creation in specific language."""
        logger.info(f"Testing business creation in {self.languages[language]}...")
        
        try:
            business_config = self.test_businesses[language]
            
            # Test business creation API
            payload = {
                'name': business_config['name'],
                'description': business_config['description'],
                'niche': business_config['niche'],
                'language': language,
                'target_audience': business_config['target_audience']
            }
            
            response = requests.post(
                f"{self.base_url}/api/business/create",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Business creation in {language} successful")
                return {
                    'success': True,
                    'language': language,
                    'business_id': data.get('business_id'),
                    'response_time': response.elapsed.total_seconds(),
                    'data': data
                }
            else:
                logger.error(f"Business creation in {language} failed: {response.status_code}")
                return {
                    'success': False,
                    'language': language,
                    'status_code': response.status_code,
                    'error': response.text
                }
                
        except Exception as e:
            logger.error(f"Business creation test error for {language}: {e}")
            return {
                'success': False,
                'language': language,
                'error': str(e)
            }

    async def test_agent_execution(self, language: str) -> Dict[str, Any]:
        """Test agent execution in specific language."""
        logger.info(f"Testing agent execution in {self.languages[language]}...")
        
        try:
            # Test niche research agent
            payload = {
                'agent_type': 'niche_research',
                'niche': self.test_businesses[language]['niche'],
                'market_data': 'Growing market for AI solutions',
                'language': language
            }
            
            response = requests.post(
                f"{self.base_url}/api/agent/execute",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Agent execution in {language} successful")
                return {
                    'success': True,
                    'language': language,
                    'agent_type': 'niche_research',
                    'response_time': response.elapsed.total_seconds(),
                    'data': data
                }
            else:
                logger.error(f"Agent execution in {language} failed: {response.status_code}")
                return {
                    'success': False,
                    'language': language,
                    'status_code': response.status_code,
                    'error': response.text
                }
                
        except Exception as e:
            logger.error(f"Agent execution test error for {language}: {e}")
            return {
                'success': False,
                'language': language,
                'error': str(e)
            }

    async def test_multilingual_content(self, language: str) -> Dict[str, Any]:
        """Test multilingual content generation."""
        logger.info(f"Testing multilingual content in {self.languages[language]}...")
        
        try:
            # Test content creation agent
            payload = {
                'agent_type': 'content_creation',
                'topic': 'AI productivity benefits',
                'audience': self.test_businesses[language]['target_audience'],
                'content_type': 'blog post',
                'language': language
            }
            
            response = requests.post(
                f"{self.base_url}/api/agent/execute",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Multilingual content in {language} successful")
                return {
                    'success': True,
                    'language': language,
                    'content_type': 'blog post',
                    'response_time': response.elapsed.total_seconds(),
                    'data': data
                }
            else:
                logger.error(f"Multilingual content in {language} failed: {response.status_code}")
                return {
                    'success': False,
                    'language': language,
                    'status_code': response.status_code,
                    'error': response.text
                }
                
        except Exception as e:
            logger.error(f"Multilingual content test error for {language}: {e}")
            return {
                'success': False,
                'language': language,
                'error': str(e)
            }

    async def test_payment_processing(self, language: str) -> Dict[str, Any]:
        """Test payment processing with multi-currency support."""
        logger.info(f"Testing payment processing in {self.languages[language]}...")
        
        try:
            # Test payment endpoint
            payload = {
                'language': language,
                'currency': self._get_currency_for_language(language),
                'amount': 1000,  # $10.00
                'test': True
            }
            
            response = requests.post(
                f"{self.base_url}/webhook/test-payment",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Payment processing in {language} successful")
                return {
                    'success': True,
                    'language': language,
                    'currency': data.get('currency'),
                    'amount': data.get('amount'),
                    'response_time': response.elapsed.total_seconds()
                }
            else:
                logger.error(f"Payment processing in {language} failed: {response.status_code}")
                return {
                    'success': False,
                    'language': language,
                    'status_code': response.status_code,
                    'error': response.text
                }
                
        except Exception as e:
            logger.error(f"Payment processing test error for {language}: {e}")
            return {
                'success': False,
                'language': language,
                'error': str(e)
            }

    def _get_currency_for_language(self, language: str) -> str:
        """Get currency for language."""
        currency_map = {
            'ar': 'USD',
            'ja': 'JPY',
            'en': 'USD',
            'es': 'EUR',
            'zh': 'CNY'
        }
        return currency_map.get(language, 'USD')

    async def test_performance_metrics(self) -> Dict[str, Any]:
        """Test performance metrics endpoint."""
        logger.info("Testing performance metrics...")
        
        try:
            response = requests.get(f"{self.base_url}/api/metrics", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                logger.info("Performance metrics test successful")
                return {
                    'success': True,
                    'data': data,
                    'response_time': response.elapsed.total_seconds()
                }
            else:
                logger.error(f"Performance metrics test failed: {response.status_code}")
                return {
                    'success': False,
                    'status_code': response.status_code,
                    'error': response.text
                }
                
        except Exception as e:
            logger.error(f"Performance metrics test error: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def test_autonomous_features(self) -> Dict[str, Any]:
        """Test autonomous features."""
        logger.info("Testing autonomous features...")
        
        try:
            response = requests.get(f"{self.base_url}/api/autonomous/status", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                logger.info("Autonomous features test successful")
                return {
                    'success': True,
                    'autonomy_level': data.get('autonomy_level'),
                    'agents_initialized': data.get('agents_initialized'),
                    'data': data
                }
            else:
                logger.error(f"Autonomous features test failed: {response.status_code}")
                return {
                    'success': False,
                    'status_code': response.status_code,
                    'error': response.text
                }
                
        except Exception as e:
            logger.error(f"Autonomous features test error: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive global deployment test."""
        logger.info("Starting comprehensive global deployment test...")
        
        start_time = time.time()
        test_results = {
            'timestamp': datetime.utcnow().isoformat(),
            'base_url': self.base_url,
            'tests': {},
            'summary': {}
        }
        
        try:
            # Test health endpoint
            test_results['tests']['health'] = await self.test_health_endpoint()
            
            # Test webhook endpoint
            test_results['tests']['webhook'] = await self.test_webhook_endpoint()
            
            # Test business creation in different languages
            business_results = {}
            for language in ['ar', 'ja', 'en']:
                business_results[language] = await self.test_business_creation(language)
            test_results['tests']['business_creation'] = business_results
            
            # Test agent execution in different languages
            agent_results = {}
            for language in ['ar', 'ja', 'en']:
                agent_results[language] = await self.test_agent_execution(language)
            test_results['tests']['agent_execution'] = agent_results
            
            # Test multilingual content
            content_results = {}
            for language in ['ar', 'ja', 'en']:
                content_results[language] = await self.test_multilingual_content(language)
            test_results['tests']['multilingual_content'] = content_results
            
            # Test payment processing
            payment_results = {}
            for language in ['ar', 'ja', 'en']:
                payment_results[language] = await self.test_payment_processing(language)
            test_results['tests']['payment_processing'] = payment_results
            
            # Test performance metrics
            test_results['tests']['performance_metrics'] = await self.test_performance_metrics()
            
            # Test autonomous features
            test_results['tests']['autonomous_features'] = await self.test_autonomous_features()
            
            # Generate summary
            test_results['summary'] = self._generate_test_summary(test_results['tests'])
            test_results['execution_time'] = time.time() - start_time
            
            logger.info("Comprehensive global deployment test completed")
            return test_results
            
        except Exception as e:
            logger.error(f"Comprehensive test failed: {e}")
            test_results['error'] = str(e)
            test_results['execution_time'] = time.time() - start_time
            return test_results

    def _generate_test_summary(self, tests: Dict[str, Any]) -> Dict[str, Any]:
        """Generate test summary."""
        summary = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'success_rate': 0.0,
            'languages_tested': [],
            'performance_metrics': {}
        }
        
        # Count test results
        for test_category, test_result in tests.items():
            if isinstance(test_result, dict):
                if test_result.get('success', False):
                    summary['passed_tests'] += 1
                else:
                    summary['failed_tests'] += 1
                summary['total_tests'] += 1
                
                # Check for language-specific tests
                if 'language' in test_result:
                    lang = test_result['language']
                    if lang not in summary['languages_tested']:
                        summary['languages_tested'].append(lang)
                
                # Collect performance metrics
                if 'response_time' in test_result:
                    if 'response_times' not in summary['performance_metrics']:
                        summary['performance_metrics']['response_times'] = []
                    summary['performance_metrics']['response_times'].append(test_result['response_time'])
        
        # Calculate success rate
        if summary['total_tests'] > 0:
            summary['success_rate'] = (summary['passed_tests'] / summary['total_tests']) * 100
        
        # Calculate average response time
        if 'response_times' in summary['performance_metrics']:
            response_times = summary['performance_metrics']['response_times']
            if response_times:
                summary['performance_metrics']['average_response_time'] = sum(response_times) / len(response_times)
                summary['performance_metrics']['max_response_time'] = max(response_times)
                summary['performance_metrics']['min_response_time'] = min(response_times)
        
        return summary

    def print_test_report(self, test_results: Dict[str, Any]):
        """Print comprehensive test report."""
        print("\n" + "="*80)
        print("🌍 GLOBAL DEPLOYMENT TEST REPORT")
        print("="*80)
        
        # Basic info
        print(f"📅 Timestamp: {test_results['timestamp']}")
        print(f"🌐 Base URL: {test_results['base_url']}")
        print(f"⏱️  Execution Time: {test_results.get('execution_time', 0):.2f}s")
        
        # Summary
        summary = test_results.get('summary', {})
        print(f"\n📊 SUMMARY:")
        print(f"   Total Tests: {summary.get('total_tests', 0)}")
        print(f"   Passed: {summary.get('passed_tests', 0)}")
        print(f"   Failed: {summary.get('failed_tests', 0)}")
        print(f"   Success Rate: {summary.get('success_rate', 0):.1f}%")
        
        # Languages tested
        languages = summary.get('languages_tested', [])
        if languages:
            print(f"   Languages Tested: {', '.join(languages)}")
        
        # Performance metrics
        perf_metrics = summary.get('performance_metrics', {})
        if 'average_response_time' in perf_metrics:
            print(f"\n⚡ PERFORMANCE:")
            print(f"   Average Response Time: {perf_metrics['average_response_time']:.3f}s")
            print(f"   Max Response Time: {perf_metrics['max_response_time']:.3f}s")
            print(f"   Min Response Time: {perf_metrics['min_response_time']:.3f}s")
        
        # Detailed results
        print(f"\n🔍 DETAILED RESULTS:")
        tests = test_results.get('tests', {})
        
        for test_name, test_result in tests.items():
            if isinstance(test_result, dict):
                status = "✅ PASS" if test_result.get('success', False) else "❌ FAIL"
                print(f"   {test_name}: {status}")
                
                if 'language' in test_result:
                    lang_name = self.languages.get(test_result['language'], test_result['language'])
                    print(f"     Language: {lang_name}")
                
                if 'response_time' in test_result:
                    print(f"     Response Time: {test_result['response_time']:.3f}s")
                
                if not test_result.get('success', False) and 'error' in test_result:
                    print(f"     Error: {test_result['error']}")
        
        print("\n" + "="*80)


async def main():
    """Main test function."""
    print("🌍 AutoPilot Ventures Global Deployment Test")
    print("="*50)
    
    tester = GlobalDeploymentTester()
    
    # Run comprehensive test
    test_results = await tester.run_comprehensive_test()
    
    # Print report
    tester.print_test_report(test_results)
    
    # Save results to file
    with open('global_deployment_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(test_results, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n📄 Detailed results saved to: global_deployment_test_results.json")
    
    # Exit with appropriate code
    summary = test_results.get('summary', {})
    success_rate = summary.get('success_rate', 0)
    
    if success_rate >= 90:
        print("🎉 Excellent! Global deployment test passed with high success rate.")
        exit(0)
    elif success_rate >= 70:
        print("✅ Good! Global deployment test passed with acceptable success rate.")
        exit(0)
    else:
        print("⚠️  Issues detected in global deployment test.")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 