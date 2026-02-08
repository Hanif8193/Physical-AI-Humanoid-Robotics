---
name: store_logs
description: Stores audit logs in PostgreSQL/NeonDB with optimized schema and indexing
agent: audit-agent
tags: [database, postgresql, neondb, storage, persistence]
---

# Store Logs Skill

## Purpose
Persist enriched audit log records to PostgreSQL/NeonDB with an optimized schema design, efficient batch operations, and robust error handling for compliance-grade audit trails.

## Responsibilities

1. **Database Schema Management**
   - Maintain audit_logs table with appropriate columns and types
   - Implement partitioning strategy for high-volume data
   - Create and maintain indexes for query performance
   - Handle schema migrations safely

2. **Data Persistence**
   - Insert audit records with complete metadata
   - Use batch inserts for performance optimization
   - Implement connection pooling for efficiency
   - Handle constraint violations gracefully

3. **Transaction Management**
   - Ensure atomicity of audit log writes
   - Coordinate with idempotency checks
   - Implement retry logic for transient failures
   - Use proper isolation levels

4. **Performance Optimization**
   - Batch insert operations when appropriate
   - Use prepared statements to prevent SQL injection
   - Implement connection pooling
   - Monitor query performance and optimize indexes

## Configuration Parameters

```python
DATABASE_URL = os.getenv("DATABASE_URL")
# Example: postgresql://user:password@host:5432/database
# NeonDB: postgresql://user:password@ep-name.region.aws.neon.tech/database

CONNECTION_POOL_SIZE = 10
MAX_OVERFLOW = 20
POOL_TIMEOUT = 30
BATCH_INSERT_SIZE = 100
BATCH_TIMEOUT_SECONDS = 5
ENABLE_PARTITIONING = os.getenv("ENABLE_AUDIT_PARTITIONING", "false") == "true"
```

## Database Schema

### Main Audit Logs Table

```sql
CREATE TABLE audit_logs (
    -- Primary identification
    log_id BIGSERIAL PRIMARY KEY,
    event_id VARCHAR(255) UNIQUE NOT NULL,

    -- Task and user references
    task_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,

    -- Operation details
    operation_type VARCHAR(20) NOT NULL,  -- 'create', 'update', 'delete', 'complete'
    event_type VARCHAR(50) NOT NULL,      -- 'task.created', 'task.updated', etc.

    -- Timing
    event_timestamp TIMESTAMP NOT NULL,   -- When the event occurred
    processed_at TIMESTAMP DEFAULT NOW(), -- When it was logged

    -- Correlation and tracing
    correlation_id VARCHAR(255),
    source VARCHAR(100),                  -- 'api-server', 'recurring-automator', etc.

    -- Data payload (JSONB for flexibility)
    payload JSONB,                        -- Full task data for create/delete
    changes JSONB,                        -- Before/after values for updates

    -- Metadata (JSONB for extensibility)
    metadata JSONB,                       -- IP, user_agent, session_id, etc.

    -- Audit timestamps
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for query performance
CREATE INDEX idx_audit_logs_task_id ON audit_logs(task_id);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_operation_type ON audit_logs(operation_type);
CREATE INDEX idx_audit_logs_event_timestamp ON audit_logs(event_timestamp DESC);
CREATE INDEX idx_audit_logs_correlation_id ON audit_logs(correlation_id);

-- Composite indexes for common query patterns
CREATE INDEX idx_audit_logs_user_timestamp ON audit_logs(user_id, event_timestamp DESC);
CREATE INDEX idx_audit_logs_task_timestamp ON audit_logs(task_id, event_timestamp DESC);

-- GIN index for JSONB searching
CREATE INDEX idx_audit_logs_payload ON audit_logs USING GIN(payload);
CREATE INDEX idx_audit_logs_metadata ON audit_logs USING GIN(metadata);

-- Constraint to ensure valid operation types
ALTER TABLE audit_logs ADD CONSTRAINT chk_operation_type
CHECK (operation_type IN ('create', 'update', 'delete', 'complete'));
```

### Partitioning Strategy (Optional, for high volume)

```sql
-- Partition by month for easier archival and query performance
CREATE TABLE audit_logs (
    log_id BIGSERIAL,
    event_id VARCHAR(255) NOT NULL,
    task_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    operation_type VARCHAR(20) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    event_timestamp TIMESTAMP NOT NULL,
    processed_at TIMESTAMP DEFAULT NOW(),
    correlation_id VARCHAR(255),
    source VARCHAR(100),
    payload JSONB,
    changes JSONB,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (log_id, event_timestamp)
) PARTITION BY RANGE (event_timestamp);

-- Create partitions for each month
CREATE TABLE audit_logs_2026_02 PARTITION OF audit_logs
FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');

CREATE TABLE audit_logs_2026_03 PARTITION OF audit_logs
FOR VALUES FROM ('2026-03-01') TO ('2026-04-01');

-- Auto-create partitions with a scheduled job
```

## Insert Operations

### Single Insert

```python
from psycopg2 import pool
import json

connection_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=CONNECTION_POOL_SIZE,
    dsn=DATABASE_URL
)

def store_audit_log(audit_record: dict) -> dict:
    """
    Store a single audit log record in the database.
    """
    conn = connection_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO audit_logs (
                    event_id, task_id, user_id, operation_type, event_type,
                    event_timestamp, correlation_id, source,
                    payload, changes, metadata
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING log_id, created_at
            """, (
                audit_record["event_id"],
                audit_record["task_id"],
                audit_record["user_id"],
                audit_record["operation_type"],
                audit_record["event_type"],
                audit_record["timestamp"],
                audit_record.get("correlation_id"),
                audit_record.get("metadata", {}).get("source"),
                json.dumps(audit_record.get("payload")),
                json.dumps(audit_record.get("changes")),
                json.dumps(audit_record.get("metadata"))
            ))

            result = cur.fetchone()
            conn.commit()

            return {
                "success": True,
                "log_id": result[0],
                "created_at": result[1].isoformat()
            }

    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to store audit log: {e}")
        return {
            "success": False,
            "error": str(e)
        }

    finally:
        connection_pool.putconn(conn)
```

### Batch Insert (Performance Optimization)

```python
from psycopg2.extras import execute_batch

def store_audit_logs_batch(audit_records: list) -> dict:
    """
    Store multiple audit log records in a single batch operation.
    """
    if not audit_records:
        return {"success": True, "count": 0}

    conn = connection_pool.getconn()
    try:
        with conn.cursor() as cur:
            records = [
                (
                    r["event_id"], r["task_id"], r["user_id"],
                    r["operation_type"], r["event_type"], r["timestamp"],
                    r.get("correlation_id"), r.get("metadata", {}).get("source"),
                    json.dumps(r.get("payload")), json.dumps(r.get("changes")),
                    json.dumps(r.get("metadata"))
                )
                for r in audit_records
            ]

            execute_batch(cur, """
                INSERT INTO audit_logs (
                    event_id, task_id, user_id, operation_type, event_type,
                    event_timestamp, correlation_id, source,
                    payload, changes, metadata
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, records, page_size=BATCH_INSERT_SIZE)

            conn.commit()

            return {
                "success": True,
                "count": len(audit_records)
            }

    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to batch insert audit logs: {e}")
        return {
            "success": False,
            "error": str(e),
            "count": 0
        }

    finally:
        connection_pool.putconn(conn)
```

## Input Schema

```python
{
  "event_id": "evt-uuid-123",
  "task_id": "task-123",
  "user_id": "user-456",
  "operation_type": "create",
  "event_type": "task.created",
  "timestamp": "2026-02-06T12:00:00Z",
  "correlation_id": "corr-uuid-456",
  "payload": {
    "title": "Complete project proposal",
    "priority": "high",
    "due_date": "2026-02-10T17:00:00Z",
    ...
  },
  "changes": None,  # Only for update operations
  "metadata": {
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0...",
    "session_id": "sess-uuid-789",
    "source": "api-server"
  }
}
```

## Output Schema

```python
{
  "success": True|False,
  "log_id": 12345,
  "created_at": "2026-02-06T12:00:00.123Z",
  "error": None|"Database connection failed"
}
```

## Error Handling

**Constraint Violations:**
- Duplicate event_id: Log warning, return success (idempotent)
- Invalid operation_type: Reject and send to DLQ
- Foreign key violations: Validate before insert

**Connection Failures:**
- Implement exponential backoff retry (3 attempts)
- Use circuit breaker pattern for database outages
- Queue failed writes for later processing

**Transaction Failures:**
- Rollback on any error
- Retry transient failures
- Log permanent failures for manual review

## Performance Considerations

1. **Connection Pooling**: Reuse database connections
2. **Batch Inserts**: Group multiple records (100-1000) for bulk insert
3. **Async Processing**: Use background workers for non-critical writes
4. **Partitioning**: Partition by time for large datasets (>10M records)
5. **Index Optimization**: Monitor query patterns and adjust indexes
6. **JSONB Indexing**: Use GIN indexes for JSONB column searches

## Data Retention

```sql
-- Archive old audit logs (move to archive table)
CREATE TABLE audit_logs_archive AS SELECT * FROM audit_logs WHERE 1=0;

-- Move logs older than 1 year to archive
INSERT INTO audit_logs_archive
SELECT * FROM audit_logs
WHERE event_timestamp < NOW() - INTERVAL '1 year';

-- Delete archived records from main table
DELETE FROM audit_logs
WHERE event_timestamp < NOW() - INTERVAL '1 year';

-- Or drop old partitions (if using partitioning)
DROP TABLE IF EXISTS audit_logs_2025_01;
```

## Success Criteria

- [ ] Audit logs stored with all required fields
- [ ] Duplicate event_ids handled idempotently
- [ ] Database constraints enforced properly
- [ ] Indexes improve query performance (verified with EXPLAIN)
- [ ] Connection pooling reduces overhead
- [ ] Batch inserts improve throughput
- [ ] Failed writes logged for debugging
- [ ] Database schema supports future extensibility
- [ ] Data retention policy implemented

## Integration Points

- **Called By**: `log_task_event` skill after event processing
- **Stores To**: PostgreSQL/NeonDB audit_logs table
- **Queried By**: `query_activity_history` skill
- **Dependencies**: Database connection, connection pool
- **Monitoring**: Track insert latency, connection pool usage, storage growth
