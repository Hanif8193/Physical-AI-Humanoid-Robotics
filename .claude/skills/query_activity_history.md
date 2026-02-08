---
name: query_activity_history
description: Provides query interface for retrieving user activity history with filtering and pagination
agent: audit-agent
tags: [query, api, history, filtering, pagination]
---

# Query Activity History Skill

## Purpose
Provide a robust query interface for retrieving audit log data with flexible filtering, pagination, and optimized performance for activity history analysis and compliance reporting.

## Responsibilities

1. **Query Interface Design**
   - REST API endpoints for activity history retrieval
   - Support multiple filter criteria combinations
   - Implement pagination for large result sets
   - Return consistent, well-structured responses

2. **Filter Support**
   - **user_id**: All activities by a specific user
   - **task_id**: All operations on a specific task
   - **operation_type**: Filter by create/update/delete/complete
   - **date_range**: Activities within start_date and end_date
   - **correlation_id**: Trace related events across services

3. **Performance Optimization**
   - Leverage database indexes for fast queries
   - Implement result caching for frequently accessed data
   - Use query pagination to limit memory usage
   - Optimize JSONB queries for payload/metadata searches

4. **Response Formatting**
   - Return structured JSON with consistent schema
   - Include pagination metadata (total_count, has_more)
   - Format timestamps in ISO 8601
   - Provide human-readable operation descriptions

## Configuration Parameters

```python
DATABASE_URL = os.getenv("DATABASE_URL")
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 1000
CACHE_TTL_SECONDS = 300  # 5 minutes
ENABLE_QUERY_CACHE = os.getenv("ENABLE_AUDIT_QUERY_CACHE", "false") == "true"
MAX_DATE_RANGE_DAYS = 90
```

## API Endpoints

### 1. Get Activity History by User

```
GET /api/audit/users/{user_id}/activity
```

**Query Parameters:**
- `start_date` (optional): ISO 8601 timestamp
- `end_date` (optional): ISO 8601 timestamp
- `operation_type` (optional): create|update|delete|complete
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Records per page (default: 50, max: 1000)

**Example Request:**
```
GET /api/audit/users/user-456/activity?start_date=2026-01-01T00:00:00Z&end_date=2026-01-31T23:59:59Z&operation_type=create&page=1&page_size=50
```

### 2. Get Activity History by Task

```
GET /api/audit/tasks/{task_id}/history
```

**Query Parameters:**
- `page` (optional): Page number
- `page_size` (optional): Records per page

**Example Request:**
```
GET /api/audit/tasks/task-123/history?page=1&page_size=20
```

### 3. Get Activity by Operation Type

```
GET /api/audit/operations/{operation_type}
```

**Query Parameters:**
- `start_date` (optional)
- `end_date` (optional)
- `user_id` (optional): Filter by specific user
- `page` (optional)
- `page_size` (optional)

**Example Request:**
```
GET /api/audit/operations/delete?start_date=2026-02-01T00:00:00Z&page=1
```

### 4. Get Activity by Correlation ID

```
GET /api/audit/correlation/{correlation_id}
```

**Example Request:**
```
GET /api/audit/correlation/corr-uuid-456
```

## Query Implementation

### User Activity Query

```python
from flask import Flask, request, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/api/audit/users/<user_id>/activity', methods=['GET'])
def get_user_activity(user_id):
    """
    Retrieve activity history for a specific user with optional filters.
    """
    # Parse query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    operation_type = request.args.get('operation_type')
    page = int(request.args.get('page', 1))
    page_size = min(int(request.args.get('page_size', DEFAULT_PAGE_SIZE)), MAX_PAGE_SIZE)

    # Validate date range
    if start_date and end_date:
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        if (end - start).days > MAX_DATE_RANGE_DAYS:
            return jsonify({
                "error": f"Date range cannot exceed {MAX_DATE_RANGE_DAYS} days"
            }), 400

    # Build query
    query = """
        SELECT
            log_id, event_id, task_id, user_id, operation_type, event_type,
            event_timestamp, correlation_id, source, payload, changes, metadata,
            created_at
        FROM audit_logs
        WHERE user_id = %s
    """
    params = [user_id]

    # Add filters
    if start_date:
        query += " AND event_timestamp >= %s"
        params.append(start_date)

    if end_date:
        query += " AND event_timestamp <= %s"
        params.append(end_date)

    if operation_type:
        query += " AND operation_type = %s"
        params.append(operation_type)

    # Count total records (for pagination metadata)
    count_query = f"SELECT COUNT(*) FROM ({query}) AS filtered"

    # Add pagination
    query += " ORDER BY event_timestamp DESC"
    offset = (page - 1) * page_size
    query += f" LIMIT %s OFFSET %s"
    params.extend([page_size, offset])

    # Execute queries
    conn = connection_pool.getconn()
    try:
        with conn.cursor() as cur:
            # Get total count
            cur.execute(count_query, params[:-2])  # Exclude LIMIT/OFFSET params
            total_count = cur.fetchone()[0]

            # Get paginated results
            cur.execute(query, params)
            rows = cur.fetchall()

            # Format results
            activities = [
                {
                    "log_id": row[0],
                    "event_id": row[1],
                    "task_id": row[2],
                    "user_id": row[3],
                    "operation_type": row[4],
                    "event_type": row[5],
                    "event_timestamp": row[6].isoformat(),
                    "correlation_id": row[7],
                    "source": row[8],
                    "payload": row[9],
                    "changes": row[10],
                    "metadata": row[11],
                    "created_at": row[12].isoformat()
                }
                for row in rows
            ]

            # Calculate pagination metadata
            total_pages = (total_count + page_size - 1) // page_size
            has_more = page < total_pages

            return jsonify({
                "success": True,
                "data": activities,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_count": total_count,
                    "total_pages": total_pages,
                    "has_more": has_more
                }
            })

    except Exception as e:
        logger.error(f"Query failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

    finally:
        connection_pool.putconn(conn)
```

### Task History Query

```python
@app.route('/api/audit/tasks/<task_id>/history', methods=['GET'])
def get_task_history(task_id):
    """
    Retrieve complete history of operations on a specific task.
    """
    page = int(request.args.get('page', 1))
    page_size = min(int(request.args.get('page_size', DEFAULT_PAGE_SIZE)), MAX_PAGE_SIZE)

    query = """
        SELECT
            log_id, event_id, user_id, operation_type, event_type,
            event_timestamp, correlation_id, source, payload, changes, metadata
        FROM audit_logs
        WHERE task_id = %s
        ORDER BY event_timestamp ASC
        LIMIT %s OFFSET %s
    """

    offset = (page - 1) * page_size
    params = [task_id, page_size, offset]

    conn = connection_pool.getconn()
    try:
        with conn.cursor() as cur:
            # Get total count
            cur.execute("SELECT COUNT(*) FROM audit_logs WHERE task_id = %s", [task_id])
            total_count = cur.fetchone()[0]

            # Get paginated results
            cur.execute(query, params)
            rows = cur.fetchall()

            history = [
                {
                    "log_id": row[0],
                    "event_id": row[1],
                    "user_id": row[2],
                    "operation_type": row[3],
                    "event_type": row[4],
                    "event_timestamp": row[5].isoformat(),
                    "correlation_id": row[6],
                    "source": row[7],
                    "payload": row[8],
                    "changes": row[9],
                    "metadata": row[10]
                }
                for row in rows
            ]

            return jsonify({
                "success": True,
                "task_id": task_id,
                "data": history,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_count": total_count,
                    "has_more": page * page_size < total_count
                }
            })

    except Exception as e:
        logger.error(f"Query failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

    finally:
        connection_pool.putconn(conn)
```

## Response Schema

### Standard Response Format

```json
{
  "success": true,
  "data": [
    {
      "log_id": 12345,
      "event_id": "evt-uuid-123",
      "task_id": "task-123",
      "user_id": "user-456",
      "operation_type": "create",
      "event_type": "task.created",
      "event_timestamp": "2026-02-06T12:00:00Z",
      "correlation_id": "corr-uuid-456",
      "source": "api-server",
      "payload": {
        "title": "Complete project proposal",
        "priority": "high"
      },
      "changes": null,
      "metadata": {
        "ip_address": "192.168.1.100",
        "user_agent": "Mozilla/5.0..."
      },
      "created_at": "2026-02-06T12:00:00.123Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 50,
    "total_count": 235,
    "total_pages": 5,
    "has_more": true
  }
}
```

### Error Response Format

```json
{
  "success": false,
  "error": "Date range cannot exceed 90 days",
  "error_code": "INVALID_DATE_RANGE"
}
```

## Query Optimization

### Index Usage Verification

```sql
-- Verify index usage with EXPLAIN ANALYZE
EXPLAIN ANALYZE
SELECT * FROM audit_logs
WHERE user_id = 'user-456'
  AND event_timestamp >= '2026-01-01'
  AND event_timestamp <= '2026-01-31'
ORDER BY event_timestamp DESC
LIMIT 50;

-- Should use: idx_audit_logs_user_timestamp
```

### Caching Strategy

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=100)
def get_cached_activity(cache_key: str):
    """
    Cache frequently accessed query results.
    """
    pass

def generate_cache_key(user_id, start_date, end_date, operation_type, page, page_size):
    """
    Generate deterministic cache key from query parameters.
    """
    params = f"{user_id}:{start_date}:{end_date}:{operation_type}:{page}:{page_size}"
    return hashlib.sha256(params.encode()).hexdigest()
```

## Success Criteria

- [ ] All query endpoints return results within 200ms (p95)
- [ ] Pagination works correctly for large result sets
- [ ] Date range filtering accurate to the second
- [ ] Operation type filtering returns correct records
- [ ] Correlation ID queries trace related events
- [ ] Response format consistent across endpoints
- [ ] Error messages informative and actionable
- [ ] Query cache improves performance (when enabled)
- [ ] Database indexes utilized efficiently (verified with EXPLAIN)
- [ ] Maximum page size enforced to prevent memory issues

## Integration Points

- **Called By**: Frontend UI, reporting tools, compliance auditors
- **Queries**: audit_logs table created by `store_logs` skill
- **Returns**: Formatted activity history records
- **Dependencies**: Database connection, query cache (optional)
- **Authentication**: Requires user authentication and authorization
