# Frontend/Backend Alignment Strategy

**Project:** NEWMES (FastAPI + Vue.js TypeScript)
**Researched:** 2024-05-20
**Confidence:** HIGH

## Overview

To prevent runtime errors and ensure data consistency in a "stabilization" phase, the project must move away from manual type definition and adopt **Schema-Driven Development**. The Pydantic models in the FastAPI backend should serve as the "Single Source of Truth," and TypeScript interfaces/API clients should be automatically generated from the OpenAPI specification.

## Recommended Tooling: `@hey-api/openapi-ts`

The industry-standard tool for 2024 is `@hey-api/openapi-ts` (the modern successor to `openapi-typescript-codegen`).

### Why this tool?
- **End-to-End Type Safety:** Generates full TypeScript SDKs, including request/response types and API call functions.
- **Pydantic v2 Support:** Perfectly handles the Pydantic v2 schemas used in the NEWMES backend.
- **Axios Integration:** Can be configured to use the existing `axios` instance in `frontend/src/api/index.ts`.
- **Validation Consistency:** Ensures that frontend calls match backend expectations before the code even runs.

## Alignment Patterns

### 1. Case Sensitivity & Naming Conventions
The NEWMES backend currently uses `SCREAMING_SNAKE_CASE` (e.g., `USER_ID`, `PROCESS_ID`) in Pydantic models, likely reflecting the database schema.

**Recommendation:**
- **Option A (Preserve):** Keep the uppercase names in the frontend. The generator will produce `USER_ID: string`. This is the "path of least resistance" and prevents mapping errors.
- **Option B (Transform):** Use Pydantic's `alias_generator` to convert `SCREAMING_SNAKE_CASE` to `camelCase` (e.g., `userId`) in the JSON layer.
  ```python
  from pydantic.alias_generators import to_camel
  # Custom generator might be needed for SCREAMING case
  ```
**Verdict:** Use **Option A** for stabilization speed. The generator ensures that if the backend expects `USER_ID`, the frontend provides `USER_ID`.

### 2. Synchronization Workflow
1. **Backend:** Define Pydantic models with explicit `response_model` in routers.
2. **Export:** Generate `openapi.json` from the running FastAPI server or via a script.
3. **Generate:** Run `@hey-api/openapi-ts` to update `frontend/src/api/generated`.
4. **Consume:** Import the generated client and types in Vue components.

### 3. Handling Enums
Define Enums in Python using `enum.Enum`. FastAPI will export these as string unions in OpenAPI.
```python
class UserGubun(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"
```
The generator will create a corresponding TypeScript Enum or Union, preventing "magic string" bugs in the frontend.

## Implementation Roadmap

| Step | Action | Responsibility |
|------|--------|----------------|
| 1 | Standardize Pydantic models (ensure `Optional` is accurate) | Backend |
| 2 | Add `openapi.json` export script to `backend/main.py` | Backend |
| 3 | Install `@hey-api/openapi-ts` in `frontend` | Frontend |
| 4 | Configure `package.json` script: `"api:sync": "openapi-ts -i ../backend/openapi.json -o ./src/api/client -c axios"` | Frontend |
| 5 | Refactor existing API calls to use the generated client | Frontend |

## Critical Pitfalls to Avoid

- **Manual Interface Duplication:** Never manually create `interface User { ... }` in the frontend. It *will* drift from the backend.
- **Relaxed Types:** Avoid using `any` or `Record<string, any>`. If a type is missing in the generator, fix the Pydantic model first.
- **Missing `response_model`:** If a FastAPI endpoint doesn't define a `response_model`, the OpenAPI spec will be incomplete, leading to `any` types in the frontend.

## Sources
- [FastAPI Documentation on OpenAPI](https://fastapi.tiangolo.com/advanced/openapi-generation/)
- [@hey-api/openapi-ts Documentation](https://heyapi.vercel.app/openapi-ts/)
- [Pydantic v2 Migration Guide](https://docs.pydantic.dev/latest/migration/)
