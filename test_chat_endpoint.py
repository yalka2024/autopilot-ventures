"""
Test script for the chat endpoint
"""

import requests
import json
import time

def test_chat_endpoint():
    """Test the chat endpoint with multilingual prompts"""
    
    # Configuration
    base_url = "https://autopilot-ventures-1027187250482.us-central1.run.app"
    chat_url = f"{base_url}/api/chat"
    headers = {"Content-Type": "application/json"}
    
    # Test cases
    tests = [
        {
            "lang": "Spanish",
            "prompt": "¿Cuál es el clima hoy en Madrid?",
            "expected": "despejado"
        },
        {
            "lang": "French", 
            "prompt": "Donne-moi les dernières nouvelles économiques.",
            "expected": "nouvelles"
        },
        {
            "lang": "Chinese",
            "prompt": "请告诉我今天的汇率。",
            "expected": "汇率"
        },
        {
            "lang": "Arabic",
            "prompt": "ما هي أخبار الرياضة اليوم؟",
            "expected": "كرة القدم"
        },
        {
            "lang": "Hindi",
            "prompt": "आज की राजनीति पर कुछ बताइए।",
            "expected": "संसद"
        }
    ]
    
    print("🧪 Testing Chat Endpoint")
    print("=" * 50)
    
    results = []
    
    for test in tests:
        print(f"\n📝 Testing {test['lang']}: {test['prompt']}")
        
        try:
            # Prepare request
            body = {
                "prompt": test["prompt"],
                "language": test["lang"].lower()[:2]  # Get language code
            }
            
            # Make request
            start_time = time.time()
            response = requests.post(chat_url, headers=headers, json=body, timeout=30)
            end_time = time.time()
            
            duration = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get("response", "")
                
                # Check if expected content is in response
                if test["expected"].lower() in response_text.lower():
                    status = "✅ PASS"
                else:
                    status = "❌ MISMATCH"
                
                print(f"   Status: {status}")
                print(f"   Response: {response_text}")
                print(f"   Time: {duration:.2f}s")
                
                results.append({
                    "language": test["lang"],
                    "status": status,
                    "response": response_text,
                    "time": f"{duration:.2f}s"
                })
                
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                print(f"   Response: {response.text}")
                
                results.append({
                    "language": test["lang"],
                    "status": f"❌ HTTP {response.status_code}",
                    "response": response.text,
                    "time": "N/A"
                })
                
        except requests.exceptions.Timeout:
            print(f"   ⚠️ Timeout")
            results.append({
                "language": test["lang"],
                "status": "⚠️ Timeout",
                "response": "Request timed out",
                "time": "N/A"
            })
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            results.append({
                "language": test["lang"],
                "status": f"❌ Error",
                "response": str(e),
                "time": "N/A"
            })
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    
    for result in results:
        print(f"{result['language']:10} | {result['status']:15} | {result['time']:8}")
    
    # Count results
    passed = sum(1 for r in results if "PASS" in r["status"])
    total = len(results)
    
    print(f"\n✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    return results

if __name__ == "__main__":
    test_chat_endpoint() 