---
name: send_push_notification
description: Sends push notifications to mobile devices via FCM/APNS
agent: notification-agent
tags: [push, notification, fcm, apns]
---

# Send Push Notification Skill

## Purpose
Deliver push notifications to mobile devices using Firebase Cloud Messaging (FCM) or Apple Push Notification Service (APNS).

## Responsibilities

1. **Recipient Validation**
   - Validate device token format
   - Check token against blacklist/invalid tokens
   - Verify notification payload size limits

2. **Payload Preparation**
   - Format notification title and body
   - Include custom data payload if provided
   - Set appropriate priority and TTL
   - Configure notification behavior (sound, badge, etc.)

3. **Delivery Execution**
   - Select appropriate provider (FCM for Android, APNS for iOS)
   - Send notification via provider API
   - Handle provider-specific response codes
   - Extract delivery confirmation or error details

4. **Response Processing**
   - Parse provider response for success/failure
   - Identify retryable vs permanent failures
   - Return structured result for retry logic
   - Update device token status if invalid

## Configuration Parameters

```python
FCM_API_KEY = os.getenv("FCM_API_KEY")
APNS_CERT_PATH = os.getenv("APNS_CERT_PATH")
PUSH_NOTIFICATION_TIMEOUT = 10  # seconds
MAX_PAYLOAD_SIZE = 4096  # bytes
```

## Input Schema

```python
{
  "recipient": "device-token-string",
  "title": "Notification Title",
  "body": "Notification message",
  "data": {
    "task_id": "123",
    "action": "open_task"
  },
  "platform": "android|ios"
}
```

## Output Schema

```python
{
  "success": True|False,
  "message_id": "provider-message-id",
  "error_code": "INVALID_TOKEN|TIMEOUT|RATE_LIMIT|None",
  "retryable": True|False,
  "delivery_timestamp": "2026-02-06T12:00:01Z"
}
```

## Error Classification

**Retryable Errors:**
- Network timeout
- HTTP 429 (rate limit)
- HTTP 503 (service unavailable)
- Temporary provider outage

**Permanent Failures:**
- Invalid device token
- Expired token
- Malformed payload
- HTTP 400 (bad request)

## Success Criteria

- [ ] Device token validation before sending
- [ ] Correct provider selected based on platform
- [ ] Notification delivered within timeout
- [ ] Proper error classification (retryable vs permanent)
- [ ] Response includes delivery confirmation or error details
- [ ] Invalid tokens flagged for cleanup

## Integration Points

- **Called By**: `subscribe_reminders` when notification_type is "push"
- **Triggers**: `retry_notification` on retryable failures
- **Triggers**: `log_notification` for all delivery attempts
- **Dependencies**: FCM/APNS credentials, network connectivity
