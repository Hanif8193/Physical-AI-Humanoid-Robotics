---
name: create_next_task
description: Automatically creates the next occurrence of a recurring task with calculated due date
agent: recurring-task-automator
tags: [task-creation, recurrence, scheduling, automation]
---

# Create Next Task Skill

## Purpose
Automatically generate the next occurrence of a recurring task by calculating the next due date, preserving task template properties, and creating a new task instance in the database.

## Responsibilities

1. **Next Occurrence Date Calculation**
   - Apply recurrence rules to calculate next due date
   - Support multiple patterns: daily, weekly, monthly, yearly, custom cron
   - Handle timezone conversions correctly
   - Account for edge cases (month-end, leap years, DST transitions)

2. **Task Template Preservation**
   - Copy task properties from parent template or previous occurrence
   - Preserve: title, description, priority, labels, assignee
   - Update: due_date, occurrence_number, created_at
   - Generate new unique task_id

3. **Parent-Child Relationship Management**
   - Link new task to parent recurring template
   - Track occurrence sequence number
   - Maintain reference to previous occurrence
   - Store recurrence metadata with new task

4. **Database Persistence**
   - Insert new task record into tasks table
   - Use transactions to ensure atomicity
   - Handle constraint violations (duplicate IDs)
   - Validate foreign key relationships

## Configuration Parameters

```python
DATABASE_URL = os.getenv("DATABASE_URL")
TASKS_TABLE = "tasks"
DEFAULT_TIMEZONE = os.getenv("USER_TIMEZONE", "UTC")
MAX_FUTURE_OCCURRENCES = 1  # How many future occurrences to create at once
```

## Recurrence Calculation Logic

```python
from dateutil.relativedelta import relativedelta
from datetime import datetime, timezone

def calculate_next_due_date(
    last_due_date: datetime,
    pattern: str,
    frequency: int,
    day_of_week: Optional[int] = None,
    day_of_month: Optional[int] = None,
    user_timezone: str = "UTC"
) -> datetime:
    """
    Calculate next occurrence date based on recurrence pattern.

    Patterns:
    - daily: Add frequency days
    - weekly: Add frequency weeks (on specific day_of_week if provided)
    - monthly: Add frequency months (on specific day_of_month if provided)
    - yearly: Add frequency years
    - custom: Use cron expression (if provided)
    """
    tz = timezone(user_timezone)
    base_date = last_due_date.astimezone(tz)

    if pattern == "daily":
        return base_date + timedelta(days=frequency)

    elif pattern == "weekly":
        next_date = base_date + timedelta(weeks=frequency)
        if day_of_week is not None:
            # Adjust to specific day of week (0=Monday, 6=Sunday)
            days_ahead = (day_of_week - next_date.weekday()) % 7
            next_date += timedelta(days=days_ahead)
        return next_date

    elif pattern == "monthly":
        next_date = base_date + relativedelta(months=frequency)
        if day_of_month is not None:
            # Handle month-end edge cases
            try:
                next_date = next_date.replace(day=day_of_month)
            except ValueError:
                # Day doesn't exist in month (e.g., Feb 31)
                # Use last day of month instead
                next_date = next_date.replace(day=1) + relativedelta(months=1) - timedelta(days=1)
        return next_date

    elif pattern == "yearly":
        return base_date + relativedelta(years=frequency)

    else:
        raise ValueError(f"Unsupported recurrence pattern: {pattern}")
```

## Input Schema

```python
{
  "parent_task": {
    "task_id": "task-789",
    "user_id": "user-123",
    "title": "Weekly team meeting",
    "description": "Discuss project updates",
    "priority": "medium",
    "labels": ["meeting", "team"],
    "assignee_id": "user-123",
    "last_due_date": "2026-02-03T10:00:00Z"
  },
  "recurring_config": {
    "pattern": "weekly",
    "frequency": 1,
    "day_of_week": 0,  # Monday
    "current_occurrence": 12,
    "parent_task_id": "recurring-template-456"
  },
  "user_timezone": "America/New_York"
}
```

## Output Schema

```python
{
  "success": True|False,
  "new_task": {
    "task_id": "task-new-890",
    "user_id": "user-123",
    "title": "Weekly team meeting",
    "description": "Discuss project updates",
    "priority": "medium",
    "due_date": "2026-02-10T10:00:00Z",
    "status": "pending",
    "recurring": {
      "enabled": true,
      "pattern": "weekly",
      "frequency": 1,
      "current_occurrence": 13,
      "parent_task_id": "recurring-template-456",
      "previous_occurrence_id": "task-789"
    },
    "created_at": "2026-02-06T12:00:00Z",
    "created_by": "system:recurring-automator"
  },
  "error": None|"Database constraint violation"
}
```

## Database Schema Integration

```sql
-- Tasks table should support recurring task fields
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS recurring_enabled BOOLEAN DEFAULT FALSE;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS recurring_pattern VARCHAR(50);
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS recurring_frequency INTEGER;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS recurring_day_of_week INTEGER;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS recurring_day_of_month INTEGER;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS recurring_end_date TIMESTAMP;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS recurring_max_occurrences INTEGER;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS recurring_current_occurrence INTEGER DEFAULT 1;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS recurring_parent_id VARCHAR(255);
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS recurring_previous_id VARCHAR(255);

CREATE INDEX idx_recurring_parent ON tasks(recurring_parent_id);
CREATE INDEX idx_recurring_enabled ON tasks(recurring_enabled) WHERE recurring_enabled = TRUE;
```

## Edge Cases to Handle

1. **Month-End Edge Case**: Task due on 31st when next month has 30 days
   - Solution: Use last day of month instead

2. **Daylight Saving Time**: Task due at 2:00 AM during DST transition
   - Solution: Normalize to user's timezone and handle ambiguous times

3. **Leap Year**: Task due on Feb 29th
   - Solution: For non-leap years, use Feb 28th or Mar 1st based on config

4. **Skipped Occurrences**: What if 3 occurrences were missed?
   - Solution: Create only next occurrence (not backfilling)

5. **Concurrent Creation**: Two workers try to create same next occurrence
   - Solution: Use database unique constraint + idempotency check

## Success Criteria

- [ ] Next due date calculated correctly for all recurrence patterns
- [ ] Task template properties preserved accurately
- [ ] Occurrence sequence number incremented
- [ ] Parent-child relationships properly established
- [ ] Timezone handling correct (no date shifts)
- [ ] Database transaction ensures atomicity
- [ ] Edge cases handled (month-end, leap year, DST)
- [ ] Concurrent creation prevented via constraints
- [ ] New task ID is unique and properly generated

## Integration Points

- **Called By**: `detect_completed_tasks` when recurring task identified
- **Triggers**: `publish_new_task` with created task data
- **Triggers**: `log_task_creation` for audit trail
- **Dependencies**: Database (tasks table), timezone library
- **Outputs**: New task record in database
