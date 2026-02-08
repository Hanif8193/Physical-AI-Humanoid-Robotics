---
name: send_email_notification
description: Sends email notifications via configured email service provider
agent: notification-agent
tags: [email, notification, smtp, sendgrid]
---

# Send Email Notification Skill

## Purpose
Deliver email notifications using a configured email service provider (SendGrid, AWS SES, or SMTP).

## Responsibilities

1. **Recipient Validation**
   - Validate email address format
   - Check against bounce/complaint lists
   - Verify domain exists (optional DNS check)

2. **Email Composition**
   - Render email subject and body from template or raw content
   - Support both plain text and HTML formats
   - Include proper headers (From, Reply-To, etc.)
   - Attach metadata for tracking

3. **Delivery Execution**
   - Send email via configured provider
   - Handle provider-specific API requirements
   - Set appropriate timeout for delivery attempt
   - Retrieve delivery tracking ID

4. **Response Processing**
   - Parse provider response for acceptance/rejection
   - Extract delivery ID for tracking
   - Classify errors as retryable or permanent
   - Handle bounce notifications

## Configuration Parameters

```python
EMAIL_PROVIDER = os.getenv("EMAIL_PROVIDER", "sendgrid")  # sendgrid|ses|smtp
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@todoapp.com")
FROM_NAME = os.getenv("FROM_NAME", "Todo App")
EMAIL_TIMEOUT = 15  # seconds
```

## Input Schema

```python
{
  "recipient": "user@example.com",
  "subject": "Task Reminder",
  "body": "You have a task due soon...",
  "body_html": "<p>You have a task due soon...</p>",
  "reply_to": "support@todoapp.com",
  "metadata": {
    "user_id": "123",
    "task_id": "456"
  }
}
```

## Output Schema

```python
{
  "success": True|False,
  "message_id": "provider-message-id",
  "error_code": "INVALID_EMAIL|BOUNCE|TIMEOUT|RATE_LIMIT|None",
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
- Recipient mailbox full (soft bounce)

**Permanent Failures:**
- Invalid email address format
- Domain does not exist
- Recipient not found (hard bounce)
- Email blocked (spam/complaint)
- HTTP 400 (bad request)

## Success Criteria

- [ ] Email address validation before sending
- [ ] Proper email headers configured
- [ ] Both plain text and HTML versions supported
- [ ] Email delivered within timeout
- [ ] Proper error classification (retryable vs permanent)
- [ ] Bounce/complaint addresses tracked for cleanup
- [ ] Delivery tracking ID captured

## Integration Points

- **Called By**: `subscribe_reminders` when notification_type is "email"
- **Triggers**: `retry_notification` on retryable failures
- **Triggers**: `log_notification` for all delivery attempts
- **Dependencies**: Email provider credentials, valid sender domain
