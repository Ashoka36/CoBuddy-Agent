#!/usr/bin/env python3
"""
End-to-End Connectivity Test for Twin Agent System
Tests communication between Giffy, Aegis, and Co-Buddy
"""

import asyncio
import json
import time
import sys
from pathlib import Path
import subprocess
import requests
from datetime import datetime

class AgentConnectivityTest:
    """Test suite for three-agent system connectivity"""
    
    def __init__(self):
        self.agents = {
            'giffy': {'port': 8001, 'url': 'http://localhost:8001', 'process': None},
            'aegis': {'port': 8000, 'url': 'http://localhost:8000', 'process': None},
            'cobuddy': {'port': 8002, 'url': 'http://localhost:8002', 'process': None}
        }
        self.test_results = {
            'startups': {},
            'health_checks': {},
            'communications': {},
            'training': {},
            'execution': {},
            'overall': 'FAILED'
        }
    
    def log(self, message: str, agent: str = None):
        """Log test progress"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        if agent:
            print(f"[{timestamp}] [{agent.upper()}] {message}")
        else:
            print(f"[{timestamp}] {message}")
    
    def start_agent(self, agent_name: str) -> bool:
        """Start an agent process"""
        try:
            self.log(f"Starting {agent_name}...", agent_name)
            
            if agent_name == 'giffy':
                cmd = ["python3", "main.py", "--port", str(self.agents[agent_name]['port'])]
                cwd = "/home/ash/Desktop/twin agent system/Giffy"
            elif agent_name == 'aegis':
                cmd = ["python3", "agent_server.py", "--port", str(self.agents[agent_name]['port'])]
                cwd = "/home/ash/Desktop/twin agent system/Aegis"
            elif agent_name == 'cobuddy':
                cmd = ["python3", "server/cobuddy_lightweight.py", "--port", str(self.agents[agent_name]['port'])]
                cwd = "/home/ash/Desktop/Co-buddy- Windsurf/cobuddy_agi_updated"
            else:
                return False
            
            # Start process
            process = subprocess.Popen(
                cmd,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.agents[agent_name]['process'] = process
            self.log(f"Process started with PID: {process.pid}", agent_name)
            
            # Wait for startup
            time.sleep(3)
            
            # Check if process is still running
            if process.poll() is None:
                self.log("Agent started successfully", agent_name)
                self.test_results['startups'][agent_name] = 'SUCCESS'
                return True
            else:
                stdout, stderr = process.communicate()
                self.log(f"Agent failed to start. Error: {stderr}", agent_name)
                self.test_results['startups'][agent_name] = 'FAILED'
                return False
                
        except Exception as e:
            self.log(f"Error starting agent: {e}", agent_name)
            self.test_results['startups'][agent_name] = 'FAILED'
            return False
    
    def health_check(self, agent_name: str) -> bool:
        """Check agent health endpoint"""
        try:
            url = f"{self.agents[agent_name]['url']}/health"
            self.log(f"Checking health at {url}", agent_name)
            
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"Health check passed: {data}", agent_name)
                self.test_results['health_checks'][agent_name] = 'SUCCESS'
                return True
            else:
                self.log(f"Health check failed: HTTP {response.status_code}", agent_name)
                self.test_results['health_checks'][agent_name] = 'FAILED'
                return False
                
        except Exception as e:
            self.log(f"Health check error: {e}", agent_name)
            self.test_results['health_checks'][agent_name] = 'FAILED'
            return False
    
    def test_communication(self, source: str, target: str) -> bool:
        """Test communication between agents"""
        try:
            self.log(f"Testing {source} → {target} communication", source)
            
            # Test different communication patterns based on agent types
            
            if source == 'cobuddy' and target == 'giffy':
                # Test memory storage
                url = f"{self.agents['giffy']['url']}/memory/add"
                data = {
                    "content": "Test memory from connectivity test",
                    "tags": ["test", "connectivity"],
                    "metadata": {"source": "cobuddy", "timestamp": datetime.now().isoformat()}
                }
                
            elif source == 'cobuddy' and target == 'aegis':
                # Test execution validation
                url = f"{self.agents['aegis']['url']}/test/execute"
                data = {
                    "task": "Test connectivity task",
                    "expected_outcome": "success"
                }
                
            elif source == 'giffy' and target == 'cobuddy':
                # Test memory retrieval
                url = f"{self.agents['cobuddy']['url']}/search/memories"
                data = {"query": "test", "limit": 5}
                
            else:
                # Generic test
                url = f"{self.agents[target]['url']}/health"
                data = {}
            
            response = requests.post(url, json=data, timeout=5) if data else requests.get(url, timeout=5)
            
            if response.status_code in [200, 201]:
                self.log(f"Communication {source} → {target}: SUCCESS", source)
                self.test_results['communications'][f"{source}_to_{target}"] = 'SUCCESS'
                return True
            else:
                self.log(f"Communication {source} → {target}: FAILED (HTTP {response.status_code})", source)
                self.test_results['communications'][f"{source}_to_{target}"] = 'FAILED'
                return False
                
        except Exception as e:
            self.log(f"Communication error {source} → {target}: {e}", source)
            self.test_results['communications'][f"{source}_to_{target}"] = 'FAILED'
            return False
    
    def test_training_functionality(self) -> bool:
        """Test training material addition"""
        try:
            self.log("Testing training material addition", "cobuddy")
            
            # Test URL learning
            url = f"{self.agents['cobuddy']['url']}/learn/url"
            data = {
                "skill_name": "Connectivity Test Skill",
                "content": "https://example.com/test",
                "tags": ["test", "connectivity"]
            }
            
            response = requests.post(url, json=data, timeout=10)
            
            if response.status_code in [200, 201]:
                self.log("Training material added successfully", "cobuddy")
                self.test_results['training']['url_learning'] = 'SUCCESS'
                return True
            else:
                self.log(f"Training failed: HTTP {response.status_code}", "cobuddy")
                self.test_results['training']['url_learning'] = 'FAILED'
                return False
                
        except Exception as e:
            self.log(f"Training test error: {e}", "cobuddy")
            self.test_results['training']['url_learning'] = 'FAILED'
            return False
    
    def test_execution_functionality(self) -> bool:
        """Test skill execution"""
        try:
            self.log("Testing skill execution", "cobuddy")
            
            # Create a test skill first
            skill_url = f"{self.agents['cobuddy']['url']}/skills/create"
            skill_data = {
                "name": "Test Execution Skill",
                "description": "A test skill for connectivity",
                "steps": [
                    {"action": "test", "description": "Test step"},
                    {"action": "verify", "description": "Verify step"}
                ]
            }
            
            skill_response = requests.post(skill_url, json=skill_data, timeout=5)
            
            if skill_response.status_code in [200, 201]:
                skill_id = skill_response.json().get('id', 'test_skill_1')
                
                # Now execute the skill
                exec_url = f"{self.agents['cobuddy']['url']}/execute/skill"
                exec_data = {
                    "skill_id": skill_id,
                    "user_input": "Test execution",
                    "watch_mode": True
                }
                
                exec_response = requests.post(exec_url, json=exec_data, timeout=10)
                
                if exec_response.status_code in [200, 201]:
                    self.log("Skill execution successful", "cobuddy")
                    self.test_results['execution']['skill_execution'] = 'SUCCESS'
                    return True
                else:
                    self.log(f"Skill execution failed: HTTP {exec_response.status_code}", "cobuddy")
                    self.test_results['execution']['skill_execution'] = 'FAILED'
                    return False
            else:
                self.log(f"Skill creation failed: HTTP {skill_response.status_code}", "cobuddy")
                self.test_results['execution']['skill_execution'] = 'FAILED'
                return False
                
        except Exception as e:
            self.log(f"Execution test error: {e}", "cobuddy")
            self.test_results['execution']['skill_execution'] = 'FAILED'
            return False
    
    def stop_all_agents(self):
        """Stop all agent processes"""
        self.log("Stopping all agents...")
        for agent_name, agent_info in self.agents.items():
            if agent_info['process']:
                try:
                    agent_info['process'].terminate()
                    agent_info['process'].wait(timeout=5)
                    self.log(f"Agent stopped", agent_name)
                except Exception as e:
                    self.log(f"Error stopping agent: {e}", agent_name)
                    try:
                        agent_info['process'].kill()
                    except:
                        pass
    
    def run_full_test(self) -> dict:
        """Run complete connectivity test"""
        self.log("="*80)
        self.log("STARTING END-TO-END CONNECTIVITY TEST")
        self.log("="*80)
        
        try:
            # Step 1: Start all agents
            self.log("\n" + "="*40 + " STEP 1: STARTING AGENTS " + "="*40)
            
            for agent in ['giffy', 'aegis', 'cobuddy']:
                if not self.start_agent(agent):
                    self.log(f"Failed to start {agent}, aborting test")
                    self.stop_all_agents()
                    return self.test_results
            
            # Step 2: Health checks
            self.log("\n" + "="*40 + " STEP 2: HEALTH CHECKS " + "="*40)
            
            for agent in ['giffy', 'aegis', 'cobuddy']:
                self.health_check(agent)
            
            # Step 3: Communication tests
            self.log("\n" + "="*40 + " STEP 3: COMMUNICATION TESTS " + "="*40)
            
            # Test all communication paths
            communications = [
                ('cobuddy', 'giffy'),
                ('cobuddy', 'aegis'),
                ('giffy', 'cobuddy')
            ]
            
            for source, target in communications:
                self.test_communication(source, target)
            
            # Step 4: Training functionality
            self.log("\n" + "="*40 + " STEP 4: TRAINING FUNCTIONALITY " + "="*40)
            self.test_training_functionality()
            
            # Step 5: Execution functionality
            self.log("\n" + "="*40 + " STEP 5: EXECUTION FUNCTIONALITY " + "="*40)
            self.test_execution_functionality()
            
            # Step 6: Training material location verification
            self.log("\n" + "="*40 + " STEP 6: TRAINING MATERIAL LOCATION " + "="*40)
            self.verify_training_material_location()
            
            # Calculate overall result
            all_success = True
            for category, results in self.test_results.items():
                if category == 'overall':
                    continue
                for test, result in results.items():
                    if result != 'SUCCESS':
                        all_success = False
                        break
            
            self.test_results['overall'] = 'SUCCESS' if all_success else 'FAILED'
            
        except Exception as e:
            self.log(f"Test execution error: {e}")
            self.test_results['overall'] = 'FAILED'
        
        finally:
            # Always stop agents
            self.stop_all_agents()
        
        # Print results
        self.print_results()
        
        return self.test_results
    
    def verify_training_material_location(self):
        """Verify where training materials are stored"""
        self.log("Verifying training material storage locations...")
        
        locations = {
            'cobuddy': '/home/ash/Desktop/Co-buddy- Windsurf/cobuddy_agi_updated/cobuddy_memory.db',
            'giffy': '/home/ash/Desktop/twin agent system/Giffy/cobuddy_memory.db'
        }
        
        for agent, path in locations.items():
            if Path(path).exists():
                size = Path(path).stat().st_size
                self.log(f"Training DB found: {path} ({size} bytes)", agent)
                self.test_results['training'][f'{agent}_db_location'] = 'SUCCESS'
            else:
                self.log(f"Training DB not found: {path}", agent)
                self.test_results['training'][f'{agent}_db_location'] = 'FAILED'
        
        # Check for training panels in UI
        ui_path = '/home/ash/Desktop/Co-buddy- Windsurf/cobuddy_agi_updated/client/index.html'
        if Path(ui_path).exists():
            with open(ui_path, 'r') as f:
                content = f.read()
            
            if 'Training' in content and 'From URL' in content:
                self.log("Training panel found in UI", "cobuddy")
                self.test_results['training']['ui_training_panel'] = 'SUCCESS'
            else:
                self.log("Training panel not found in UI", "cobuddy")
                self.test_results['training']['ui_training_panel'] = 'FAILED'
    
    def print_results(self):
        """Print test results"""
        self.log("\n" + "="*80)
        self.log("TEST RESULTS SUMMARY")
        self.log("="*80)
        
        for category, results in self.test_results.items():
            if category == 'overall':
                continue
            
            self.log(f"\n{category.upper()}:")
            for test, result in results.items():
                status = "✅" if result == 'SUCCESS' else "❌"
                self.log(f"  {status} {test}: {result}")
        
        self.log(f"\nOVERALL RESULT: {self.test_results['overall']}")
        
        if self.test_results['overall'] == 'SUCCESS':
            self.log("\n🎉 ALL TESTS PASSED - SYSTEM IS FULLY FUNCTIONAL!")
        else:
            self.log("\n⚠️ SOME TESTS FAILED - CHECK LOGS ABOVE")
        
        self.log("="*80)

def main():
    """Main test runner"""
    tester = AgentConnectivityTest()
    results = tester.run_full_test()
    
    # Save results to file
    results_file = "/home/ash/Desktop/connectivity_test_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Results saved to: {results_file}")
    
    return results['overall'] == 'SUCCESS'

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
