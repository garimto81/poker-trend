# 📰 PokerNews AI 트렌드 분석 시스템

## 🎯 개요

PokerNews.com에서 최신 포커 뉴스를 자동으로 수집하고, Gemini AI로 트렌드를 분석하여 매일 Slack으로 리포팅하는 시스템입니다.

## 🚀 주요 기능

### 1. 뉴스 수집 (`pokernews_collector.py`)
- PokerNews.com의 다양한 섹션에서 최신 뉴스 수집
  - 메인 뉴스 (`/news/`)
  - 전략 기사 (`/strategy/`)
  - 토너먼트 소식 (`/tours/`)
  - 온라인 포커 (`/online-poker/`)
  - 라이브 리포팅 (`/live-reporting/`)
- BeautifulSoup을 활용한 웹 스크래핑
- 중복 제거 및 날짜순 정렬
- 오늘/어제 날짜 뉴스 필터링

### 2. AI 분석 (`pokernews_ai_analyzer.py`)
- Gemini AI를 활용한 심층 트렌드 분석
- 분석 항목:
  - 🎯 핵심 트렌드 (3-5개)
  - 🏆 주요 토너먼트 소식
  - 🌟 주목할 선수/인물
  - 💼 시장 동향 및 비즈니스
  - 🔮 향후 전망 (단기/중기)
  - 💡 콘텐츠 아이디어 추천
  - 📝 한 줄 요약
- 한국어 번역 및 로컬라이징

### 3. Slack 리포팅 (`pokernews_slack_reporter.py`)
- 매일 오전 9시 30분 자동 실행 (KST)
- 구조화된 Slack 메시지 포맷
- 주요 기사 링크 포함
- 에러 발생 시 자동 알림

## 📦 설치 방법

### 1. 의존성 설치

```bash
cd backend/news-analyzer
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일 생성:
```env
GEMINI_API_KEY=your_gemini_api_key
SLACK_WEBHOOK_URL=your_slack_webhook_url
```

### 3. GitHub Secrets 설정

GitHub 저장소 Settings → Secrets and variables → Actions:
- `GEMINI_API_KEY`: Gemini AI API 키
- `SLACK_WEBHOOK_URL`: Slack Webhook URL

## 🧪 테스트

### 미리보기 (Slack 전송 없이 확인)

```bash
# 전체 프로세스 미리보기
python pokernews_preview.py

# 수집만 미리보기
python pokernews_preview.py --collection-only

# AI 분석 건너뛰고 미리보기
python pokernews_preview.py --skip-ai

# 더 많은 기사로 미리보기
python pokernews_preview.py --articles 20
```

### 개별 모듈 테스트

```bash
# 뉴스 수집 테스트
python pokernews_collector.py

# AI 분석 테스트 (테스트 데이터 사용)
python pokernews_ai_analyzer.py

# 전체 시스템 테스트
python test_pokernews.py
```

### 실제 실행 (Slack 전송)

```bash
# 실제 뉴스 수집 → AI 분석 → Slack 전송
python pokernews_slack_reporter.py
```

## ⚙️ GitHub Actions 자동화

### 스케줄
- **일일 실행**: 매일 오전 9시 30분 (KST)
- **수동 실행**: GitHub Actions 페이지에서 수동 트리거 가능

### 워크플로우 파일
`.github/workflows/pokernews-daily-report.yml`

## 📊 출력 예시

### Slack 리포트 형식

```
📰 PokerNews 일일 트렌드 분석
━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 2025년 8월 8일 | 🔍 분석 기사: 15개

🎯 오늘의 핵심 트렌드
1. Phil Ivey가 Triton Series에서 복귀 우승
2. 미국 온라인 포커 규제 완화 움직임
3. AI 포커 봇 논란 재점화

🏆 주요 토너먼트 소식
• Triton Series Montenegro 진행 중
• WSOP Online 브레이슬릿 이벤트 시작
• EPT Barcelona 일정 발표

🌟 주목할 선수
• Phil Ivey - Triton $100k 우승
• Daniel Negreanu - 새 마스터클래스 출시
• Vanessa Selbst - 복귀 루머

💼 시장 동향
• GGPoker 아시아 시장 확장
• PokerStars 새로운 보상 프로그램
• 암호화폐 포커 사이트 증가

💡 추천 콘텐츠 아이디어
1. Phil Ivey 플레이 스타일 분석
2. 온라인 포커 규제 변화 가이드
3. Triton Series 하이라이트 영상

📝 오늘의 요약
하이롤러 토너먼트 활성화와 미국 시장 규제 완화가 포커 산업 성장을 이끌고 있습니다.

📚 주요 기사
• [news] Phil Ivey Wins Triton $100K
• [strategy] GTO vs Exploitative Play
• [online] Michigan Online Poker Update
━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 Powered by Gemini AI | 📰 Source: PokerNews.com
```

## 🔧 커스터마이징

### 수집 설정 변경

```python
# pokernews_collector.py
collector = PokerNewsCollector()
articles = collector.collect_latest_news(
    max_articles=30  # 수집할 최대 기사 수
)
```

### AI 분석 프롬프트 수정

`pokernews_ai_analyzer.py`의 `_create_analysis_prompt()` 메서드에서 프롬프트 커스터마이징 가능

### Slack 메시지 포맷 변경

`pokernews_slack_reporter.py`의 `_create_slack_message()` 메서드에서 메시지 구조 수정

## 📁 파일 구조

```
news-analyzer/
├── pokernews_collector.py      # 뉴스 수집 모듈
├── pokernews_ai_analyzer.py    # AI 분석 모듈
├── pokernews_slack_reporter.py # Slack 리포터
├── test_pokernews.py           # 테스트 스크립트
├── requirements.txt            # Python 의존성
├── README.md                   # 문서
└── reports/                    # 리포트 저장 디렉토리
    └── pokernews_report_*.json
```

## ⚠️ 주의사항

1. **API 제한**
   - Gemini API: 일일 요청 제한 확인
   - 웹 스크래핑: 과도한 요청 자제 (1초 지연 포함)

2. **데이터 정확성**
   - 웹사이트 구조 변경 시 선택자 업데이트 필요
   - AI 분석 결과는 참고용으로 활용

3. **보안**
   - API 키와 Webhook URL은 절대 커밋하지 않음
   - GitHub Secrets 사용 권장

## 🐛 문제 해결

### 뉴스 수집 실패
- PokerNews 사이트 구조 변경 확인
- `pokernews_collector.py`의 선택자 업데이트

### AI 분석 실패
- Gemini API 키 유효성 확인
- API 할당량 확인

### Slack 전송 실패
- Webhook URL 유효성 확인
- 네트워크 연결 상태 확인

## 📈 향후 개선 계획

- [ ] 다른 포커 뉴스 사이트 추가 (CardPlayer, PokerStrategy)
- [ ] 뉴스 감정 분석 기능
- [ ] 트렌드 시각화 차트
- [ ] 주간/월간 종합 리포트
- [ ] 키워드 알림 기능
- [ ] 데이터베이스 저장 및 히스토리 관리

## 📝 라이선스

MIT License

## 👨‍💻 개발자

- GitHub: [@garimto81](https://github.com/garimto81)

---

최종 업데이트: 2025-08-08