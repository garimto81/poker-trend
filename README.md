# 📊 Poker Trend Analysis System

YouTube에서 포커 관련 트렌드를 분석하고 Slack으로 리포트를 자동 전송하는 GitHub Actions 기반 자동화 시스템입니다.

## 🎯 주요 기능

- **YouTube 트렌드 분석**: 포커 관련 영상의 조회수, 인기도, 채널 분석
- **AI 기반 인사이트**: Gemini AI를 활용한 트렌드 요약 및 콘텐츠 아이디어 제안
- **자동 Slack 리포트**: 평일 매일 오전 10시 자동 리포트 전송
- **다양한 리포트 타입**: 일간, 주간, 월간 리포트 자동 생성
- **하이퍼링크 지원**: 클릭 가능한 YouTube 영상 링크 제공

## 📅 자동 실행 스케줄

- **일간 리포트**: 화~금요일 오전 10시 (KST)
- **주간 리포트**: 월요일 오전 10시 (첫째주 제외)
- **월간 리포트**: 매월 첫째주 월요일 오전 10시

## 📋 리포트 내용

### 일간 리포트
- 🔍 **검색 키워드**: 사용된 검색어 목록
- 🎬 **TOP 채널**: 가장 많은 영상을 업로드한 채널 TOP 5
- 🤖 **AI 트렌드 분석**: 당일 트렌드 한 줄 요약
- 📺 **TOP 5 영상**: 조회수 기준 상위 5개 영상 (하이퍼링크 포함)
- 💡 **AI 쇼츠 아이디어**: 5개의 창의적인 콘텐츠 제안

### 주간/월간 리포트
- 📊 기간별 통계 분석
- 🏆 채널별 순위
- 📈 성장 트렌드
- 🎯 카테고리별 분석

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

`backend/data-collector/scripts/youtube_trend_webhook_enhanced.py` 파일에서 `search_terms` 리스트를 수정:

```python
self.search_terms = [
    'poker', '포커', 'holdem', '홀덤', 
    'WSOP', 'WPT', 'EPT', 
    # 원하는 키워드 추가
]
```

### 3. 수동 실행

GitHub Actions 탭에서 "Unified Trend Reporting" 워크플로우를 선택하고 "Run workflow" 클릭

## 📁 프로젝트 구조

```
poker-trend/
├── .github/
│   └── workflows/
│       └── unified-reporting.yml      # 메인 워크플로우
├── backend/
│   └── data-collector/
│       └── scripts/
│           ├── youtube_trend_webhook_enhanced.py  # 일간 리포트
│           ├── weekly_trend_report.py            # 주간 리포트
│           └── monthly_trend_report.py           # 월간 리포트
└── docs/                              # 문서 및 가이드
```

## 📊 Slack 메시지 예시

```
🎰 포커 트렌드 분석 리포트

📅 2025-08-04
📊 분석 영상: 87개

🔍 검색 키워드: poker, 포커, holdem, 홀덤, WSOP, WPT

🎬 TOP 채널: PokerGO (15개), PokerStars (12개), 포커마스터TV (8개)

🤖 AI 트렌드 분석
WSOP 시즌으로 토너먼트 콘텐츠가 급증하며, 프로 선수들의 블러프 영상이 높은 참여율을 보임

📺 TOP 5 인기 영상
1. Phil Ivey's INSANE Bluff at WSOP 2024! → 385,234 views
   (클릭하면 YouTube로 이동)
...

💡 AI 쇼츠 아이디어
1. "5초 만에 배우는 포커 용어" 시리즈
2. "프로 vs 아마추어 텔 구분법"
...
```

## 🤝 기여 방법

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.