---
name: detect_completed_tasks
description: Detects completed recurring tasks from Kafka task-events and identifies tasks requiring next occurrence
agent: recurring-task-automator
tags: [kafka, detection, recurring, events]
---

# Detect Completed Tasks Skill

## Purpose
Subscribe to the "task-events" Kafka topic, filter for task completion events, and identify recurring tasks that require automatic creation of their next occurrence.

## Responsibilities

1. **Kafka Event Subscription**
   - Subscribe to "task-events" topic with appropriate consumer group
   - Configure offset management for at-least-once delivery
   - Handle partition rebalancing without message loss
   - Implement graceful consumer lifecycle management

2. **Event Filtering**
   - Filter events by type to identify "task.completed" events
   - Validate event schema and required fields
   - Extract task metadata from completion events
   - Deserialize event payloads reliably

3. **Recurring Task Detection**
   - Check if completed task has recurring configuration
   - Validate recurring task metadata (pattern, frequency, end_date)
   - Determine if next occurrence should be created
   - Check termination conditions (end date, max occurrences)

4. **Idempotency Management**
   - Track processed task completion events by event ID
   - Prevent duplicate processing using database-backed idempotency keys
   - Handle retry scenarios without creating duplicate tasks
   - Implement efficient idempotency key cleanup

## Configuration Parameters

```python
KAFKA_BROKER_URL = os.getenv("KAFKA_BROKER_URL")
KAFKA_TOPIC = "task-events"
CONSUMER_GROUP_ID = "recurring-task-automator-group"
AUTO_OFFSET_RESET = "earliest"
ENABLE_AUTO_COMMIT = False
IDEMPOTENCY_TABLE = "recurring_task_processed_events"
```

## Expected Event Schema

```json
{
  "event_id": "evt-uuid-123",
  "event_type": "task.completed",
  "timestamp": "2026-02-06T12:00:00Z",
  "correlation_id": "corr-uuid-456",
  "task": {
    "task_id": "task-789",
    "user_id": "user-123",
    "title": "Weekly team meeting",
    "completed_at": "2026-02-06T12:00:00Z",
    "recurring": {
      "enabled": true,
      "pattern": "weekly",
      "frequency": 1,
      "day_of_week": "monday",
      "end_date": "2026-12-31",
      "max_occurrences": 52,
      "current_occurrence": 12,
      "parent_task_id": "recurring-template-456"
    }
  }
}
```

## Detection Logic

```python
def should_create_next_occurrence(task_data: dict) -> bool:
    """
    Determines if a completed task requires next occurrence creation.

    Returns True if:
    - Task has recurring.enabled = true
    - End date not reached (or no end date set)
    - Max occurrences not exceeded (or no max set)
    - Task was actually completed (not cancelled/deleted)
    """
    if not task_data.get("recurring", {}).get("enabled"):
        return False

    recurring = task_data["recurring"]

    # Check end date
    if recurring.get("end_date"):
        end_date = parse_datetime(recurring["end_date"])
        if datetime.now(UTC) > end_date:
            return False

    # Check max occurrences
    if recurring.get("max_occurrences"):
        current = recurring.get("current_occurrence", 0)
        if current >= recurring["max_occurrences"]:
            return False

    return True
```

## Output Schema

```python
{
  "is_recurring": True|False,
  "requires_next_occurrence": True|False,
  "task_data": {
    "task_id": "task-789",
    "user_id": "user-123",
    "recurring_config": {...},
    "completed_at": "2026-02-06T12:00:00Z"
  },
  "termination_reason": None|"end_date_reached"|"max_occurrences_exceeded",
  "event_id": "evt-uuid-123",
  "correlation_id": "corr-uuid-456"
}
```

## Idempotency Schema

```sql
CREATE TABLE recurring_task_processed_events (
    event_id VARCHAR(255) PRIMARY KEY,
    task_id VARCHAR(255) NOT NULL,
    processed_at TIMESTAMP DEFAULT NOW(),
    next_task_created BOOLEAN DEFAULT FALSE,
    next_task_id VARCHAR(255),
    INDEX idx_task_id (task_id),
    INDEX idx_processed_at (processed_at)
);
```

## Edge Cases to Handle

1. **Partial Completion**: Tasks marked as "partially completed" should not trigger next occurrence
2. **Cancelled Recurring Tasks**: Respect cancellation flags to stop future occurrences
3. **Modified Recurrence Rules**: Detect if recurrence pattern was changed and apply new rules
4. **Timezone Handling**: Ensure completion timestamps respect user's timezone
5. **Duplicate Events**: Same task completion event published multiple times
6. **Out-of-Order Events**: Completion events arriving after deletion events

## Success Criteria

- [ ] Successfully subscribes to task-events topic
- [ ] Correctly filters for task.completed events
- [ ] Accurately detects recurring task configuration
- [ ] Properly evaluates termination conditions
- [ ] Implements idempotency to prevent duplicate processing
- [ ] Handles malformed events without crashing
- [ ] Logs detection decisions with context
- [ ] Consumer handles rebalancing gracefully

## Integration Points

- **Triggered By**: Kafka task-events topic (task.completed events)
- **Triggers**: `create_next_task` when recurring task detected
- **Dependencies**: Kafka broker, idempotency database table
- **Outputs**: Detected recurring task metadata for processing
