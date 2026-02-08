---
name: handle_reconnects
description: Manages WebSocket client reconnections with event replay and duplicate detection
agent: realtime-sync-agent
tags: [websocket, reconnection, replay, reliability]
---

# Handle Reconnects Skill

## Purpose
Provide robust client reconnection handling with event replay capabilities, ensuring clients don't miss updates during temporary disconnections and can seamlessly resume from where they left off.

## Responsibilities

1. **Reconnection Detection**
   - Identify returning clients using connection tokens or session IDs
   - Distinguish between new connections and reconnections
   - Track client connection history and last known state
   - Implement secure reconnection authentication

2. **Event Replay**
   - Maintain a time-bounded buffer of recent events for replay
   - Support "resume from sequence number" protocol
   - Replay missed events in correct order
   - Rate-limit replay to prevent overwhelming reconnecting clients

3. **State Synchronization**
   - Provide full state snapshot for clients disconnected beyond buffer window
   - Support incremental updates vs. full sync based on disconnect duration
   - Validate client state checksum to detect desynchronization
   - Implement efficient diff-based sync when possible

4. **Duplicate Prevention**
   - Use event IDs to enable client-side deduplication
   - Track which events were acknowledged by clients
   - Implement idempotent event processing guidance for clients
   - Log duplicate delivery statistics for monitoring

## Configuration Parameters

```python
RECONNECT_TOKEN_TTL_SEC = int(os.getenv("RECONNECT_TOKEN_TTL", "3600"))
EVENT_REPLAY_BUFFER_SIZE = int(os.getenv("EVENT_REPLAY_BUFFER_SIZE", "1000"))
EVENT_REPLAY_MAX_AGE_HOURS = int(os.getenv("EVENT_REPLAY_MAX_AGE_HOURS", "24"))
REPLAY_RATE_LIMIT_PER_SEC = int(os.getenv("REPLAY_RATE_LIMIT", "50"))
FULL_SYNC_THRESHOLD_MIN = int(os.getenv("FULL_SYNC_THRESHOLD_MIN", "60"))
ENABLE_STATE_CHECKSUM = os.getenv("ENABLE_STATE_CHECKSUM", "true") == "true"
```

## Reconnection Protocol

### Client Reconnection Handshake

```json
// Client sends on reconnection
{
  "type": "reconnect",
  "reconnect_token": "token-abc-123",
  "last_sequence_number": 12345,
  "last_event_id": "evt-uuid-last",
  "client_id": "client-uuid-456",
  "state_checksum": "sha256-hash-of-client-state"
}

// Server response
{
  "type": "reconnect_ack",
  "status": "success",
  "replay_required": true,
  "replay_count": 42,
  "replay_mode": "incremental|full",
  "new_reconnect_token": "token-def-789"
}
```

## Reconnection Handling Strategy

```python
from typing import Dict, Optional
import time
import hashlib

class ReconnectionManager:
    def __init__(self, event_order_manager):
        self.event_order_manager = event_order_manager

        # Track client reconnection state
        self.client_sessions: Dict[str, dict] = {}
        self.reconnect_tokens: Dict[str, str] = {}  # token -> client_id

    async def handle_reconnection(
        self,
        websocket,
        reconnect_data: dict
    ) -> dict:
        """
        Handle client reconnection with event replay.
        """
        client_id = reconnect_data.get("client_id")
        last_seq = reconnect_data.get("last_sequence_number")
        reconnect_token = reconnect_data.get("reconnect_token")

        # Validate reconnection token
        if not self._validate_reconnect_token(reconnect_token, client_id):
            return {
                "type": "reconnect_ack",
                "status": "invalid_token",
                "error": "Invalid or expired reconnect token"
            }

        # Check if full sync is needed (client disconnected too long)
        if self._needs_full_sync(client_id):
            return await self._perform_full_sync(websocket, client_id)

        # Perform incremental replay
        return await self._perform_incremental_replay(
            websocket,
            client_id,
            last_seq
        )

    def _validate_reconnect_token(
        self,
        token: str,
        client_id: str
    ) -> bool:
        """Validate reconnection token."""
        if token not in self.reconnect_tokens:
            return False

        if self.reconnect_tokens[token] != client_id:
            return False

        # Check token expiry
        session = self.client_sessions.get(client_id, {})
        token_created = session.get("token_created_at", 0)

        if time.time() - token_created > RECONNECT_TOKEN_TTL_SEC:
            return False

        return True

    def _needs_full_sync(self, client_id: str) -> bool:
        """
        Determine if client needs full state sync vs. incremental replay.
        """
        session = self.client_sessions.get(client_id)

        if not session:
            return True  # New client, needs full sync

        last_connected = session.get("last_connected_at", 0)
        disconnect_duration_min = (time.time() - last_connected) / 60

        if disconnect_duration_min > FULL_SYNC_THRESHOLD_MIN:
            return True

        return False

    async def _perform_incremental_replay(
        self,
        websocket,
        client_id: str,
        last_sequence_number: int
    ) -> dict:
        """
        Replay events missed during disconnect.
        """
        # Get missed events from buffer
        missed_events = self.event_order_manager.get_events_since_sequence(
            partition=0,  # TODO: Handle multiple partitions
            since_sequence=last_sequence_number
        )

        replay_count = len(missed_events)

        if replay_count > EVENT_REPLAY_BUFFER_SIZE:
            # Too many missed events, fall back to full sync
            logger.warning(
                f"Client {client_id} missed {replay_count} events, "
                f"exceeding buffer. Performing full sync."
            )
            return await self._perform_full_sync(websocket, client_id)

        # Send replay acknowledgment
        ack_response = {
            "type": "reconnect_ack",
            "status": "success",
            "replay_required": True,
            "replay_count": replay_count,
            "replay_mode": "incremental",
            "new_reconnect_token": self._generate_reconnect_token(client_id)
        }
        await websocket.send(json.dumps(ack_response))

        # Replay events with rate limiting
        for i, event in enumerate(missed_events):
            await websocket.send(json.dumps({
                "type": "replay_event",
                "replay_index": i + 1,
                "replay_total": replay_count,
                **event
            }))

            # Rate limit to prevent overwhelming client
            if (i + 1) % REPLAY_RATE_LIMIT_PER_SEC == 0:
                await asyncio.sleep(1)

        # Send replay complete marker
        await websocket.send(json.dumps({
            "type": "replay_complete",
            "replay_count": replay_count
        }))

        return ack_response

    async def _perform_full_sync(
        self,
        websocket,
        client_id: str
    ) -> dict:
        """
        Perform full state synchronization for clients that missed too many events.
        """
        # Fetch current full state of all tasks for the user
        # This would query the database or state store
        full_state = await self._fetch_full_task_state(client_id)

        ack_response = {
            "type": "reconnect_ack",
            "status": "success",
            "replay_required": True,
            "replay_mode": "full",
            "state_count": len(full_state),
            "new_reconnect_token": self._generate_reconnect_token(client_id)
        }
        await websocket.send(json.dumps(ack_response))

        # Send full state
        await websocket.send(json.dumps({
            "type": "full_sync",
            "tasks": full_state,
            "sync_timestamp": datetime.now(timezone.utc).isoformat()
        }))

        return ack_response

    def _generate_reconnect_token(self, client_id: str) -> str:
        """Generate a secure reconnect token."""
        token = hashlib.sha256(
            f"{client_id}:{time.time()}:{os.urandom(16).hex()}".encode()
        ).hexdigest()

        self.reconnect_tokens[token] = client_id

        # Update session
        if client_id not in self.client_sessions:
            self.client_sessions[client_id] = {}

        self.client_sessions[client_id].update({
            "token_created_at": time.time(),
            "reconnect_token": token,
            "last_connected_at": time.time()
        })

        return token

    async def _fetch_full_task_state(self, client_id: str) -> list:
        """
        Fetch full task state from database.
        This is a placeholder - actual implementation depends on data layer.
        """
        # TODO: Query database for all tasks belonging to user
        # For now, return empty list
        return []

    def register_new_connection(self, client_id: str, websocket):
        """Register a new client connection."""
        token = self._generate_reconnect_token(client_id)

        # Send token to client for future reconnections
        asyncio.create_task(websocket.send(json.dumps({
            "type": "connection_established",
            "reconnect_token": token,
            "token_ttl_sec": RECONNECT_TOKEN_TTL_SEC
        })))
```

## Client-Side Reconnection Logic

```javascript
// Client-side JavaScript for handling reconnections
class ReconnectableWebSocket {
    constructor(url, options = {}) {
        this.url = url;
        this.reconnectToken = null;
        this.lastSequenceNumber = null;
        this.maxReconnectDelay = options.maxReconnectDelay || 30000;
        this.reconnectDelay = 1000;

        this.connect();
    }

    connect() {
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
            console.log('WebSocket connected');
            this.reconnectDelay = 1000; // Reset backoff

            // If we have a reconnect token, send it
            if (this.reconnectToken) {
                this.ws.send(JSON.stringify({
                    type: 'reconnect',
                    reconnect_token: this.reconnectToken,
                    last_sequence_number: this.lastSequenceNumber,
                    client_id: this.clientId
                }));
            }
        };

        this.ws.onmessage = (event) => {
            const message = JSON.parse(event.data);

            switch (message.type) {
                case 'connection_established':
                    this.reconnectToken = message.reconnect_token;
                    this.clientId = message.client_id || this.generateClientId();
                    break;

                case 'reconnect_ack':
                    if (message.status === 'success') {
                        this.reconnectToken = message.new_reconnect_token;
                        console.log(`Reconnection successful. Replay mode: ${message.replay_mode}`);
                    }
                    break;

                case 'replay_event':
                    console.log(`Replaying event ${message.replay_index}/${message.replay_total}`);
                    this.processEvent(message);
                    break;

                case 'replay_complete':
                    console.log('Event replay complete');
                    this.onReplayComplete();
                    break;

                default:
                    // Regular event
                    if (message.sequence_number) {
                        this.lastSequenceNumber = message.sequence_number;
                    }
                    this.processEvent(message);
            }
        };

        this.ws.onclose = () => {
            console.log('WebSocket disconnected. Reconnecting...');
            this.scheduleReconnect();
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }

    scheduleReconnect() {
        setTimeout(() => {
            this.connect();

            // Exponential backoff
            this.reconnectDelay = Math.min(
                this.reconnectDelay * 2,
                this.maxReconnectDelay
            );
        }, this.reconnectDelay);
    }

    processEvent(event) {
        // Process event (update UI, etc.)
        console.log('Processing event:', event);
    }

    onReplayComplete() {
        // Called when event replay is complete
        console.log('Caught up with missed events');
    }

    generateClientId() {
        return 'client-' + Math.random().toString(36).substr(2, 9);
    }
}

// Usage
const ws = new ReconnectableWebSocket('ws://localhost:8080/ws/tasks');
```

## Error Handling

**Invalid Reconnect Token:**
- Return error response to client
- Client should establish new connection (not reconnect)
- Log failed reconnection attempts for security monitoring

**Replay Buffer Overflow:**
- Fall back to full state sync
- Log buffer overflow events
- Consider increasing buffer size if frequent

**Slow Replay:**
- Implement rate limiting to prevent overwhelming client
- Monitor replay duration
- Alert if replay takes excessive time

**State Desynchronization:**
- Compare client state checksum with server state
- If mismatch detected, force full sync
- Log desynchronization events for investigation

## Success Criteria

- [ ] Reconnection tokens generated and validated correctly
- [ ] Expired tokens rejected appropriately
- [ ] Event replay sends missed events in correct order
- [ ] Replay rate limiting prevents client overload
- [ ] Full sync triggered when disconnect duration exceeds threshold
- [ ] Duplicate events handled idempotently by clients
- [ ] Client-side reconnection logic implements exponential backoff
- [ ] Reconnection metrics logged for monitoring

## Monitoring Metrics

```python
# Key metrics to emit
- reconnection.attempts.total (counter)
- reconnection.success (counter)
- reconnection.failed (counter)
- reconnection.replay.events (histogram)
- reconnection.replay.duration (histogram)
- reconnection.full_sync.triggered (counter)
- reconnection.token.expired (counter)
- reconnection.buffer.overflow (counter)
```

## Integration Points

- **Called By**: WebSocket server on client connection with reconnect token
- **Uses**: `maintain_order` skill to retrieve buffered events for replay
- **Uses**: Database/state store for full state synchronization
- **Dependencies**: Event buffer, session storage, reconnect token manager
- **Related Skills**: `broadcast_task_updates`, `maintain_order`, `sync_all_clients`
