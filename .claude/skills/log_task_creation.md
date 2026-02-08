---
name: log_task_creation
description: Logs automated task creation events in audit database for compliance and debugging
agent: recurring-task-automator
tags: [audit, logging, compliance, observability]
---

# Log Task Creation Skill

## Purpose
Maintain a comprehensive audit trail of all automated recurring task creation operations, capturing who/what/when/why for compliance, debugging, and operational visibility.

## Responsibilities

1. **Audit Record Creation**
   - Record every automated task creation attempt
   - Capture complete context: source task, new task, recurrence rule
   - Include timestamps and system user identification
   - Store success/failure status with error details

2. **Database Persistence**
   - Insert records into audit_logs table atomically
   - Use database transactions to coordinate with task creation
   - Handle database failures gracefully
   - Implement batch writing for performance

3. **Structured Logging**
   - Emit structured logs for aggregation and analysis
   - Include correlation IDs for distributed tracing
   - Tag with appropriate log levels (INFO/ERROR)
   - Format for easy querying and filtering

4. **Metrics Emission**
   - Track task creation success/failure rates
   - Measure automation processing latency
   - Count occurrences created per pattern type
   - Monitor audit log write failures

## Configuration Parameters

```python
DATABASE_URL = os.getenv("DATABASE_URL")
AUDIT_TABLE = "recurring_task_audit_logs"
BATCH_AUDIT_WRITES = os.getenv("BATCH_AUDIT_WRITES", "false") == "true"
BATCH_SIZE = 50
BATCH_TIMEOUT_SECONDS = 5
ENABLE_METRICS = True
```

## Database Schema

```sql
CREATE TABLE recurring_task_audit_logs (
    id SERIAL PRIMARY KEY,

    -- Event identification
    audit_id VARCHAR(255) UNIQUE NOT NULL,
    correlation_id VARCHAR(255),
    event_id VARCHAR(255),  -- Triggering event ID

    -- Task references
    original_task_id VARCHAR(255) NOT NULL,
    new_task_id VARCHAR(255),
    parent_template_id VARCHAR(255),

    -- User context
    user_id VARCHAR(255) NOT NULL,
    created_by VARCHAR(100) DEFAULT 'system:recurring-automator',

    -- Recurrence details
    recurrence_pattern VARCHAR(50) NOT NULL,
    recurrence_frequency INTEGER,
    occurrence_number INTEGER,
    calculated_due_date TIMESTAMP,

    -- Operation status
    operation VARCHAR(50) NOT NULL,  -- 'task_created', 'creation_failed', 'termination_reached'
    status VARCHAR(20) NOT NULL,  -- 'success', 'failed', 'skipped'
    error_code VARCHAR(50),
    error_message TEXT,

    -- Timing
    triggered_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    processing_duration_ms INTEGER,

    -- Metadata
    metadata JSONB,

    -- Audit timestamps
    created_at TIMESTAMP DEFAULT NOW(),

    -- Indexes
    INDEX idx_correlation_id (correlation_id),
    INDEX idx_original_task_id (original_task_id),
    INDEX idx_new_task_id (new_task_id),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    INDEX idx_operation (operation)
);
```

## Input Schema

```python
{
  "audit_id": "audit-uuid-123",
  "correlation_id": "corr-uuid-456",
  "event_id": "evt-uuid-123",

  "original_task_id": "task-789",
  "new_task_id": "task-new-890",
  "parent_template_id": "recurring-template-456",

  "user_id": "user-123",
  "created_by": "system:recurring-automator",

  "recurrence_pattern": "weekly",
  "recurrence_frequency": 1,
  "occurrence_number": 13,
  "calculated_due_date": "2026-02-10T10:00:00Z",

  "operation": "task_created",
  "status": "success",
  "error_code": None,
  "error_message": None,

  "triggered_at": "2026-02-06T12:00:00Z",
  "completed_at": "2026-02-06T12:00:01Z",
  "processing_duration_ms": 1234,

  "metadata": {
    "timezone": "America/New_York",
    "day_of_week": 0,
    "automation_version": "1.2.0"
  }
}
```

## Output Schema

```python
{
  "logged": True|False,
  "audit_id": "audit-uuid-123",
  "log_id": 12345,
  "timestamp": "2026-02-06T12:00:01Z",
  "error": None|"Database connection failed"
}
```

## Audit Operation Types

| Operation | Description | Status Values |
|-----------|-------------|---------------|
| `task_created` | Successfully created next occurrence | success |
| `creation_failed` | Failed to create next occurrence | failed |
| `termination_reached` | Recurring task reached end condition | skipped |
| `duplicate_detected` | Duplicate event (idempotency) | skipped |
| `validation_failed` | Invalid recurrence configuration | failed |

## Logging Strategy

```python
import logging
import json

logger = logging.getLogger("recurring_task_automator")

def log_task_creation(
    original_task_id: str,
    new_task_id: Optional[str],
    recurrence_config: dict,
    status: str,
    error: Optional[Exception] = None,
    correlation_id: Optional[str] = None
) -> dict:
    """
    Log automated task creation to database and structured logs.
    """
    audit_id = str(uuid.uuid4())
    triggered_at = datetime.now(timezone.utc)

    # Structured log
    log_data = {
        "audit_id": audit_id,
        "correlation_id": correlation_id,
        "original_task_id": original_task_id,
        "new_task_id": new_task_id,
        "recurrence_pattern": recurrence_config["pattern"],
        "occurrence_number": recurrence_config.get("current_occurrence"),
        "status": status,
        "error": str(error) if error else None
    }

    if status == "success":
        logger.info(f"Recurring task created: {json.dumps(log_data)}")
    else:
        logger.error(f"Recurring task creation failed: {json.dumps(log_data)}")

    # Database audit record
    completed_at = datetime.now(timezone.utc)
    duration_ms = int((completed_at - triggered_at).total_seconds() * 1000)

    try:
        db.execute("""
            INSERT INTO recurring_task_audit_logs
            (audit_id, correlation_id, original_task_id, new_task_id,
             user_id, recurrence_pattern, recurrence_frequency, occurrence_number,
             operation, status, error_code, error_message,
             triggered_at, completed_at, processing_duration_ms, metadata)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            audit_id, correlation_id, original_task_id, new_task_id,
            recurrence_config["user_id"], recurrence_config["pattern"],
            recurrence_config["frequency"], recurrence_config.get("current_occurrence"),
            "task_created" if status == "success" else "creation_failed",
            status, error.__class__.__name__ if error else None,
            str(error) if error else None,
            triggered_at, completed_at, duration_ms,
            json.dumps(recurrence_config.get("metadata", {}))
        ))

        db.commit()

        return {
            "logged": True,
            "audit_id": audit_id,
            "timestamp": completed_at.isoformat()
        }

    except Exception as db_error:
        logger.error(f"Failed to write audit log to database: {db_error}")
        return {
            "logged": False,
            "audit_id": audit_id,
            "error": str(db_error)
        }
```

## Metrics to Track

```python
# Success/failure rates
recurring_task_creation_total{pattern="weekly", status="success|failed"}
recurring_task_termination_total{reason="end_date|max_occurrences"}

# Performance
recurring_task_processing_duration_seconds{pattern="weekly", percentile="50|95|99"}
audit_log_write_duration_seconds{percentile="50|95|99"}

# Errors
recurring_task_creation_errors_total{error_type="DatabaseError|ValidationError"}
audit_log_write_errors_total
```

## Success Criteria

- [ ] All task creation attempts logged (success and failure)
- [ ] Audit records include complete context for debugging
- [ ] Correlation IDs enable distributed tracing
- [ ] Database writes are atomic with task creation
- [ ] Failed database writes trigger alerts
- [ ] Structured logs formatted for aggregation
- [ ] Metrics available for monitoring dashboards
- [ ] Audit records queryable by task ID, user ID, date range
- [ ] Log retention policy configured

## Integration Points

- **Called By**: `create_next_task` after task creation attempt
- **Outputs To**: Database (recurring_task_audit_logs table)
- **Outputs To**: Structured logging system (Elasticsearch/CloudWatch)
- **Outputs To**: Metrics system (Prometheus/CloudWatch Metrics)
- **Dependencies**: Database connection, logging infrastructure
- **Consumers**: Audit reports, compliance tools, debugging queries
