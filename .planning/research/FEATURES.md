# Feature Landscape: Backend Integrity

**Domain:** Industrial MES Backend
**Researched:** 2024-11-20

## Table Stakes

Features users expect. Missing = product feels incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Connection Pooling | Performance & Stability | Medium | Essential for SQL Server. |
| Transaction Safety | Data Consistency | Low | atomic CRUD operations. |
| Parameterized Queries | Security | Low | Prevents SQL Injection. |
| Robust Paging | User Experience | Low | Handled in XML via OFFSET/FETCH. |

## Differentiators

Features that set product apart. Not expected, but valued.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Unified Dynamic SQL | Powerful filtering without code changes | High | Move from `re` to `Jinja2`. |
| Automatic Logging | Traceability for every DB change | Medium | Interceptor at the Mapper level. |
| Schema Enforcement | Fail fast on data entry errors | Low | Pydantic integration in Repos. |
| Connection Pre-ping | Resilience against DB downtime | Low | Built-in to SQLAlchemy pool. |

## Anti-Features

Features to explicitly NOT build.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| Raw String Injection | Security risk (SQLi) | Always use `#{param}`. |
| Manual Encoding Fixes | High maintenance burden | Centralize in DB driver/mapper. |
| Global Single Connection | Thread safety issues | Use Connection Pooling per request. |

## Feature Dependencies

```
Connection Pooling → Transaction Safety
Dynamic SQL Engine → Advanced Filtering
Pydantic Models → Schema Enforcement
```

## MVP Recommendation

Prioritize:
1. **Connection Pooling** (SQLAlchemy)
2. **Standardized Transaction Scope** (FastAPI Depends)
3. **Centralized Encoding Fix** (Driver level)

Defer: **Jinja2 Migration**: Can be done incrementally for complex queries.

## Sources
- MyBatis Dynamic SQL: https://mybatis.org/mybatis-3/dynamic-sql.html
- Pydantic v2 Features: https://docs.pydantic.dev/latest/concepts/models/
