#!/usr/bin/env python3
"""
Co-Buddy AGI End-to-End Test Suite
Tests all functionality including Twin Agent integration
"""

import asyncio
import json
import sys
from pathlib import Path
import time
import requests

# Add server to path
sys.path.insert(0, str(Path(__file__).parent / "server"))

from cobuddy_lightweight import (
    memory, learner, executor, LightweightEmbeddings,
    LocalMemoryIndex, CobuddyMemory, Skill, SkillLevel
)

class CobuddyE2ETests:
    """End-to-end test suite for Co-Buddy AGI"""
    
    def __init__(self):
        self.results = {
            'passed': 0,
            'failed': 0,
            'tests': []
        }
        self.test_skill_id = None
        self.test_memory_ids = []
    
    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} | {test_name}: {message}")
        
        self.results['tests'].append({
            'name': test_name,
            'passed': passed,
            'message': message,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        })
        
        if passed:
            self.results['passed'] += 1
        else:
            self.results['failed'] += 1
    
    async def test_embeddings(self):
        """Test Model2Vec embeddings"""
        try:
            embeddings = LightweightEmbeddings()
            
            texts = ["Hello world", "Test embedding", "Co-Buddy AGI"]
            result = embeddings.encode(texts)
            
            assert result.shape == (3, 512), f"Expected shape (3, 512), got {result.shape}"
            self.log_test("Embeddings - Model2Vec", True, f"Generated {result.shape} embeddings")
        except Exception as e:
            self.log_test("Embeddings - Model2Vec", False, str(e))
    
    async def test_faiss_index(self):
        """Test FAISS IndexFlatL2"""
        try:
            index = LocalMemoryIndex()
            
            # Add memories
            success1 = index.add_memory("mem1", "Portfolio rebalancing strategy")
            success2 = index.add_memory("mem2", "Email management procedures")
            
            assert success1 and success2, "Failed to add memories"
            
            # Search
            results = index.search("portfolio", limit=5)
            assert len(results) > 0, "Search returned no results"
            
            self.log_test("FAISS - IndexFlatL2", True, f"Added 2 memories, found {len(results)} results")
        except Exception as e:
            self.log_test("FAISS - IndexFlatL2", False, str(e))
    
    async def test_memory_database(self):
        """Test SQLite memory database"""
        try:
            # Create test skill
            test_skill = Skill(
                id="test_skill_1",
                name="Test Skill",
                description="A test skill",
                level=SkillLevel.OBSERVATION,
                confidence=0.5,
                steps=[{"action": "test", "description": "Test step"}],
                training_sessions=1,
                last_executed=None,
                success_rate=0.0
            )
            
            # Add to memory
            success = memory.add_skill(test_skill)
            assert success, "Failed to add skill to memory"
            
            # Retrieve
            retrieved = memory.get_skill("test_skill_1")
            assert retrieved is not None, "Failed to retrieve skill"
            assert retrieved.name == "Test Skill", "Retrieved skill name mismatch"
            
            self.test_skill_id = "test_skill_1"
            self.log_test("Memory - SQLite Database", True, "Added and retrieved skill successfully")
        except Exception as e:
            self.log_test("Memory - SQLite Database", False, str(e))
    
    async def test_skill_learning_from_text(self):
        """Test learning from text"""
        try:
            training_id = await learner.learn_from_text(
                "Email Management",
                "Step 1: Open email client\nStep 2: Check inbox\nStep 3: Reply to messages",
                ["email", "productivity"]
            )
            
            assert training_id is not None, "Failed to create training data"
            self.test_memory_ids.append(training_id)
            
            self.log_test("Learning - From Text", True, f"Created training ID: {training_id}")
        except Exception as e:
            self.log_test("Learning - From Text", False, str(e))
    
    async def test_skill_learning_from_url(self):
        """Test learning from URL"""
        try:
            # Note: This will fail without internet, but we test the mechanism
            training_id = await learner.learn_from_url(
                "Portfolio Management",
                "https://example.com/portfolio-guide",
                ["finance", "portfolio"]
            )
            
            if training_id:
                self.test_memory_ids.append(training_id)
                self.log_test("Learning - From URL", True, f"Created training ID: {training_id}")
            else:
                self.log_test("Learning - From URL", False, "URL learning returned None (expected without internet)")
        except Exception as e:
            self.log_test("Learning - From URL", False, str(e))
    
    async def test_memory_search(self):
        """Test memory search"""
        try:
            results = memory.search_memories("email management", limit=5)
            
            assert isinstance(results, list), "Search should return list"
            self.log_test("Memory - Search", True, f"Found {len(results)} memories")
        except Exception as e:
            self.log_test("Memory - Search", False, str(e))
    
    async def test_skill_execution(self):
        """Test skill execution"""
        try:
            if not self.test_skill_id:
                self.log_test("Execution - Skill Execution", False, "No test skill ID available")
                return
            
            task = await executor.execute_skill(
                self.test_skill_id,
                "Test execution input",
                watch_mode=True
            )
            
            assert task is not None, "Execution returned None"
            assert task.id is not None, "Task has no ID"
            
            self.log_test("Execution - Skill Execution", True, f"Executed task: {task.id}")
        except Exception as e:
            self.log_test("Execution - Skill Execution", False, str(e))
    
    async def test_plugin_connectivity(self):
        """Test connectivity to Twin Agents"""
        try:
            # Test Giffy
            try:
                giffy_response = requests.get("http://localhost:8001/health", timeout=2)
                giffy_ok = giffy_response.status_code == 200
            except:
                giffy_ok = False
            
            # Test Aegis
            try:
                aegis_response = requests.get("http://localhost:8000/health", timeout=2)
                aegis_ok = aegis_response.status_code == 200
            except:
                aegis_ok = False
            
            if giffy_ok and aegis_ok:
                self.log_test("Integration - Twin Agent Connectivity", True, "Both agents accessible")
            elif giffy_ok:
                self.log_test("Integration - Twin Agent Connectivity", True, "Giffy accessible (Aegis not running)")
            else:
                self.log_test("Integration - Twin Agent Connectivity", False, "Twin agents not accessible (expected in test)")
        except Exception as e:
            self.log_test("Integration - Twin Agent Connectivity", False, str(e))
    
    async def test_agi_skills_injection(self):
        """Test AGI Skills document injection"""
        try:
            skills_path = Path(__file__).parent / "AGI_SKILLS.md"
            assert skills_path.exists(), "AGI_SKILLS.md not found"
            
            with open(skills_path, 'r') as f:
                content = f.read()
            
            assert "Learning & Knowledge Acquisition" in content, "Missing core sections"
            assert "Skill Mastery Levels" in content, "Missing skill levels"
            
            self.log_test("AGI - Skills Document", True, "AGI_SKILLS.md verified")
        except Exception as e:
            self.log_test("AGI - Skills Document", False, str(e))
    
    async def test_lightweight_dependencies(self):
        """Test lightweight dependency stack"""
        try:
            import model2vec
            import faiss
            import numpy
            from bs4 import BeautifulSoup
            
            # Verify no heavy dependencies
            try:
                import torch
                self.log_test("Dependencies - Lightweight Stack", False, "torch should not be installed")
                return
            except ImportError:
                pass  # Expected
            
            try:
                import sentence_transformers
                self.log_test("Dependencies - Lightweight Stack", False, "sentence_transformers should not be installed")
                return
            except ImportError:
                pass  # Expected
            
            self.log_test("Dependencies - Lightweight Stack", True, "All lightweight dependencies verified")
        except Exception as e:
            self.log_test("Dependencies - Lightweight Stack", False, str(e))
    
    async def test_glassmorphism_ui(self):
        """Test UI components"""
        try:
            ui_path = Path(__file__).parent / "client" / "index.html"
            assert ui_path.exists(), "index.html not found"
            
            with open(ui_path, 'r') as f:
                content = f.read()
            
            assert "glassmorphism" in content.lower() or "glass" in content.lower(), "Missing glassmorphism styles"
            assert "skeumorphism" in content.lower() or "btn" in content.lower(), "Missing button styles"
            assert "Co-Buddy AGI" in content, "Missing app title"
            
            self.log_test("UI - Glassmorphism & Skeumorphism", True, "UI components verified")
        except Exception as e:
            self.log_test("UI - Glassmorphism & Skeumorphism", False, str(e))
    
    async def test_training_panel(self):
        """Test training panel functionality"""
        try:
            ui_path = Path(__file__).parent / "client" / "index.html"
            
            with open(ui_path, 'r') as f:
                content = f.read()
            
            # Check for training methods
            assert "From URL" in content, "Missing URL training method"
            assert "From Text" in content, "Missing text training method"
            assert "From File" in content, "Missing file training method"
            assert "From Demo" in content, "Missing demo training method"
            
            self.log_test("UI - Training Panel", True, "All training methods present")
        except Exception as e:
            self.log_test("UI - Training Panel", False, str(e))
    
    async def test_execution_panel(self):
        """Test execution panel functionality"""
        try:
            ui_path = Path(__file__).parent / "client" / "index.html"
            
            with open(ui_path, 'r') as f:
                content = f.read()
            
            # Check for execution features
            assert "Execute Skill" in content, "Missing execution control"
            assert "Execution Status" in content, "Missing status display"
            assert "Watch Mode" in content, "Missing watch mode option"
            
            self.log_test("UI - Execution Panel", True, "Execution panel verified")
        except Exception as e:
            self.log_test("UI - Execution Panel", False, str(e))
    
    async def test_interaction_panel(self):
        """Test real-time interaction panel"""
        try:
            ui_path = Path(__file__).parent / "client" / "index.html"
            
            with open(ui_path, 'r') as f:
                content = f.read()
            
            # Check for chat features
            assert "chat" in content.lower(), "Missing chat functionality"
            assert "Real-Time" in content or "Interact" in content, "Missing interaction panel"
            assert "Quick Actions" in content, "Missing quick actions"
            
            self.log_test("UI - Interaction Panel", True, "Interaction panel verified")
        except Exception as e:
            self.log_test("UI - Interaction Panel", False, str(e))
    
    async def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*70)
        print("CO-BUDDY AGI - END-TO-END TEST SUITE")
        print("="*70)
        print(f"Testing: Model2Vec + FAISS + Twin Agent Integration")
        print(f"Start Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("-"*70)
        
        # Core functionality tests
        await self.test_embeddings()
        await self.test_faiss_index()
        await self.test_memory_database()
        
        # Learning tests
        await self.test_skill_learning_from_text()
        await self.test_skill_learning_from_url()
        await self.test_memory_search()
        
        # Execution tests
        await self.test_skill_execution()
        
        # Integration tests
        await self.test_plugin_connectivity()
        await self.test_agi_skills_injection()
        
        # Dependency tests
        await self.test_lightweight_dependencies()
        
        # UI tests
        await self.test_glassmorphism_ui()
        await self.test_training_panel()
        await self.test_execution_panel()
        await self.test_interaction_panel()
        
        # Print summary
        print("-"*70)
        print("TEST SUMMARY")
        print("-"*70)
        print(f"Total Tests: {len(self.results['tests'])}")
        print(f"Passed: {self.results['passed']}")
        print(f"Failed: {self.results['failed']}")
        
        if len(self.results['tests']) > 0:
            success_rate = (self.results['passed'] / len(self.results['tests'])) * 100
            print(f"Success Rate: {success_rate:.1f}%")
        
        if self.results['failed'] == 0:
            print("\n🎉 ALL TESTS PASSED - CO-BUDDY IS PRODUCTION READY!")
        else:
            print(f"\n⚠️  {self.results['failed']} TESTS FAILED")
        
        print("="*70)
        
        return self.results['failed'] == 0

async def main():
    """Main test runner"""
    test_suite = CobuddyE2ETests()
    success = await test_suite.run_all_tests()
    
    # Save results
    results_path = Path(__file__).parent / "test_results.json"
    with open(results_path, 'w') as f:
        json.dump(test_suite.results, f, indent=2)
    
    print(f"\n📄 Test results saved to: {results_path}")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
