/**
 * k6 load testing script for Clinical Trials Platform
 * Run with: k6 run k6_test.js
 */
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');
const uploadDuration = new Trend('upload_duration');
const mlCheckDuration = new Trend('ml_check_duration');

export const options = {
  stages: [
    { duration: '2m', target: 50 },   // Ramp up to 50 users
    { duration: '5m', target: 50 },   // Stay at 50 users
    { duration: '2m', target: 100 },  // Ramp up to 100 users
    { duration: '5m', target: 100 },  // Stay at 100 users
    { duration: '2m', target: 200 },  // Ramp up to 200 users
    { duration: '5m', target: 200 },  // Stay at 200 users
    { duration: '2m', target: 0 },     // Ramp down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'], // 95% of requests < 500ms, 99% < 1s
    http_req_failed: ['rate<0.01'],                  // Error rate < 1%
    errors: ['rate<0.01'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const API_TOKEN = __ENV.API_TOKEN || '';

export default function () {
  const headers = {
    'Content-Type': 'application/json',
  };
  
  if (API_TOKEN) {
    headers['Authorization'] = `Bearer ${API_TOKEN}`;
  }

  // 1. Upload Trial (30% of requests)
  if (Math.random() < 0.3) {
    const uploadStart = Date.now();
    const formData = {
      file: http.file('test_data.csv', 'participant_id,age,gender\n1,45,Male\n2,52,Female', 'text/csv'),
    };
    
    const uploadRes = http.post(`${BASE_URL}/api/uploadTrial`, formData, { headers });
    const uploadTime = Date.now() - uploadStart;
    uploadDuration.add(uploadTime);
    
    const uploadSuccess = check(uploadRes, {
      'upload status 201': (r) => r.status === 201,
      'upload has trial_id': (r) => r.json('trial_id') !== undefined,
    });
    
    errorRate.add(!uploadSuccess);
    
    if (uploadSuccess) {
      const trialId = uploadRes.json('trial_id');
      
      // 2. Run ML Check (20% of requests)
      if (Math.random() < 0.2) {
        const mlStart = Date.now();
        const mlRes = http.post(
          `${BASE_URL}/api/runMLBiasCheck?trial_id=${trialId}`,
          null,
          { headers }
        );
        const mlTime = Date.now() - mlStart;
        mlCheckDuration.add(mlTime);
        
        check(mlRes, {
          'ml check status 200': (r) => r.status === 200,
          'ml check has decision': (r) => r.json('decision') !== undefined,
        });
      }
      
      // 3. Write to Blockchain (10% of requests)
      if (Math.random() < 0.1) {
        const blockchainRes = http.post(
          `${BASE_URL}/api/blockchain/write?trial_id=${trialId}`,
          null,
          { headers }
        );
        
        check(blockchainRes, {
          'blockchain write status 200': (r) => r.status === 200,
        });
      }
    }
  }
  
  // 4. Compare Blockchains (10% of requests)
  if (Math.random() < 0.1) {
    const compareRes = http.get(`${BASE_URL}/api/blockchain/compare`, { headers });
    check(compareRes, {
      'compare status 200': (r) => r.status === 200,
    });
  }
  
  sleep(1);
}

export function handleSummary(data) {
  return {
    'summary.json': JSON.stringify(data),
    stdout: textSummary(data, { indent: ' ', enableColors: true }),
  };
}

