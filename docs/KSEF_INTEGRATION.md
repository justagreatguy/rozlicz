# KSeF Integration — Technical Specification

**Document:** KSeF API Integration for Rozlicz  
**API Version:** KSeF 2.0  
**Date:** 2026-03-10  
**Status:** Ready for development

---

## Overview

Rozlicz integrates with KSeF (Krajowy System e-Faktur) to automatically retrieve invoices for JDG clients. We only **READ** from KSeF — invoice issuance happens through client's existing tools (Apilo, etc.).

## Environments

| Environment | URL | Purpose |
|-------------|-----|---------|
| **Production** | `https://ksef.podatki.gov.pl` | Live data |
| **Integration (Test)** | `https://ksef-test.podatki.gov.pl` | Development & testing |
| **Demo** | `https://ksef-demo.podatki.gov.pl` | Pre-production testing |

## Authentication

### Method 1: ePUAP / Profil Zaufany (Recommended)

**Flow:**
1. Client clicks "Connect KSeF" in Rozlicz
2. Redirect to ePUAP/Profil Zaufany login
3. User authorizes access to their KSeF
4. Callback with authorization token
5. Exchange token for session token
6. Store encrypted session credentials

**Pros:**
- No certificate management
- Familiar flow for users
- Secure (government-level auth)

**Cons:**
- Token expires (requires refresh flow)
- Requires ePUAP/Profil Zaufany

### Method 2: Client Certificate

**Flow:**
1. Client generates/exports KSeF certificate
2. Uploads to Rozlicz (encrypted storage)
3. We use certificate for API calls

**Pros:**
- No token expiration
- Works without ePUAP

**Cons:**
- Certificate management burden
- Security risk if leaked

## API Endpoints (Key)

### 1. Initiate Session
```http
POST /api/online/Session/InitToken
Content-Type: application/json

{
  "context": {
    "identifier": "NIP",
    "identifierValue": "5223226169"
  }
}
```

**Response:**
```json
{
  "sessionToken": {
    "token": "...",
    "referenceNumber": "..."
  }
}
```

### 2. Query Invoices
```http
POST /api/online/Query/Invoice/Sync
Authorization: Bearer {sessionToken}
Content-Type: application/json

{
  "queryCriteria": {
    "subjectType": "subject1",
    "type": "incremental",
    "incremental": {
      "dateFrom": "2026-03-01",
      "dateTo": "2026-03-10"
    }
  }
}
```

### 3. Get Invoice Details
```http
GET /api/online/Invoice/Get/{ksefReferenceNumber}
Authorization: Bearer {sessionToken}
```

**Response:** FA_VAT XML document

## Invoice Processing Flow

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────────┐
│  Celery Worker  │────▶│  KSeF API    │────▶│  XML Response   │
│  (every 15 min) │     │  Query       │     │  (FA_VAT)       │
└─────────────────┘     └──────────────┘     └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐     ┌──────────────┐     ┌─────────────────┐
│  Tax Engine     │◀────│  Document    │◀────│  Parser         │
│  (recalculate)  │     │  (save to DB)│     │  (extract data) │
└─────────────────┘     └──────────────┘     └─────────────────┘
```

## XML Schema (FA_VAT)

Key fields to extract:

| Field | Path | Description |
|-------|------|-------------|
| **Invoice Number** | `//FaWiersz/NrFaWiersz` | Unique invoice number |
| **Issue Date** | `//FaWiersz/DataWytworzeniaFa` | When issued |
| **Seller NIP** | `//Podmiot1/IdentyfikatorPodmiotu/NIP` | Seller's tax ID |
| **Buyer NIP** | `//Podmiot2/IdentyfikatorPodmiotu/NIP` | Buyer's tax ID |
| **Total Net** | `//FaWiersz/P_15` | Net amount |
| **Total VAT** | `//FaWiersz/P_18` | VAT amount |
| **Total Gross** | `//FaWiersz/P_19` | Gross amount |
| **Currency** | `//FaWiersz/KodWaluty` | PLN or other |

## Error Handling

| Error Code | Meaning | Action |
|------------|---------|--------|
| `401` | Unauthorized | Refresh token / re-auth |
| `404` | Invoice not found | Log and skip |
| `429` | Rate limited | Exponential backoff |
| `500` | KSeF error | Retry with backoff, alert if persistent |

## Security Considerations

1. **Encryption at rest:** Session tokens encrypted with AES-256
2. **Encryption in transit:** TLS 1.3 for all API calls
3. **Access logging:** All KSeF operations logged
4. **Token rotation:** Session tokens refreshed every 24h
5. **Data retention:** KSeF data retained for 5 years (tax requirement)

## Testing

### Test Credentials
- **NIP:** 5223226169
- **Environment:** Integration (ksef-test.podatki.gov.pl)
- **Auth:** ePUAP / Profil Zaufany

### Test Scenarios
1. Initial connection flow
2. Invoice retrieval (sales)
3. Invoice retrieval (purchases)
4. Large batch processing (100+ invoices)
5. Error handling (expired token)
6. Rate limiting behavior

## Implementation Tasks

- [ ] KSeF client library (Python)
- [ ] Authentication flow (ePUAP)
- [ ] Invoice query worker (Celery)
- [ ] XML parser (FA_VAT schema)
- [ ] Document storage service
- [ ] Error handling & retry logic
- [ ] Monitoring & alerting

---

*Reference: https://ksef.podatki.gov.pl/ksef-na-okres-obligatoryjny/wsparcie-dla-integratorow/*
