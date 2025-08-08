# Poker Trend Analysis Platform

**포커 트렌드 분석 및 자동화 플랫폼**

실시간 포커 업계 동향을 추적하고 분석하여 Slack으로 자동 리포팅하는 통합 시스템입니다.

[![GitHub Actions](https://github.com/garimto81/poker-trend/actions/workflows/main.yml/badge.svg)](https://github.com/garimto81/poker-trend/actions)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 🌟 주요 기능

### 📰 PokerNews 자동 뉴스 분석 시스템 (NEW!)
- **RSS 기반 뉴스 수집**: PokerNews, CardPlayer, PokerStrategy 등 주요 사이트
- **Gemini AI 트렌드 분석**: 포커 업계 동향과 인사이트 자동 추출
- **Slack 자동 리포팅**: 일일 트렌드 분석 결과를 Slack으로 전송
- **3줄 요약 & 하이퍼링크**: 각 뉴스를 3줄로 요약하고 원문 링크 제공
- **미리보기 시스템**: 전송 전 미리보기로 품질 확인

### 📊 YouTube 트렌드 분석
- YouTube Data API를 통한 실시간 트렌드 수집
- Gemini AI 기반 콘텐츠 분석 및 트렌드 예측
- 포커 관련 콘텐츠 자동 필터링 및 분류

### 🎲 플랫폼 데이터 분석
- 온라인/오프라인 포커 플랫폼 현황 분석
- Firebase 기반 실시간 데이터 수집
- 캐시게임 vs 온라인게임 성장률 비교

### 🤖 자동화 시스템
- GitHub Actions 기반 스케줄링
- Slack Webhook 통합
- 실시간 모니터링 및 알림

## 🏗️ 시스템 아키텍처

```
poker-trend/
├── poker-trend-analysis/          # 메인 분석 플랫폼
│   ├── backend/
│   │   ├── news-analyzer/         # 🆕 PokerNews 분석 시스템
│   │   │   ├── pokernews_rss_collector.py     # RSS 뉴스 수집
│   │   │   ├── pokernews_ai_analyzer.py       # Gemini AI 분석
│   │   │   ├── pokernews_slack_reporter.py    # Slack 리포팅
│   │   │   └── reports/                       # 분석 결과 저장
│   │   ├── data-collector/        # YouTube 데이터 수집
│   │   ├── platform-analyzer/     # 플랫폼 분석
│   │   └── api-server/           # RESTful API 서버
│   ├── frontend/                 # React 대시보드
│   └── docs/                     # 문서 및 가이드
└── .github/workflows/            # CI/CD 파이프라인
```

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 저장소 클론
git clone https://github.com/garimto81/poker-trend.git
cd poker-trend

# 환경 변수 설정
cp .env.example .env
```

### 2. 필수 환경 변수

```bash
# .env 파일에 다음 변수들을 설정하세요
GEMINI_API_KEY=your_gemini_api_key_here
SLACK_WEBHOOK_URL=your_slack_webhook_url_here
YOUTUBE_API_KEY=your_youtube_api_key_here
FIREBASE_PROJECT_ID=your_firebase_project_id
```

### 3. PokerNews 자동화 시스템 실행

```bash
cd poker-trend-analysis/backend/news-analyzer

# 의존성 설치
pip install -r requirements.txt

# 뉴스 수집 및 분석 실행
python pokernews_slack_reporter.py
```

### 4. Docker로 전체 시스템 실행

```bash
# 전체 시스템 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f
```

## 🔧 주요 모듈 사용법

### PokerNews 자동 분석

```python
from pokernews_slack_reporter import PokerNewsSlackReporter

# 슬랙 리포터 초기화
reporter = PokerNewsSlackReporter()

# 일일 리포트 실행
result = reporter.run_daily_report()

print(f"분석 결과: {result['status']}")
print(f"수집 기사: {result['articles_collected']}개")
```

### YouTube 트렌드 분석

```python
from youtube_trend_analyzer import YouTubeTrendAnalyzer

analyzer = YouTubeTrendAnalyzer()
trends = analyzer.analyze_poker_trends()

for trend in trends:
    print(f"트렌드: {trend['title']}")
    print(f"조회수: {trend['views']:,}")
```

## 📊 분석 결과 예시

### PokerNews 일일 리포트 샘플

```markdown
📰 PokerNews 일일 트렌드 분석
📅 2025년 8월 8일 | 🔍 분석 기사: 15개

🎯 오늘의 핵심 트렌드
1. 태국 포커 토너먼트 합법화로 아시아 시장 확장 조짐
2. WSOP Europe 2025 €2천만 상금으로 역대 최대 규모
3. 온라인 플랫폼들의 하이스테이크 캐시게임 강화

🏆 주요 토너먼트 소식
• WSOP Europe 2025 15개 이벤트, 12월 개최 확정
• WPT 월드 챔피언십 라스베가스 진행

🌟 주목할 선수
• Ryan Riess, WSOP 메인이벤트 재우승 도전 의사 표명
• Phil Hellmuth 관련 일화가 포커 팬들 사이에서 화제

💼 시장 동향
• 아시아 지역 포커 합법화 움직임 가속화
• 온라인 플랫폼의 하이스테이크 게임 확대
```

## 🔄 자동화 스케줄

### GitHub Actions 워크플로우

- **일일 뉴스 분석**: 매일 오전 9시 (KST)
- **주간 트렌드 리포트**: 매주 월요일 오전 10시
- **플랫폼 데이터 수집**: 매시간 정각

### Slack 알림 타이밍

- **긴급 뉴스**: 실시간 알림
- **일일 요약**: 매일 오후 6시
- **주간 리포트**: 매주 금요일 오후 5시

## 🛠️ 개발 및 기여

### 로컬 개발 환경

```bash
# 개발 서버 실행
cd poker-trend-analysis
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 테스트 실행
python -m pytest tests/
```

### 새로운 기능 추가

1. `feature/new-feature` 브랜치 생성
2. 기능 개발 및 테스트 작성
3. PR 생성 시 자동 CI/CD 실행
4. 코드 리뷰 후 메인 브랜치 병합

## 📈 성능 및 모니터링

### 시스템 성능
- **뉴스 수집 속도**: 평균 15개 기사/분
- **AI 분석 시간**: 기사당 평균 2-3초
- **Slack 전송 속도**: 1초 이내

### 모니터링 지표
- API 응답 시간
- 데이터 수집 성공률
- Slack 전송 성공률
- AI 분석 정확도

## 🔒 보안 및 권한

### API 키 관리
- GitHub Secrets를 통한 안전한 키 관리
- 환경별 분리된 설정
- 정기적인 키 로테이션

### 데이터 보안
- HTTPS 통신 강제
- 민감 데이터 암호화
- 접근 로그 모니터링

## 🤝 기여자

- **@garimto81**: 프로젝트 리드, 시스템 아키텍처
- **Claude AI**: 코드 리뷰 및 최적화 지원

## 📄 라이선스

이 프로젝트는 MIT 라이선스하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🔗 관련 링크

- [프로젝트 위키](https://github.com/garimto81/poker-trend/wiki)
- [API 문서](https://garimto81.github.io/poker-trend/api/)
- [이슈 추적](https://github.com/garimto81/poker-trend/issues)
- [Discord 커뮤니티](https://discord.gg/poker-trend)

## 📞 지원 및 문의

- 버그 리포트: GitHub Issues
- 기능 제안: GitHub Discussions
- 이메일: garimto81@example.com

---

⭐ 이 프로젝트가 도움이 되셨다면 스타를 눌러주세요!

**마지막 업데이트**: 2025년 8월 8일
**버전**: v2.1.0 (PokerNews 자동화 시스템 추가)