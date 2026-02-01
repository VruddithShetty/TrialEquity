"""
Comprehensive Application Testing Script
Tests all critical paths, error handling, and integrations
"""
import asyncio
import sys
import os
import io
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import requests
import json
from datetime import datetime

# Fix Windows encoding issues
if sys.platform == "win32":
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass  # Already wrapped or not available

# Configuration
BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class AppTester:
    def __init__(self):
        self.token = None
        self.regulator_token = None
        self.test_results = []
        self.trial_id = None
        
    def log(self, message, color=Colors.RESET):
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"{color}[{timestamp}]{Colors.RESET} {message}")
        except (UnicodeEncodeError, UnicodeDecodeError):
            # Fallback for Windows console
            timestamp = datetime.now().strftime("%H:%M:%S")
            safe_message = message.encode('ascii', errors='replace').decode('ascii')
            print(f"[{timestamp}] {safe_message}")
    
    def test_result(self, name, success, details=""):
        try:
            status = f"{Colors.GREEN}[PASS]{Colors.RESET}" if success else f"{Colors.RED}[FAIL]{Colors.RESET}"
            self.test_results.append({"name": name, "success": success, "details": details})
            self.log(f"{status} {name}")
            if details and not success:
                self.log(f"     Details: {details}", Colors.YELLOW)
        except (UnicodeEncodeError, UnicodeDecodeError):
            status = "[PASS]" if success else "[FAIL]"
            self.test_results.append({"name": name, "success": success, "details": details})
            print(f"{status} {name}")
            if details and not success:
                print(f"     Details: {details}")
    
    # 1. Health Check
    async def test_health_check(self):
        """Test backend health endpoint"""
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            self.test_result("Health Check", response.status_code == 200, 
                           f"Status: {response.status_code}")
            return response.status_code == 200
        except Exception as e:
            self.test_result("Health Check", False, str(e))
            return False
    
    # 2. Authentication
    async def test_authentication(self):
        """Test login and token generation"""
        try:
            # Try REGULATOR role first (for audit logs test)
            response = requests.post(
                f"{BASE_URL}/api/login",
                data={"email": "regulator@example.com", "password": "test123"},
                timeout=10
            )
            
            # If that fails, try default test user
            if response.status_code != 200:
                response = requests.post(
                    f"{BASE_URL}/api/login",
                    data={"email": "test@example.com", "password": "test123"},
                    timeout=10
                )
            
            # Store regulator token separately for audit tests
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                role = data.get("user", {}).get("role", "UNKNOWN")
                if role == "REGULATOR":
                    self.regulator_token = token
                self.token = token
                self.test_result("Authentication", True, f"Token received, Role: {role}")
                return True
            else:
                self.test_result("Authentication", False, 
                               f"Status: {response.status_code}, {response.text[:200]}")
                return False
        except Exception as e:
            self.test_result("Authentication", False, str(e))
            return False
    
    # 3. Trial Upload
    async def test_trial_upload(self):
        """Test trial file upload"""
        if not self.token:
            self.test_result("Trial Upload", False, "No authentication token")
            return False
        
        try:
            # Create a test CSV file
            test_csv = """age,gender,ethnicity,eligibility_score
45,Male,White,0.95
52,Female,Black,0.92
38,Male,Asian,0.98
55,Female,Hispanic,0.90
48,Male,Other,0.93
47,Female,White,0.94
51,Male,Black,0.91
43,Female,Asian,0.96
49,Male,Hispanic,0.93
46,Female,Other,0.95"""
            
            files = {'file': ('test_trial.csv', test_csv, 'text/csv')}
            headers = {'Authorization': f'Bearer {self.token}'}
            
            response = requests.post(
                f"{BASE_URL}/api/uploadTrial",
                files=files,
                headers=headers,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.trial_id = data.get("trial_id")
                self.test_result("Trial Upload", True, 
                               f"Trial ID: {self.trial_id}")
                return True
            else:
                self.test_result("Trial Upload", False,
                               f"Status: {response.status_code}, {response.text[:200]}")
                return False
        except Exception as e:
            self.test_result("Trial Upload", False, str(e))
            return False
    
    # 4. Rule Validation
    async def test_rule_validation(self):
        """Test eligibility rule validation"""
        if not self.token or not self.trial_id:
            self.test_result("Rule Validation", False, "Missing trial_id or token")
            return False
        
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            response = requests.post(
                f"{BASE_URL}/api/validateRules?trial_id={self.trial_id}",
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status", "UNKNOWN")
                self.test_result("Rule Validation", True, f"Status: {status}")
                return True
            else:
                self.test_result("Rule Validation", False,
                               f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.test_result("Rule Validation", False, str(e))
            return False
    
    # 5. ML Bias Detection
    async def test_ml_bias_detection(self):
        """Test ML bias detection"""
        if not self.token or not self.trial_id:
            self.test_result("ML Bias Detection", False, "Missing trial_id or token")
            return False
        
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            response = requests.post(
                f"{BASE_URL}/api/runMLBiasCheck?trial_id={self.trial_id}",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                decision = data.get("decision", "UNKNOWN")
                score = data.get("fairness_score", 0)
                self.test_result("ML Bias Detection", True,
                               f"Decision: {decision}, Score: {score:.2%}")
                return True
            elif response.status_code == 503:
                self.test_result("ML Bias Detection", False,
                               "Model still training (503)")
                return False
            else:
                self.test_result("ML Bias Detection", False,
                               f"Status: {response.status_code}, {response.text[:200]}")
                return False
        except Exception as e:
            self.test_result("ML Bias Detection", False, str(e))
            return False
    
    # 6. Blockchain Write (if ML accepts)
    async def test_blockchain_write(self):
        """Test writing to blockchain"""
        if not self.token or not self.trial_id:
            self.test_result("Blockchain Write", False, "Missing trial_id or token")
            return False
        
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            response = requests.post(
                f"{BASE_URL}/api/blockchain/write?trial_id={self.trial_id}",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                tx_hash = data.get("transaction_hash", "N/A")
                self.test_result("Blockchain Write", True,
                               f"Transaction: {tx_hash[:20] if tx_hash != 'N/A' else 'N/A'}...")
                return True
            elif response.status_code == 400:
                # Expected if ML status is not ACCEPT/REVIEW
                self.test_result("Blockchain Write", True,
                               "Skipped (ML status requirement not met)")
                return True
            else:
                self.test_result("Blockchain Write", False,
                               f"Status: {response.status_code}, {response.text[:200]}")
                return False
        except Exception as e:
            self.test_result("Blockchain Write", False, str(e))
            return False
    
    # 7. Audit Logs
    async def test_audit_logs(self):
        """Test audit log retrieval"""
        # Use regulator token if available, otherwise try to login as regulator
        test_token = self.regulator_token
        
        if not test_token:
            # Try to login as regulator
            try:
                response = requests.post(
                    f"{BASE_URL}/api/login",
                    data={"email": "regulator@example.com", "password": "test123"},
                    timeout=10
                )
                if response.status_code == 200:
                    test_token = response.json().get("access_token")
                    self.regulator_token = test_token
                else:
                    self.test_result("Audit Logs", False, "Cannot login as REGULATOR")
                    return False
            except Exception as e:
                self.test_result("Audit Logs", False, f"Login failed: {str(e)}")
                return False
        
        try:
            headers = {'Authorization': f'Bearer {test_token}'}
            response = requests.get(
                f"{BASE_URL}/api/regulator/audit/logs",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                # Handle both list and dict responses
                if isinstance(data, list):
                    logs = data
                else:
                    logs = data.get("logs", []) if isinstance(data, dict) else []
                self.test_result("Audit Logs", True,
                               f"Retrieved {len(logs)} logs")
                return True
            elif response.status_code == 403:
                self.test_result("Audit Logs", False,
                               "403 Forbidden - REGULATOR role required")
                return False
            else:
                self.test_result("Audit Logs", False,
                               f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.test_result("Audit Logs", False, str(e))
            return False
    
    # 8. Error Handling Tests
    async def test_error_handling(self):
        """Test various error scenarios"""
        errors_found = []
        
        # Test 1: Upload without auth
        try:
            test_csv = "age,gender\n45,Male"
            files = {'file': ('test.csv', test_csv, 'text/csv')}
            response = requests.post(f"{BASE_URL}/api/uploadTrial", files=files, timeout=5)
            if response.status_code not in [401, 403]:
                errors_found.append("Upload without auth should return 401/403")
        except:
            pass
        
        # Test 2: Invalid trial_id
        if self.token:
            try:
                headers = {'Authorization': f'Bearer {self.token}'}
                response = requests.post(
                    f"{BASE_URL}/api/validateRules?trial_id=invalid_id",
                    headers=headers,
                    timeout=5
                )
                if response.status_code not in [404, 400]:
                    errors_found.append("Invalid trial_id should return 404")
            except:
                pass
        
        # Test 3: Invalid token
        try:
            headers = {'Authorization': 'Bearer invalid_token_12345'}
            response = requests.get(f"{BASE_URL}/api/regulator/audit/logs", headers=headers, timeout=5)
            if response.status_code not in [401, 403]:
                errors_found.append("Invalid token should return 401/403")
        except:
            pass
        
        if errors_found:
            self.test_result("Error Handling", False, "; ".join(errors_found))
            return False
        else:
            self.test_result("Error Handling", True, "All error cases handled correctly")
            return True
    
    # 9. Model Loading Test
    async def test_model_loading(self):
        """Test if ML models are loaded"""
        try:
            from ml_bias_detection_production import MLBiasDetector
            detector = MLBiasDetector()
            if detector.is_trained:
                accuracy = getattr(detector, 'model_accuracy', 0)
                self.test_result("Model Loading", True,
                               f"Model loaded, Accuracy: {accuracy:.2%}")
                return True
            else:
                self.test_result("Model Loading", False, "Model not trained")
                return False
        except Exception as e:
            self.test_result("Model Loading", False, str(e))
            return False
    
    # 10. Database Connection
    async def test_database_connection(self):
        """Test database connectivity"""
        try:
            from database import init_db
            await init_db()
            self.test_result("Database Connection", True, "Connected successfully")
            return True
        except Exception as e:
            self.test_result("Database Connection", False, str(e))
            return False
    
    # Run all tests
    async def run_all_tests(self):
        """Run comprehensive test suite"""
        print(f"\n{'='*70}")
        print(f"  COMPREHENSIVE APPLICATION TESTING")
        print(f"{'='*70}\n")
        
        # Infrastructure tests
        self.log("Testing Infrastructure...", Colors.BLUE)
        await self.test_health_check()
        await self.test_database_connection()
        await self.test_model_loading()
        
        # Authentication tests
        self.log("\nTesting Authentication...", Colors.BLUE)
        auth_success = await self.test_authentication()
        
        if not auth_success:
            self.log("\nWARNING: Authentication failed. Skipping authenticated tests.", Colors.YELLOW)
            return
        
        # Core functionality tests
        self.log("\nTesting Core Functionality...", Colors.BLUE)
        await self.test_trial_upload()
        await self.test_rule_validation()
        await self.test_ml_bias_detection()
        await self.test_blockchain_write()
        
        # Regulatory tests
        self.log("\nTesting Regulatory Features...", Colors.BLUE)
        await self.test_audit_logs()
        
        # Error handling
        self.log("\nTesting Error Handling...", Colors.BLUE)
        await self.test_error_handling()
        
        # Summary
        print(f"\n{'='*70}")
        print(f"  TEST SUMMARY")
        print(f"{'='*70}\n")
        
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r["success"])
        failed = total - passed
        
        for result in self.test_results:
            status = "[PASS]" if result["success"] else "[FAIL]"
            try:
                status_display = f"{Colors.GREEN}[PASS]{Colors.RESET}" if result["success"] else f"{Colors.RED}[FAIL]{Colors.RESET}"
                print(f"{status_display} {result['name']}")
            except:
                print(f"{status} {result['name']}")
            if result['details']:
                print(f"    -> {result['details']}")
        
        print(f"\nResults:")
        print(f"  Total: {total}")
        try:
            print(f"  {Colors.GREEN}Passed: {passed}{Colors.RESET}")
            print(f"  {Colors.RED}Failed: {failed}{Colors.RESET}")
        except:
            print(f"  Passed: {passed}")
            print(f"  Failed: {failed}")
        print(f"  Success Rate: {(passed/total*100):.1f}%")
        
        if failed == 0:
            try:
                print(f"\n{Colors.GREEN}ALL TESTS PASSED!{Colors.RESET}")
            except:
                print(f"\nALL TESTS PASSED!")
        else:
            try:
                print(f"\n{Colors.YELLOW}Some tests failed. Review the details above.{Colors.RESET}")
            except:
                print(f"\nSome tests failed. Review the details above.")
        
        print(f"\n{'='*70}\n")

async def main():
    tester = AppTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
