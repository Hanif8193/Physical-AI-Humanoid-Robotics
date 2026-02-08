---
name: broadcast_task_updates
description: Broadcasts task update events via WebSocket to all connected clients in real-time
agent: realtime-sync-agent
tags: [websocket, broadcast, real-time, task-updates]
---

# Broadcast Task Updates Skill

## Purpose
Efficiently broadcast task change events received from Kafka to all connected WebSocket clients, ensuring low-latency real-time updates across the application.

## Responsibilities

1. **WebSocket Connection Management**
   - Maintain an active registry of connected WebSocket clients
   - Track client connection metadata (connection ID, user ID, session info)
   - Clean up stale or disconnected clients automatically
   - Implement connection health checks via heartbeat mechanism

2. **Message Broadcasting**
   - Serialize task update events into client-friendly JSON format
   - Broadcast messages to all active WebSocket connections
   - Use non-blocking writes to prevent slow clients from blocking fast clients
   - Implement per-client message buffers with overflow protection

3. **Client Filtering**
   - Support user-specific filtering (only send updates relevant to user)
   - Implement room/channel-based broadcasting for multi-tenancy
   - Handle authorization checks before broadcasting sensitive task data
   - Support client-side subscription preferences

4. **Performance Optimization**
   - Batch multiple updates when appropriate to reduce overhead
   - Implement message deduplication to prevent redundant broadcasts
   - Use efficient serialization to minimize payload size
   - Monitor broadcast latency and emit performance metrics

## Configuration Parameters

```python
WEBSOCKET_PORT = os.getenv("WEBSOCKET_PORT", "8080")
WEBSOCKET_PATH = "/ws/tasks"
CLIENT_BUFFER_SIZE = int(os.getenv("WS_CLIENT_BUFFER_SIZE", "100"))
HEARTBEAT_INTERVAL_SEC = int(os.getenv("WS_HEARTBEAT_INTERVAL", "30"))
MAX_BROADCAST_LATENCY_MS = int(os.getenv("WS_MAX_LATENCY", "100"))
ENABLE_CLIENT_FILTERING = os.getenv("WS_ENABLE_FILTERING", "true") == "true"
```

## Event Schema (Broadcasted to Clients)

```json
{
  "event_id": "evt-uuid-123",
  "event_type": "task.updated",
  "sequence_number": 12345,
  "timestamp": "2026-02-06T12:00:01Z",
  "task": {
    "task_id": "task-890",
    "user_id": "user-123",
    "title": "Updated task title",
    "description": "Updated description",
    "status": "in_progress",
    "priority": "high",
    "due_date": "2026-02-10T10:00:00Z",
    "updated_at": "2026-02-06T12:00:00Z",
    "updated_by": "user-456"
  },
  "changes": {
    "status": {"old": "pending", "new": "in_progress"},
    "priority": {"old": "medium", "new": "high"}
  },
  "metadata": {
    "partition": 2,
    "offset": 67890,
    "source": "realtime-sync-agent"
  }
}
```

## Broadcasting Strategy

```python
from typing import Dict, Set
import asyncio
import json
from websockets.server import WebSocketServerProtocol

class WebSocketBroadcaster:
    def __init__(self):
        self.clients: Dict[str, WebSocketServerProtocol] = {}
        self.user_clients: Dict[str, Set[str]] = {}

    async def register_client(
        self,
        client_id: str,
        websocket: WebSocketServerProtocol,
        user_id: str
    ):
        """Register a new WebSocket client."""
        self.clients[client_id] = websocket
        if user_id not in self.user_clients:
            self.user_clients[user_id] = set()
        self.user_clients[user_id].add(client_id)

    async def unregister_client(self, client_id: str):
        """Remove a disconnected client."""
        if client_id in self.clients:
            del self.clients[client_id]
        # Clean up user_clients mapping
        for user_id, client_set in self.user_clients.items():
            client_set.discard(client_id)

    async def broadcast_task_update(
        self,
        event: dict,
        target_user_id: str = None
    ):
        """
        Broadcast task update to relevant clients.
        If target_user_id is provided, only send to that user's connections.
        """
        message = json.dumps(event)

        # Determine target clients
        if target_user_id and ENABLE_CLIENT_FILTERING:
            target_clients = [
                self.clients[cid]
                for cid in self.user_clients.get(target_user_id, [])
                if cid in self.clients
            ]
        else:
            target_clients = list(self.clients.values())

        # Broadcast to all target clients concurrently
        if target_clients:
            await asyncio.gather(
                *[self._send_to_client(client, message) for client in target_clients],
                return_exceptions=True
            )

    async def _send_to_client(
        self,
        client: WebSocketServerProtocol,
        message: str
    ):
        """Send message to a single client with error handling."""
        try:
            await asyncio.wait_for(
                client.send(message),
                timeout=MAX_BROADCAST_LATENCY_MS / 1000
            )
        except asyncio.TimeoutError:
            logger.warning(f"Broadcast timeout for client {client.id}")
        except Exception as e:
            logger.error(f"Failed to send to client {client.id}: {e}")
            # Mark client for removal
            await self.unregister_client(client.id)
```

## Kafka Consumer Integration

```python
from kafka import KafkaConsumer
import json

async def consume_and_broadcast():
    """Main loop: consume from Kafka and broadcast via WebSocket."""
    consumer = KafkaConsumer(
        'task-updates',
        bootstrap_servers=KAFKA_BROKER_URL,
        group_id='realtime-sync-group',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='latest',
        enable_auto_commit=False
    )

    broadcaster = WebSocketBroadcaster()

    for message in consumer:
        try:
            event = message.value

            # Extract target user from event
            target_user_id = event.get('task', {}).get('user_id')

            # Broadcast to WebSocket clients
            await broadcaster.broadcast_task_update(
                event=event,
                target_user_id=target_user_id
            )

            # Commit offset after successful broadcast
            consumer.commit()

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            # Continue processing, don't crash the consumer
```

## Error Handling

**Slow Client Handling:**
- Use non-blocking sends with timeout
- Drop slow clients that exceed buffer limits
- Log dropped connections with metrics

**Connection Failures:**
- Catch WebSocket exceptions and remove dead connections
- Implement automatic cleanup of stale connections
- Use heartbeat/ping-pong to detect dead connections proactively

**Serialization Errors:**
- Validate event schema before broadcasting
- Log malformed events and skip broadcasting
- Emit error metrics for monitoring

**Backpressure:**
- Monitor client buffer usage
- Implement flow control to prevent memory overflow
- Alert when broadcast lag exceeds threshold

## Success Criteria

- [ ] WebSocket server accepts client connections
- [ ] Client registry maintained with accurate connection state
- [ ] Task update events broadcasted to all active clients
- [ ] Non-blocking sends prevent slow clients from blocking fast ones
- [ ] User-specific filtering works correctly (if enabled)
- [ ] Stale connections cleaned up automatically
- [ ] Broadcast latency stays below MAX_BROADCAST_LATENCY_MS
- [ ] Error rates and broadcast metrics logged
- [ ] Heartbeat mechanism detects dead connections

## Monitoring Metrics

```python
# Key metrics to emit
- websocket.connections.active (gauge)
- websocket.broadcast.latency (histogram)
- websocket.broadcast.errors (counter)
- websocket.messages.sent (counter)
- websocket.clients.dropped (counter)
- websocket.buffer.overflow (counter)
```

## Integration Points

- **Called By**: Main Kafka consumer loop after receiving task update events
- **Consumes From**: Kafka topic "task-updates"
- **Broadcasts To**: All connected WebSocket clients (or filtered subset)
- **Dependencies**: WebSocket server, Kafka consumer, client registry
- **Related Skills**: `handle_reconnects`, `maintain_order`, `sync_all_clients`
