# 🧪 포커 트렌드 분석 시스템 테스트 가이드

## 📋 테스트 전 준비사항

### 1. API 키 준비
테스트를 위해 다음 3개의 API 키가 필요합니다:

#### YouTube Data API v3
1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. "API 및 서비스" → "라이브러리"에서 "YouTube Data API v3" 검색 및 활성화
4. "사용자 인증 정보" → "사용자 인증 정보 만들기" → "API 키"
5. API 키 복사

#### Google Gemini API
1. [Google AI Studio](https://makersuite.google.com/app/apikey) 접속
2. "Get API key" 클릭
3. 새 API 키 생성 또는 기존 키 사용
4. API 키 복사

#### Slack Webhook URL
1. [Slack API](https://api.slack.com/apps) 접속
2. "Create New App" → "From scratch"
3. App 이름과 워크스페이스 선택
4. "Incoming Webhooks" 활성화
5. "Add New Webhook to Workspace" → 채널 선택
6. Webhook URL 복사

### 2. 환경 변수 설정

#### 방법 1: .env 파일 사용 (권장)
```bash
cd backend/data-collector
cp .env.example .env
```

`.env` 파일을 열어 실제 값 입력:
```env
YOUTUBE_API_KEY=AIzaSy...실제키...
GEMINI_API_KEY=AIzaSy...실제키...
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T.../B.../...
```

#### 방법 2: 시스템 환경 변수
Windows:
```cmd
set YOUTUBE_API_KEY=your_key_here
set GEMINI_API_KEY=your_key_here
set SLACK_WEBHOOK_URL=your_webhook_here
```

Linux/Mac:
```bash
export YOUTUBE_API_KEY=your_key_here
export GEMINI_API_KEY=your_key_here
export SLACK_WEBHOOK_URL=your_webhook_here
```

## 🚀 테스트 실행

### 자동 테스트 스크립트

#### Windows
```cmd
cd backend/data-collector
run_test.bat
```

#### Linux/Mac
```bash
cd backend/data-collector
chmod +x run_test.sh
./run_test.sh
```

### 수동 테스트

1. **필요한 패키지 설치**
```bash
cd backend/data-collector
pip install -r requirements.txt
```

2. **테스트 스크립트 실행**
```bash
cd scripts
python test_integrated_analyzer.py
```

## 📊 테스트 항목

### 1. 환경 변수 확인
- 3개의 필수 API 키가 모두 설정되었는지 확인
- 키 형식이 올바른지 검증

### 2. YouTube API 테스트
- API 연결 확인
- 간단한 검색 쿼리 실행
- 응답 데이터 확인

### 3. Gemini AI 테스트
- API 연결 확인
- 간단한 프롬프트 실행
- AI 응답 확인

### 4. Slack Webhook 테스트 (선택적)
- 테스트 메시지 전송
- Slack 채널에서 메시지 수신 확인

### 5. 미니 분석 테스트 (선택적)
- 실제 데이터 수집 (제한된 키워드)
- 기본 분석 프로세스 실행
- 결과 확인

## 🎯 예상 출력

### 성공적인 테스트
```
===============================================
환경 변수 확인 중...
===============================================
✅ .env 파일 로드됨
✅ YOUTUBE_API_KEY: AIzaSy...
✅ GEMINI_API_KEY: AIzaSy...
✅ SLACK_WEBHOOK_URL: https://ho...

===============================================
YouTube API 테스트 중...
===============================================
✅ YouTube API 연결 성공!
   테스트 영상: Phil Ivey AMAZING Bluff at WSOP...

===============================================
Gemini AI API 테스트 중...
===============================================
✅ Gemini AI 연결 성공!
   응답: 포커 트렌드 분석 테스트 성공!

===============================================
📊 테스트 결과 요약
===============================================
environment: ✅ 성공
youtube_api: ✅ 성공
gemini_api: ✅ 성공
slack_webhook: ✅ 성공
mini_analysis: ✅ 성공

🎉 모든 테스트가 성공했습니다!
```

## 🔧 문제 해결

### API 키 오류
```
❌ 필수: YouTube Data API v3 키
```
→ API 키가 설정되지 않았거나 잘못된 형식입니다.

### YouTube API 할당량 초과
```
❌ YouTube API 오류: quotaExceeded
```
→ 일일 할당량을 초과했습니다. 내일 다시 시도하거나 새 프로젝트를 생성하세요.

### Gemini API 오류
```
❌ Gemini AI 오류: 403 Forbidden
```
→ API 키가 유효하지 않거나 Gemini API가 활성화되지 않았습니다.

### Slack Webhook 오류
```
❌ Slack 전송 실패: 404
```
→ Webhook URL이 잘못되었거나 만료되었습니다. 새 Webhook을 생성하세요.

## 📝 다음 단계

테스트가 성공적으로 완료되면:

1. **전체 분석 실행**
```bash
python integrated_trend_analyzer.py --report-type daily
```

2. **GitHub Actions 설정**
- Repository Settings → Secrets and variables → Actions
- 3개의 시크릿 추가 (YOUTUBE_API_KEY, GEMINI_API_KEY, SLACK_WEBHOOK_URL)

3. **자동 실행 확인**
- 평일 오전 10시에 자동으로 실행되는지 확인
- Actions 탭에서 워크플로우 상태 모니터링

## 💡 팁

1. **테스트 데이터 제한**
   - 테스트 시에는 키워드를 2-3개로 제한하여 API 할당량 절약
   - `maxResults`를 5 이하로 설정

2. **로그 확인**
   - 상세한 디버그 정보가 필요하면 로깅 레벨을 DEBUG로 변경
   - 로그 파일은 `reports/` 폴더에 저장됨

3. **Slack 채널 준비**
   - 테스트용 별도 채널 생성 권장
   - 중요한 채널에 테스트 메시지가 가지 않도록 주의