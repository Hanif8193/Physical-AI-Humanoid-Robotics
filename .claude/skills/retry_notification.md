---
name: retry_notification
description: Retries failed notification delivery up to 3 times with exponential backoff
agent: notification-agent
tags: [retry, backoff, resilience]
---

# Retry Notification Skill

## Purpose
Implement resilient retry logic with exponential backoff for failed notification deliveries, ensuring transient failures don't result in lost notifications.

## Responsibilities

1. **Retry Decision Logic**
   - Determine if error is retryable based on error classification
   - Check current retry attempt count against maximum (3)
   - Calculate next retry delay using exponential backoff
   - Skip retry for permanent failures

2. **Backoff Calculation**
   - Implement exponential backoff: attempt 1: 1s, attempt 2: 5s, attempt 3: 15s
   - Add jitter to prevent thundering herd
   - Respect maximum backoff ceiling
   - Log retry scheduling details

3. **Retry Execution**
   - Schedule retry with calculated delay
   - Re-invoke appropriate delivery skill (send_push or send_email)
   - Track retry attempt number in metadata
   - Implement timeout for retry operation

4. **Retry Exhaustion Handling**
   - Move to Dead Letter Queue (DLQ) after 3 failed attempts
   - Log final failure with full context
   - Trigger alert for manual investigation
   - Mark notification as permanently failed

## Configuration Parameters

```python
MAX_RETRY_ATTEMPTS = 3
RETRY_BACKOFF_INTERVALS = [1, 5, 15]  # seconds
RETRY_JITTER_MAX = 0.5  # 50% jitter
DLQ_TOPIC = "reminders-dlq"
ENABLE_CIRCUIT_BREAKER = True
CIRCUIT_BREAKER_THRESHOLD = 5  # failures before opening
```

## Retry Strategy

```python
def calculate_backoff(attempt: int) -> float:
    """
    Exponential backoff with jitter:
    - Attempt 1: ~1s (0.5-1.5s with jitter)
    - Attempt 2: ~5s (2.5-7.5s with jitter)
    - Attempt 3: ~15s (7.5-22.5s with jitter)
    """
    base_delay = RETRY_BACKOFF_INTERVALS[attempt - 1]
    jitter = random.uniform(-RETRY_JITTER_MAX, RETRY_JITTER_MAX)
    return base_delay * (1 + jitter)
```

## Input Schema

```python
{
  "notification": {
    "message_id": "uuid",
    "recipient": "user@example.com",
    "notification_type": "email|push",
    "content": {...}
  },
  "previous_result": {
    "success": False,
    "error_code": "TIMEOUT",
    "retryable": True
  },
  "attempt_number": 1,
  "original_timestamp": "2026-02-06T12:00:00Z"
}
```

## Output Schema

```python
{
  "retry_scheduled": True|False,
  "next_attempt": 2,
  "backoff_delay": 1.23,
  "scheduled_at": "2026-02-06T12:00:01.23Z",
  "moved_to_dlq": False,
  "reason": "Retrying due to TIMEOUT error"
}
```

## Retry Decision Matrix

| Error Type | Attempt 1 | Attempt 2 | Attempt 3 | After 3 |
|------------|-----------|-----------|-----------|---------|
| Timeout | Retry 1s | Retry 5s | Retry 15s | DLQ |
| Rate Limit | Retry 1s | Retry 5s | Retry 15s | DLQ |
| Invalid Token | DLQ | - | - | - |
| Network Error | Retry 1s | Retry 5s | Retry 15s | DLQ |
| Bad Request | DLQ | - | - | - |

## Circuit Breaker Pattern

```python
class CircuitBreaker:
    """
    Prevents cascading failures when downstream service is down:
    - Open: Fast-fail without attempting delivery
    - Half-Open: Allow limited retry attempts
    - Closed: Normal operation
    """
    states = ["CLOSED", "OPEN", "HALF_OPEN"]
    failure_threshold = 5
    timeout = 60  # seconds before attempting half-open
```

## Success Criteria

- [ ] Retry logic correctly identifies retryable errors
- [ ] Exponential backoff properly calculated with jitter
- [ ] Maximum retry attempts enforced (3)
- [ ] Permanent failures immediately moved to DLQ
- [ ] Circuit breaker prevents overwhelming failing services
- [ ] Each retry attempt logged with context
- [ ] DLQ messages include full diagnostic information
- [ ] Alerts triggered for retry exhaustion

## Integration Points

- **Called By**: `send_push_notification`, `send_email_notification` on delivery failure
- **Triggers**: Same delivery skill for retry attempt
- **Triggers**: `log_notification` for each retry attempt
- **Outputs To**: DLQ topic for exhausted retries
- **Dependencies**: Async task scheduler, DLQ configuration
