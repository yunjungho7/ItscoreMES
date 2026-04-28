# Codebase Structure

**Analysis Date:** 2025-02-13

## Directory Layout

```
[project-root]/
├── backend/            # Python FastAPI backend
│   ├── db/             # Database connection and XML mapping logic
│   ├── models/         # Pydantic data models (organized by domain)
│   ├── routers/        # API route definitions (organized by domain)
│   ├── services/       # Business logic layer (organized by domain)
│   ├── sql/            # MyBatis-style SQL XML templates
│   └── main.py         # Application entry point
├── frontend/           # Vue 3 frontend
│   ├── public/         # Static assets
│   ├── src/            # Application source
│   │   ├── api/        # Axios client and API definitions
│   │   ├── components/ # Reusable Vue components
│   │   ├── router/     # Vue Router configuration
│   │   └── views/      # Page components (organized by domain)
│   └── package.json    # Frontend dependencies
└── .planning/          # GSD planning and codebase maps
```

## Directory Purposes

**backend/db/:**
- Purpose: Core database infrastructure.
- Contains: Connection management and the custom XML Mapper engine.
- Key files: `backend/db/connection.py`, `backend/db/xml_mapper.py`.

**backend/models/:**
- Purpose: Request and response data structures.
- Contains: Pydantic models for validation and serialization, mirroring DB tables and API payloads.
- Key files: `backend/models/master/bom.py`, `backend/models/system/user.py`.

**backend/routers/:**
- Purpose: HTTP endpoint definitions.
- Contains: FastAPI APIRouter instances that map URLs to service methods.
- Key files: `backend/routers/auth.py`, `backend/routers/production/__init__.py`.

**backend/services/:**
- Purpose: Business logic implementation.
- Contains: Logic for processing data before/after DB operations and transaction control.
- Key files: `backend/services/base_service.py`, `backend/services/master/bom.py`.

**backend/sql/:**
- Purpose: Externalized SQL storage.
- Contains: XML files containing parameterized SQL queries with dynamic tags.
- Key files: `backend/sql/master/goods.xml`, `backend/sql/logistics/order.xml`.

**frontend/src/views/:**
- Purpose: Main application pages.
- Contains: Vue components representing different screens of the MES.
- Key files: `frontend/src/views/management/master/BomView.vue`.

## Key File Locations

**Entry Points:**
- `backend/main.py`: Main FastAPI application file.
- `frontend/src/main.ts`: Main Vue application entry point.

**Configuration:**
- `frontend/vite.config.ts`: Vite build configuration.
- `backend/requirements.txt`: Python dependencies.

**Core Logic:**
- `backend/db/xml_mapper.py`: Custom logic for parsing XML SQL templates.
- `backend/services/base_service.py`: Base class for all CRUD-related services.

**Testing:**
- Not detected (no dedicated `tests/` directory found in initial scan).

## Naming Conventions

**Files:**
- Backend: `snake_case.py` (e.g., `base_service.py`).
- SQL XML: `snake_case.xml` (e.g., `fail_lot.xml`).
- Frontend: `PascalCase.vue` (for components) or `camelCase.ts`.

**Directories:**
- Mostly `snake_case` (e.g., `master`, `production`).

## Where to Add New Code

**New Feature (Backend):**
- Primary code: `backend/services/[domain]/[feature]_service.py`.
- API endpoints: `backend/routers/[domain]/[feature].py`.
- SQL queries: `backend/sql/[domain]/[feature].xml`.
- Models: `backend/models/[domain]/[feature].py`.

**New Component/Module (Frontend):**
- Implementation: `frontend/src/components/[category]/[Name].vue` or `frontend/src/views/[domain]/[Name].vue`.

**Utilities:**
- Shared helpers: `backend/db/connection.py` (for DB) or a new `utils/` folder if needed.

## Special Directories

**backend/__pycache__/:**
- Purpose: Compiled Python bytecode.
- Generated: Yes.
- Committed: No.

**.planning/:**
- Purpose: Project management and codebase documentation.
- Generated: No (managed by GSD tools).
- Committed: Yes.

---

*Structure analysis: 2025-02-13*
