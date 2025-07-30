# 포커 트렌드 일일 자동 실행 및 슬랙 알림 가이드

## 🎯 구현된 기능

### ✅ 완전 자동화 시스템
1. **매일 정해진 시간 자동 실행** (기본: 오전 9시)
2. **정량적 트렌드 분석 수행**
3. **슬랙 채널에 결과 자동 전송**
4. **오류 발생 시 알림**
5. **API 할당량 초과 시 특별 알림**

## 🔧 설정 방법

### 1. 슬랙 웹훅 URL 생성

#### 단계별 가이드:
1. **슬랙 워크스페이스 접속**
   - https://api.slack.com/messaging/webhooks

2. **Incoming Webhooks 앱 설치**
   - "Create your Slack app" 클릭
   - "From scratch" 선택
   - 앱 이름: "포커트렌드봇" 입력
   - 워크스페이스 선택

3. **웹훅 활성화**
   - "Incoming Webhooks" 메뉴
   - "Activate Incoming Webhooks" ON
   - "Add New Webhook to Workspace" 클릭

4. **채널 선택**
   - 알림을 받을 채널 선택 (예: #poker-trends)
   - "Allow" 클릭

5. **웹훅 URL 복사**
   - 생성된 URL 복사 (https://hooks.slack.com/services/...)

### 2. 환경 변수 설정

**.env 파일 업데이트:**
```bash
# 기존 API 키들
YOUTUBE_API_KEY=your_youtube_api_key
GEMINI_API_KEY=your_gemini_api_key

# 새로 추가: 슬랙 웹훅 URL
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
```

### 3. 필수 라이브러리 설치

```bash
pip install schedule
```

또는 전체 재설치:
```bash
pip install -r requirements.txt
```

## 🚀 실행 방법

### 방법 1: 일일 스케줄러 시작 (메인)
```bash
python daily_scheduler.py
```
- 매일 오전 9시에 자동 실행
- 백그라운드에서 지속적으로 동작
- Ctrl+C로 중단 가능

### 방법 2: 즉시 테스트 실행
```bash
python daily_scheduler.py test
```
- 스케줄 기다리지 않고 바로 실행
- 시스템 동작 확인용

### 방법 3: 슬랙 알림만 테스트
```bash
python daily_scheduler.py test slack
```
- 슬랙 연결 상태만 확인
- 테스트 메시지 전송

## 📱 슬랙 알림 예시

### 성공 시 알림 형태:
```
🎯 포커 트렌드 일일 분석 리포트 - 2025-07-31

📊 총 분석 비디오: 50개
👀 총 조회수: 24,442,808회  
👍 총 좋아요: 500,134개
💬 평균 참여율: 0.023

🏆 키워드별 성과 순위 (바이럴 점수 기준)

🥇 GTO
바이럴점수: 14.4 | 평균조회수: 6,434 | 참여율: 0.041

🥈 Holdem  
바이럴점수: 11.9 | 평균조회수: 1,699,133 | 참여율: 0.030

🥉 Cashgame
바이럴점수: 10.0 | 평균조회수: 113,850 | 참여율: 0.024

💡 핵심 인사이트
• 최고 성과: GTO (신뢰도: 95%)
• 최고 모멘텀: GTO (신뢰도: 85%)  
• 최고 참여도: GTO (신뢰도: 90%)

🎬 오늘의 TOP 성과 비디오
🏆 WSOP 카테고리
조회수: 30,118 | 참여율: 0.079 | 바이럴점수: 26.3
```

### 오류 시 알림 형태:
```
❌ 포커 트렌드 일일 분석 실패
시간: 2025-07-31 09:00:15
오류: YouTube API 할당량 초과

💡 대안책
• 새 Google Cloud 프로젝트 생성
• 추가 API 키 발급  
• 기존 분석 데이터 활용
```

## ⚙️ 고급 설정

### 실행 시간 변경
`daily_scheduler.py` 파일에서 수정:
```python
# 오전 9시 → 오전 8시로 변경
schedule.every().day.at("08:00").do(...)

# 하루에 2번 실행 (오전 9시, 오후 6시)
schedule.every().day.at("09:00").do(...)
schedule.every().day.at("18:00").do(...)
```

### 여러 슬랙 채널에 전송
```python
# 여러 웹훅 URL 사용
SLACK_WEBHOOK_URL_1=https://hooks.slack.com/...  # #poker-trends
SLACK_WEBHOOK_URL_2=https://hooks.slack.com/...  # #analytics
```

## 🖥️ 서버 배포 (선택사항)

### Linux/Mac 서버에서 백그라운드 실행:
```bash
# nohup으로 백그라운드 실행
nohup python daily_scheduler.py > scheduler.log 2>&1 &

# 프로세스 확인
ps aux | grep daily_scheduler

# 중단
kill [프로세스ID]
```

### Windows에서 서비스로 실행:
- 작업 스케줄러 사용
- 시스템 시작 시 자동 실행 가능

## 📊 로그 및 모니터링

### 로그 파일:
- `daily_scheduler.log` - 스케줄러 실행 로그
- `poker_trend_analyzer.log` - 분석기 실행 로그

### 로그 확인:
```bash
# 실시간 로그 확인
tail -f daily_scheduler.log

# 최근 로그 확인  
tail -20 daily_scheduler.log
```

## 🎉 완성된 워크플로우

1. **매일 오전 9시** → 자동 실행
2. **YouTube API** → 최신 비디오 50개 수집
3. **정량적 분석** → 바이럴 점수, 참여율, 트렌드 모멘텀 계산
4. **슬랙 알림** → 채널에 자동으로 분석 결과 전송
5. **JSON 저장** → 상세 데이터 파일로 보관
6. **오류 처리** → 문제 발생시 즉시 알림

**✅ 이제 완전 자동화된 포커 트렌드 분석 시스템이 완성되었습니다!**

매일 자동으로 실행되어 슬랙으로 트렌드 리포트를 받아볼 수 있습니다. 🚀