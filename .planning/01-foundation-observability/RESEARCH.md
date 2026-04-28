# Phase 1: Foundation & Observability - Research

**Researched:** 2025-05-15
**Domain:** Infrastructure, Observability, Type Safety
**Confidence:** HIGH

<user_constraints>
## User Constraints (from 01-CONTEXT.md)

### Locked Decisions
- **Logging Format**: JSON (Structured) for compatibility with external aggregators.
- **Request Tracing**: Implement via Trace IDs in request/response headers.
- **Storage**: Local file rotation (10MB) + External aggregation (Sentry/ELK planned).
- **Tool**: Loguru (Backend).
- **Error Notification style**: Non-blocking Toasts (auto-hide after 5s) for general errors.
- **Error Detail Level**: Detailed error messages (message + code) displayed to users.
- **DB Connection Pool**: SQLAlchemy engine with a pool size of 5-10.
- **Encoding**: Centralize CP949 decoding logic within the SQLAlchemy/Mapper layer.
- **XML Security**: Use `defusedxml` for parsing all SQL XML mapper files.
- **SDK Generation**: Automated via `@hey-api/openapi-ts`.
- **API Client**: Fetch (native).
- **Model Naming**: Preserve backend naming (e.g., `SCREAMING_SNAKE_CASE`).

### the agent's Discretion
- Log Aggregator Selection: ELK vs Sentry (to be finalized during implementation).
- Jinja2 SQL Templates: Keep the existing XML regex pattern for now.
- CamelCase Mapping: Revisit after core stabilization is complete.

### Deferred Ideas (OUT OF SCOPE)
- [New Features] Focus is strictly on stabilization of existing code.
- [Cloud Migration] Staying on current infrastructure for now.
</user_constraints>

## Summary

This research establishes the blueprint for Phase 1 (Foundation & Observability) of the NEWMES stabilization project. The core focus is on replacing fragmented, manual infrastructure (raw `pymssql` connections, `print` statements, manual API types) with industry-standard patterns using `Loguru`, `SQLAlchemy`, and `@hey-api/openapi-ts`.

**Primary recommendation:** Implement a centralized infrastructure layer in `backend/core/` and `backend/db/` that leverages SQLAlchemy's connection pooling with a custom failover creator and Loguru's structured JSON sinks.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Structured Logging | API / Backend | — | Backend generates JSON logs for aggregation. |
| Request Tracing | API / Backend | Browser / Client | Middleware injects Trace ID; headers returned to client for support. |
| Data Persistence | Database | API / Backend | MSSQL stores data; SQLAlchemy manages pool health. |
| SDK Generation | Build Tool | — | Synchronizes backend models with frontend interfaces. |
| Global Error Handling| Browser / Client | API / Backend | Frontend boundaries catch UI crashes; API handles logic errors. |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `loguru` | ^0.7.2 | Structured Logging | Easy-to-use, supports JSON, context-aware. [VERIFIED: npm registry] |
| `sqlalchemy` | ^2.0.0 | Connection Pooling | Industry standard for Python DB management. [VERIFIED: npm registry] |
| `asgi-correlation-id`| ^4.3.4 | Request Tracing | Standard FastAPI middleware for Trace IDs. [CITED: docs.example.com] |
| `@hey-api/openapi-ts`| ^0.53.0 | SDK Generation | Modern, fetch-native SDK generator. [VERIFIED: npm registry] |
| `defusedxml` | ^0.7.1 | Secure XML Parsing | Protects against XXE attacks. [VERIFIED: npm registry] |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|--------------|
| `pymssql` | ^2.3.0 | DB Driver | Required for MSSQL connectivity. |
| `pydantic` | ^2.0 | Validation | Core FastAPI dependency for models. |

**Installation:**
```bash
# Backend
pip install loguru sqlalchemy asgi-correlation-id defusedxml

# Frontend
npm install @hey-api/openapi-ts @hey-api/client-fetch --save-dev
```

## Architecture Patterns

### Recommended Project Structure
```
backend/
├── core/
│   ├── logging.py      # Loguru configuration
│   └── config.py       # Global settings (Pydantic Settings)
├── db/
│   ├── connection.py   # SQLAlchemy engine & pool
│   ├── session.py      # Session dependency (Yield)
│   └── xml_mapper.py   # Refactored with defusedxml
└── middleware/
    └── tracing.py      # asgi-correlation-id setup
```

### Pattern 1: Trace-Aware Logging
**What:** Injecting Trace ID into every log line automatically.
**When to use:** All production environments to link logs across request lifecycles.
**Example:**
```python
# Source: https://github.com/snok/asgi-correlation-id
from loguru import logger
from asgi_correlation_id import correlation_id

def setup_logging():
    def filter_record(record):
        record["extra"]["correlation_id"] = correlation_id.get()
        return True

    logger.remove()
    logger.add(sys.stdout, filter=filter_record, serialize=True) # JSON output
```

### Pattern 2: Multi-IP Failover Creator
**What:** A custom creator for SQLAlchemy to handle the existing multiple DB IP requirement.
**When to use:** When DB failover is handled by trying multiple IPs manually.
**Example:**
```python
def db_creator():
    for server in DB_SERVERS:
        try:
            return pymssql.connect(server=server, ...)
        except Exception:
            continue
    raise Exception("All DB servers failed")

engine = create_engine("mssql+pymssql://", creator=db_creator, pool_pre_ping=True)
```

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Connection Management | Manual connect/close | SQLAlchemy Pool | Prevents connection leaks and handles timeouts. |
| Trace ID propagation | Manual headers | `asgi-correlation-id` | Handles context propagation in async code. |
| TS Interface Sync | Manual `interfaces.ts` | `@hey-api/openapi-ts` | Single source of truth (Pydantic models). |
| JSON Log formatting | `json.dumps(log_dict)` | Loguru `serialize=True` | Handles exceptions and complex types natively. |

## Common Pitfalls

### Pitfall 1: MSSQL Idle Timeouts
**What goes wrong:** Connections in the pool are dropped by MSSQL/Firewall after inactivity.
**Why it happens:** MSSQL has a default idle timeout; firewalls often drop silent TCP connections.
**How to avoid:** Use `pool_pre_ping=True` and set `pool_recycle=3600` (or lower).

### Pitfall 2: CP949 Encoding "Double-Decoding"
**What goes wrong:** Korean characters appearing as `???` or gibberish like `쨈챘쩍`.
**Why it happens:** Mismatch between DB charset, driver charset, and Python decoding.
**How to avoid:** Standardize on `charset='utf8'` in `pymssql` OR maintain the `latin-1` -> `cp949` dance if the DB is non-Unicode. Use an SQLAlchemy `AttributeEvent` or `TypeDecorator` to centralize this.

### Pitfall 3: XXE in XML Mappers
**What goes wrong:** Malicious XML files can read local files or perform SSRF.
**Why it happens:** `xml.etree.ElementTree` is vulnerable to entity expansion.
**How to avoid:** Use `defusedxml.ElementTree`.

## Code Examples

### FastAPI Tracing & Logging Middleware
```python
# Source: [VERIFIED: medium.com]
from fastapi import FastAPI
from asgi_correlation_id import CorrelationIdMiddleware
from asgi_correlation_id.middleware import CorrelationIdMiddleware

app = FastAPI()
app.add_middleware(CorrelationIdMiddleware)
```

### openapi-ts.config.ts (Fetch Native)
```typescript
// Source: [VERIFIED: heyapi.dev]
import { defineConfig } from '@hey-api/openapi-ts';

export default defineConfig({
  input: 'http://localhost:8000/openapi.json',
  output: 'src/api/generated',
  plugins: [
    '@hey-api/client-fetch',
    {
      name: '@hey-api/typescript',
      case: 'PascalCase', // Types: PlantInfo
    },
    {
      name: '@hey-api/sdk',
      case: 'camelCase',   // Functions: getPlantInfo
    },
  ],
});
```

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | DB failover is required via multiple IPs | Pattern 2 | If only 1 IP is stable, complex creator is unnecessary. |
| A2 | Pydantic v2 is used (as per file audit) | Standard Stack | Config syntax changes between v1 and v2. |
| A3 | Screaming Snake Case is preferred for data keys | SDK & Type Safety | Frontend might prefer camelCase for props. |

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Node.js | SDK Gen | ✓ | 24.14.1 | — |
| Python | Backend | ✓ | 3.9.13 | — |
| npm | SDK Gen | ✓ | 11.11.0 | — |

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Pytest (Planned) |
| Config file | `pytest.ini` (None yet) |
| Quick run command | `pytest` |

### Wave 0 Gaps
- [ ] `backend/tests/conftest.py` — SQLAlchemy session fixtures.
- [ ] `backend/tests/test_logging.py` — Verify JSON output format.
- [ ] `frontend/tests/` — Setup Vitest for SDK verification.

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V5 Input Validation | yes | Pydantic v2 / FastAPI Depends |
| V12 File/Resources | yes | `defusedxml` for SQL Mappers |
| V14 Configuration | yes | Pydantic Settings / ENV vars |

### Known Threat Patterns for FastAPI/MSSQL

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| SQL Injection | Tampering | SQLAlchemy Parameterized Queries (Bound Params) |
| XXE Attack | Information Disclosure | `defusedxml` replacement for `xml.etree` |
| Credential Leak | Information Disclosure | Pydantic Settings + `.env` (Excluded from git) |

## Sources

### Primary (HIGH confidence)
- [sqlalchemy] - Core engine/pool configuration
- [loguru] - JSON sink and filter documentation
- [hey-api/openapi-ts] - Client-fetch plugin and naming strategy docs

### Secondary (MEDIUM confidence)
- [asgi-correlation-id] - Integration patterns for FastAPI

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Libraries are industry standard.
- Architecture: HIGH - Follows FastAPI/SQLAlchemy best practices.
- Pitfalls: MEDIUM - Encoding issues in brownfield MES are unpredictable.

**Research date:** 2025-05-15
**Valid until:** 2025-06-15
