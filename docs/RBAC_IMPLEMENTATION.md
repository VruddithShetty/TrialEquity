# Role-Based Access Control (RBAC) Implementation

## Overview

This document describes the comprehensive Role-Based Access Control (RBAC) system implemented in the Clinical Trials Blockchain Platform. All endpoints are now properly restricted based on user roles to ensure security and compliance.

## User Roles

### 1. SPONSOR
**Purpose**: Pharmaceutical companies or organizations funding clinical trials

**Permissions**:
- ✅ Upload clinical trials
- ✅ Validate trial rules
- ✅ Run ML bias checks
- ✅ Write to blockchain
- ✅ Verify blockchain integrity
- ✅ Digitally sign trials
- ✅ Download reports
- ✅ Use IPFS, tokenization, ZKP features (read/write)
- ✅ Trigger tamper alerts
- ❌ View audit logs
- ❌ View all trials (regulatory view)
- ❌ Access admin panel

### 2. INVESTIGATOR
**Purpose**: Researchers conducting clinical trials

**Permissions**:
- ✅ Upload clinical trials
- ✅ Validate trial rules
- ✅ Run ML bias checks
- ✅ Write to blockchain
- ✅ Verify blockchain integrity
- ✅ Digitally sign trials
- ✅ Download reports
- ✅ Use IPFS, tokenization, ZKP features (read/write)
- ✅ Trigger tamper alerts
- ❌ View audit logs
- ❌ View all trials (regulatory view)
- ❌ Access admin panel

### 3. REGULATOR
**Purpose**: Regulatory authorities (FDA, EMA, etc.) overseeing compliance

**Permissions**:
- ✅ **All SPONSOR/INVESTIGATOR permissions**
- ✅ View audit logs (`GET /api/regulator/audit/logs`)
- ✅ View all trials (`GET /api/regulator/trials`)
- ✅ Access admin panel:
  - View blockchain nodes (`GET /api/admin/nodes`)
  - View all users (`GET /api/admin/users`)
  - Retrain ML model (`POST /api/admin/retrain-model`)
- ✅ Receive tamper alerts
- ✅ Download regulatory reports

**Highest Access Level**: Full system access including regulatory oversight

### 4. ADMIN
**Purpose**: System administrators managing infrastructure

**Permissions**:
- ✅ **All SPONSOR/INVESTIGATOR permissions**
- ✅ Access admin panel:
  - View blockchain nodes (`GET /api/admin/nodes`)
  - View all users (`GET /api/admin/users`)
  - Retrain ML model (`POST /api/admin/retrain-model`)
- ❌ View audit logs (REGULATOR only)
- ❌ View all trials (REGULATOR only)

**Note**: ADMIN shares admin panel access with REGULATOR but does NOT have regulatory oversight capabilities.

### 5. AUDITOR
**Purpose**: External auditors with read-only access

**Permissions**:
- ✅ Verify blockchain integrity (read-only)
- ✅ Download reports (read-only)
- ✅ View model explanations (read-only)
- ✅ Verify digital signatures (read-only)
- ✅ Verify Zero-Knowledge Proofs (read-only)
- ✅ Generate tokens (read-only tokenization)
- ✅ Compare blockchain platforms (read-only)
- ❌ Upload trials
- ❌ Validate rules
- ❌ Run ML bias checks
- ❌ Write to blockchain
- ❌ Digitally sign trials
- ❌ Upload to IPFS
- ❌ Generate ZKP
- ❌ Trigger tamper alerts
- ❌ View audit logs
- ❌ Access admin panel

**Read-Only Access**: AUDITOR role is strictly read-only and cannot modify any data.

## Endpoint Access Matrix

| Endpoint | SPONSOR | INVESTIGATOR | REGULATOR | ADMIN | AUDITOR |
|----------|---------|--------------|-----------|-------|---------|
| `POST /api/uploadTrial` | ✅ | ✅ | ✅ | ✅ | ❌ |
| `POST /api/validateRules` | ✅ | ✅ | ✅ | ✅ | ❌ |
| `POST /api/runMLBiasCheck` | ✅ | ✅ | ✅ | ✅ | ❌ |
| `POST /api/model/explain` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `POST /api/blockchain/write` | ✅ | ✅ | ✅ | ✅ | ❌ |
| `POST /api/blockchain/verify` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `GET /api/regulator/audit/logs` | ❌ | ❌ | ✅ | ❌ | ❌ |
| `GET /api/regulator/trials` | ❌ | ❌ | ✅ | ❌ | ❌ |
| `GET /api/downloadReport` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `GET /api/blockchain/compare` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `POST /api/trial/sign` | ✅ | ✅ | ✅ | ❌ | ❌ |
| `POST /api/trial/verify-signature` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `POST /api/ipfs/upload` | ✅ | ✅ | ✅ | ✅ | ❌ |
| `POST /api/trial/tokenize` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `POST /api/zkp/generate` | ✅ | ✅ | ✅ | ✅ | ❌ |
| `POST /api/zkp/verify` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `GET /api/admin/nodes` | ❌ | ❌ | ✅ | ✅ | ❌ |
| `GET /api/admin/users` | ❌ | ❌ | ✅ | ✅ | ❌ |
| `POST /api/admin/retrain-model` | ❌ | ❌ | ✅ | ✅ | ❌ |
| `POST /api/alerts/tamper` | ✅ | ✅ | ✅ | ✅ | ❌ |

## RBAC Helper Functions

The system uses the following helper functions defined in `backend/auth.py`:

### `require_standard_access()`
- **Allowed Roles**: SPONSOR, INVESTIGATOR, REGULATOR, ADMIN
- **Use Case**: Standard operations like upload, validate, ML check, blockchain write
- **Excludes**: AUDITOR (read-only)

### `require_read_access()`
- **Allowed Roles**: SPONSOR, INVESTIGATOR, REGULATOR, ADMIN, AUDITOR
- **Use Case**: Read-only operations like verify, download reports, view explanations
- **Includes**: AUDITOR (read-only access)

### `require_regulatory_access()`
- **Allowed Roles**: REGULATOR only
- **Use Case**: Regulatory oversight features like audit logs, all trials view
- **Excludes**: All other roles

### `require_admin_access()`
- **Allowed Roles**: REGULATOR, ADMIN
- **Use Case**: Admin panel features like node management, user management, model retraining
- **Excludes**: SPONSOR, INVESTIGATOR, AUDITOR

### `require_signing_access()`
- **Allowed Roles**: INVESTIGATOR, REGULATOR, SPONSOR
- **Use Case**: Digital signature operations
- **Excludes**: ADMIN, AUDITOR

### `require_write_access()`
- **Allowed Roles**: SPONSOR, INVESTIGATOR, REGULATOR, ADMIN
- **Use Case**: Write operations like upload, blockchain write, IPFS upload
- **Excludes**: AUDITOR (read-only)

## Implementation Details

### Authentication Flow
1. User logs in via `POST /api/login`
2. JWT token is generated with user ID and role
3. Token is included in `Authorization: Bearer <token>` header
4. `verify_token()` validates the token and extracts user info
5. `get_current_user()` provides user info to endpoints
6. Role-based decorators check permissions before allowing access

### Error Handling
- **401 Unauthorized**: Invalid or missing authentication token
- **403 Forbidden**: Valid authentication but insufficient role permissions
- Clear error messages indicate required roles for access

### Security Features
- All endpoints require authentication (except `/health` and `/`)
- Role-based restrictions enforced at endpoint level
- AUDITOR role explicitly blocked from write operations
- Clear separation between regulatory and administrative functions
- Audit logs track all actions with user attribution

## Testing RBAC

To test role-based access:

1. **Create users with different roles**:
   ```python
   # Via registration endpoint
   POST /api/register
   {
     "email": "sponsor@example.com",
     "username": "sponsor",
     "password": "password123",
     "role": "SPONSOR"
   }
   ```

2. **Login and get token**:
   ```python
   POST /api/login
   email=sponsor@example.com&password=password123
   ```

3. **Test endpoint access**:
   - Use token in `Authorization: Bearer <token>` header
   - Verify 403 errors for unauthorized access
   - Verify 200/201 for authorized access

## Compliance & Security

This RBAC implementation ensures:
- ✅ **Principle of Least Privilege**: Users only have access to what they need
- ✅ **Separation of Duties**: Regulatory and administrative functions are separate
- ✅ **Audit Trail**: All actions are logged with user attribution
- ✅ **Read-Only Access**: AUDITOR role cannot modify any data
- ✅ **Market-Ready**: Professional-grade access control suitable for production

## Future Enhancements

Potential improvements:
- Fine-grained permissions (e.g., SPONSOR can only view their own trials)
- Permission inheritance and role hierarchies
- Dynamic role assignment
- Time-based access restrictions
- IP-based access restrictions

