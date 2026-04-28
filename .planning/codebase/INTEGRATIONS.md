# External Integrations

**Analysis Date:** 2026-04-28

## APIs & External Services

**Internal Backend API:**
- FastAPI - The primary interface for the frontend to communicate with the system.
  - SDK/Client: `axios` (Frontend)
  - Auth: Custom login logic in `backend/routers/auth.py`

## Data Storage

**Databases:**
- Microsoft SQL Server
  - Connection: Configured in `backend/db/connection.py` using `pymssql`.
  - Client: `pymssql`
  - Fallback: Multiple server IPs defined (`220.88.3.118:6433`, `192.168.0.5`, `192.168.1.5`) for redundancy.

**File Storage:**
- Local filesystem
  - Used for storing and reading MyBatis-style XML SQL maps in `backend/sql/`.

**Caching:**
- None detected.

## Authentication & Identity

**Auth Provider:**
- Custom
  - Implementation: Validates credentials against `TBL_COM_MEMBERS` in the SQL Server database. Updates `LOGINYN` and `LOGINDATE` on successful login.
  - Location: `backend/routers/auth.py`

## Monitoring & Observability

**Error Tracking:**
- None detected.

**Logs:**
- Standard output/console logging via FastAPI/Uvicorn.
- Debug prints observed in `backend/services/base_service.py`.

## CI/CD & Deployment

**Hosting:**
- Not explicitly defined in the codebase, but the structure suggests a containerized or standard server deployment for FastAPI and static hosting for Vue.

**CI Pipeline:**
- None detected (no `.github/workflows`, `.gitlab-ci.yml`, etc.).

## Environment Configuration

**Required env vars:**
- `DB_NAME`: Name of the SQL Server database (default: `PFMES`).
- `DB_UID`: Database user ID (default: `SA`).
- `DB_PWD`: Database password.
- `VITE_API_URL`: URL of the backend API for the frontend.

**Secrets location:**
- Environment variables and `.env` files (not committed).

## Webhooks & Callbacks

**Incoming:**
- None detected.

**Outgoing:**
- None detected.

---

*Integration audit: 2026-04-28*
