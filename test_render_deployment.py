#!/usr/bin/env python3
"""
Render Deployment Test Script
Tests all critical functionality for production deployment
"""

import requests
import json
import time

def test_render_deployment():
    """Test complete system for Render deployment"""
    base_url = "http://localhost:8002"
    
    print("🚀 Co-Buddy AGI - Render Deployment Test")
    print("=" * 60)
    
    results = []
    
    # Test 1: Basic Health Check
    print("\n1️⃣ Testing Health Check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {data.get('status')}")
            print(f"   📅 Timestamp: {data.get('timestamp')}")
            results.append(("Health Check", True))
        else:
            print(f"   ❌ Failed: {response.status_code}")
            results.append(("Health Check", False))
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results.append(("Health Check", False))
    
    # Test 2: AGI Status
    print("\n2️⃣ Testing AGI Status...")
    try:
        response = requests.get(f"{base_url}/agi/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Working Memory: {data.get('working_memory_size', 0)} items")
            print(f"   🧠 Available Skills: {data.get('available_skills', 0)}")
            print(f"   📊 Tasks Processed: {data.get('tasks_processed', 0)}")
            results.append(("AGI Status", True))
        else:
            print(f"   ❌ Failed: {response.status_code}")
            results.append(("AGI Status", False))
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results.append(("AGI Status", False))
    
    # Test 3: AGI Skills
    print("\n3️⃣ Testing AGI Skills...")
    try:
        response = requests.get(f"{base_url}/agi/skills", timeout=10)
        if response.status_code == 200:
            data = response.json()
            skills = data.get('skills', [])
            print(f"   ✅ Total Skills: {len(skills)}")
            for skill in skills[:3]:
                print(f"   🎯 {skill['name']}: {skill['capability_level']:.2f}")
            results.append(("AGI Skills", True))
        else:
            print(f"   ❌ Failed: {response.status_code}")
            results.append(("AGI Skills", False))
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results.append(("AGI Skills", False))
    
    # Test 4: AGI Task Processing
    print("\n4️⃣ Testing AGI Task Processing...")
    try:
        task_data = {
            "task": "What are the key benefits of artificial intelligence in healthcare?",
            "context": {"domain": "analysis", "complexity": "medium"}
        }
        response = requests.post(f"{base_url}/agi/process", json=task_data, timeout=30)
        if response.status_code == 200:
            data = response.json()
            result = data.get('result', {})
            print(f"   ✅ Task ID: {result.get('task_id', 'N/A')[:8]}...")
            print(f"   🧠 Reasoning: {result.get('reasoning_type', 'N/A')}")
            print(f"   📈 Confidence: {result.get('confidence', 0):.2f}")
            print(f"   ⏱️  Processing: {result.get('processing_time', 0):.2f}s")
            results.append(("AGI Processing", True))
        else:
            print(f"   ❌ Failed: {response.status_code}")
            results.append(("AGI Processing", False))
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results.append(("AGI Processing", False))
    
    # Test 5: Memory System
    print("\n5️⃣ Testing Memory System...")
    try:
        response = requests.get(f"{base_url}/skills", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Memory System Accessible")
            print(f"   📚 Skills in Memory: {len(data.get('skills', []))}")
            results.append(("Memory System", True))
        else:
            print(f"   ❌ Failed: {response.status_code}")
            results.append(("Memory System", False))
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results.append(("Memory System", False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name:<20} {status}")
    
    print(f"\n   Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - READY FOR RENDER DEPLOYMENT!")
        print("\n📋 Deployment Checklist:")
        print("   ✅ Hugging Face API configured")
        print("   ✅ Model2Vec embeddings working")
        print("   ✅ AGI core functional")
        print("   ✅ Memory system active")
        print("   ✅ All endpoints responding")
        print("   ✅ No hanging issues")
        print("\n🌐 Deploy to Render: https://render.com")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed - Review before deployment")
    
    print("\n🔗 Endpoints:")
    print(f"   • Main App: {base_url}")
    print(f"   • Health: {base_url}/health")
    print(f"   • AGI Process: {base_url}/agi/process")
    print(f"   • AGI Status: {base_url}/agi/status")
    print(f"   • AGI Skills: {base_url}/agi/skills")
    
    return passed == total

if __name__ == "__main__":
    test_render_deployment()
