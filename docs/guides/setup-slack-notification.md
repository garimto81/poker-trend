# Slack 알림 설정 가이드

## 1. Slack Bot 생성

### 1.1 Slack App 생성
1. [Slack API](https://api.slack.com/apps) 페이지 접속
2. "Create New App" 클릭
3. "From scratch" 선택
4. App Name: `Poker Trend Bot`
5. Workspace 선택

### 1.2 Bot 권한 설정
1. 좌측 메뉴에서 "OAuth & Permissions" 클릭
2. "Scopes" 섹션에서 다음 권한 추가:
   - `chat:write` - 메시지 전송
   - `chat:write.public` - 공개 채널에 메시지 전송
   - `files:write` - 파일 업로드 (선택사항)

### 1.3 Bot 설치
1. "Install to Workspace" 클릭
2. 권한 승인
3. `Bot User OAuth Token` 복사 (xoxb-로 시작)

## 2. 환경 변수 설정

`.env` 파일에 다음 정보 추가:

```env
# Slack Bot Token
SLACK_BOT_TOKEN=xoxb-your-bot-token-here

# Slack Channel ID 찾기
# 1. Slack에서 채널 우클릭
# 2. "View channel details" 클릭
# 3. 하단의 Channel ID 복사
SLACK_CHANNEL_ID=C1234567890

# 에러 알림용 채널 (선택사항)
SLACK_ERROR_CHANNEL=#poker-trends-errors
```

## 3. Webhook 설정 (선택사항)

Webhook을 사용하면 Bot Token 없이도 메시지를 전송할 수 있습니다.

### 3.1 Incoming Webhook 활성화
1. Slack App 설정에서 "Incoming Webhooks" 클릭
2. "Activate Incoming Webhooks" 토글 ON
3. "Add New Webhook to Workspace" 클릭
4. 채널 선택
5. Webhook URL 복사

### 3.2 환경 변수 추가
```env
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

## 4. 채널에 Bot 추가

1. Slack에서 알림을 받을 채널로 이동
2. 채널명 클릭 → "Integrations" → "Add apps"
3. "Poker Trend Bot" 검색 후 추가

## 5. 테스트

### 5.1 수동 테스트 실행
```bash
# API 서버에서 스케줄러 수동 실행
curl -X POST http://localhost:3000/api/scheduler/run
```

### 5.2 Slack 메시지 확인
- 설정한 채널에서 테스트 메시지 확인
- 메시지 포맷이 올바른지 확인

## 6. 알림 커스터마이징

### 6.1 알림 시간 변경
`.env` 파일에서 크론 표현식 수정:
```env
# 매일 오전 10시 (기본값)
TREND_ANALYSIS_SCHEDULE=0 10 * * *

# 매일 오전 9시와 오후 6시
TREND_ANALYSIS_SCHEDULE=0 9,18 * * *

# 평일만 오전 10시
TREND_ANALYSIS_SCHEDULE=0 10 * * 1-5
```

### 6.2 타임존 설정
```env
# 한국 시간 (기본값)
TREND_ANALYSIS_TIMEZONE=Asia/Seoul

# 미국 동부 시간
TREND_ANALYSIS_TIMEZONE=America/New_York
```

### 6.3 알림 임계값 조정
```env
# 트렌드 스코어 임계값 (0.0 ~ 1.0)
TREND_THRESHOLD=0.8

# 급상승 알림 기준 (조회수 증가율 %)
TREND_ALERT_GROWTH_RATE=50

# 최소 조회수 기준
TREND_ALERT_MIN_VIEWS=10000
```

## 7. 문제 해결

### 7.1 Bot이 메시지를 전송하지 않는 경우
- Bot Token이 올바른지 확인
- Bot이 채널에 추가되었는지 확인
- 채널 ID가 정확한지 확인 (C로 시작하는 ID)

### 7.2 권한 오류
- OAuth Scopes에 필요한 권한이 추가되었는지 확인
- Bot을 재설치하여 권한 업데이트

### 7.3 타임존 문제
- 서버 시간대 확인: `date` 명령어
- Docker 컨테이너의 경우 타임존 설정 확인

## 8. 고급 설정

### 8.1 멀티 채널 지원
여러 채널에 다른 내용을 전송하려면:

```javascript
// slackNotifier.js 수정
const channels = {
  general: process.env.SLACK_CHANNEL_GENERAL,
  detailed: process.env.SLACK_CHANNEL_DETAILED,
  alerts: process.env.SLACK_CHANNEL_ALERTS
};
```

### 8.2 멘션 추가
특정 사용자나 그룹을 멘션하려면:

```javascript
// 사용자 멘션
text: `<@U1234567890> 급상승 영상 발견!`

// 채널 멘션
text: `<!channel> 오늘의 포커 트렌드`

// here 멘션 (온라인 사용자만)
text: `<!here> 주목할 만한 트렌드`
```

### 8.3 인터랙티브 버튼 추가
```javascript
blocks.push({
  type: "actions",
  elements: [
    {
      type: "button",
      text: {
        type: "plain_text",
        text: "전체 리포트 보기"
      },
      url: "https://poker-trend.example.com/reports",
      style: "primary"
    }
  ]
});
```

## 9. 모니터링

### 9.1 알림 로그 확인
```sql
-- 최근 전송된 알림 확인
SELECT * FROM notification_logs 
WHERE channel = 'slack' 
ORDER BY created_at DESC 
LIMIT 10;
```

### 9.2 실패한 알림 확인
```sql
-- 실패한 알림 조회
SELECT * FROM notification_logs 
WHERE status = 'failed' 
AND channel = 'slack'
ORDER BY created_at DESC;
```

## 10. 보안 주의사항

- Slack Token을 절대 코드에 직접 포함하지 마세요
- `.env` 파일을 `.gitignore`에 추가하세요
- Token이 노출된 경우 즉시 재생성하세요
- 프로덕션 환경에서는 환경 변수 관리 시스템 사용을 권장합니다