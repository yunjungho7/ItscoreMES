# REQUIREMENTS

## Project: NEWMES Stabilization

## 1. Functional Requirements

### [STAB-F-01] Robust MES Workflows
- **Validation**: Implement strict input validation for all Logistics and Production services using Pydantic models.
- **Referential Integrity**: All operations must verify the existence of referenced Master Data (BOM, Goods, Factory, etc.) before execution.
- **State Enforcement**: Implement state machine logic for Workorders and Lots (e.g., status transitions: Created -> Started -> Completed -> Cancelled).
- **Transactional Inventory**: Inventory updates (Purchase, Shipment, Adjustment) must be transactional to prevent "negative inventory" and data corruption.

### [STAB-F-02] Comprehensive Audit Trails
- **Audit Logging**: Implement a centralized audit log table (`TBL_SYS_AUDIT_LOG`) to track all data-modifying operations (CREATE, UPDATE, DELETE).
- **Operation History**: Ensure `LotService` and Logistics modules consistently record operational history with user ID, timestamp, and "reason codes."

### [STAB-F-03] Observability & UX
- **Structured Logging**: Replace `print()` statements with structured JSON logging using `Loguru` in the backend.
- **Global Error Handling**: Implement global error boundaries and interceptors in Vue.js to replace blocking `window.alert()` with trackable notifications.
- **Request Tracing**: Add Correlation ID middleware to FastAPI to trace requests through logs.

## 2. Technical Requirements

### [STAB-T-01] Backend Infrastructure
- **Connection Pooling**: Replace raw `pymssql` connection management with an SQLAlchemy-backed connection pool.
- **Secure XML Parsing**: Switch to `defusedxml` for parsing SQL XML mapper files to mitigate XXE risks.
- **Jinja2 SQL Templates**: (Optional/Recommended) Explore migrating from regex-based XML mapping to Jinja2 for more robust dynamic SQL.
- **Encoding Correction**: Centralize Korean character encoding (CP949) handling within the database driver or mapper layer.

### [STAB-T-02] Type-Safe Alignment
- **SDK Generation**: Implement `@hey-api/openapi-ts` to generate a TypeScript SDK from FastAPI's OpenAPI spec.
- **Model Synchronization**: Align frontend TypeScript interfaces with backend Pydantic models.
- **Legacy Naming Strategy**: Maintain `SCREAMING_SNAKE_CASE` naming convention during initial stabilization to avoid breaking changes.

## 3. Compliance & Quality

### [STAB-Q-01] Data Integrity (ALCOA+)
- Ensure data is Attributable, Legible, Contemporaneous, Original, and Accurate.
- Implement "Check then Act" patterns for all high-stakes manufacturing operations.

### [STAB-Q-02] Automated Testing
- Establish a baseline of unit tests for core services (Lot, Inventory, Workorder).
- Implement basic integration tests for the API layer.
