# Domain Pitfalls: Backend Integrity

**Domain:** Industrial MES Backend
**Researched:** 2024-11-20

## Critical Pitfalls

### Pitfall 1: Connection Exhaustion (No Pooling)
**What goes wrong:** Every API request opens a new TCP connection to SQL Server and closes it. Under moderate load, the database server runs out of available ports or connection slots.
**Why it happens:** Current `get_db_connection()` logic lacks a centralized pool.
**Consequences:** `Connection Refused` errors, high latency (handshake overhead), and potential server-side resource exhaustion.
**Prevention:** Use `SQLAlchemy`'s `QueuePool` with a fixed size and `max_overflow`.
**Detection:** Monitoring DB connection counts and tracking `TCP_WAIT` sockets.

### Pitfall 2: Silent Data Corruption (Encoding Mojibake)
**What goes wrong:** Korean characters appear as `쩍쨀` or `?`.
**Why it happens:** The database uses `Latin-1` collation but stores `CP949` data, and the Python driver is not correctly configured to bridge the two.
**Consequences:** Permanent data corruption if corrupted strings are saved back to the DB; broken search/filters for Korean names.
**Prevention:** Standardize connection `charset='cp949'` (or matching DB collation) and use `NVARCHAR` for all text columns. Centralize encoding logic in the `execute_query` wrapper rather than ad-hoc in services.
**Detection:** Integration tests that write and read back special characters.

### Pitfall 3: Fragmented Transactions
**What goes wrong:** A "Search" operation returns a "Total Count" and a "List of Items" that are inconsistent (e.g., count says 10, but list has 11 items).
**Why it happens:** The count and select queries are executed in separate database connections/transactions.
**Consequences:** UI glitches, off-by-one errors in pagination, and user confusion.
**Prevention:** Ensure all related queries in a single service call use the same connection/session.

## Moderate Pitfalls

### Pitfall 1: Fragile Dynamic SQL (Regex-based Eval)
**What goes wrong:** `<if test="param != null">` works, but complex logic like `<if test="type == 'A' and status != 'X'">` fails or requires manual code changes to the parser.
**Prevention:** Use a proper template engine like `Jinja2` for SQL generation.

### Pitfall 2: XXE (XML External Entity) Vulnerability
**What goes wrong:** Malicious XML files could be used to read files from the server's filesystem.
**Prevention:** Use `defusedxml` to parse XML files.

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| DB Migration | Collation Mismatch | Run a script to verify `SERVERPROPERTY('Collation')` before connecting. |
| Paging | Offset Performance | Large offsets in SQL Server can be slow. Use Keyset pagination for very large tables. |
| Transactions | Deadlocks | Implement a basic retry decorator for `pymssql.InternalError` with state `1205`. |

## Sources
- SQL Server Deadlock Handling: https://learn.microsoft.com/en-us/sql/relational-databases/performance/deadlocks
- Python XML Security: https://docs.python.org/3/library/xml.html#xml-vulnerabilities
