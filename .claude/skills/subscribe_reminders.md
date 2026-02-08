---
name: subscribe_reminders
description: Subscribes to Kafka topic "reminders" and processes incoming reminder events
agent: notification-agent
tags: [kafka, consumer, reminders]
---

# Subscribe Reminders Skill

## Purpose
Establish and maintain a Kafka consumer subscription to the "reminders" topic for processing reminder notification events.

## Responsibilities

1. **Consumer Configuration**
   - Configure Kafka consumer with appropriate group ID
   - Set up connection to Kafka broker using environment variables
   - Configure serialization/deserialization for message payloads
   - Set appropriate offset management strategy

2. **Topic Subscription**
   - Subscribe to the "reminders" topic
   - Handle partition assignment and rebalancing
   - Implement graceful consumer lifecycle management

3. **Message Processing**
   - Poll for new messages in a non-blocking manner
   - Deserialize message payloads into structured format
   - Validate message schema and required fields
   - Extract notification type, recipient, and content

4. **Error Handling**
   - Handle deserialization failures gracefully
   - Implement proper offset commit strategy
   - Log consumer errors with appropriate context
   - Implement dead letter queue for poison messages

## Configuration Parameters

```python
KAFKA_BROKER_URL = os.getenv("KAFKA_BROKER_URL")
KAFKA_TOPIC = "reminders"
CONSUMER_GROUP_ID = "notification-consumer-group"
AUTO_OFFSET_RESET = "earliest"
ENABLE_AUTO_COMMIT = False
```

## Expected Message Schema

```json
{
  "message_id": "unique-uuid",
  "user_id": "user-123",
  "notification_type": "email|push",
  "recipient": "user@example.com|device-token",
  "subject": "Reminder Subject",
  "body": "Reminder message content",
  "scheduled_at": "2026-02-06T12:00:00Z",
  "metadata": {}
}
```

## Success Criteria

- [ ] Consumer successfully connects to Kafka broker
- [ ] Messages are consumed from "reminders" topic
- [ ] Message schema validation is performed
- [ ] Consumer handles rebalancing without message loss
- [ ] Failed messages are logged and moved to DLQ
- [ ] Consumer lag is monitored and logged

## Integration Points

- **Triggers**: `send_push_notification` or `send_email_notification` based on notification_type
- **Outputs**: Parsed notification event ready for delivery
- **Dependencies**: Kafka broker connectivity, message schema definition
