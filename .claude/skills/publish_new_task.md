---
name: publish_new_task
description: Publishes new task creation events to Kafka topic "task-events" for downstream consumers
agent: recurring-task-automator
tags: [kafka, publisher, events, task-events]
---

# Publish New Task Skill

## Purpose
Publish well-formed task creation events to the "task-events" Kafka topic to notify other services (notifications, real-time sync, audit) about newly created recurring task occurrences.

## Responsibilities

1. **Event Construction**
   - Build standardized task.created event payload
   - Include all relevant task metadata
   - Add correlation IDs for distributed tracing
   - Embed recurring task context

2. **Kafka Publishing**
   - Publish to "task-events" topic
   - Configure producer for reliability (acks=all)
   - Handle producer acknowledgments
   - Implement retry logic for transient failures

3. **Transactional Publishing**
   - Coordinate with database writes using outbox pattern or transactions
   - Ensure exactly-once semantics where possible
   - Handle partial failures (DB success, Kafka failure)
   - Implement compensating actions if needed

4. **Event Ordering**
   - Use task_id as partition key for ordered processing
   - Ensure events for same task go to same partition
   - Maintain causal ordering of task events

## Configuration Parameters

```python
KAFKA_BROKER_URL = os.getenv("KAFKA_BROKER_URL")
KAFKA_TOPIC = "task-events"
PRODUCER_ACKS = "all"  # Wait for all replicas
PRODUCER_RETRIES = 3
PRODUCER_TIMEOUT_MS = 30000
ENABLE_IDEMPOTENCE = True
USE_TRANSACTIONAL_PRODUCER = os.getenv("KAFKA_TRANSACTIONS_ENABLED", "false") == "true"
```

## Event Schema

```json
{
  "event_id": "evt-uuid-new-123",
  "event_type": "task.created",
  "event_version": "1.0",
  "timestamp": "2026-02-06T12:00:01Z",
  "correlation_id": "corr-uuid-456",
  "source": "recurring-task-automator",
  "task": {
    "task_id": "task-new-890",
    "user_id": "user-123",
    "title": "Weekly team meeting",
    "description": "Discuss project updates",
    "priority": "medium",
    "due_date": "2026-02-10T10:00:00Z",
    "status": "pending",
    "labels": ["meeting", "team"],
    "assignee_id": "user-123",
    "created_at": "2026-02-06T12:00:00Z",
    "created_by": "system:recurring-automator",
    "recurring": {
      "enabled": true,
      "pattern": "weekly",
      "frequency": 1,
      "current_occurrence": 13,
      "parent_task_id": "recurring-template-456",
      "previous_occurrence_id": "task-789",
      "auto_created": true
    }
  },
  "metadata": {
    "triggered_by_event_id": "evt-uuid-123",
    "triggered_by_task_id": "task-789",
    "automation_rule": "weekly_recurrence"
  }
}
```

## Publishing Strategy

```python
from kafka import KafkaProducer
import json

def publish_task_created_event(
    task_data: dict,
    correlation_id: str,
    triggered_by_event_id: str
) -> dict:
    """
    Publish task.created event to Kafka with proper error handling.
    """
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER_URL,
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        acks='all',
        retries=3,
        enable_idempotence=True
    )

    event = {
        "event_id": str(uuid.uuid4()),
        "event_type": "task.created",
        "event_version": "1.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "correlation_id": correlation_id,
        "source": "recurring-task-automator",
        "task": task_data,
        "metadata": {
            "triggered_by_event_id": triggered_by_event_id,
            "triggered_by_task_id": task_data.get("recurring", {}).get("previous_occurrence_id"),
            "automation_rule": f"{task_data['recurring']['pattern']}_recurrence"
        }
    }

    try:
        # Use task_id as partition key for ordering
        future = producer.send(
            topic=KAFKA_TOPIC,
            value=event,
            key=task_data["task_id"].encode('utf-8')
        )

        # Wait for acknowledgment
        record_metadata = future.get(timeout=30)

        return {
            "success": True,
            "event_id": event["event_id"],
            "partition": record_metadata.partition,
            "offset": record_metadata.offset
        }

    except Exception as e:
        logger.error(f"Failed to publish task.created event: {e}")
        return {
            "success": False,
            "error": str(e),
            "event_id": event["event_id"]
        }

    finally:
        producer.flush()
        producer.close()
```

## Transactional Publishing (Outbox Pattern)

```sql
-- Outbox table for transactional event publishing
CREATE TABLE event_outbox (
    id SERIAL PRIMARY KEY,
    event_id VARCHAR(255) UNIQUE NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    topic VARCHAR(100) NOT NULL,
    partition_key VARCHAR(255),
    payload JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    published_at TIMESTAMP,
    published BOOLEAN DEFAULT FALSE,
    retry_count INTEGER DEFAULT 0,
    last_error TEXT,
    INDEX idx_published (published, created_at) WHERE published = FALSE
);
```

## Input Schema

```python
{
  "task_data": {
    "task_id": "task-new-890",
    "user_id": "user-123",
    ...
  },
  "correlation_id": "corr-uuid-456",
  "triggered_by_event_id": "evt-uuid-123"
}
```

## Output Schema

```python
{
  "success": True|False,
  "event_id": "evt-uuid-new-123",
  "partition": 2,
  "offset": 12345,
  "timestamp": "2026-02-06T12:00:01Z",
  "error": None|"Producer timeout exceeded"
}
```

## Error Handling

**Retryable Errors:**
- Network timeouts
- Broker temporarily unavailable
- Leader election in progress
- Message size exceeds limit (should not happen with proper validation)

**Permanent Failures:**
- Invalid topic name
- Serialization errors
- Message exceeds configured max size
- Authorization failures

**Compensating Actions:**
- If publish fails after DB write: Store in outbox table for later retry
- If DB write fails after publish: Log as audit gap (requires reconciliation)
- Implement background worker to process outbox table periodically

## Success Criteria

- [ ] Event schema conforms to standard format
- [ ] Correlation IDs properly propagated
- [ ] Producer configured for reliability (acks=all)
- [ ] Partition key ensures ordered delivery
- [ ] Idempotence prevents duplicate events
- [ ] Transactional guarantees with DB writes (if enabled)
- [ ] Retry logic handles transient failures
- [ ] Failed events logged for manual intervention
- [ ] Event includes all necessary metadata for consumers

## Integration Points

- **Called By**: `create_next_task` after successful task creation
- **Publishes To**: Kafka topic "task-events"
- **Consumed By**:
  - notification-agent (for user notifications)
  - realtime-sync-agent (for WebSocket updates)
  - audit-agent (for audit logging)
- **Dependencies**: Kafka producer, correlation ID from upstream event
- **Fallback**: Outbox table for guaranteed eventual publishing
