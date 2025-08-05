# 📊 YouTube 포커 트렌드 통합 분석 시스템

YouTube 포커 트렌드를 일간, 주간, 월간으로 체계적으로 분석하여 Slack으로 자동 전송하는 통합 리포팅 시스템입니다.

## 🎯 주요 기능

- **통합 리포팅 체계**: 일간(매일), 주간(월요일), 월간(첫째주 월요일) 분석
- **키워드별 데이터 수집**: 8개 키워드 각각 상위 5개 영상 수집
- **Gemini AI 심층 분석**: 
  - 🎯 트렌드 패턴 인식 및 예측
  - 📊 시장 역학 분석
  - 🔮 1주-1개월 미래 트렌드 예측
  - 💡 맞춤형 콘텐츠 전략 제안
- **자동 Slack 전송**: 평일 오전 10시 자동 리포트 전송
- **하이퍼링크 지원**: 모든 영상 링크 클릭 가능

## 📅 리포팅 스케줄

### 자동 실행 시간
- **모든 리포트**: 평일 오전 10시 (KST)
- **주말 제외**: 토요일, 일요일 실행 안함

### 리포트 타입별 스케줄
- **월간 리포트**: 매월 첫째주 월요일 (지난 30일 분석)
- **주간 리포트**: 매주 월요일 - 첫째주 제외 (지난 7일 분석)
- **일간 리포트**: 화~금요일 (최근 24시간 분석)

## 📋 리포트 내용

### 공통 분석 항목
- 🔍 **검색 키워드**: 8개 영어 키워드 (poker, holdem, wsop, wpt, ept, pokerstars, ggpoker, triton poker)
- 📊 **키워드별 TOP 5**: 각 키워드당 조회수 상위 5개 영상
- 🎬 **채널 통계**: 가장 활발한 채널 및 조회수
- 🤖 **Gemini AI 심층 추론**:
  - 현재 트렌드의 근본 원인 분석
  - 숨겨진 패턴 발견
  - 미래 트렌드 예측 (확률 기반)
  - 실행 가능한 전략 제안

### 리포트 타입별 특징
- **일간**: 오늘의 핫 토픽, 즉각적인 트렌드
- **주간**: 주간 트렌드 변화, 성장률 분석
- **월간**: 종합 통계, 장기 트렌드 예측

## 🛠️ 기술 스택

- **언어**: Python 3.11
- **API**: YouTube Data API v3, Gemini AI API
- **자동화**: GitHub Actions
- **알림**: Slack Webhook

## ⚙️ 설정 방법

### 1. 필수 API 키 설정

GitHub Repository Settings → Secrets and variables → Actions에서 다음 시크릿을 추가:

```
YOUTUBE_API_KEY     # YouTube Data API v3 키
SLACK_WEBHOOK_URL   # Slack Webhook URL
GEMINI_API_KEY      # Google Gemini API 키
```

### 2. 검색 키워드 수정

검색 키워드는 `docs/SEARCH_KEYWORDS.md` 파일에 정의되어 있습니다.

현재 설정된 키워드 (영어 전용, Global 검색):
- poker, holdem, wsop, wpt, ept, pokerstars, ggpoker, triton poker

키워드 변경 시:
1. `docs/SEARCH_KEYWORDS.md` 파일 수정
2. `backend/data-collector/scripts/youtube_trend_webhook_enhanced.py`의 `search_terms` 업데이트

### 3. 수동 실행

GitHub Actions 탭에서 "Integrated Poker Trend Reporting" 워크플로우를 선택하고 "Run workflow" 클릭

수동 실행 시 리포트 타입 선택:
- `auto`: 날짜에 따라 자동 결정
- `daily`: 일간 리포트 강제 실행
- `weekly`: 주간 리포트 강제 실행
- `monthly`: 월간 리포트 강제 실행

## 📁 프로젝트 구조

```
poker-trend/
├── .github/
│   └── workflows/
│       └── integrated-reporting.yml      # 통합 리포팅 워크플로우
├── backend/
│   └── data-collector/
│       └── scripts/
│           └── integrated_trend_analyzer.py  # 통합 분석 스크립트
├── docs/
│   ├── SEARCH_KEYWORDS.md                # 검색 키워드 설정
│   ├── planning/
│   │   └── INTEGRATED_REPORTING_SYSTEM.md # 통합 시스템 설계
│   ├── technical/
│   │   └── GEMINI_AI_TREND_INFERENCE.md  # AI 트렌드 추론 시스템
│   └── guides/
│       └── daily-slack-setup.md          # Slack 설정 가이드
└── README.md
```

## 📊 Slack 메시지 예시

### 일간 리포트
```
🎰 포커 트렌드 일일 분석
━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 2025년 1월 15일 (수)
⏰ 분석 기간: 최근 24시간
📊 분석 영상: 35개

🤖 AI 트렌드 심층 분석
────────────────
【현재 트렌드】
WSOP 관련 콘텐츠가 전체 조회수의 45%를 차지하며 압도적인 
관심을 받고 있습니다. 이는 단순한 토너먼트 인기를 넘어 
"큰 판돈의 심리전"에 대한 시청자들의 갈증을 보여줍니다.

【숨겨진 패턴】
• 블러프 성공 영상이 스트레이트 플러시보다 3배 높은 참여율
• 오후 2-4시 업로드 영상이 저녁 시간대보다 2.5배 높은 도달률
• 5-10분 길이의 하이라이트가 풀 영상보다 완주율 85% 높음

【24시간 예측】
🔺 상승 예상 (신뢰도 78%): Phil Ivey 관련 콘텐츠
🔺 신규 트렌드 (신뢰도 65%): 온라인 포커 사기 방지 콘텐츠
🔻 하락 예상 (신뢰도 82%): 초보자 튜토리얼

【즉시 실행 전략】
1. "Phil Ivey vs Daniel Negreanu" 대결 구도 콘텐츠 제작
2. 오후 2-3시 사이 업로드 (골든 타임)
3. 썸네일에 칩 스택과 확률 표시 필수

📺 키워드별 TOP 영상
────────────────
【poker】
1. Epic Final Table at WSOP 2025
   조회수: 125,430 | PokerGO
   
【holdem】
1. Texas Hold'em Million Dollar Cash Game
   조회수: 98,765 | Hustler Casino

[... 각 키워드별 상위 영상 ...]
```

### 주간 리포트
```
📊 포커 트렌드 주간 분석
━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 2025년 1월 13일 - 19일
⏰ 분석 기간: 지난 7일
📊 분석 영상: 280개

🤖 AI 주간 인사이트
────────────────
이번 주는 고액 캐시게임 콘텐츠가 폭발적인 성장을 보였습니다. 
Triton Poker 시리즈의 시작과 함께 프리미엄 콘텐츠 수요가 
급증했으며, 다음 주에도 이러한 트렌드가 지속될 전망입니다.

추천 콘텐츠 전략:
1. 고액 캐시게임 하이라이트
2. 프로 선수 인터뷰
3. 전략 분석 콘텐츠

[... 더 상세한 주간 분석 ...]
```

## 🤝 기여 방법

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.