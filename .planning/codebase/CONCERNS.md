# Codebase Concerns

**Analysis Date:** 2025-01-24

## Tech Debt

**Database Connection Management:**
- Issue: Lack of connection pooling. Every query opens and closes a new physical connection to the MS SQL server, which is inefficient and can lead to connection exhaustion under load.
- Files: `backend/db/connection.py`, `backend/services/base_service.py`
- Impact: Performance degradation and reduced scalability.
- Fix approach: Implement a connection pool using `DBUtils` or a similar library, or switch to an ORM like SQLAlchemy that handles pooling automatically.

**Code Duplication (Query Execution):**
- Issue: Logic for executing queries, mapping columns to upper case, and handling character encoding hacks is duplicated across multiple files.
- Files: `backend/db/connection.py`, `backend/services/base_service.py`, `backend/services/production/lot_service.py`
- Impact: Increased maintenance burden and risk of inconsistent behavior.
- Fix approach: Consolidate all database execution and mapping logic into `backend/db/connection.py` or a dedicated repository layer.

**XML Mapper Limitations:**
- Issue: The home-grown `XMLMapper` only supports a very small subset of dynamic SQL (simple `if`, `where`, `set` tags) and lacks caching for parsed templates.
- Files: `backend/db/xml_mapper.py`
- Impact: Performance overhead for parsing XML on every request; inability to use complex conditional logic in SQL.
- Fix approach: Add caching for parsed XML trees and consider using a more robust MyBatis-like library for Python if requirements grow.

**Lack of Automated Tests:**
- Issue: No unit or integration tests were found in the codebase.
- Files: Entire repository.
- Impact: High risk of regressions during refactoring or feature additions; difficulty in ensuring system reliability.
- Fix approach: Introduce a testing framework like `pytest` and start adding tests for critical business logic (e.g., `LotService`, `BomService`).

## Known Bugs

**Character Encoding Mismatch:**
- Symptoms: Database returns "깨진" (broken) Korean characters, requiring a manual `latin-1` to `cp949` conversion in the application layer.
- Files: `backend/db/connection.py`, `backend/services/base_service.py`
- Trigger: Occurs whenever reading string values from the database.
- Workaround: Manual decoding logic `value.encode('latin-1').decode('cp949')`.
- Fix approach: Correct the database collation and connection charset settings to match the application's expected UTF-8 encoding.

## Security Considerations

**Credential Management:**
- Risk: Hardcoded database credentials (including a fallback password) and server IP addresses in the code.
- Files: `backend/db/connection.py`
- Current mitigation: Uses `os.getenv` with a default value.
- Recommendations: Remove hardcoded fallback values; use a `.env` file or a secret management service for all environment-specific configurations.

**Authentication and Session Management:**
- Risk: No JWT or session tokens are used. Passwords appear to be stored/compared in plaintext in the database.
- Files: `backend/routers/auth.py`, `frontend/src/views/Login.vue`
- Current mitigation: Simple equality check `WHERE EMPID = %s AND PASS = %s`.
- Recommendations: Implement password hashing (e.g., `bcrypt`); introduce JWT-based authentication for secure, stateless requests.

**Information Leakage:**
- Risk: Global exception handlers in the backend return raw error messages to the client.
- Files: `backend/main.py`
- Current mitigation: None.
- Recommendations: Log the full error on the server side, but return a sanitized, generic error message to the client in production.

**CORS Policy:**
- Risk: Permissive CORS configuration (`allow_origins=["*"]`).
- Files: `backend/main.py`
- Current mitigation: None.
- Recommendations: Restrict allowed origins to the specific domain(s) where the frontend is hosted.

## Performance Bottlenecks

**XML Parsing Overhead:**
- Problem: XML mapper files are read and parsed from disk on every service instantiation or query execution.
- Files: `backend/db/xml_mapper.py`, `backend/services/base_service.py`
- Cause: Lack of caching for the `XMLMapper` instances or the parsed XML trees.
- Improvement path: Implement a singleton pattern or a registry for `XMLMapper` instances to ensure each file is parsed only once.

## Fragile Areas

**Stateful Login Flag:**
- Files: `backend/routers/auth.py`
- Why fragile: Uses a `LOGINYN` column in the database to track user sessions. This is prone to "ghost sessions" if users don't log out properly (e.g., browser crash).
- Safe modification: Transition to a token-based (JWT) approach where session validity is determined by the token expiration.
- Test coverage: None.

## Missing Critical Features

**Audit Logging:**
- Problem: There is no systematic way to track who changed what data beyond some `EDITUSERID` and `EDITDTM` columns in specific tables.
- Blocks: Accountability and debugging of data issues.

---

*Concerns audit: 2025-01-24*
