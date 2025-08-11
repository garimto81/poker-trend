# GitHub Actions 자동 실행 설정 가이드

GitHub Actions를 사용하여 매일 자동으로 YouTube 포커 트렌드를 분석하고 Slack으로 알림을 보내는 방법입니다.

## 📋 사전 준비사항

1. **YouTube Data API 키**
2. **Slack Bot Token 및 Channel ID**
3. **GitHub 저장소 접근 권한**

## 🔑 Step 1: GitHub Secrets 설정

GitHub 저장소에서 다음 Secret들을 설정해야 합니다.

### 1.1 Secrets 페이지 접속
1. GitHub 저장소로 이동
2. **Settings** 탭 클릭
3. 좌측 메뉴에서 **Secrets and variables** → **Actions** 클릭
4. **New repository secret** 버튼 클릭

### 1.2 필수 Secrets 추가

다음 Secret들을 하나씩 추가합니다:

#### `YOUTUBE_API_KEY`
- **Name**: `YOUTUBE_API_KEY`
- **Value**: YouTube Data API v3 키
- 발급 방법:
  1. [Google Cloud Console](https://console.cloud.google.com/) 접속
  2. 새 프로젝트 생성 또는 기존 프로젝트 선택
  3. YouTube Data API v3 활성화
  4. 사용자 인증 정보 → API 키 생성
  5. API 키 복사

#### `SLACK_BOT_TOKEN`
- **Name**: `SLACK_BOT_TOKEN`
- **Value**: `xoxb-`로 시작하는 Bot User OAuth Token
- 발급 방법: [Slack 알림 설정 가이드](./setup-slack-notification.md) 참조

#### `SLACK_CHANNEL_ID`
- **Name**: `SLACK_CHANNEL_ID`
- **Value**: Slack 채널 ID (예: C1234567890)
- 찾는 방법:
  1. Slack에서 채널 우클릭
  2. "View channel details" 클릭
  3. 하단의 Channel ID 복사

#### `SLACK_WEBHOOK_URL` (선택사항)
- **Name**: `SLACK_WEBHOOK_URL`
- **Value**: Slack Incoming Webhook URL
- Bot Token이 실패할 경우 백업으로 사용

## 🚀 Step 2: GitHub Actions 활성화

### 2.1 workflow 파일 확인
`.github/workflows/youtube-trend-analysis.yml` 파일이 저장소에 있는지 확인

### 2.2 Actions 탭에서 확인
1. GitHub 저장소의 **Actions** 탭 클릭
2. "YouTube Poker Trend Analysis" workflow 확인
3. 활성화되어 있는지 확인

## ⏰ Step 3: 실행 스케줄 설정

기본 설정은 매일 한국 시간 오전 10시입니다.

### 3.1 시간 변경하기
`.github/workflows/youtube-trend-analysis.yml` 파일의 cron 표현식 수정:

```yaml
on:
  schedule:
    # 매일 한국 시간 오전 10시 (UTC 01:00)
    - cron: '0 1 * * *'
```

#### Cron 표현식 예시:
- `0 1 * * *` - 매일 UTC 01:00 (KST 10:00)
- `0 22 * * *` - 매일 UTC 22:00 (KST 07:00)
- `0 1,13 * * *` - 매일 UTC 01:00, 13:00 (KST 10:00, 22:00)
- `0 1 * * 1-5` - 평일만 UTC 01:00

### 3.2 타임존 계산
- 한국 시간(KST) = UTC + 9시간
- 예: KST 10:00 = UTC 01:00

## 🧪 Step 4: 수동 테스트

### 4.1 수동 실행
1. **Actions** 탭으로 이동
2. "YouTube Poker Trend Analysis" 클릭
3. **Run workflow** 버튼 클릭
4. Branch 선택 (보통 main)
5. Debug mode 선택 (선택사항)
6. **Run workflow** 클릭

### 4.2 실행 모니터링
1. 실행 중인 workflow 클릭
2. 각 step의 로그 확인
3. 성공/실패 여부 확인

## 📊 Step 5: 실행 결과 확인

### 5.1 Slack 메시지 확인
설정한 Slack 채널에서 다음과 같은 메시지를 확인:
- 🎰 오늘의 포커 YouTube 트렌드
- TOP 5 급상승 영상
- 카테고리별 트렌드
- 인기 채널 TOP 3

### 5.2 GitHub에서 로그 확인
1. **Actions** 탭에서 실행된 workflow 클릭
2. "analyze-trends" job 클릭
3. 각 step의 상세 로그 확인

### 5.3 아티팩트 다운로드
실행 후 7일간 보관되는 분석 결과:
1. workflow 실행 페이지에서 "Artifacts" 섹션 확인
2. `trend-analysis-{run_number}` 다운로드
3. 로그 및 JSON 리포트 확인

## 🔧 Step 6: 문제 해결

### 6.1 일반적인 오류

#### "Missing required environment variable"
- GitHub Secrets가 올바르게 설정되었는지 확인
- Secret 이름이 정확한지 확인 (대소문자 구분)

#### "YouTube API error"
- API 키가 유효한지 확인
- YouTube Data API v3가 활성화되었는지 확인
- API 할당량이 남아있는지 확인

#### "Slack API error"
- Bot Token이 `xoxb-`로 시작하는지 확인
- Bot이 채널에 추가되었는지 확인
- 필요한 권한(chat:write)이 있는지 확인

### 6.2 디버그 모드 사용
1. 수동 실행 시 "Enable debug mode" 선택
2. 더 자세한 로그 출력 확인
3. 문제 원인 파악

## 📈 Step 7: 모니터링

### 7.1 실행 기록 확인
- **Actions** 탭에서 과거 실행 기록 확인
- 성공/실패 패턴 분석
- 실행 시간 모니터링

### 7.2 실패 알림
workflow가 실패하면 자동으로 Slack에 오류 알림 전송

### 7.3 GitHub 알림 설정
1. GitHub 프로필 → Settings → Notifications
2. Actions 알림 활성화
3. 이메일로 실패 알림 받기

## 🚨 보안 주의사항

1. **Secret 관리**
   - Secret 값을 코드에 직접 포함하지 마세요
   - 로그에 Secret이 출력되지 않도록 주의
   - Secret이 노출된 경우 즉시 재생성

2. **권한 최소화**
   - 필요한 최소한의 권한만 부여
   - 정기적으로 사용하지 않는 토큰 제거

3. **API 할당량 관리**
   - YouTube API: 일일 10,000 유닛 제한
   - 효율적인 API 호출로 할당량 절약

## 📚 추가 리소스

- [GitHub Actions 문서](https://docs.github.com/en/actions)
- [YouTube Data API 문서](https://developers.google.com/youtube/v3)
- [Slack API 문서](https://api.slack.com/)
- [Cron 표현식 생성기](https://crontab.guru/)

---

**문제가 발생하면 GitHub Issues에 문의해주세요!**