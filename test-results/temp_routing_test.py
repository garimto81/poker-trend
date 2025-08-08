
class SlackChannelRouter:
    def __init__(self):
        self.channel_config = {
            "poker-daily": {
                "webhook": "daily_webhook_url",
                "report_types": ["daily"],
                "priority": "normal"
            },
            "poker-weekly": {
                "webhook": "weekly_webhook_url", 
                "report_types": ["weekly"],
                "priority": "high"
            },
            "poker-alerts": {
                "webhook": "alerts_webhook_url",
                "report_types": ["error", "warning"],
                "priority": "urgent"
            },
            "poker-monthly": {
                "webhook": "monthly_webhook_url",
                "report_types": ["monthly"],
                "priority": "high"
            }
        }
    
    def get_target_channels(self, report_type):
        target_channels = []
        for channel, config in self.channel_config.items():
            if report_type in config["report_types"]:
                target_channels.append({
                    "channel": channel,
                    "webhook": config["webhook"],
                    "priority": config["priority"]
                })
        return target_channels
    
    def validate_routing_rules(self):
        validation_results = {}
        
        for channel, config in self.channel_config.items():
            validation_results[channel] = {
                "has_webhook": bool(config.get("webhook")),
                "has_report_types": bool(config.get("report_types")),
                "has_priority": bool(config.get("priority")),
                "valid": all([
                    config.get("webhook"),
                    config.get("report_types"),
                    config.get("priority")
                ])
            }
        
        return validation_results

# 채널 라우팅 테스트
router = SlackChannelRouter()

print("Slack Channel Routing Test:")

# 라우팅 규칙 검증
print("\n1. Routing Rules Validation:")
validation = router.validate_routing_rules()
for channel, rules in validation.items():
    status = "✓" if rules["valid"] else "✗"
    print(f"   {channel}: {status}")

# 리포트 타입별 라우팅 테스트
print("\n2. Report Type Routing:")
test_report_types = ["daily", "weekly", "monthly", "error"]

for report_type in test_report_types:
    targets = router.get_target_channels(report_type)
    print(f"   {report_type}: {len(targets)} target(s)")
    for target in targets:
        print(f"     → {target['channel']} ({target['priority']} priority)")

print("\n3. Priority Distribution:")
priority_counts = {}
for channel, config in router.channel_config.items():
    priority = config["priority"]
    priority_counts[priority] = priority_counts.get(priority, 0) + 1

for priority, count in priority_counts.items():
    print(f"   {priority}: {count} channel(s)")

print("\nChannel routing: COMPLETED")
