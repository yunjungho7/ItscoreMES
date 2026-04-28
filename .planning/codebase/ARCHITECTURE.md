# Architecture

**Analysis Date:** 2025-02-13

## System Overview

```text
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Vue 3)                       │
│             `frontend/src/views`, `frontend/src/api`        │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼ HTTP (JSON)
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                        │
│         `backend/routers`, `backend/services`               │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼ SQL (pymssql)
┌─────────────────────────────────────────────────────────────┐
│                    Database (SQL Server)                    │
│         `backend/sql/*.xml` (SQL Templates)                  │
└─────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| API Routers | Entry points for HTTP requests, parameter extraction, and calling services. | `backend/routers/` |
| Business Services | Core logic, transaction management, and interacting with the XML mapper. | `backend/services/` |
| XML Mapper | Dynamic SQL generation from MyBatis-style XML templates. | `backend/db/xml_mapper.py` |
| Data Models | Request/Response validation and data structure definitions (Pydantic). | `backend/models/` |
| Database Layer | Connection pooling and raw query execution. | `backend/db/connection.py` |
| API Client | Axios instance for making requests to the backend. | `frontend/src/api/index.ts` |
| UI Views | Page-level components organized by manufacturing domains. | `frontend/src/views/` |

## Pattern Overview

**Overall:** Layered Architecture with Externalized SQL Mapping.

**Key Characteristics:**
- **Decoupled SQL:** SQL queries are stored in XML files (`backend/sql/`), allowing DBAs or developers to tune queries without changing Python code.
- **Service Layer:** Business logic is encapsulated in services that extend `BaseCrudService` for standard CRUD operations.
- **Domain-Driven Organization:** Both frontend and backend are organized by domain (Master, Logistics, Production, etc.).

## Layers

**API Layer (Routers):**
- Purpose: Handles HTTP routing and input validation.
- Location: `backend/routers/`
- Contains: FastAPI router definitions.
- Depends on: Services, Models.
- Used by: External clients (Frontend).

**Service Layer:**
- Purpose: Implements business logic and orchestrates database operations.
- Location: `backend/services/`
- Contains: Service classes inheriting from `BaseCrudService`.
- Depends on: XML Mapper, Database connection.
- Used by: Routers.

**Data Access Layer (XML Mapper):**
- Purpose: Map XML-defined SQL to executable queries with parameter binding.
- Location: `backend/db/xml_mapper.py`
- Contains: `XMLMapper` class.
- Depends on: XML files in `backend/sql/`.
- Used by: Services.

## Data Flow

### Primary Request Path (Backend)

1. **HTTP Request** arrives at a FastAPI route (`backend/routers/master/bom.py:16`).
2. **Router** validates input using Pydantic models and calls the **Service** (`backend/services/master/bom.py:4`).
3. **Service** requests a query from the **XML Mapper** using a query ID (`backend/services/base_service.py:53`).
4. **XML Mapper** parses the corresponding XML (`backend/sql/master/bom.xml`), evaluates conditional tags (`<if>`, `<where>`), and returns formatted SQL.
5. **Service** executes the SQL via **pymssql** and processes the results (`backend/services/base_service.py:61`).
6. **Router** returns the JSON response.

**State Management:**
- **Backend:** Stateless.
- **Frontend:** Primarily handled via local component state or Vue Router params.

## Key Abstractions

**BaseCrudService:**
- Purpose: Provides standard CRUD implementations (get_all, get_one, create, update, delete) using XML queries.
- Examples: `backend/services/base_service.py`
- Pattern: Template Method.

**XMLMapper:**
- Purpose: Mimics MyBatis behavior in Python for dynamic SQL.
- Examples: `backend/db/xml_mapper.py`
- Pattern: Data Mapper / Template Engine.

## Entry Points

**FastAPI App:**
- Location: `backend/main.py`
- Triggers: Uvicorn/FastAPI server start.
- Responsibilities: Middleware configuration, Router registration, Error handling.

**Vue App:**
- Location: `frontend/src/main.ts`
- Triggers: Browser load.
- Responsibilities: App mounting, Router injection.

## Architectural Constraints

- **SQL Server Dependency:** The system is heavily optimized for MS SQL Server (using `pymssql`).
- **XML-Based SQL:** All database logic must be defined in XML files; inline SQL in services is discouraged.
- **Synchronous DB Calls:** Database operations are synchronous, which may limit concurrency under heavy load despite FastAPI's async capabilities.

## Anti-Patterns

### Inline SQL in Services

**What happens:** Writing SQL strings directly inside service methods.
**Why it's wrong:** Breaks the separation of concerns provided by the XML Mapper.
**Do this instead:** Define the query in the corresponding XML file in `backend/sql/`.

## Error Handling

**Strategy:** Global exception handling in FastAPI.

**Patterns:**
- **HttpException:** Used for controlled API errors (`backend/routers/master/bom.py:10`).
- **Global Handler:** Catches unexpected errors and returns a 500 JSON response (`backend/main.py:41`).

---

*Architecture analysis: 2025-02-13*
