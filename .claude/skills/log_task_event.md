---
name: log_task_event
description: Logs all task events (create, update, delete, complete) from Kafka for audit trail
agent: audit-agent
tags: [kafka, audit, events, logging]
---

# Log Task Event Skill

## Purpose
Subscribe to the "task-events" Kafka topic, consume all task operation events, validate and enrich them, and prepare them for persistent storage in the audit database.

## Responsibilities

1. **Kafka Event Consumption**
   - Subscribe to "task-events" topic with dedicated consumer group
   - Implement reliable offset management for exactly-once or at-least-once semantics
   - Handle consumer rebalancing and partition assignment
   - Process events in near real-time

2. **Event Type Handling**
   - **task.created**: Capture new task creation with all initial properties
   - **task.updated**: Log field changes with before/after values
   - **task.deleted**: Record deletion with final task state
   - **task.completed**: Log completion with completion timestamp and user

3. **Event Validation & Enrichment**
   - Validate event schema and required fields
   - Extract core metadata: event_id, task_id, user_id, timestamp
   - Enrich with contextual data: IP address, user agent, session ID
   - Parse change deltas for update events
   - Calculate event processing latency

4. **Idempotency Management**
   - Track processed event IDs to prevent duplicate logging
   - Use database-backed idempotency checks
   - Handle event replays gracefully
   - Clean up old idempotency records periodically

## Configuration Parameters

```python
KAFKA_BROKER_URL = os.getenv("KAFKA_BROKER_URL")
KAFKA_TOPIC = "task-events"
CONSUMER_GROUP_ID = "audit-agent-consumer-group"
AUTO_OFFSET_RESET = "earliest"
ENABLE_AUTO_COMMIT = False
MAX_POLL_RECORDS = 500
SESSION_TIMEOUT_MS = 30000
IDEMPOTENCY_CHECK_ENABLED = True
```

## Event Schemas

### task.created Event
```json
{
  "event_id": "evt-uuid-123",
  "event_type": "task.created",
  "event_version": "1.0",
  "timestamp": "2026-02-06T12:00:00Z",
  "correlation_id": "corr-uuid-456",
  "source": "api-server",
  "task": {
    "task_id": "task-123",
    "user_id": "user-456",
    "title": "Complete project proposal",
    "description": "Draft proposal document",
    "priority": "high",
    "due_date": "2026-02-10T17:00:00Z",
    "status": "pending",
    "labels": ["work", "urgent"],
    "assignee_id": "user-456",
    "created_at": "2026-02-06T12:00:00Z",
    "created_by": "user-456"
  },
  "metadata": {
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0...",
    "session_id": "sess-uuid-789"
  }
}
```

### task.updated Event
```json
{
  "event_id": "evt-uuid-124",
  "event_type": "task.updated",
  "event_version": "1.0",
  "timestamp": "2026-02-06T14:30:00Z",
  "correlation_id": "corr-uuid-457",
  "source": "api-server",
  "task": {
    "task_id": "task-123",
    "user_id": "user-456"
  },
  "changes": {
    "priority": {
      "old": "high",
      "new": "medium"
    },
    "due_date": {
      "old": "2026-02-10T17:00:00Z",
      "new": "2026-02-12T17:00:00Z"
    }
  },
  "metadata": {
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0...",
    "session_id": "sess-uuid-789",
    "updated_by": "user-456"
  }
}
```

### task.completed Event
```json
{
  "event_id": "evt-uuid-125",
  "event_type": "task.completed",
  "event_version": "1.0",
  "timestamp": "2026-02-08T16:45:00Z",
  "correlation_id": "corr-uuid-458",
  "source": "api-server",
  "task": {
    "task_id": "task-123",
    "user_id": "user-456",
    "completed_at": "2026-02-08T16:45:00Z",
    "completed_by": "user-456"
  },
  "metadata": {
    "ip_address": "192.168.1.101",
    "user_agent": "Mobile App v2.1",
    "session_id": "sess-uuid-790"
  }
}
```

### task.deleted Event
```json
{
  "event_id": "evt-uuid-126",
  "event_type": "task.deleted",
  "event_version": "1.0",
  "timestamp": "2026-02-09T10:15:00Z",
  "correlation_id": "corr-uuid-459",
  "source": "api-server",
  "task": {
    "task_id": "task-123",
    "user_id": "user-456",
    "deleted_at": "2026-02-09T10:15:00Z",
    "deleted_by": "user-456",
    "final_state": {
      "title": "Complete project proposal",
      "status": "completed",
      "completed_at": "2026-02-08T16:45:00Z"
    }
  },
  "metadata": {
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0...",
    "session_id": "sess-uuid-791",
    "deletion_reason": "user_requested"
  }
}
```

## Event Processing Flow

```python
from kafka import KafkaConsumer
import json

def process_task_events():
    """
    Main event processing loop for audit logging.
    """
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BROKER_URL,
        group_id=CONSUMER_GROUP_ID,
        auto_offset_reset=AUTO_OFFSET_RESET,
        enable_auto_commit=False,
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )

    for message in consumer:
        try:
            event = message.value
            event_id = event.get("event_id")

            # Idempotency check
            if is_already_processed(event_id):
                logger.info(f"Event {event_id} already processed, skipping")
                consumer.commit()
                continue

            # Validate event schema
            if not validate_event_schema(event):
                logger.error(f"Invalid event schema: {event_id}")
                send_to_dlq(event, "schema_validation_failed")
                consumer.commit()
                continue

            # Extract and enrich event data
            audit_record = extract_audit_data(event)

            # Store in database (via store_logs skill)
            store_result = store_audit_log(audit_record)

            if store_result["success"]:
                # Mark as processed
                mark_processed(event_id)
                consumer.commit()
                logger.info(f"Successfully logged event {event_id}")
            else:
                logger.error(f"Failed to store event {event_id}: {store_result['error']}")
                # Retry logic or DLQ

        except Exception as e:
            logger.error(f"Error processing event: {e}")
            # Handle error, potentially send to DLQ
```

## Idempotency Table Schema

```sql
CREATE TABLE audit_event_idempotency (
    event_id VARCHAR(255) PRIMARY KEY,
    task_id VARCHAR(255),
    event_type VARCHAR(50),
    processed_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_processed_at (processed_at)
);

-- Cleanup old idempotency records (retain last 30 days)
CREATE INDEX idx_cleanup ON audit_event_idempotency(processed_at)
WHERE processed_at < NOW() - INTERVAL '30 days';
```

## Output Schema

```python
{
  "event_id": "evt-uuid-123",
  "event_type": "task.created",
  "task_id": "task-123",
  "user_id": "user-456",
  "operation_type": "create",
  "timestamp": "2026-02-06T12:00:00Z",
  "correlation_id": "corr-uuid-456",
  "payload": {
    "title": "Complete project proposal",
    "priority": "high",
    ...
  },
  "changes": None,  # For update events
  "metadata": {
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0...",
    "session_id": "sess-uuid-789",
    "source": "api-server"
  },
  "processed_at": "2026-02-06T12:00:00.123Z"
}
```

## Error Handling

**Retryable Errors:**
- Kafka broker temporarily unavailable
- Database connection timeout
- Transient network issues

**Non-Retryable Errors:**
- Malformed event schema
- Missing required fields
- Invalid data types
- Unknown event type

**Dead Letter Queue Strategy:**
- Events that fail validation go to DLQ immediately
- Events that fail storage after 3 retries go to DLQ
- Include original event + error details in DLQ message

## Success Criteria

- [ ] Consumer successfully subscribes to task-events topic
- [ ] All event types (create, update, delete, complete) processed
- [ ] Event schema validation catches malformed events
- [ ] Idempotency prevents duplicate audit records
- [ ] Event enrichment adds contextual metadata
- [ ] Failed events sent to DLQ with error details
- [ ] Consumer lag stays within acceptable limits (<1000 messages)
- [ ] Processing latency < 100ms per event (p95)

## Integration Points

- **Triggered By**: Kafka task-events topic
- **Triggers**: `store_logs` skill to persist audit records
- **Dependencies**: Kafka broker, idempotency database
- **Outputs**: Enriched audit records ready for storage
- **Consumers**: query_activity_history uses stored logs
