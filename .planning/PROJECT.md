# NEWMES

## What This Is

A Manufacturing Execution System (MES) designed to manage factory operations, including master data (BOM, code, company, factory, goods, line, plant, etc.), logistics (inventory, order, purchase, receive, shipment), and production (daily report, fail lot, lot, workorder).

## Core Value

Provide a reliable and stable platform for tracking and managing manufacturing processes and inventory.

## Requirements

### Validated

<!-- Shipped and confirmed valuable. -->

(None yet ??ship to validate)

### Active

<!-- Current scope. Building toward these. -->

- [ ] [STAB-1] Stabilize existing backend services and SQL mappers.
- [ ] [STAB-2] Ensure consistency between frontend views and backend models.
- [ ] [STAB-3] Improve error handling and logging across the system.
- [ ] [STAB-4] Validate and document core workflows (Logistics, Production, Master Data).

### Out of Scope

<!-- Explicit boundaries. Includes reasoning to prevent re-adding. -->

- [New Features] ??Focus is strictly on stabilization of existing code.
- [Cloud Migration] ??Staying on current infrastructure for now.

## Context

- **Backend**: Python (FastAPI), SQL (XML Mappers).
- **Frontend**: Vue.js (TypeScript), Vite.
- **Current State**: Brownfield codebase with multiple modules (Master, Logistics, Production, System, Status, Inspection).
- **Goal**: Resolve potential bugs, ensure data integrity, and improve code quality.

## Constraints

- **Tech Stack**: Must maintain current stack (FastAPI/Vue).
- **Stability**: No breaking changes to existing database schema unless absolutely necessary.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Focus on Stabilization | Ensure a solid foundation before adding more features. | ??Pending |
| Parallel Execution | Faster completion of independent stabilization tasks. | ??Pending |
| Granular Research | Identify patterns and surface hidden issues in existing code. | ??Pending |
