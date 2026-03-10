# KSeF 2.0 API Integration Research

> **Research Date:** 2026-03-10  
> **API Version:** 2.2.0  
> **Target Project:** Rozlicz

---

## Table of Contents

1. [Overview](#overview)
2. [API Endpoints for Invoice Retrieval](#1-api-endpoints-for-invoice-retrieval)
3. [Authentication Flows](#2-authentication-flows)
4. [Rate Limiting](#3-rate-limiting)
5. [Error Codes](#4-error-codes)
6. [Python Libraries & Examples](#5-python-libraries--examples)
7. [Existing Integrations](#6-existing-integrations)
8. [Recommended Approach](#7-recommended-approach)
9. [Blockers & Considerations](#8-blockers--considerations)

---

## Overview

**KSeF (Krajowy System e-Faktur)** is Poland's National e-Invoice System - a centralized teleinformatics system for issuing and receiving structured electronic invoices. KSeF 2.0 is the current version with a comprehensive REST API.

### API Base URLs by Environment

| Environment | Base URL | Purpose |
|-------------|----------|---------|
| **TEST** | `https://api-test.ksef.mf.gov.pl` | Development & testing (10x higher rate limits) |
| **DEMO** | `https://api-demo.ksef.mf.gov.pl` | Pre-production validation (production-like limits) |
| **PRODUCTION** | `https://api.ksef.mf.gov.pl` | Live environment |

### Official Documentation

- **OpenAPI Spec:** Available at `/docs/v2` on each environment
- **Official Docs:** https://github.com/CIRFMF/ksef-docs (Polish)
- **API Version:** 2.2.0 (as of March 2026)

---

## 1. API Endpoints for Invoice Retrieval

### 1.1 Key Endpoints Summary

| Operation | Endpoint | Method | Rate Limits (PRD) |
|-----------|----------|--------|-------------------|
| Query invoice metadata | `/invoices/query/metadata` | POST | 8/s, 16/min, 20/h |
| Export invoices (batch) | `/invoices/exports` | POST | 4/s, 8/min, 20/h |
| Check export status | `/invoices/exports/{referenceNumber}` | GET | 10/s, 60/min, 600/h |
| Download single invoice | `/invoices/ksef/{ksefNumber}` | GET | 8/s, 16/min, 64/h |
| Download UPO (receipt) | `/sessions/{ref}/invoices/{invRef}/upo` | GET | Session-based |

### 1.2 Detailed Endpoint Documentation

#### Query Invoice Metadata
**`POST /invoices/query/metadata`**

Primary endpoint for incremental synchronization. Returns invoice metadata (not full content).

**Request Body:**
```json
{
  "subjectType": "Subject1",
  "dateRange": {
    "dateType": "Issue",
    "from": "2025-01-01",
    "to": "2025-01-31"
  }
}
```

**Subject Types:**
- `Subject1` - Sales invoices (you are the seller)
- `Subject2` - Purchase invoices (you are the buyer)
- `Subject3` - Invoices where you are an authorized entity

**Date Types:**
- `Issue` - Invoice issue date
- `Invoicing` - Date accepted by KSeF
- `PermanentStorage` - Date of permanent storage

#### Export Invoices (Async Batch)
**`POST /invoices/exports`**

For high-volume scenarios. Creates an async export job that packages multiple invoices into a ZIP file.

**Flow:**
1. POST `/invoices/exports` → Returns `referenceNumber`
2. Poll GET `/invoices/exports/{referenceNumber}` until status = "Ready"
3. Download the ZIP package

#### Download Single Invoice
**`GET /invoices/ksef/{ksefNumber}``**

Returns the full invoice XML by KSeF number. For low-volume scenarios only.

### 1.3 Session Management Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/sessions/online` | POST | Open interactive session |
| `/sessions/online/{ref}/invoices` | POST | Send invoice in session |
| `/sessions/online/{ref}/close` | POST | Close interactive session |
| `/sessions/batch` | POST | Open batch session |
| `/sessions/batch/{ref}/close` | POST | Close batch session |
| `/sessions` | GET | List active sessions |

---

## 2. Authentication Flows

KSeF 2.0 supports multiple authentication methods:

### 2.1 Authentication Methods Comparison

| Method | Environment | Use Case | Complexity |
|--------|-------------|----------|------------|
| **XAdES Certificate** | All | Production, high-volume | High |
| **KSeF Token** | All | API integrations, read-only | Medium |
| **Test Certificate** | TEST only | Development testing | Low |

### 2.2 XAdES Certificate Authentication (Production)

**Flow:**
1. Obtain qualified electronic seal certificate from MCU (Ministry of Digital Affairs)
2. Load certificate + private key (PEM or P12/PFX format)
3. Authenticate via XAdES signature
4. Receive access token + refresh token
5. Use Bearer token for subsequent requests

**Certificate Requirements:**
- Must be a qualified electronic seal (pieczęć kwalifikowana)
- Issued by certified provider in Poland
- Linked to company NIP number

**Python Example (using ksef2):**
```python
from ksef2 import Client, Environment
from ksef2.core.xades import (
    load_certificate_from_pem,
    load_private_key_from_pem
)

# Load certificate and key
cert = load_certificate_from_pem("cert.pem")
key = load_private_key_from_pem("key.pem")

# Or from P12/PFX
cert, key = load_certificate_and_key_from_p12("cert.p12", password=b"secret")

# Authenticate
client = Client(Environment.PRODUCTION)
auth = client.authentication.with_xades(
    nip="1234567890",
    cert=cert,
    private_key=key,
)

print(auth.access_token)  # Bearer token
print(auth.refresh_token)  # For token refresh
```

### 2.3 KSeF Token Authentication (Recommended for Read-Only)

**Flow:**
1. Generate token in KSeF web portal (ksef.gov.pl)
2. Select permissions (e.g., `invoice_read` for read-only)
3. Use token directly for API authentication
4. Token has expiration date and can be revoked

**Token Types:**
- **Read-only** - For invoice retrieval, monitoring
- **Read-write** - For sending invoices, managing sessions

**Python Example:**
```python
from ksef2 import Client

client = Client()
auth = client.authentication.with_token(
    ksef_token="your-ksef-token",
    nip="1234567890",
)

# Use auth for API calls
metadata = auth.invoices.query_metadata(filters=...)
```

### 2.4 Test Certificate (Development Only)

For TEST environment, self-signed certificates can be generated by the SDK.

```python
from ksef2 import Client, Environment

client = Client(Environment.TEST)
auth = client.authentication.with_test_certificate(nip="1234567890")
```

### 2.5 Token Refresh

Access tokens expire. Use refresh token to obtain new access tokens without re-authenticating.

```python
# Refresh tokens
refreshed = client.authentication.refresh(refresh_token=auth.refresh_token)
print(refreshed.access_token.token)
```

---

## 3. Rate Limiting

### 3.1 Rate Limit Model

KSeF uses a **sliding/rolling window** rate limiting model:

- **req/s** - Requests in the last second
- **req/min** - Requests in the last 60 seconds
- **req/h** - Requests in the last 60 minutes

Limits are enforced per **context + IP address** pair. Different IPs for the same NIP/context have separate limits.

### 3.2 Production Rate Limits

#### Invoice Retrieval
| Endpoint | req/s | req/min | req/h |
|----------|-------|---------|-------|
| POST /invoices/query/metadata | 8 | 16 | 20 |
| POST /invoices/exports | 4 | 8 | 20 |
| GET /invoices/exports/{ref} | 10 | 60 | 600 |
| GET /invoices/ksef/{ksefNumber} | 8 | 16 | 64 |

#### Interactive Sessions
| Endpoint | req/s | req/min | req/h |
|----------|-------|---------|-------|
| POST /sessions/online | 10 | 30 | 120 |
| POST /sessions/online/{ref}/invoices | 10 | 30 | 180 |
| POST /sessions/online/{ref}/close | 10 | 30 | 120 |

#### Batch Sessions
| Endpoint | req/s | req/min | req/h |
|----------|-------|---------|-------|
| POST /sessions/batch | 10 | 20 | 60 |
| POST /sessions/batch/{ref}/close | 10 | 20 | 60 |
| Batch part uploads | No limits | - | - |

#### Other Endpoints
| Endpoint | req/s | req/min | req/h |
|----------|-------|---------|-------|
| GET /auth/sessions | 10 | 30 | 120 |
| POST /auth/* | 10 | 30 | 120 |
| Other endpoints | 10 | 30 | 120 |

### 3.3 Rate Limit Response

When limits are exceeded, API returns:

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 30
Content-Type: application/json

{
  "status": {
    "code": 429,
    "description": "Too Many Requests",
    "details": ["Przekroczono limit 20 żądań na minutę. Spróbuj ponownie po 30 sekundach."]
  }
}
```

### 3.4 Test Environment Limits

TEST environment has **10x higher limits** than production for development.

### 3.5 Best Practices

- Use **incremental synchronization** with `/invoices/query/metadata`
- For high volumes, use **batch exports** (`/invoices/exports`)
- Store data locally; don't query KSeF for UI operations
- Implement exponential backoff with jitter
- Respect `Retry-After` header

---

## 4. Error Codes

### 4.1 HTTP Status Codes

| Code | Description | Handling |
|------|-------------|----------|
| 200 | OK | Success |
| 202 | Accepted | Async operation started (poll for status) |
| 204 | No Content | Success, no response body |
| 400 | Bad Request | Validation error, check request |
| 401 | Unauthorized | Invalid or expired token, re-authenticate |
| 403 | Forbidden | Insufficient permissions |
| 429 | Too Many Requests | Rate limit exceeded, retry after delay |
| 460 | Auth Status Error | Authentication rejected (suspended cert, etc.) |
| 500 | Internal Server Error | KSeF error, retry with backoff |

### 4.2 SDK Error Classes (Python/TypeScript)

| Class | When | Key Fields |
|-------|------|------------|
| `KsefError` | Base SDK error | `message` |
| `KsefHttpError` | HTTP >= 400 without JSON | `statusCode`, `responseBody` |
| `KsefApiError` | HTTP >= 400 with JSON | `statusCode`, `responseBody` |
| `KsefRateLimitError` | 429 Too Many Requests | `statusCode`, `retryAfter` |
| `KsefAuthStatusError` | 460 Auth rejected | `statusCode`, `statusDetails` |
| `KsefSessionExpiredError` | Session/token expired | `message` |
| `KsefValidationError` | Input validation failed | `message`, `details` |

### 4.3 Common Exception Codes

| Code | Description | Context |
|------|-------------|---------|
| 21405 | Validation error | Various endpoints |
| 21418 | Invalid continuation token | Pagination |
| 25001 | Cannot get CSR data for auth method | Certificates |
| 25002 | Cannot submit CSR for auth method | Certificates |
| 25003 | CSR data doesn't match auth data | Certificates |
| 25004 | Invalid CSR format or signature | Certificates |
| 25005 | Certificate enrollment not found | Certificates |
| 25006 | Max enrollment limit reached | Certificates |
| 25007 | Max certificate limit reached | Certificates |

---

## 5. Python Libraries & Examples

### 5.1 Available Python Libraries

| Library | Stars | Last Update | Features |
|---------|-------|-------------|----------|
| **[ksef2](https://github.com/artpods56/ksef2)** | 61 | 2 days ago | Full SDK, 100% API coverage, Python 3.12+ |
| **[KSeF_Monitor](https://github.com/mlotocki2k/KSeF_Monitor)** | 1 | Active | Invoice monitor with notifications |

### 5.2 Recommended: ksef2

**Installation:**
```bash
pip install ksef2
# or
uv add ksef2
```

**Key Features:**
- Typed public API for all 73 endpoints (100% coverage)
- XAdES and KSeF token authentication
- Online and batch sessions
- Built-in encryption helpers
- Test environment tooling
- Session resume support
- Export package decryption

**Basic Usage Example:**
```python
from datetime import datetime, timedelta, timezone
from pathlib import Path

from ksef2 import Client, Environment, FormSchema
from ksef2.domain.models import InvoicesFilter

# Initialize client
NIP = "1234567890"
client = Client(Environment.TEST)

# Authenticate with test certificate
auth = client.authentication.with_test_certificate(nip=NIP)

# Send an invoice via online session
with auth.online_session(form_code=FormSchema.FA3) as session:
    result = session.send_invoice(
        invoice_xml=Path("invoice.xml").read_bytes()
    )
    print(result.reference_number)
    
    # Wait for processing
    status = session.wait_for_invoice_ready(
        invoice_reference_number=result.reference_number
    )
    print(status.ksef_number)

# Query and export invoices
filters = InvoicesFilter(
    role="seller",
    date_type="issue_date",
    date_from=datetime.now(tz=timezone.utc) - timedelta(days=7),
    date_to=datetime.now(tz=timezone.utc),
    amount_type="brutto",
)

# Schedule export
export = auth.invoices.schedule_export(filters=filters)

# Wait and download package
package = auth.invoices.wait_for_export_package(
    reference_number=export.reference_number
)
paths = auth.invoices.fetch_package(
    package=package,
    export=export,
    target_directory="downloads",
)
```

**XAdES Authentication Example:**
```python
from ksef2 import Client, Environment
from ksef2.core.xades import (
    load_certificate_from_pem,
    load_private_key_from_pem
)

# Load production certificate
cert = load_certificate_from_pem("cert.pem")
key = load_private_key_from_pem("key.pem")

# Authenticate
client = Client(Environment.PRODUCTION)
auth = client.authentication.with_xades(
    nip="1234567890",
    cert=cert,
    private_key=key,
)
```

**Token Authentication Example:**
```python
from ksef2 import Client

client = Client()
auth = client.authentication.with_token(
    ksef_token="your-read-only-token",
    nip="1234567890",
)

# Query metadata
metadata = auth.invoices.query_metadata(filters=filters)
```

### 5.3 Other Language SDKs

| Language | Repository | Status |
|----------|------------|--------|
| C# | [ksef-client-csharp](https://github.com/CIRFMF/ksef-client-csharp) | Official (MF) |
| Java | [ksef-client-java](https://github.com/CIRFMF/ksef-client-java) | Official (MF) |
| TypeScript | [ksef-client-typescript](https://github.com/smekcio/ksef-client-typescript) | Community |
| Rust | [ksef-client-rust](https://github.com/ireneuszwitek/ksef-client-rust) | Community |

---

## 6. Existing Integrations

### 6.1 Open Source Projects

| Project | Language | Purpose | Key Features |
|---------|----------|---------|--------------|
| **ksef2** | Python | Full SDK | 100% API coverage, all auth methods |
| **KSeF_Monitor** | Python | Invoice monitor | Polling, multi-channel notifications, PDF generation |
| **ksef-client-typescript** | TypeScript | SDK | Node.js SDK with workflows |
| **ksef-pdf-generator** | TypeScript | PDF generation | REST API + Docker for KSeF invoice PDFs |
| **ksef-client-rust** | Rust | SDK | Rust client library |

### 6.2 KSeF_Monitor Features (Reference)

- Cyclical invoice metadata polling from KSeF API v2.1/v2.2
- Multi-channel notifications: Pushover, Discord, Slack, Email, Webhook
- PDF generation from XML invoices
- Prometheus metrics export
- Docker deployment ready
- 5 scheduling modes: simple, minutes, hourly, daily, weekly

---

## 7. Recommended Approach

### 7.1 For Rozlicz Project

Based on research, here is the recommended integration approach:

#### Architecture
```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Rozlicz App   │────▶│  KSeF Sync Service │────▶│   KSeF API      │
│                 │     │  (Python/ksef2)   │     │   (Production)  │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌──────────────────┐
                        │  Local Database  │
                        │  (Invoices Cache)│
                        └──────────────────┘
```

#### Phase 1: Read-Only Invoice Retrieval (Recommended Start)

1. **Use KSeF Token Authentication**
   - Generate read-only token in KSeF portal
   - Lower complexity than XAdES certificates
   - Can be revoked if compromised
   - No certificate management required

2. **Implement Incremental Sync**
   ```python
   # Pseudocode for sync service
   def sync_invoices():
       last_sync = get_last_sync_timestamp()
       
       filters = InvoicesFilter(
           role="seller",  # and/or "buyer"
           date_type="Invoicing",
           date_from=last_sync,
           date_to=now(),
       )
       
       # Query metadata
       metadata = auth.invoices.query_metadata(filters)
       
       # For high volume: use export
       if len(metadata.invoices) > 50:
           export = auth.invoices.schedule_export(filters)
           package = auth.invoices.wait_for_export_package(export.ref)
           auth.invoices.fetch_package(package, export, "downloads")
       else:
           # Low volume: download individually
           for inv in metadata.invoices:
               xml = auth.invoices.download_invoice(inv.ksef_number)
               save_to_database(xml)
       
       update_last_sync_timestamp(now())
   ```

3. **Sync Schedule**
   - Minimum interval: 15 minutes per NIP (per KSeF guidelines)
   - Recommended: Every 15-30 minutes during business hours
   - Option for manual sync trigger by user

#### Phase 2: Invoice Sending (Future)

1. **Obtain XAdES Certificate**
   - Qualified electronic seal from certified provider
   - Required for sending invoices

2. **Use Online Sessions for Single Invoices**
   ```python
   with auth.online_session(form_code=FormSchema.FA3) as session:
       result = session.send_invoice(invoice_xml)
       status = session.wait_for_invoice_ready(result.reference_number)
       return status.ksef_number
   ```

3. **Use Batch Sessions for Bulk**
   ```python
   # For multiple invoices
   batch = auth.batch.prepare_batch(invoices)
   result = auth.batch.submit(batch)
   ```

### 7.2 Technology Stack Recommendation

| Component | Recommendation |
|-----------|---------------|
| **SDK** | `ksef2` (Python) - actively maintained, 100% coverage |
| **Auth (read)** | KSeF Token (read-only permissions) |
| **Auth (write)** | XAdES Certificate (when needed) |
| **Storage** | Local database (PostgreSQL recommended) |
| **Sync** | Celery/Redis or APScheduler for periodic tasks |
| **Monitoring** | Prometheus metrics (optional) |

### 7.3 Security Best Practices

1. **Never commit tokens or certificates**
   - Use environment variables or secrets manager
   - Add `.p12`, `.pem`, `.pfx` to `.gitignore`

2. **Use read-only tokens where possible**
   - Generate separate tokens for different contexts
   - Set expiration dates
   - Revoke unused tokens

3. **Implement proper retry logic**
   - Exponential backoff for 429 errors
   - Respect `Retry-After` header
   - Circuit breaker for repeated failures

4. **Log securely**
   - Never log tokens, certificates, or private keys
   - Mask NIP numbers in logs if needed

---

## 8. Blockers & Considerations

### 8.1 Known Blockers

| Issue | Impact | Mitigation |
|-------|--------|------------|
| **No direct ePUAP integration** | ePUAP is not directly supported for API auth | Use XAdES certificate or KSeF token instead |
| **Rate limits on production** | 20 req/hour for metadata queries | Implement local caching, use export for bulk |
| **Certificate requirements** | Qualified seal required for sending | Budget for certificate (~500-1000 PLN/year) |
| **Polish documentation** | Most docs are in Polish | Use SDKs with English documentation |
| **Test environment differences** | TEST has 10x higher limits | Always test with production-like limits on DEMO |

### 8.2 Important Considerations

1. **Date of Receipt**
   - Date of receipt = KSeF number assignment date
   - Not dependent on when invoice is downloaded
   - Important for VAT settlement timing

2. **Synchronization Strategy**
   - API is designed for **sync to local DB**, not direct UI queries
   - All business operations should use local data
   - KSeF is the "source of truth" for invoice existence

3. **Compliance**
   - Monitor KSeF API changelog for breaking changes
   - API version 2.2.0 is current as of March 2026
   - Test environment allows limit modification for testing

4. **Scaling**
   - For accounting agencies: each client's NIP is separate context
   - Rate limits apply per (context + IP), not per integrator
   - Consider IP rotation only if legitimate need (can trigger security alerts)

### 8.3 Next Steps

1. **Immediate:**
   - Register for TEST environment access
   - Install `ksef2` SDK and run quickstart example
   - Generate test NIP and test certificate

2. **Short-term:**
   - Implement read-only invoice retrieval with KSeF token
   - Set up local database schema for invoice storage
   - Build sync scheduler (15+ min intervals)

3. **Long-term:**
   - Obtain qualified seal certificate for invoice sending
   - Implement online session workflow
   - Consider batch mode for bulk operations

---

## Resources

### Official Documentation
- **KSeF Portal:** https://ksef.gov.pl
- **API Docs (Official):** https://github.com/CIRFMF/ksef-docs
- **OpenAPI Spec:** https://api-test.ksef.mf.gov.pl/docs/v2

### SDKs & Libraries
- **Python SDK (ksef2):** https://github.com/artpods56/ksef2
- **Python Monitor:** https://github.com/mlotocki2k/KSeF_Monitor
- **C# SDK (Official):** https://github.com/CIRFMF/ksef-client-csharp
- **Java SDK (Official):** https://github.com/CIRFMF/ksef-client-java

### Support
- **KSeF Contact Form:** https://ksef.podatki.gov.pl/formularz/
- **Technical Issues:** Contact KSeF support for limit increases

---

*Document generated: 2026-03-10  
Research by: SAVIOR Subagent for Rozlicz Project*
