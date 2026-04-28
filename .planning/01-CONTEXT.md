# CONTEXT: Phase 1 - Foundation & Observability

## 1. Decisions Locked

### [Logging & Tracing]
- **Format**: JSON (Structured) for compatibility with external aggregators.
- **Request Tracing**: Implement via Trace IDs in request/response headers.
- **Storage**: Local file rotation (10MB) + External aggregation (Sentry/ELK planned).
- **Tool**: Loguru (Backend).

### [Error Notification UI]
- **Style**: Non-blocking Toasts (auto-hide after 5s) for general errors.
- **Detail Level**: Detailed error messages (message + code) displayed to users.
- **Recovery**: Full-page fallback for critical frontend crashes.
- **Implementation**: Global error boundaries and interceptors in Vue.js.

### [DB Connection & Mapping]
- **Connection Pool**: SQLAlchemy engine with a pool size of 5-10.
- **Encoding**: Centralize CP949 decoding logic within the SQLAlchemy/Mapper layer (moving it out of individual service calls).
- **Security**: Use `defusedxml` for parsing all SQL XML mapper files.
- **Session Management**: Use FastAPI dependencies (Yield) for managing database sessions and transactions.

### [SDK & Type Safety]
- **Generation**: Automated via `@hey-api/openapi-ts`.
- **API Client**: Fetch (native).
- **Model Naming**: Preserve backend naming (e.g., `SCREAMING_SNAKE_CASE`) to ensure stability during the initial phase.
- **Auth**: Automated token handling (Bearer tokens) within the generated SDK client.

## 2. Technical Context
- **Current DB**: SQL Server (MSSQL).
- **Frontend Stack**: Vue 3 (Composition API) + TypeScript.
- **Backend Stack**: FastAPI + Pydantic v2.

## 3. Deferred Ideas
- **Log Aggregator Selection**: ELK vs Sentry (to be finalized during implementation).
- **Jinja2 SQL Templates**: Keep the existing XML regex pattern for now; explore Jinja2 in a later stabilization phase if needed.
- **CamelCase Mapping**: Revisit after core stabilization is complete.
