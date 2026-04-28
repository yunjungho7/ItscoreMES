# Coding Conventions

**Analysis Date:** 2025-05-22

## Naming Patterns

**Files:**
- **Frontend Components:** PascalCase (e.g., `src/components/common/DataGrid.vue`, `src/views/management/system/User.vue`).
- **Backend Python files:** snake_case (e.g., `backend/services/base_service.py`, `backend/routers/auth.py`).
- **SQL Mappers:** snake_case with `.xml` extension (e.g., `backend/sql/master/plant.xml`).

**Functions:**
- **Frontend (TS):** camelCase (e.g., `fetchData`, `handleSave`, `onRowClick`).
- **Backend (Python):** snake_case (e.g., `get_all`, `execute_query`, `create_user`).

**Variables:**
- **Frontend (TS):** camelCase (e.g., `loading`, `searchPlant`, `selectedIdx`).
- **Backend (Python):** snake_case (e.g., `query_info`, `user_dict`, `row_count`).
- **Database Fields (in code):** UPPERCASE (e.g., `PLANTCD`, `EMPID`, `NAME`, `SHOWYN`). This is consistent across both frontend and backend to match the MSSQL schema.

**Types:**
- **Frontend (TS):** PascalCase for interfaces/types (though many are currently used as `any`).
- **Backend (Python):** PascalCase for Pydantic models (e.g., `UserCreate`, `UserUpdate`).

## Code Style

**Formatting:**
- **Frontend:** Standard Vue 3 / TypeScript formatting. No specific `.prettierrc` or `.eslintrc` found, likely using IDE defaults or `vue-tsc` for basic validation.
- **Backend:** PEP 8 inspired snake_case naming. Mixed use of English and Korean comments.

**Linting:**
- **Frontend:** `vue-tsc` is used for type checking during build (`package.json`).
- **Backend:** No dedicated linter (like flake8 or black) detected in `requirements.txt`.

## Import Organization

**Order:**
1. **Frontend:**
   - Framework imports (`vue`, `pinia`, `vue-router`)
   - Internal API/Utils (`../../../api`)
   - Components (`../../../components/common/...`)
2. **Backend:**
   - Standard library (`os`, `typing`)
   - Third-party libraries (`fastapi`, `pymssql`)
   - Internal modules (`services`, `models`, `db`, `routers`)

**Path Aliases:**
- Not explicitly used in the observed files; relative paths like `../../../` are common in components.

## Error Handling

**Patterns:**
- **Backend:** Uses FastAPI global exception handlers in `backend/main.py`. Services raise `HTTPException` with specific status codes.
- **Frontend:** Axios response interceptor in `frontend/src/api/index.ts` catches errors and displays an `alert()` to the user. Local `try-catch` blocks in components are used for logging errors to the console.

## Logging

**Framework:** `console` for frontend, `print` for backend (e.g., `backend/services/base_service.py`).

**Patterns:**
- Debugging prints are occasionally present in backend services (e.g., `print(f"DEBUG [{query_id}]: {len(results)} rows fetched.")`).
- Frontend logs errors via `console.error`.

## Comments

**When to Comment:**
- Major modules and classes have docstrings in Korean (e.g., `backend/services/base_service.py`).
- Complex logic sections are sometimes marked with emoji-like separators (e.g., `# ── 라우터 등록 ──`).

**JSDoc/TSDoc:**
- Not observed in the codebase.

## Function Design

**Size:** Most functions are focused, but some frontend event handlers (like `handleSave` in `User.vue`) handle multiple responsibilities (validation, API call, user notification).

**Parameters:**
- **Backend:** Uses Pydantic models for complex inputs (`create_user(user: UserCreate)`).
- **Frontend:** Pass objects or multiple refs to functions.

**Return Values:**
- **Backend:** Returns dictionaries (JSON) or row counts.
- **Frontend:** Mostly `void` for event handlers, `Promise` for API calls.

## Module Design

**Exports:**
- **Frontend:** Default exports for the API client (`api/index.ts`). Named exports for components are not common; they are imported via their file path.
- **Backend:** Routers are exported as `router` and aggregated in `main.py`.

**Barrel Files:**
- `__init__.py` files are used in backend directories to manage imports and sometimes aggregate routers.

---

*Convention analysis: 2025-05-22*
