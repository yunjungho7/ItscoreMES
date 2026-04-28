# ROADMAP

## Project: NEWMES Stabilization

## Phase 1: Foundation & Observability (Current)
*Goal: Establish robust infrastructure and visibility before touching business logic.*

- [ ] [P1-1] Implement structured logging (Loguru) and Request Tracing middleware.
- [ ] [P1-2] Implement global error boundaries and notification system in Vue.js.
- [ ] [P1-3] Implement SQLAlchemy connection pooling and secure XML parsing (`defusedxml`).
- [ ] [P1-4] Set up `@hey-api/openapi-ts` for type-safe SDK generation.

## Phase 2: Core Module Stabilization (Master & Logistics)
*Goal: Ensure data integrity and transactional safety for master data and logistics.*

- [ ] [P2-1] Apply Pydantic validation and referential integrity to Master Data services.
- [ ] [P2-2] Implement transactional inventory updates and "Check then Act" patterns in Logistics.
- [ ] [P2-3] Align Master and Logistics frontend views with the new type-safe SDK.
- [ ] [P2-4] Implement centralized audit logging for all Master/Logistics modifications.

## Phase 3: Production & Compliance
*Goal: Stabilize critical production workflows and enforce process controls.*

- [ ] [P3-1] Implement state machine logic for Workorders and Lots.
- [ ] [P3-2] Apply Pydantic validation and audit trails to Production services.
- [ ] [P3-3] Stabilize Production frontend views (Workorder/Lot tracking).
- [ ] [P3-4] Implement anomaly detection (e.g., negative stock alerts) and data integrity reports.

## Phase 4: Validation & Quality
*Goal: Final verification and project closure.*

- [ ] [P4-1] Establish baseline unit and integration tests for all stabilized modules.
- [ ] [P4-2] Final audit of data integrity (ALCOA+ compliance).
- [ ] [P4-3] Update documentation and handover.
