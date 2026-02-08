---
name: log_notification
description: Logs all notification attempts (success and failure) to database for audit and debugging
agent: notification-agent
tags: [logging, observability, audit]
---

# Log Notification Skill

## Purpose
Maintain a comprehensive audit trail of all notification delivery attempts, enabling debugging, analytics, and compliance reporting.

## Responsibilities

1. **Event Capture**
   - Record every notification attempt (success, failure, retry)
   - Capture relevant context and metadata
   - Include correlation IDs for tracing
   - Store structured data for querying

2. **Database Persistence**
   - Insert notification log record into database
   - Use efficient batch writing for high throughput
   - Handle database connection failures gracefully
   - Implement async writing to avoid blocking

3. **Log Enrichment**
   - Add timestamps (attempt time, completion time)
   - Calculate delivery latency
   - Include error details and stack traces for failures
   - Attach user and notification identifiers

4. **Metrics Emission**
   - Emit metrics for monitoring dashboards
   - Track success/failure rates
   - Measure delivery latency percentiles
   - Monitor retry counts and DLQ rates

## Configuration Parameters

```python
DATABASE_URL = os.getenv("DATABASE_URL")
NOTIFICATION_LOG_TABLE = "notification_logs"
BATCH_SIZE = 100  # records per batch write
BATCH_TIMEOUT = 5  # seconds
ASYNC_LOGGING = True
```

## Database Schema

```sql
CREATE TABLE notification_logs (
    id SERIAL PRIMARY KEY,
    message_id VARCHAR(255) UNIQUE NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    notification_type VARCHAR(20) NOT NULL,  -- 'email' or 'push'
    recipient VARCHAR(255) NOT NULL,
    channel VARCHAR(50),  -- 'fcm', 'apns', 'sendgrid', 'ses'

    -- Attempt tracking
    attempt_number INTEGER NOT NULL DEFAULT 1,
    max_attempts INTEGER NOT NULL DEFAULT 3,

    -- Delivery status
    status VARCHAR(20) NOT NULL,  -- 'success', 'failed', 'retrying', 'dlq'
    error_code VARCHAR(50),
    error_message TEXT,
    retryable BOOLEAN,

    -- Timing
    scheduled_at TIMESTAMP,
    attempted_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    delivery_latency_ms INTEGER,

    -- Context
    correlation_id VARCHAR(255),
    metadata JSONB,

    -- Indexes
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_message_id ON notification_logs(message_id);
CREATE INDEX idx_user_id ON notification_logs(user_id);
CREATE INDEX idx_status ON notification_logs(status);
CREATE INDEX idx_attempted_at ON notification_logs(attempted_at);
CREATE INDEX idx_correlation_id ON notification_logs(correlation_id);
```

## Input Schema

```python
{
  "message_id": "uuid",
  "user_id": "user-123",
  "notification_type": "email|push",
  "recipient": "user@example.com|device-token",
  "channel": "sendgrid|fcm|apns",

  "attempt_number": 1,
  "max_attempts": 3,

  "status": "success|failed|retrying|dlq",
  "error_code": "TIMEOUT|INVALID_EMAIL|None",
  "error_message": "Detailed error description",
  "retryable": True|False,

  "scheduled_at": "2026-02-06T12:00:00Z",
  "attempted_at": "2026-02-06T12:00:01Z",
  "completed_at": "2026-02-06T12:00:02Z",
  "delivery_latency_ms": 1234,

  "correlation_id": "trace-uuid",
  "metadata": {
    "task_id": "456",
    "subject": "Task Reminder"
  }
}
```

## Output Schema

```python
{
  "logged": True|False,
  "log_id": 12345,
  "timestamp": "2026-02-06T12:00:02Z",
  "error": None|"Database connection failed"
}
```

## Log Levels and Contexts

**INFO Level:**
- Successful deliveries
- Scheduled retries
- Consumer lifecycle events

**WARNING Level:**
- Retryable failures
- Circuit breaker state changes
- High consumer lag

**ERROR Level:**
- Permanent failures
- Retry exhaustion
- Database logging failures
- Critical system errors

## Metrics to Track

```python
notification_attempts_total{type="email|push", status="success|failed"}
notification_delivery_latency_seconds{type="email|push", percentile="50|95|99"}
notification_retry_count{type="email|push"}
notification_dlq_rate{type="email|push"}
kafka_consumer_lag{topic="reminders"}
database_write_errors_total
```

## Success Criteria

- [ ] All notification attempts logged to database
- [ ] Logs include sufficient context for debugging
- [ ] Correlation IDs enable end-to-end tracing
- [ ] Database writes don't block notification processing
- [ ] Failed database writes trigger alerts
- [ ] Metrics available for monitoring dashboards
- [ ] Log retention policy configured
- [ ] Query performance optimized with indexes

## Integration Points

- **Called By**: All notification delivery skills (`send_push`, `send_email`, `retry_notification`)
- **Outputs To**: Database (notification_logs table)
- **Outputs To**: Metrics system (Prometheus/CloudWatch)
- **Dependencies**: Database connection, metrics collector
