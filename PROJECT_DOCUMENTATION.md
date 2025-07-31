# 포커 트렌드 분석 시스템 - 프로젝트 기획서

## 📋 프로젝트 개요

### 프로젝트명
YouTube 포커 트렌드 자동 분석 시스템

### 프로젝트 목적
YouTube에서 포커 관련 콘텐츠의 트렌드를 자동으로 수집, 분석하여 정량적 지표 기반의 인사이트를 제공하고, 이를 Slack을 통해 자동으로 공유하는 시스템 구축

### 핵심 가치
- **자동화**: 매일/매주/매월 자동으로 트렌드 분석
- **정량적 분석**: 조회수, 참여율, 바이럴 점수 등 객관적 지표 활용
- **실시간성**: 최신 트렌드를 빠르게 파악
- **접근성**: Slack을 통한 쉬운 정보 공유

## 🎯 주요 기능

### 1. 데이터 수집
- YouTube Data API v3를 활용한 비디오 메타데이터 수집
- 검색 키워드: "poker", "WSOP" 등 설정 가능
- 시간 필터링: 오늘, 24시간, 7일, 한달 등 다양한 기간 설정
- 상위 10개 비디오 선별 (조회수 기준)

### 2. 데이터 분석

#### 정량적 지표
- **조회수 (View Count)**: 비디오의 총 조회수
- **좋아요 (Like Count)**: 시청자의 긍정적 반응
- **댓글 (Comment Count)**: 시청자 참여도
- **참여율 (Engagement Rate)**: `(좋아요 + 댓글) ÷ 조회수 × 100`
- **바이럴 점수 (Viral Score)**: 복합 지표
  ```
  바이럴 점수 = log₁₀(조회수)×0.4 + 참여율×1000×0.3 + log₁₀(좋아요)×0.2 + log₁₀(댓글)×0.1
  ```

#### AI 분석 (Gemini AI)
- 트렌드 패턴 분석
- 인기 콘텐츠 특징 도출
- 콘텐츠 제작 아이디어 제안

### 3. 리포트 생성 및 전송

#### Slack 리포트 구성
- 📊 전체 통계 요약
- 👀 조회수 TOP 3 비디오 (클릭 가능한 제목)
- 💎 최고 참여율 비디오
- ⏰ 업로드 시간 분포
- 🤖 AI 인사이트
- 📐 참여율 계산 공식 표시

#### 스케줄링
- **일간 업데이트**: 매일 오전 10시 (최근 24시간 또는 오늘)
- **주간 업데이트**: 매주 월요일 (최근 7일)
- **월간 업데이트**: 매월 첫째 월요일 (지난달 전체)

## 🛠 기술 스택

### 개발 환경
- **언어**: Python 3.x
- **플랫폼**: Windows (UTF-8 인코딩 처리)
- **패키지 관리**: pip

### 주요 라이브러리
```python
googleapiclient  # YouTube Data API
google-generativeai  # Gemini AI
requests  # HTTP 통신
python-dotenv  # 환경변수 관리
schedule  # 스케줄링
```

### 외부 API
- **YouTube Data API v3**: 비디오 데이터 수집
- **Gemini AI (gemini-1.5-flash)**: AI 트렌드 분석
- **Slack Webhook**: 메시지 전송

## 📁 프로젝트 구조

```
poker-trend/
├── .env                          # API 키 및 환경변수
├── requirements.txt              # 의존성 패키지
├── README.md                     # 프로젝트 소개
├── PROJECT_PROPOSAL.md           # 초기 기획서
├── TECHNICAL_ARCHITECTURE.md     # 기술 아키텍처
├── PROJECT_DOCUMENTATION.md      # 종합 문서 (현재 파일)
│
├── daily_today_poker.py          # 오늘 필터 일간 분석
├── daily_keyword_analyzer.py     # 24시간 일간 분석
├── multi_schedule_analyzer.py    # 일/주/월 통합 스케줄러
├── enhanced_slack_report.py      # 향상된 Slack 리포트
│
├── wsop_analysis.py              # WSOP 키워드 특화 분석
├── wsop_demo_clear.py            # WSOP 데모 (명확한 설명)
├── engagement_rate_demo.py       # 참여율 계산 설명
│
└── test_slack_message.py         # Slack 메시지 테스트

```

## 💻 구현 상세

### 1. 일간 분석 (daily_today_poker.py)

```python
# 오늘 00:00 이후 업로드된 비디오만 검색
today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
today_start_iso = today_start.isoformat() + 'Z'

search_response = self.youtube.search().list(
    q=self.search_keyword,
    part='id,snippet',
    maxResults=50,
    order='relevance',
    type='video',
    regionCode='US',
    publishedAfter=today_start_iso  # 오늘 00:00 이후
).execute()
```

### 2. 참여율 계산 및 표시

```python
# 참여율 계산
engagement_rate = ((like_count + comment_count) / view_count) if view_count > 0 else 0

# Slack 메시지에 공식 표시
f"• 평균 참여율: *{self.analysis['avg_engagement']*100:.2f}%*\n"
f"  _→ 참여율 = (좋아요 + 댓글) ÷ 조회수 × 100_"
```

### 3. 클릭 가능한 비디오 제목

```python
# Slack 링크 형식으로 제목 변환
linked_title = f"<{video['url']}|{title}>"
```

### 4. Windows 인코딩 처리

```python
# UTF-8 인코딩 설정
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
```

## 📊 실행 결과 예시

### 일간 분석 결과 (2025-07-31)
- **검색 키워드**: poker
- **검색 필터**: 오늘 업로드된 영상
- **수집 비디오**: 50개 중 조회수 상위 10개
- **총 조회수**: 234,580
- **평균 참여율**: 1.69%
- **1위 비디오**: "Mariano, Britney & Henry Play $25/50/100" (62,815 조회)

## 🚀 향후 개선 계획

### 단기 계획
1. 다중 키워드 동시 분석 기능
2. 채널별 성과 추적
3. 트렌드 변화 그래프 생성
4. 이메일 리포트 옵션

### 장기 계획
1. 웹 대시보드 개발
2. 실시간 모니터링 시스템
3. 경쟁 채널 분석 기능
4. 콘텐츠 추천 AI 고도화

## 📝 사용 방법

### 1. 환경 설정
```bash
# .env 파일 생성
YOUTUBE_API_KEY=your_youtube_api_key
GEMINI_API_KEY=your_gemini_api_key
SLACK_WEBHOOK_URL=your_slack_webhook_url
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 실행
```bash
# 일간 분석 (오늘)
python daily_today_poker.py

# 일간 분석 (24시간)
python daily_keyword_analyzer.py

# 통합 스케줄러 실행
python multi_schedule_analyzer.py
```

## ⚠️ 주의사항

1. **YouTube API 할당량**: 일일 10,000 유닛 제한
2. **시간대**: UTC 기준으로 시간 계산
3. **인코딩**: Windows에서 UTF-8 처리 필수
4. **API 키 보안**: .env 파일을 git에 포함시키지 않을 것

## 📄 라이선스
이 프로젝트는 내부 사용 목적으로 개발되었습니다.

---

*마지막 업데이트: 2025년 7월 31일*