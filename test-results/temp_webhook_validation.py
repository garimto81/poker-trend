
import re
import os

# Slack 웹훅 URL 형식 검증
webhook_patterns = [
    r'^https://hooks\.slack\.com/services/T[A-Z0-9]{8}/B[A-Z0-9]{8}/[A-Za-z0-9]{24}$',
    r'^https://hooks\.slack\.com/services/T[A-Z0-9]{10}/B[A-Z0-9]{10}/[A-Za-z0-9]{24}$'
]

# 테스트용 가상 웹훅 URL
test_webhooks = [
    "https://hooks.slack.com/services/T12345678/B12345678/abcd1234efgh5678ijkl9012",
    "https://hooks.slack.com/services/T1234567890/B1234567890/abcd1234efgh5678ijkl9012",
    "invalid-webhook-url",
    "https://wrong-domain.com/webhook"
]

print("Slack Webhook URL Validation:")
for i, url in enumerate(test_webhooks):
    valid = any(re.match(pattern, url) for pattern in webhook_patterns)
    status = "✓ VALID" if valid else "✗ INVALID"
    print(f"  URL {i+1}: {status}")

print("\nWebhook URL validation: COMPLETED")
