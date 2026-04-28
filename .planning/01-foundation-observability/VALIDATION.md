# Phase 1 Validation Plan: Foundation & Observability

This document defines the goal-backward verification criteria for Phase 1. Achievement of these "truths" confirms the infrastructure is stable and observable.

## 1. Goal
Establish a robust, observable, and secure foundation for NEWMES by implementing structured logging, request tracing, database connection pooling, and type-safe frontend-backend synchronization.

## 2. Observable Truths (User/Dev Perspective)

| Truth ID | Truth | Verification Method |
|----------|-------|---------------------|
| TR-01-01 | Every API response contains a unique `X-Correlation-ID`. | `curl -v http://localhost:8000/health` check headers. |
| TR-01-02 | Logs are emitted in JSON format and include the current `correlation_id`. | `tail -f logs/backend.log` during API calls. |
| TR-01-03 | Backend automatically recovers from a single DB IP failure. | Temporarily block primary DB IP; verify app still serves requests. |
| TR-01-04 | Malicious XML (XXE) is rejected during parsing. | Attempt to parse XML with `<!ENTITY ...>`; expect `defusedxml` error. |
| TR-01-05 | Korean characters (CP949) from DB are correctly rendered in UI. | Verify specific records with Korean names via frontend UI. |
| TR-01-06 | Frontend displays a toast notification for 4xx/5xx API errors. | Trigger a 404/500; verify toast appears and auto-hides after 5s. |
| TR-01-07 | Frontend types are in sync with backend Pydantic models. | Run `npm run type-check`; verify zero errors in `src/api/`. |

## 3. Required Artifacts & Wiring

### Backend Artifacts
- **File**: `backend/core/logging.py`
  - **Truths**: TR-01-02
  - **Wiring**: Registered in `main.py` startup; uses `asgi-correlation-id`.
- **File**: `backend/db/connection.py`
  - **Truths**: TR-01-03, TR-01-05
  - **Wiring**: SQLAlchemy engine with custom `creator` for multi-IP; `TypeDecorator` for CP949.
- **File**: `backend/db/xml_mapper.py`
  - **Truths**: TR-01-04
  - **Wiring**: Replaces `xml.etree` imports with `defusedxml.ElementTree`.

### Frontend Artifacts
- **File**: `frontend/src/api/generated/`
  - **Truths**: TR-01-07
  - **Wiring**: Produced by `@hey-api/openapi-ts` from static `openapi.json`.
- **File**: `frontend/src/composables/useNotification.ts`
  - **Truths**: TR-01-06
  - **Wiring**: Reactive toast state; injected into `App.vue`.
- **File**: `frontend/src/api/client.ts`
  - **Truths**: TR-01-06
  - **Wiring**: Intercepts fetch responses; pushes errors to `useNotification`.

## 4. Key Links (Critical Paths)

1.  **Traceability Loop**: `CorrelationIdMiddleware` -> `correlation_id.get()` -> `loguru` extra -> JSON log entry.
2.  **SDK Sync**: `extract_openapi.py` -> `openapi.json` -> `npx openapi-ts` -> `src/api/generated/`.
3.  **Data Integrity**: MSSQL (CP949) -> `pymssql` -> SQLAlchemy `CP949String(TypeDecorator)` -> Pydantic Model (UTF-8) -> JSON Response.

## 5. Reachability Check
- [x] **Logging**: `main.py` -> `setup_logging()` -> `loguru` sinks.
- [x] **DB Failover**: `get_db_session` -> `engine` -> `db_creator` loop.
- [x] **UI Notifications**: `fetch` interceptor -> `useNotification` -> `NotificationToast.vue`.
- [x] **Type Sync**: `generate-api` script -> `openapi.json` -> `@hey-api/openapi-ts`.
