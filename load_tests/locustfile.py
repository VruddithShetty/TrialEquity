"""
Locust load testing script for Clinical Trials Platform
"""
from locust import HttpUser, task, between
import random
import json

class ClinicalTrialsUser(HttpUser):
    """
    Simulates a user interacting with the Clinical Trials Platform
    """
    wait_time = between(1, 3)
    trial_ids = []
    
    def on_start(self):
        """Called when a simulated user starts"""
        # Login and get token
        # Note: In production, use actual test credentials
        try:
            response = self.client.post("/api/auth/login", json={
                "username": "test_user",
                "password": "test_password"
            })
            if response.status_code == 200:
                self.token = response.json()["access_token"]
                self.headers = {"Authorization": f"Bearer {self.token}"}
            else:
                # If login fails, continue without auth (some endpoints may be public)
                self.headers = {}
        except:
            self.headers = {}
    
    @task(3)
    def upload_trial(self):
        """Upload a clinical trial (weight: 3)"""
        # Create a simple test file
        files = {
            'file': ('trial.csv', 
                    'participant_id,age,gender,ethnicity\n1,45,Male,White\n2,52,Female,Black',
                    'text/csv')
        }
        response = self.client.post(
            "/api/uploadTrial",
            files=files,
            headers=self.headers
        )
        if response.status_code == 201:
            trial_id = response.json().get("trial_id")
            if trial_id:
                self.trial_ids.append(trial_id)
    
    @task(2)
    def run_ml_check(self):
        """Run ML bias check (weight: 2)"""
        if not self.trial_ids:
            return
        
        trial_id = random.choice(self.trial_ids)
        self.client.post(
            f"/api/runMLBiasCheck?trial_id={trial_id}",
            headers=self.headers
        )
    
    @task(2)
    def validate_rules(self):
        """Validate eligibility rules (weight: 2)"""
        if not self.trial_ids:
            return
        
        trial_id = random.choice(self.trial_ids)
        self.client.post(
            f"/api/validateRules?trial_id={trial_id}",
            headers=self.headers
        )
    
    @task(1)
    def write_to_blockchain(self):
        """Write trial to blockchain (weight: 1)"""
        if not self.trial_ids:
            return
        
        trial_id = random.choice(self.trial_ids)
        self.client.post(
            f"/api/blockchain/write?trial_id={trial_id}",
            headers=self.headers
        )
    
    @task(1)
    def verify_blockchain(self):
        """Verify blockchain integrity (weight: 1)"""
        if not self.trial_ids:
            return
        
        trial_id = random.choice(self.trial_ids)
        self.client.post(
            f"/api/blockchain/verify?trial_id={trial_id}",
            headers=self.headers
        )
    
    @task(1)
    def get_audit_logs(self):
        """Get audit logs (weight: 1) - Regulator only"""
        self.client.get(
            "/api/regulator/audit/logs",
            headers=self.headers
        )
    
    @task(1)
    def compare_blockchains(self):
        """Compare blockchain platforms (weight: 1)"""
        self.client.get(
            "/api/blockchain/compare",
            headers=self.headers
        )

