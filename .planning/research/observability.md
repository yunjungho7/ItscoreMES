# Research: Error Handling & Logging (Observability)

**Project:** NEWMES (FastAPI + Vue.js)
**Researched:** 2025-02-13
**Overall confidence:** HIGH

## Executive Summary

The current brownfield codebase lacks a formal logging strategy and relies on basic `alert()` and `print()` statements for error reporting. This creates "silent failures" where errors are swallowed or only visible to the end-user, making server-side debugging and compliance auditing nearly impossible. 

To transform NEWMES into a production-grade MES, we must implement structured logging, centralized exception handling, and a dedicated audit trail for critical manufacturing operations.

## Key Findings

- **Backend:** Zero use of the `logging` module; relies on `print`. Global exception handlers catch errors but do not log tracebacks.
- **Frontend:** No global Vue error handler. Uses blocking `alert()` for API errors, which provides a poor UX and no persistent record.
- **Auditability:** No database-level or application-level audit logs for tracking record changes (Who/When/What).
- **Silent Failures:** Connection failures in `db/connection.py` are partially swallowed during retry logic, hiding infrastructure instability.

---

## 1. Backend: Structured Observability (FastAPI)

### Recommended Stack
| Technology | Purpose | Why |
|------------|---------|-----|
| **Loguru** | Logging Library | Zero-config, thread-safe, and produces human-readable + JSON logs. |
| **Asgi-Correlation-Id** | Tracing | Generates a unique `request_id` for every request to link logs across layers. |
| **Sentry (Optional)** | Error Tracking | Industry standard for real-time error alerts and stack trace aggregation. |

### Implementation Strategy

1.  **Transition to Loguru:** Replace all `print` statements with `logger.info`, `logger.error`, etc.
2.  **JSON Logging in Production:** Configure Loguru to output JSON to `stdout` for ingestion by log collectors (ELK, CloudWatch).
3.  **Request ID Middleware:**
    - Generate a `X-Request-ID` for every incoming request.
    - Include this ID in every log line using Loguru's `contextualize`.
4.  **Database Layer Logging:** 
    - Modify `execute_query` to log the SQL query and parameters (sanitized) whenever an exception occurs.
5.  **Enhanced Global Exception Handlers:**
    ```python
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        request_id = request.headers.get("X-Request-ID")
        logger.exception(f"Unhandled Exception [ID: {request_id}]: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={"statusCode": 500, "message": "Internal Server Error", "requestId": request_id}
        )
    ```

---

## 2. Frontend: Resilience & Monitoring (Vue.js 3)

### Global Error Handlers
We must implement three types of global catch-alls in `main.ts`:

1.  **Vue Component Errors:** `app.config.errorHandler` for errors in templates and lifecycle hooks.
2.  **Unhandled Promise Rejections:** `window.addEventListener('unhandledrejection', ...)` for failed API calls not wrapped in try-catch.
3.  **Runtime Errors:** `window.onerror` for generic JS crashes.

### Centralized Logger Service
Create a `src/utils/logger.ts` that:
- Prints to console in DEV mode.
- Sends a POST request to `/api/system/logs` in PROD for critical errors (log shipping).
- Replaces `alert()` with a Toast notification system (e.g., `vue-toastification`).

### Axios Interceptor Upgrades
- **Correlation ID:** Inject `X-Request-ID` into every outgoing request.
- **Retry Logic:** Automatically retry idempotent requests (GET) on network failure.

---

## 3. MES Audit Trail (The "Who, What, When, Why")

For MES compliance (traceability), critical tables (Lot, Shipment, Production Plan) require auditing.

### Audit Log Schema
```sql
CREATE TABLE TBL_SYS_AUDIT_LOG (
    LOG_ID BIGINT IDENTITY(1,1) PRIMARY KEY,
    EVENT_TIME DATETIME DEFAULT GETDATE(),
    USER_ID VARCHAR(50),      -- Who performed the action
    ACTION_TYPE VARCHAR(10),  -- INSERT, UPDATE, DELETE
    TABLE_NAME VARCHAR(50),   -- Target table
    RECORD_ID VARCHAR(100),   -- PK of the record
    OLD_DATA NVARCHAR(MAX),   -- JSON representation of record before
    NEW_DATA NVARCHAR(MAX),   -- JSON representation after
    REASON_CODE VARCHAR(20),  -- Why (e.g., 'SCRAP', 'CORRECTION')
    IP_ADDRESS VARCHAR(45)
);
```

### Implementation Pattern (Service Layer)
Since the project uses MyBatis-style XML mappers instead of an ORM, automated auditing is difficult.
- **Recommendation:** Implement an `AuditService` and call it within `BaseCrudService.update` and `BaseCrudService.delete`.
- **Reason Codes:** Add a mandatory `reason` field to sensitive API endpoints (e.g., deleting a production lot).

---

## 4. Identifying & Fixing Silent Failures

| Current Silent Failure | Impact | Fix |
|-----------------------|--------|-----|
| `get_db_connection` retries | Hides DB instability / DNS issues. | Log every failed attempt at `WARNING` level with the target IP. |
| `XMLMapper.get_query` failure | Returns `None`, causing `AttributeError` later. | Raise a specific `QueryNotFoundError` immediately. |
| Encoding `try-except` | Could hide data corruption issues. | Log `DEBUG` message when fallback encoding is used. |
| Axios `alert()` only | Errors are lost once the user clicks OK. | Implement persistent client-side logs or ship to backend. |

---

## Implications for Roadmap

1.  **Phase 1 (Infrastructure):** Setup `Loguru` and Correlation ID middleware. Replace `print` with `logger`.
2.  **Phase 2 (Frontend):** Global error handlers and Toast notifications. Remove `alert()`.
3.  **Phase 3 (Audit Trail):** Create `TBL_SYS_AUDIT_LOG` and integrate with `BaseCrudService`.
4.  **Phase 4 (Refinement):** Add "Reason for Change" prompts to critical UI workflows.

## Sources

- [FastAPI Logging Best Practices (2025)](https://fastapi.tiangolo.com/advanced/settings/) - HIGH confidence
- [Vue 3 Error Handling Guide](https://vuejs.org/api/application.html#app-config-errorhandler) - HIGH confidence
- [FDA 21 CFR Part 11 Audit Trail Requirements](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/part-11-electronic-records-electronic-signatures-scope-and-application) - MEDIUM confidence (adapted for MyBatis)
