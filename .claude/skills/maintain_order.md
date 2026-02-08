---
name: maintain_order
description: Ensures task events maintain correct ordering from Kafka through to WebSocket clients
agent: realtime-sync-agent
tags: [ordering, kafka, partitions, sequence]
---

# Maintain Order Skill

## Purpose
Preserve the causal ordering of task events as they flow from Kafka partitions to WebSocket clients, ensuring clients see a consistent sequence of state changes.

## Responsibilities

1. **Kafka Partition Ordering**
   - Leverage Kafka's per-partition ordering guarantee
   - Use task_id as partition key to ensure related events land in same partition
   - Consume from partitions in order (single-threaded per partition)
   - Track partition assignments and handle rebalancing

2. **Sequence Number Management**
   - Assign monotonically increasing sequence numbers to broadcasted events
   - Track per-partition sequence numbers independently
   - Include sequence numbers in broadcasted messages for client validation
   - Detect and log sequence gaps that indicate message loss

3. **In-Memory Event Buffering**
   - Maintain a sliding window buffer of recent events (per partition)
   - Use buffer for event replay on client reconnection
   - Implement FIFO eviction policy when buffer reaches capacity
   - Persist buffer size and retention window in configuration

4. **Out-of-Order Detection**
   - Detect out-of-order events based on sequence numbers or timestamps
   - Log warnings when ordering violations are detected
   - Implement configurable strictness (warn vs. drop vs. reorder)
   - Provide clear error messages to clients when ordering is lost

## Configuration Parameters

```python
KAFKA_PARTITION_KEY_FIELD = "task_id"
EVENT_BUFFER_SIZE = int(os.getenv("EVENT_BUFFER_SIZE", "1000"))
EVENT_BUFFER_RETENTION_HOURS = int(os.getenv("EVENT_BUFFER_RETENTION_HOURS", "24"))
ORDERING_STRICTNESS = os.getenv("ORDERING_STRICTNESS", "warn")  # warn, drop, reorder
ENABLE_SEQUENCE_NUMBERS = os.getenv("ENABLE_SEQUENCE_NUMBERS", "true") == "true"
```

## Sequence Number Schema

```json
{
  "event_id": "evt-uuid-123",
  "sequence_number": 12345,
  "partition": 2,
  "offset": 67890,
  "timestamp": "2026-02-06T12:00:01Z",
  "task": { ... }
}
```

## Ordering Strategy

```python
from collections import deque
from typing import Dict, Deque
import threading

class EventOrderManager:
    def __init__(self):
        # Per-partition sequence tracking
        self.partition_sequences: Dict[int, int] = {}

        # Per-partition event buffer (FIFO)
        self.partition_buffers: Dict[int, Deque] = {}

        # Global sequence counter (optional, for cross-partition ordering)
        self.global_sequence = 0
        self.sequence_lock = threading.Lock()

    def process_kafka_message(self, message) -> dict:
        """
        Process incoming Kafka message and assign sequence number.
        """
        partition = message.partition
        offset = message.offset
        event = message.value

        # Initialize partition tracking if needed
        if partition not in self.partition_sequences:
            self.partition_sequences[partition] = 0
            self.partition_buffers[partition] = deque(maxlen=EVENT_BUFFER_SIZE)

        # Assign sequence number
        with self.sequence_lock:
            self.partition_sequences[partition] += 1
            sequence_number = self.partition_sequences[partition]

            # Optional: global sequence for cross-partition ordering
            self.global_sequence += 1
            global_seq = self.global_sequence

        # Enrich event with ordering metadata
        enriched_event = {
            **event,
            "sequence_number": sequence_number,
            "global_sequence": global_seq,
            "partition": partition,
            "offset": offset,
            "timestamp": event.get("timestamp", datetime.now(timezone.utc).isoformat())
        }

        # Add to partition buffer for replay
        self.partition_buffers[partition].append(enriched_event)

        # Validate ordering
        self._validate_ordering(enriched_event, partition)

        return enriched_event

    def _validate_ordering(self, event: dict, partition: int):
        """Check for ordering violations."""
        buffer = self.partition_buffers[partition]

        if len(buffer) < 2:
            return  # Not enough events to validate

        # Get previous event
        prev_event = buffer[-2]
        curr_event = event

        # Check sequence number ordering
        if ENABLE_SEQUENCE_NUMBERS:
            if curr_event["sequence_number"] <= prev_event["sequence_number"]:
                logger.warning(
                    f"Sequence number ordering violation in partition {partition}: "
                    f"prev={prev_event['sequence_number']}, curr={curr_event['sequence_number']}"
                )

        # Check timestamp ordering
        prev_ts = datetime.fromisoformat(prev_event["timestamp"].replace('Z', '+00:00'))
        curr_ts = datetime.fromisoformat(curr_event["timestamp"].replace('Z', '+00:00'))

        if curr_ts < prev_ts:
            logger.warning(
                f"Timestamp ordering violation in partition {partition}: "
                f"prev={prev_ts}, curr={curr_ts}"
            )

    def get_events_since_sequence(
        self,
        partition: int,
        since_sequence: int
    ) -> list:
        """
        Retrieve events from buffer for client reconnection replay.
        Returns events with sequence_number > since_sequence.
        """
        if partition not in self.partition_buffers:
            return []

        buffer = self.partition_buffers[partition]
        return [
            event for event in buffer
            if event["sequence_number"] > since_sequence
        ]

    def get_all_recent_events(self, max_age_hours: int = None) -> list:
        """
        Get all recent events across all partitions, sorted by global_sequence.
        Useful for new client connections.
        """
        if max_age_hours is None:
            max_age_hours = EVENT_BUFFER_RETENTION_HOURS

        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
        all_events = []

        for partition, buffer in self.partition_buffers.items():
            for event in buffer:
                event_time = datetime.fromisoformat(
                    event["timestamp"].replace('Z', '+00:00')
                )
                if event_time >= cutoff_time:
                    all_events.append(event)

        # Sort by global sequence number
        all_events.sort(key=lambda e: e["global_sequence"])
        return all_events
```

## Partition Key Strategy

```python
from kafka import KafkaProducer

def produce_task_event_with_ordering(task_event: dict):
    """
    Produce task event to Kafka with proper partition key for ordering.
    """
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER_URL,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    # Use task_id as partition key to ensure all events for same task
    # go to the same partition (and thus maintain order)
    partition_key = task_event["task"]["task_id"]

    producer.send(
        topic='task-updates',
        value=task_event,
        key=partition_key.encode('utf-8')
    )

    producer.flush()
```

## Client-Side Ordering Validation

```javascript
// Client-side JavaScript for detecting ordering violations
class TaskEventProcessor {
    constructor() {
        this.lastSequenceNumber = null;
    }

    processEvent(event) {
        if (event.sequence_number) {
            if (this.lastSequenceNumber !== null) {
                const expectedSeq = this.lastSequenceNumber + 1;

                if (event.sequence_number !== expectedSeq) {
                    console.warn(
                        `Sequence gap detected: expected ${expectedSeq}, got ${event.sequence_number}`
                    );

                    // Request replay of missing events
                    this.requestEventReplay(
                        this.lastSequenceNumber + 1,
                        event.sequence_number - 1
                    );
                }
            }

            this.lastSequenceNumber = event.sequence_number;
        }

        // Process the event
        this.updateTaskUI(event);
    }

    requestEventReplay(fromSeq, toSeq) {
        // Send replay request to server
        websocket.send(JSON.stringify({
            type: 'replay_request',
            from_sequence: fromSeq,
            to_sequence: toSeq
        }));
    }
}
```

## Error Handling

**Ordering Violations:**
- **Warn Mode**: Log warning, continue processing
- **Drop Mode**: Drop out-of-order events, log dropped count
- **Reorder Mode**: Buffer events and reorder before broadcasting (adds latency)

**Sequence Gaps:**
- Detect gaps in sequence numbers
- Log gap size and affected partition
- Emit metrics for monitoring
- Clients can request replay of missing events

**Partition Rebalancing:**
- Handle Kafka consumer group rebalancing gracefully
- Preserve sequence state during rebalancing
- Resume from last committed offset
- Log partition reassignments

**Buffer Overflow:**
- When buffer reaches capacity, evict oldest events (FIFO)
- Log eviction events with count and time range
- Emit metrics for buffer usage
- Alert if buffer churn rate is high

## Success Criteria

- [ ] Kafka messages consumed in partition order
- [ ] Sequence numbers monotonically increase per partition
- [ ] Event buffers maintain FIFO ordering
- [ ] Out-of-order events detected and logged
- [ ] Partition rebalancing preserves ordering guarantees
- [ ] Client reconnection replay maintains event order
- [ ] Buffer overflow handled without data corruption
- [ ] Ordering metrics emitted for monitoring

## Monitoring Metrics

```python
# Key metrics to emit
- ordering.sequence_number.current (gauge per partition)
- ordering.violations.detected (counter)
- ordering.gaps.detected (counter)
- ordering.buffer.size (gauge per partition)
- ordering.buffer.evictions (counter)
- ordering.replay.requests (counter)
```

## Integration Points

- **Called By**: Main Kafka consumer loop for every consumed message
- **Used By**: `broadcast_task_updates` to enrich events with sequence numbers
- **Used By**: `handle_reconnects` to replay events in correct order
- **Dependencies**: Kafka consumer, event buffer storage
- **Related Skills**: `broadcast_task_updates`, `handle_reconnects`, `sync_all_clients`
