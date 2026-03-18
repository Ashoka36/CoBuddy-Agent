#!/usr/bin/env python3
"""
Test AGI functionality
"""

import requests
import json

def test_agi_system():
    """Test the AGI system endpoints"""
    base_url = "http://localhost:8002"
    
    print("🧪 Testing Co-Buddy AGI System")
    print("=" * 50)
    
    # Test 1: Health Check
    print("\n1. Testing Health Check...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test 2: AGI Status
    print("\n2. Testing AGI Status...")
    try:
        response = requests.get(f"{base_url}/agi/status")
        if response.status_code == 200:
            print("✅ AGI status check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ AGI status check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ AGI status check error: {e}")
    
    # Test 3: AGI Skills
    print("\n3. Testing AGI Skills...")
    try:
        response = requests.get(f"{base_url}/agi/skills")
        if response.status_code == 200:
            print("✅ AGI skills check passed")
            skills = response.json().get('skills', [])
            print(f"   Available skills: {len(skills)}")
            for skill in skills[:3]:
                print(f"   - {skill['name']}: {skill['description']}")
        else:
            print(f"❌ AGI skills check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ AGI skills check error: {e}")
    
    # Test 4: AGI Task Processing
    print("\n4. Testing AGI Task Processing...")
    try:
        task_data = {
            "task": "Solve this logical problem: If all humans are mortal, and Socrates is human, what can we conclude?",
            "context": {"domain": "logic"}
        }
        response = requests.post(f"{base_url}/agi/process", json=task_data)
        if response.status_code == 200:
            print("✅ AGI task processing passed")
            result = response.json().get('result', {})
            print(f"   Task ID: {result.get('task_id')}")
            print(f"   Reasoning Type: {result.get('reasoning_type')}")
            print(f"   Confidence: {result.get('confidence', 0):.2f}")
            print(f"   Processing Time: {result.get('processing_time', 0):.2f}s")
        else:
            print(f"❌ AGI task processing failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ AGI task processing error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 AGI System Test Complete!")
    print("\n📱 Fully Functional URL: http://localhost:8002")
    print("🔗 AGI Endpoints:")
    print("   - POST /agi/process - Process tasks with AGI")
    print("   - GET /agi/status - Check AGI system status")
    print("   - GET /agi/skills - List available AGI skills")
    print("   - GET /health - Basic health check")

if __name__ == "__main__":
    test_agi_system()
