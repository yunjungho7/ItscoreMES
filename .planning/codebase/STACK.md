# Technology Stack

**Analysis Date:** 2026-04-28

## Languages

**Primary:**
- Python 3.x - Used for the entire backend API and database mapping logic.
- TypeScript 6.0 - Primary language for frontend development, ensuring type safety.

**Secondary:**
- XML - Used for MyBatis-style SQL mapping in `backend/sql/`.
- CSS - Custom styling in `frontend/src/style.css`.
- HTML - Entry point and templates for Vue components.

## Runtime

**Environment:**
- Node.js - Frontend development and build environment.
- Python 3.x - Backend execution environment.

**Package Manager:**
- npm - Frontend dependency management.
- pip - Backend dependency management via `requirements.txt`.
- Lockfile: `package-lock.json` present for frontend.

## Frameworks

**Core:**
- FastAPI (0.128.8) - High-performance backend web framework.
- Vue 3 (3.5.32) - Frontend component framework using the Composition API.

**Testing:**
- Not detected - No explicit testing frameworks like pytest or Vitest were found in manifests.

**Build/Dev:**
- Vite (8.0.4) - Frontend build tool and development server.
- Uvicorn (0.39.0) - ASGI server for running FastAPI.

## Key Dependencies

**Critical:**
- `pymssql` (2.3.2) - Database driver for Microsoft SQL Server.
- `pinia` (3.0.4) - State management for Vue.
- `vue-router` (5.0.4) - Client-side routing for the frontend.
- `axios` (1.15.0) - HTTP client for API communication.
- `pydantic` (2.13.0) - Data validation and settings management for the backend.

**Infrastructure:**
- `python-multipart` - Handles form-data parsing in FastAPI.

## Configuration

**Environment:**
- Environment variables - Used for DB configuration (`DB_NAME`, `DB_UID`, `DB_PWD`) and API URLs (`VITE_API_URL`).
- `.env` files - Referenced in `frontend/src/api/index.ts`.

**Build:**
- `frontend/vite.config.ts` - Configures the frontend build and development proxy.
- `frontend/tsconfig.json` - TypeScript configuration.

## Platform Requirements

**Development:**
- Windows/Linux/macOS with Node.js and Python 3.x.
- SQL Server access is required for the backend.

**Production:**
- Python ASGI server (Uvicorn).
- Static file hosting for the Vite-built frontend.

---

*Stack analysis: 2026-04-28*
