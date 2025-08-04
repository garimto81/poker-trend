# Webhook 설정 가이드

## 개요
이 프로젝트는 다음 3개의 API 키만 필요합니다:
- `YOUTUBE_API_KEY` - YouTube 데이터 수집
- `SLACK_WEBHOOK_URL` - Slack 알림 전송
- `GEMINI_API_KEY` - AI 분석 (향후 구현 예정)

## 1. YouTube API 키 발급

### 1.1 Google Cloud Console 접속
1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 프로젝트 생성 또는 선택

### 1.2 YouTube Data API v3 활성화
1. "API 및 서비스" → "라이브러리"
2. "YouTube Data API v3" 검색
3. "사용 설정" 클릭

### 1.3 API 키 생성
1. "API 및 서비스" → "사용자 인증 정보"
2. "+ 사용자 인증 정보 만들기" → "API 키"
3. 생성된 API 키 복사

## 2. Slack Webhook URL 생성

### 2.1 Slack App 생성
1. [Slack API](https://api.slack.com/apps) 접속
2. "Create New App" → "From scratch"
3. App Name: `Poker Trend Bot`
4. Workspace 선택

### 2.2 Incoming Webhooks 설정
1. 좌측 메뉴에서 "Incoming Webhooks" 클릭
2. "Activate Incoming Webhooks" 토글 ON
3. "Add New Webhook to Workspace" 클릭
4. 알림을 받을 채널 선택
5. Webhook URL 복사 (https://hooks.slack.com/services/...)

## 3. Gemini API 키 발급 (선택사항)

### 3.1 Google AI Studio 접속
1. [Google AI Studio](https://makersuite.google.com/app/apikey) 접속
2. "Get API Key" 클릭
3. 프로젝트 선택 또는 생성
4. API 키 복사

## 4. GitHub Secrets 설정

### 4.1 GitHub 저장소 설정
1. GitHub 저장소 → Settings → Secrets and variables → Actions
2. "New repository secret" 클릭

### 4.2 Secret 추가
각각 다음과 같이 추가:

#### YOUTUBE_API_KEY
- Name: `YOUTUBE_API_KEY`
- Secret: (YouTube API 키 붙여넣기)

#### SLACK_WEBHOOK_URL
- Name: `SLACK_WEBHOOK_URL`
- Secret: (Slack Webhook URL 붙여넣기)

#### GEMINI_API_KEY (선택사항)
- Name: `GEMINI_API_KEY`
- Secret: (Gemini API 키 붙여넣기)

## 5. GitHub Actions 실행

### 5.1 수동 실행
1. GitHub 저장소 → Actions 탭
2. "YouTube Trends Webhook" workflow 선택
3. "Run workflow" 버튼 클릭
4. Branch: master 선택
5. "Run workflow" 클릭

### 5.2 자동 실행 확인
- 매일 오전 10시(한국시간)에 자동 실행됨
- Actions 탭에서 실행 이력 확인 가능

## 6. Slack 메시지 확인

설정한 Slack 채널에서 다음과 같은 메시지를 확인:

```
🎰 오늘의 포커 YouTube 트렌드 (2025.01.31)

📊 전체 요약
• 총 분석 영상: 50개
• 평균 조회수: 125.3K회

🔥 TOP 5 급상승 영상
1. [영상 제목]
   채널: [채널명]
   조회수: [조회수]
   ▶️ 바로가기
...
```

## 문제 해결

### YouTube API 오류
- API 키가 올바른지 확인
- YouTube Data API v3가 활성화되었는지 확인
- 일일 할당량(10,000 유닛) 초과 여부 확인

### Slack Webhook 오류
- Webhook URL이 올바른지 확인
- 채널이 존재하는지 확인
- Webhook이 활성화되어 있는지 확인

### 실행 실패
- GitHub Actions 로그 확인
- Secret이 올바르게 설정되었는지 확인
- Python 스크립트 오류 메시지 확인