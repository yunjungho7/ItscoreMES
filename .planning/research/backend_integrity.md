# Research: Backend Integrity (FastAPI + XML SQL Mapper)

This document focuses on pitfalls and stabilization patterns for the current XML-based SQL architecture.

## 1. Technical Audit of Current Architecture

The current implementation in `backend/db/xml_mapper.py` and `backend/services/base_service.py` has several points of failure:

### A. Connection Management
*   **Current:** Opens a new connection for every query via `get_db_connection()` and closes it immediately.
*   **Risk:** Extremely high overhead and potential connection exhaustion in production.
*   **Stabilization Pattern:** Use **SQLAlchemy Engine + QueuePool**.
    *   Set `pool_size=10`, `max_overflow=20`.
    *   Use `pool_pre_ping=True` to handle transient network issues common in industrial environments.

### B. Data Integrity & Encoding
*   **Current:** Ad-hoc `encode('latin-1').decode('cp949')` in each service's `_execute_select`.
*   **Risk:** Inconsistent handling across services; broken data if the DB collation changes or if `pymssql` version updates.
*   **Stabilization Pattern:** Centralize encoding in the `execute_query` wrapper or configure `pymssql` connection `charset`.
    *   Use `charset='cp949'` at connection time if the DB supports it.
    *   Otherwise, implement a standardized "Result Mapper" that handles all string conversions in one place.

### C. Dynamic SQL Fragility
*   **Current:** Custom `re.match` logic for `<if test="...">`.
*   **Risk:** Cannot handle complex logic (AND/OR, nested conditions).
*   **Stabilization Pattern:** Move to **Jinja2 Templates**.
    *   Jinja2 allows for complex logic: `{% if param1 and not param2 %}`.
    *   It is faster and safer than hand-rolled regex.

## 2. Identified Pitfalls

| Pitfall | Impact | Prevention |
|---------|--------|------------|
| **Connection Leak** | Server Crash | Use FastAPI `Depends(get_db)` to ensure connections are always closed. |
| **SQL Injection** | Data Breach | Ensure `${}` (raw) vs `#{}` (parameterized) distinction is strictly enforced. |
| **Transaction Split** | Dirty Reads | Run `SELECT COUNT` and `SELECT ITEMS` within the same transaction/session. |
| **XXE Attack** | Local File Leak | Use `defusedxml` for all XML parsing. |

## 3. Recommended Improvements

### Phase 1: Infrastructure
1. **Initialize SQLAlchemy Engine**: Replace `pymssql.connect` with `create_engine("mssql+pymssql://...")`.
2. **Dependency Injection**: Implement a `get_db` dependency for FastAPI routers.
3. **Transaction Helper**: Create a `@transactional` decorator or context manager.

### Phase 2: Mapper Hardening
1. **Standardize Result Mapping**: Ensure all column names are consistently mapped (e.g., lowercase vs uppercase).
2. **Template Integration**: Integrate Jinja2 into `XMLMapper` to replace `re.match`.
3. **Pydantic Repositories**: Create Repository classes that wrap the Mapper and return typed Pydantic objects.

## 4. Source Hierarchy & Confidence

*   **SQLAlchemy Docs**: HIGH Confidence (Official).
*   **pymssql Issues**: MEDIUM Confidence (Community reports).
*   **MyBatis Patterns**: HIGH Confidence (Established patterns in Java).

---
*Created as part of the GSD Research Phase for Backend Integrity.*
