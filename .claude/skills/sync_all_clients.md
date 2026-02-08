---
name: sync_all_clients
description: Ensures all connected WebSocket clients maintain consistent state with the server
agent: realtime-sync-agent
tags: [websocket, synchronization, consistency, state-management]
---

# Sync All Clients Skill

## Purpose
Maintain consistency across all connected WebSocket clients by coordinating state updates, detecting desynchronization, and providing mechanisms for clients to verify and repair their local state.

## Responsibilities

1. **Global State Coordination**
   - Track global application state changes that affect all clients
   - Broadcast system-wide updates (e.g., schema changes, feature flags)
   - Coordinate state transitions that require multi-client coordination
   - Implement state versioning for compatibility

2. **Consistency Verification**
   - Provide state checksum mechanism for clients to verify local state
   - Detect and alert on state divergence between clients and server
   - Implement periodic state validation heartbeats
   - Log consistency violations for debugging

3. **Batch Synchronization**
   - Support bulk state sync for newly connected clients
   - Optimize payload size for initial state transfer
   - Implement pagination for large state datasets
   - Compress state payloads when beneficial

4. **Client State Management**
   - Track which clients have received which updates
   - Support selective synchronization based on client subscriptions
   - Implement client capability negotiation (e.g., compression support)
   - Handle heterogeneous client versions gracefully

## Configuration Parameters

```python
STATE_CHECKSUM_INTERVAL_SEC = int(os.getenv("STATE_CHECKSUM_INTERVAL", "60"))
BATCH_SYNC_PAGE_SIZE = int(os.getenv("BATCH_SYNC_PAGE_SIZE", "100"))
ENABLE_STATE_COMPRESSION = os.getenv("ENABLE_STATE_COMPRESSION", "true") == "true"
CLIENT_STATE_TIMEOUT_SEC = int(os.getenv("CLIENT_STATE_TIMEOUT", "300"))
SYNC_PROTOCOL_VERSION = "1.0"
MAX_SYNC_PAYLOAD_KB = int(os.getenv("MAX_SYNC_PAYLOAD_KB", "512"))
```

## State Synchronization Protocol

### Initial Sync Request (New Client)

```json
// Client -> Server
{
  "type": "sync_request",
  "protocol_version": "1.0",
  "client_capabilities": {
    "compression": ["gzip", "none"],
    "max_payload_kb": 512,
    "supports_pagination": true
  },
  "filters": {
    "user_id": "user-123",
    "task_status": ["pending", "in_progress"]
  }
}

// Server -> Client
{
  "type": "sync_response",
  "protocol_version": "1.0",
  "sync_mode": "paginated",
  "total_items": 456,
  "page_size": 100,
  "pages_total": 5,
  "checksum": "sha256-hash",
  "compression": "gzip"
}
```

### Periodic Checksum Verification

```json
// Server -> All Clients (periodic)
{
  "type": "state_checkpoint",
  "checkpoint_id": "ckpt-uuid-123",
  "timestamp": "2026-02-06T12:00:00Z",
  "expected_checksum": "sha256-hash-of-state",
  "item_count": 456,
  "last_sequence_number": 12345
}

// Client -> Server (if checksum mismatch)
{
  "type": "resync_request",
  "checkpoint_id": "ckpt-uuid-123",
  "client_checksum": "sha256-different-hash",
  "client_item_count": 450,
  "last_sequence_number": 12340
}
```

## Synchronization Implementation

```python
from typing import Dict, List, Optional
import zlib
import json
import hashlib

class ClientSyncManager:
    def __init__(self, database_service, event_order_manager):
        self.db = database_service
        self.event_order_manager = event_order_manager

        # Track client sync state
        self.client_sync_state: Dict[str, dict] = {}

    async def handle_sync_request(
        self,
        websocket,
        client_id: str,
        sync_request: dict
    ):
        """
        Handle initial sync request from a new or reconnecting client.
        """
        # Determine sync strategy based on client capabilities
        capabilities = sync_request.get("client_capabilities", {})
        filters = sync_request.get("filters", {})

        # Fetch relevant state from database
        tasks = await self._fetch_filtered_tasks(filters)

        # Calculate response parameters
        total_items = len(tasks)
        supports_pagination = capabilities.get("supports_pagination", False)
        page_size = BATCH_SYNC_PAGE_SIZE if supports_pagination else total_items

        # Calculate checksum for verification
        checksum = self._calculate_state_checksum(tasks)

        # Prepare sync response
        sync_response = {
            "type": "sync_response",
            "protocol_version": SYNC_PROTOCOL_VERSION,
            "sync_mode": "paginated" if supports_pagination else "full",
            "total_items": total_items,
            "page_size": page_size,
            "pages_total": (total_items + page_size - 1) // page_size,
            "checksum": checksum,
            "compression": self._select_compression(capabilities)
        }

        # Send sync response
        await websocket.send(json.dumps(sync_response))

        # Send state data
        if supports_pagination:
            await self._send_paginated_state(websocket, tasks, page_size)
        else:
            await self._send_full_state(websocket, tasks, sync_response["compression"])

        # Track client sync state
        self.client_sync_state[client_id] = {
            "checksum": checksum,
            "item_count": total_items,
            "last_sync_at": time.time(),
            "sequence_number": self.event_order_manager.global_sequence
        }

    async def _fetch_filtered_tasks(self, filters: dict) -> List[dict]:
        """
        Fetch tasks from database with filters applied.
        """
        user_id = filters.get("user_id")
        status_filter = filters.get("task_status", [])

        # Query database (placeholder - actual implementation depends on DB layer)
        query = "SELECT * FROM tasks WHERE user_id = ?"
        params = [user_id]

        if status_filter:
            placeholders = ','.join(['?' for _ in status_filter])
            query += f" AND status IN ({placeholders})"
            params.extend(status_filter)

        # This is a placeholder - replace with actual DB query
        tasks = await self.db.fetch_all(query, params)
        return tasks

    def _calculate_state_checksum(self, tasks: List[dict]) -> str:
        """
        Calculate deterministic checksum of task state.
        """
        # Sort tasks by ID for deterministic ordering
        sorted_tasks = sorted(tasks, key=lambda t: t["task_id"])

        # Create canonical representation
        canonical = json.dumps(sorted_tasks, sort_keys=True, separators=(',', ':'))

        # Calculate SHA-256 hash
        return hashlib.sha256(canonical.encode()).hexdigest()

    def _select_compression(self, capabilities: dict) -> str:
        """
        Select compression method based on client capabilities and server config.
        """
        if not ENABLE_STATE_COMPRESSION:
            return "none"

        supported = capabilities.get("compression", ["none"])

        if "gzip" in supported:
            return "gzip"

        return "none"

    async def _send_full_state(
        self,
        websocket,
        tasks: List[dict],
        compression: str
    ):
        """
        Send full state to client in a single message.
        """
        payload = {
            "type": "full_state",
            "tasks": tasks,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        message = json.dumps(payload)

        # Apply compression if requested
        if compression == "gzip":
            compressed = zlib.compress(message.encode())
            # Send compressed data (actual implementation depends on WebSocket library)
            await websocket.send(compressed)
        else:
            await websocket.send(message)

    async def _send_paginated_state(
        self,
        websocket,
        tasks: List[dict],
        page_size: int
    ):
        """
        Send state to client in paginated chunks.
        """
        total_pages = (len(tasks) + page_size - 1) // page_size

        for page_num in range(total_pages):
            start_idx = page_num * page_size
            end_idx = min(start_idx + page_size, len(tasks))
            page_tasks = tasks[start_idx:end_idx]

            page_message = {
                "type": "state_page",
                "page_number": page_num + 1,
                "pages_total": total_pages,
                "tasks": page_tasks
            }

            await websocket.send(json.dumps(page_message))

            # Small delay to prevent overwhelming client
            if page_num < total_pages - 1:
                await asyncio.sleep(0.1)

        # Send completion marker
        await websocket.send(json.dumps({
            "type": "sync_complete",
            "pages_sent": total_pages,
            "items_sent": len(tasks)
        }))

    async def broadcast_state_checkpoint(self, broadcaster):
        """
        Periodically broadcast state checkpoints to all clients for verification.
        """
        # Fetch current global state
        all_tasks = await self._fetch_filtered_tasks({})
        checksum = self._calculate_state_checksum(all_tasks)

        checkpoint_message = {
            "type": "state_checkpoint",
            "checkpoint_id": f"ckpt-{int(time.time())}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "expected_checksum": checksum,
            "item_count": len(all_tasks),
            "last_sequence_number": self.event_order_manager.global_sequence
        }

        # Broadcast to all clients
        await broadcaster.broadcast_task_update(checkpoint_message)

    async def handle_resync_request(
        self,
        websocket,
        client_id: str,
        resync_request: dict
    ):
        """
        Handle client request for resynchronization due to checksum mismatch.
        """
        checkpoint_id = resync_request.get("checkpoint_id")
        client_checksum = resync_request.get("client_checksum")

        logger.warning(
            f"Client {client_id} state divergence detected at checkpoint {checkpoint_id}. "
            f"Client checksum: {client_checksum}"
        )

        # Trigger full resync
        await self.handle_sync_request(
            websocket,
            client_id,
            {"filters": {}, "client_capabilities": {}}
        )
```

## Client-Side State Management

```javascript
// Client-side JavaScript for state synchronization
class StateSyncManager {
    constructor(websocket) {
        this.ws = websocket;
        this.localState = [];
        this.lastChecksum = null;
        this.lastSequenceNumber = null;

        // Start periodic checksum verification
        setInterval(() => this.verifyChecksum(), 60000);
    }

    handleSyncResponse(message) {
        console.log(`Receiving state sync: ${message.total_items} items, ${message.pages_total} pages`);
        this.localState = [];  // Clear local state for resync
    }

    handleStatePage(message) {
        console.log(`Received page ${message.page_number}/${message.pages_total}`);
        this.localState.push(...message.tasks);
    }

    handleSyncComplete(message) {
        console.log(`Sync complete: ${message.items_sent} items received`);
        this.calculateLocalChecksum();
        this.renderUI();
    }

    handleStateCheckpoint(message) {
        const localChecksum = this.calculateLocalChecksum();

        if (localChecksum !== message.expected_checksum) {
            console.warn('State checksum mismatch detected. Requesting resync.');
            this.requestResync(message);
        } else {
            console.log('State checkpoint verified. Client in sync.');
        }

        this.lastChecksum = message.expected_checksum;
        this.lastSequenceNumber = message.last_sequence_number;
    }

    calculateLocalChecksum() {
        // Sort tasks by ID for deterministic ordering
        const sortedTasks = [...this.localState].sort((a, b) =>
            a.task_id.localeCompare(b.task_id)
        );

        // Create canonical JSON representation
        const canonical = JSON.stringify(sortedTasks);

        // Calculate SHA-256 (requires crypto library or Web Crypto API)
        return this.sha256(canonical);
    }

    requestResync(checkpoint) {
        const localChecksum = this.calculateLocalChecksum();

        this.ws.send(JSON.stringify({
            type: 'resync_request',
            checkpoint_id: checkpoint.checkpoint_id,
            client_checksum: localChecksum,
            client_item_count: this.localState.length,
            last_sequence_number: this.lastSequenceNumber
        }));
    }

    verifyChecksum() {
        // Client can proactively request checkpoint verification
        this.ws.send(JSON.stringify({
            type: 'checkpoint_request'
        }));
    }

    sha256(str) {
        // Simplified - use actual crypto library in production
        return btoa(str).substring(0, 64);
    }

    renderUI() {
        // Update UI with current state
        console.log('Rendering UI with', this.localState.length, 'tasks');
    }
}
```

## Periodic Checkpoint Broadcast

```python
import asyncio

async def periodic_checkpoint_broadcast(
    sync_manager: ClientSyncManager,
    broadcaster: WebSocketBroadcaster
):
    """
    Background task to periodically broadcast state checkpoints.
    """
    while True:
        try:
            await asyncio.sleep(STATE_CHECKSUM_INTERVAL_SEC)
            await sync_manager.broadcast_state_checkpoint(broadcaster)
        except Exception as e:
            logger.error(f"Error broadcasting checkpoint: {e}")
```

## Error Handling

**Checksum Mismatch:**
- Log mismatch details (client ID, checksums, item counts)
- Trigger automatic resync
- Emit metric for monitoring
- Investigate if mismatches are frequent

**Sync Timeout:**
- Client doesn't respond to checkpoint within timeout
- Mark client as potentially stale
- Force resync on next client activity
- Clean up timed-out client state

**Large State Transfer:**
- Monitor payload size and warn if exceeding limits
- Use pagination for large datasets
- Apply compression when beneficial
- Consider incremental sync strategies

**Version Incompatibility:**
- Detect protocol version mismatches
- Provide clear error messages to client
- Support backward compatibility when possible
- Log version mismatches for monitoring

## Success Criteria

- [ ] New clients receive full initial state sync
- [ ] Paginated sync works for large state datasets
- [ ] Compression reduces payload size when enabled
- [ ] Periodic checksum verification detects state divergence
- [ ] Automatic resync triggered on checksum mismatch
- [ ] Client capability negotiation handled correctly
- [ ] Protocol versioning supports backward compatibility
- [ ] Sync metrics emitted for monitoring

## Monitoring Metrics

```python
# Key metrics to emit
- sync.requests.total (counter)
- sync.full.completed (counter)
- sync.paginated.completed (counter)
- sync.payload.size (histogram)
- sync.duration (histogram)
- sync.checksum.mismatches (counter)
- sync.resync.triggered (counter)
- sync.compression.ratio (gauge)
- sync.clients.stale (gauge)
```

## Integration Points

- **Called By**: WebSocket server on new client connections
- **Called By**: Periodic background task for checkpoint broadcasts
- **Uses**: Database service for fetching current state
- **Uses**: `maintain_order` for sequence number tracking
- **Dependencies**: Database, event buffer, WebSocket broadcaster
- **Related Skills**: `broadcast_task_updates`, `handle_reconnects`, `maintain_order`
