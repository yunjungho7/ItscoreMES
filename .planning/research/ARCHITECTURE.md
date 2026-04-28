# Architecture Patterns: Backend Integrity

**Domain:** Industrial MES Backend
**Researched:** 2024-11-20

## Recommended Architecture: Repository-Service with XML Mapping

The system follows a 3-tier architecture with a specialized "XML SQL Mapper" layer that allows DBAs to tune SQL in XML files while developers work with Pydantic models.

### Component Boundaries

| Component | Responsibility | Communicates With |
|-----------|---------------|-------------------|
| FastAPI Router | Endpoint definition, request parsing, response status. | Service Layer |
| Service Layer | Business logic, transaction management across multiple repos. | Repository Layer |
| Repository Layer | Loading XML queries, executing SQL, mapping rows to Pydantic. | XML Mapper, Database |
| XML Mapper | Parsing MyBatis-style XML into executable SQL with parameters. | Repository |

### Data Flow

1. **Request**: FastAPI receives a request and validates it via Pydantic.
2. **Service**: Service opens a DB Session (Connection Pool) and begins a transaction.
3. **Repository**: Repo calls XML Mapper with a `query_id` and parameters.
4. **Execution**: SQL is executed via `pymssql` within the pooled session.
5. **Response**: Rows are converted to Pydantic models and returned to the frontend.

## Patterns to Follow

### Pattern 1: Dependency Injection for DB Sessions
**What:** Use FastAPI's `Depends` to provide a database connection to services.
**Example:**
```python
def get_db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@router.get("/")
def read_items(db=Depends(get_db)):
    # db is a pooled connection
    pass
```

### Pattern 2: Context-Managed Transactions
**What:** Use a context manager to ensure atomic operations.
**Example:**
```python
@contextmanager
def transaction(session):
    try:
        yield
        session.commit()
    except Exception:
        session.rollback()
        raise
```

## Anti-Patterns to Avoid

### Anti-Pattern 1: "Leak-per-Request"
**What:** Opening a connection in a service but not closing it in a `finally` block.
**Why bad:** Quickly exhausts the connection pool.
**Instead:** Use FastAPI's dependency system or a context manager to guarantee closure.

### Anti-Pattern 2: Ad-hoc String Formatting
**What:** Using `f"SELECT * FROM table WHERE id = {user_id}"`.
**Why bad:** SQL Injection and poor performance (no execution plan reuse).
**Instead:** Always use parameterized queries (`#{param}` in XML).

## Scalability Considerations

| Concern | At 100 users | At 10K users | At 1M users |
|---------|--------------|--------------|-------------|
| Connections | Single server | Connection Pool (SQLAlchemy) | Read Replicas / PGBouncer style proxy |
| Cache | None | In-memory XML parsing cache | Redis for query result caching |

## Sources
- Repository Pattern in Python: https://www.cosmicpython.com/book/chapter_02_repository.html
- FastAPI Dependencies: https://fastapi.tiangolo.com/tutorial/dependencies/
