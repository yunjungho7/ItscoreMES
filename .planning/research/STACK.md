# Technology Stack: Backend Integrity

**Project:** NEWMES
**Researched:** 2024-11-20

## Recommended Stack

### Core Framework
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| FastAPI | ^0.100.0 | Web Framework | High performance, async support, native Pydantic integration. |
| Pydantic v2 | ^2.0.0 | Data Validation | Type safety and schema enforcement for API and DB models. |

### Database
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| pymssql | ^2.2.8 | MSSQL Driver | Lightweight driver with wide support for SQL Server. |
| SQLAlchemy | ^2.0.0 | Connection Pool | Battle-tested pooling (`QueuePool`), `pre_ping`, and transaction management. |

### Infrastructure
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Jinja2 | ^3.1.0 | Dynamic SQL Engine | Replacing basic `re` logic for robust `<if>`, `<foreach>` in XML. |
| defusedxml | ^0.7.1 | Safe XML Parsing | Prevents XXE attacks in XML-based SQL mapping. |

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Connection Pool | SQLAlchemy | DBUtils | SQLAlchemy offers better integration with FastAPI and more features (pre-ping, recycle). |
| SQL Mapper | Custom (Hardened) | aiosql | Migration cost. aiosql uses `.sql` files, while project currently uses `.xml`. |
| Driver | pymssql | pyodbc | pyodbc requires system-level ODBC drivers which can be harder to configure in some environments. |

## Installation

```bash
# Core Dependencies
pip install fastapi uvicorn pydantic[email] sqlalchemy pymssql

# Integrity & Safety
pip install jinja2 defusedxml
```

## Sources
- FastAPI Official Docs: https://fastapi.tiangolo.com/advanced/database/
- SQLAlchemy Engine Configuration: https://docs.sqlalchemy.org/en/20/core/engines.html
- pymssql Encoding Guide: http://www.pymssql.org/en/stable/unicode_and_charset.html
