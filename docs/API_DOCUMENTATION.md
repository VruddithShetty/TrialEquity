# API Documentation

## Base URL

```
http://localhost:8000
```

## Authentication

All endpoints (except `/health`) require JWT authentication:

```
Authorization: Bearer <token>
```

## Endpoints

### 1. Upload Trial

**POST** `/api/uploadTrial`

Upload a clinical trial dataset file.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (CSV, JSON, or XML)

**Response:**
```json
{
  "trial_id": "uuid",
  "filename": "trial.csv",
  "status": "uploaded",
  "participant_count": 200,
  "message": "Trial uploaded successfully"
}
```

---

### 2. Validate Rules

**POST** `/api/validateRules`

Validate mandatory eligibility criteria.

**Query Parameters:**
- `trial_id` (string, required)

**Response:**
```json
{
  "status": "passed",
  "rules_passed": ["minimum_sample_size", "valid_age_range"],
  "rules_failed": [],
  "total_rules": 4
}
```

---

### 3. Run ML Bias Check

**POST** `/api/runMLBiasCheck`

Run machine learning bias detection on trial data.

**Query Parameters:**
- `trial_id` (string, required)

**Response:**
```json
{
  "trial_id": "uuid",
  "decision": "ACCEPT",
  "fairness_score": 0.85,
  "metrics": {
    "outlier_score": 0.12,
    "is_outlier": false,
    "bias_probability": 0.15,
    "fairness_metrics": {
      "demographic_parity": 0.92,
      "disparate_impact_ratio": 0.88,
      "equality_of_opportunity": 0.90
    },
    "statistical_tests": {
      "chi2_gender": 2.34,
      "p_value_gender": 0.67,
      "chi2_ethnicity": 5.12,
      "p_value_ethnicity": 0.28
    }
  },
  "recommendations": ["Trial meets fairness criteria"]
}
```

---

### 4. Write to Blockchain

**POST** `/api/blockchain/write`

Write validated trial to blockchain.

**Query Parameters:**
- `trial_id` (string, required)

**Response:**
```json
{
  "trial_id": "uuid",
  "tx_hash": "0xabc123...",
  "block_number": 42,
  "timestamp": "2024-01-15T10:30:00Z",
  "status": "success"
}
```

---

### 5. Verify Blockchain

**POST** `/api/blockchain/verify`

Verify trial integrity on blockchain.

**Query Parameters:**
- `trial_id` (string, required)

**Response:**
```json
{
  "trial_id": "uuid",
  "is_valid": true,
  "hash_match": true,
  "tamper_detected": false,
  "verification_timestamp": "2024-01-15T10:35:00Z"
}
```

---

### 6. Get Audit Logs

**GET** `/api/regulator/audit/logs`

Get audit logs (Regulator role required).

**Query Parameters:**
- `trial_id` (string, optional)
- `limit` (integer, default: 100)

**Response:**
```json
[
  {
    "log_id": "uuid",
    "trial_id": "uuid",
    "user_id": "uuid",
    "action": "blockchain_write",
    "timestamp": "2024-01-15T10:30:00Z",
    "details": {}
  }
]
```

---

### 7. Explain Model

**POST** `/api/model/explain`

Get SHAP/LIME explanations for ML model decisions.

**Query Parameters:**
- `trial_id` (string, required)

**Response:**
```json
{
  "trial_id": "uuid",
  "shap_values": {
    "values": [0.1, -0.2, 0.15, ...],
    "base_value": 0.5
  },
  "lime_explanation": {
    "explanation": "...",
    "score": 0.85
  },
  "feature_importance": {
    "feature_0": 0.25,
    "feature_1": 0.18,
    ...
  }
}
```

---

### 8. Download Report

**GET** `/api/downloadReport`

Download comprehensive PDF report.

**Query Parameters:**
- `trial_id` (string, required)

**Response:**
- Content-Type: `application/pdf`
- File download

---

### 9. Compare Blockchains

**GET** `/api/blockchain/compare`

Compare Hyperledger Fabric, MultiChain, and Quorum.

**Response:**
```json
{
  "hyperledger_fabric": {
    "tps": 3500,
    "latency_ms": 2.5,
    "privacy": "High",
    ...
  },
  "multichain": {
    "tps": 1000,
    "latency_ms": 5.0,
    ...
  },
  "quorum": {
    "tps": 100,
    "latency_ms": 15.0,
    ...
  },
  "summary": {
    "recommendation": "..."
  }
}
```

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message"
}
```

**Status Codes:**
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

