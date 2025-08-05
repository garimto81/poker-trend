# 📬 일일 포커 트렌드 Slack 알림 설정 가이드

## 🎯 개요

이 가이드는 YouTube 포커 트렌드 분석 결과를 매일 오전 10시에 Slack 특정 채널로 자동 전송하는 방법을 설명합니다.

## 📋 사전 준비사항

- Slack 워크스페이스 관리자 권한
- GitHub 저장소 설정 권한
- 포커 트렌드 리포트를 받을 Slack 채널

## 🔧 설정 단계

### 1. Slack Webhook 생성

#### 1.1 Slack App 생성
1. [Slack API](https://api.slack.com/apps) 접속
2. "Create New App" 클릭
3. "From scratch" 선택
4. App 이름: `Poker Trend Reporter`
5. 워크스페이스 선택

#### 1.2 Incoming Webhook 활성화
1. 좌측 메뉴에서 "Incoming Webhooks" 클릭
2. "Activate Incoming Webhooks" 토글 ON
3. "Add New Webhook to Workspace" 클릭
4. 리포트를 받을 채널 선택 (예: `#poker-trends`)
5. "Allow" 클릭

#### 1.3 Webhook URL 복사
```
https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX
```
⚠️ 이 URL은 비밀로 유지해야 합니다!

### 2. GitHub Secrets 설정

1. GitHub 저장소로 이동
2. Settings → Secrets and variables → Actions
3. "New repository secret" 클릭
4. 다음 시크릿 추가:

| Name | Value |
|------|-------|
| `SLACK_WEBHOOK_URL` | 위에서 복사한 Webhook URL |
| `YOUTUBE_API_KEY` | YouTube Data API v3 키 |
| `GEMINI_API_KEY` | Google Gemini API 키 |

### 3. Slack 채널 설정

#### 3.1 전용 채널 생성 (권장)
```
채널명: #poker-trends
설명: YouTube 포커 트렌드 일일 분석 리포트
공개/비공개: 팀 요구사항에 따라 설정
```

#### 3.2 채널 알림 설정
1. 채널 설정 → Notifications
2. "All new messages" 선택 (중요 정보를 놓치지 않기 위해)
3. 키워드 알림 추가: "급상승", "TOP", "트렌드"

### 4. 워크플로우 활성화

#### 4.1 GitHub Actions 확인
```yaml
# .github/workflows/daily-poker-trends.yml
name: Daily Poker Trend Report

on:
  schedule:
    # 평일 오전 10시 (KST)
    - cron: '0 1 * * 1-5'
```

#### 4.2 수동 테스트
1. GitHub Actions 탭으로 이동
2. "Daily Poker Trend Report" 워크플로우 선택
3. "Run workflow" 클릭
4. "Run workflow" 버튼 클릭
5. Slack 채널에서 메시지 수신 확인

## 📱 Slack 메시지 커스터마이징

### 알림 사운드 설정
```javascript
// Slack App 설정에서 커스텀 사운드 추가 가능
{
  "notification_sound": "coin.wav" // 카지노 느낌
}
```

### 이모지 반응 자동화
Slack 워크플로우를 통해 리포트에 자동으로 반응 추가:
- 📊 - 리포트 수신 확인
- 👀 - 읽음 표시
- 🔥 - 흥미로운 트렌드 발견

## 🚨 문제 해결

### 메시지가 오지 않는 경우

1. **GitHub Actions 로그 확인**
   ```bash
   Actions → 최근 실행 → 상세 로그 확인
   ```

2. **Webhook URL 검증**
   ```bash
   curl -X POST -H 'Content-type: application/json' \
   --data '{"text":"테스트 메시지"}' \
   YOUR_WEBHOOK_URL
   ```

3. **채널 권한 확인**
   - Bot이 채널에 추가되어 있는지 확인
   - 채널이 아카이브되지 않았는지 확인

### 시간이 맞지 않는 경우

GitHub Actions는 UTC 기준으로 동작합니다:
- KST 10:00 = UTC 01:00
- cron 표현식: `0 1 * * 1-5`

## 📊 성과 모니터링

### Slack Analytics 활용
1. 워크스페이스 Analytics 접속
2. 채널별 활동 확인
3. 메시지 조회율 추적

### 팀 피드백 수집
```
/poll "오늘의 포커 트렌드 리포트는 어떠셨나요?" 
"매우 유용함" "유용함" "보통" "개선 필요"
```

## 🔐 보안 권장사항

1. **Webhook URL 보호**
   - 절대 코드에 직접 포함하지 않기
   - GitHub Secrets 사용 필수
   - 정기적으로 URL 재생성

2. **채널 접근 제한**
   - 필요한 팀원만 채널 초대
   - 민감한 데이터는 비공개 채널 사용

3. **API 키 관리**
   - 3개월마다 키 로테이션
   - 사용량 모니터링
   - 이상 활동 알림 설정

## 💡 활용 팁

### 1. 스레드 토론 활성화
리포트 메시지에 스레드로 토론을 이어가며 인사이트 공유

### 2. 북마크 기능 활용
중요한 트렌드는 북마크하여 나중에 참조

### 3. 리마인더 설정
특정 트렌드에 대해 팔로우업이 필요한 경우 리마인더 설정

### 4. 외부 도구 연동
- Notion: 자동으로 데이터베이스에 저장
- Sheets: 트렌드 데이터 스프레드시트 연동
- Trello: 콘텐츠 아이디어 카드 자동 생성

## 📞 지원

문제가 발생하거나 개선 사항이 있다면:
- GitHub Issues 생성
- Slack #poker-trends-support 채널
- 관리자 직접 문의