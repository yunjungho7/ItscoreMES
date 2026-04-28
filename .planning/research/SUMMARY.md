# Research Summary: Backend Integrity (FastAPI + XML SQL Mapper)

**Domain:** Industrial MES Backend
**Researched:** 2024-05-24
**Overall confidence:** HIGH

## Executive Summary

The current architecture uses a custom MyBatis-style XML SQL mapper with `pymssql` and FastAPI. While this provides flexibility and decouples SQL from Python code, the current implementation has significant integrity and performance risks, primarily due to the lack of connection pooling, fragile dynamic SQL evaluation, and ad-hoc encoding fixes.

To stabilize the backend, we recommend adopting a "Hardened Custom Mapper" approach that leverages `SQLAlchemy` for connection management while keeping the XML-based SQL organization. This ensures enterprise-grade reliability (pooling, transaction safety, resilience) without a full rewrite of the existing SQL logic.

## Key Findings

**Stack:** FastAPI + SQLAlchemy (Pooling/Engine) + pymssql + Jinja2 (Dynamic SQL).
**Architecture:** Dependency Injection for DB sessions; Repository pattern for XML mapping.
**Critical pitfall:** Connection exhaustion and latency due to "one-connection-per-query" pattern.

## Implications for Roadmap

Based on research, suggested phase structure:

1. **Phase 1: Foundation Hardening** - Infrastructure improvements.
   - Introduce SQLAlchemy connection pooling.
   - Centralize encoding/decoding logic in the DB layer.
   - Implement a transaction context manager.

2. **Phase 2: Mapper Standardization** - Robust SQL mapping.
   - Replace `re`-based logic with `Jinja2` for dynamic SQL (`<if>`, `<foreach>`).
   - Add schema validation using Pydantic in the Repository layer.

3. **Phase 3: Monitoring & Observability**
   - Implement query logging and slow-query detection middleware.

**Phase ordering rationale:**
- Infrastructure (Phase 1) provides immediate performance and reliability gains with minimal change to business logic.
- Mapper standardization (Phase 2) improves developer experience and reduces bugs in complex queries.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | SQLAlchemy + pymssql is the industry standard for MSSQL in Python. |
| Features | MEDIUM | Specific MES features like "Field Status" need more domain-specific research. |
| Architecture | HIGH | Repository pattern is well-proven for SQL-first applications. |
| Pitfalls | HIGH | Common issues with custom mappers are well-documented. |

## Gaps to Address

- **Multiple Active Result Sets (MARS):** Investigation needed if complex nested queries are required in a single connection.
- **Deadlock Handling:** SQL Server specific retry logic should be considered for high-concurrency production environments.
