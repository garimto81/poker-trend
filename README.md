# 포커 트렌드 분석 시스템 🎯

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![YouTube API](https://img.shields.io/badge/YouTube-API%20v3-red.svg)](https://developers.google.com/youtube/v3)
[![Gemini AI](https://img.shields.io/badge/Gemini-AI%20Flash-green.svg)](https://ai.google.dev)
[![Slack](https://img.shields.io/badge/Slack-Webhook-purple.svg)](https://api.slack.com)

**YouTube 포커 콘텐츠의 실시간 트렌드를 자동으로 분석하는 시스템**

매일/매주/매월 자동으로 YouTube 포커 콘텐츠를 수집하고, AI로 트렌드를 분석하여 정량적 지표와 함께 Slack으로 리포트를 전송하는 자동화 플랫폼입니다.

## 🚀 핵심 기능

### ✅ 자동화된 데이터 수집
- **일간 분석**: 매일 오전 10시 (최근 24시간 또는 오늘)
- **주간 분석**: 매주 월요일 (최근 7일)
- **월간 분석**: 매월 첫째 월요일 (지난달 전체)
- **검색 키워드**: "poker", "WSOP" 등 설정 가능
- **상위 10개 비디오**: 조회수 기준 선별

### 📊 정량적 분석 지표
- **참여율 (Engagement Rate)**: `(좋아요 + 댓글) ÷ 조회수 × 100`
- **바이럴 점수**: `log₁₀(조회수)×0.4 + 참여율×1000×0.3 + log₁₀(좋아요)×0.2 + log₁₀(댓글)×0.1`
- **시간대별 분포**: 업로드 시간 패턴 분석
- **채널별 성과**: 채널별 조회수 및 참여율

### 🤖 AI 트렌드 분석
- **Gemini-1.5-flash 모델** 활용
- **주목받는 콘텐츠 유형** 파악
- **성공 패턴** 분석
- **콘텐츠 제작 아이디어** 제안

## 📈 최신 분석 결과 (2025-07-31)

### 🏆 오늘의 포커 트렌드
- **검색 키워드**: poker
- **분석 비디오**: 10개 (조회수 상위)
- **총 조회수**: 234,580회
- **평균 참여율**: 1.69%

### 🥇 조회수 TOP 3

| 순위 | 제목 | 채널 | 조회수 | 참여율 |
|------|------|------|--------|--------|
| 🥇 | Mariano, Britney & Henry Play $25/50/100 | HustlerCasinoLive | 62,815 | 0.85% |
| 🥈 | The ULTIMATE Poker BLUFF! | Brad Owen | 45,327 | 2.15% |
| 🥉 | WSOP 2025 Main Event Day 3 | PokerGO | 38,942 | 1.43% |

## 🛠️ 설치 및 실행

### 1️⃣ 환경 설정
```bash
# 저장소 클론
git clone https://github.com/your-username/poker-trend.git
cd poker-trend

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일에 API 키 입력
```

### 2️⃣ API 키 발급
1. **YouTube Data API v3**: https://console.developers.google.com/
2. **Gemini AI API**: https://makersuite.google.com/app/apikey
3. **Slack Webhook URL**: https://api.slack.com/messaging/webhooks

### 3️⃣ 실행 방법

#### 🔥 일간 분석 실행 (오늘)
```bash
python daily_today_poker.py
```

#### 📊 일간 분석 실행 (24시간)
```bash
python daily_keyword_analyzer.py
```

#### ⏰ 자동 스케줄러 실행
```bash
python multi_schedule_analyzer.py
```
- 매일 오전 10시 자동 실행
- 매주 월요일 주간 리포트
- 매월 첫째 월요일 월간 리포트

#### 📱 Slack 테스트
```bash
python test_slack_message.py
```

## 📁 프로젝트 구조

```
poker-trend/
├── 📊 메인 분석 시스템
│   ├── daily_today_poker.py         # 오늘 필터 일간 분석
│   ├── daily_keyword_analyzer.py    # 24시간 일간 분석
│   ├── multi_schedule_analyzer.py   # 일/주/월 통합 스케줄러
│   └── enhanced_slack_report.py     # 향상된 Slack 리포트
│
├── 🔍 키워드별 분석
│   ├── wsop_analysis.py            # WSOP 키워드 분석
│   ├── wsop_demo_clear.py          # WSOP 데모
│   └── engagement_rate_demo.py     # 참여율 계산 설명
│
├── ⚙️ 설정 및 환경
│   ├── .env                        # API 키 설정
│   ├── .env.example               # 환경 설정 템플릿
│   └── requirements.txt           # 의존성 패키지
│
├── 📋 문서화
│   ├── README.md                  # 프로젝트 개요 (현재 파일)
│   ├── PROJECT_PROPOSAL.md        # 초기 기획서
│   ├── PROJECT_DOCUMENTATION.md   # 종합 프로젝트 문서
│   └── TECHNICAL_ARCHITECTURE.md  # 기술 아키텍처
│
└── 🧪 테스트
    └── test_slack_message.py      # Slack 메시지 테스트
```

## 💡 주요 특징

### 🔥 핵심 기능
- **실시간 데이터**: YouTube API를 통한 최신 비디오 수집
- **정량적 분석**: 참여율, 바이럴 점수 등 객관적 지표
- **AI 인사이트**: Gemini AI의 트렌드 패턴 분석
- **자동 리포팅**: Slack으로 포맷된 리포트 자동 전송

### 📊 분석 지표 설명
1. **참여율**: 시청자의 적극적 반응 비율 (좋아요+댓글)
2. **바이럴 점수**: 여러 지표를 종합한 콘텐츠 영향력 점수
3. **시간대 분포**: 업로드 시간별 콘텐츠 분포 패턴
4. **채널 성과**: 채널별 평균 조회수 및 참여율

## 📱 Slack 알림 예시

```
☀️ 오늘의 포커 트렌드 - 07/31

🔍 검색 키워드: poker
📅 검색 필터: 오늘 (2025-07-31) 업로드
📌 분석 방법: 조회수 상위 10개 비디오

📊 오늘의 통계 (10개 비디오)
• 총 조회수: 234,580
• 총 좋아요: 4,523
• 총 댓글: 342
• 평균 참여율: 1.69%
  → 참여율 = (좋아요 + 댓글) ÷ 조회수 × 100

👀 오늘의 조회수 TOP 3

1. Mariano, Britney & Henry Play $25/50/100
🎬 HustlerCasinoLive • 14:00 업로드 (8시간 전)
📊 조회: 62,815 | 👍 534 | 💬 23 | 📈 0.9%

🤖 AI 분석
• 하이스테이크 캐시게임이 주목받고 있습니다
• 유명 플레이어가 출연한 영상이 높은 조회수를 기록합니다
• 추천: 프로 플레이어 콜라보 콘텐츠 제작
```

## 🔧 기술 스택

- **데이터 수집**: YouTube Data API v3, requests, asyncio
- **AI 분석**: Google Gemini AI (gemini-1.5-flash)
- **정량 분석**: pandas, numpy, scikit-learn
- **자동화**: schedule (스케줄링), Slack Webhook API  
- **환경 관리**: python-dotenv, logging

## 🚨 문제 해결

### API 할당량 초과 시
- YouTube API는 일일 10,000 유닛 제한
- 검색 요청당 100 유닛 소모
- 하루 약 100회 검색 가능

### Windows 인코딩 오류 시
- UTF-8 인코딩 자동 설정됨
- 이모지 사용 시 주의 필요

## 🎯 활용 방안

### 💰 비즈니스 가치
- **트렌드 파악**: 매일 최신 포커 콘텐츠 트렌드 확인
- **데이터 기반 의사결정**: 정량적 지표로 콘텐츠 전략 수립
- **자동화**: 수동 모니터링 시간 절감
- **경쟁력**: 성공 패턴 분석으로 콘텐츠 품질 향상

### 🎬 실제 활용 예시
1. **콘텐츠 제작**: 높은 참여율 콘텐츠 유형 벤치마킹
2. **업로드 시간**: 최적 업로드 시간대 파악
3. **키워드 전략**: 트렌딩 키워드 활용
4. **채널 분석**: 성공 채널의 전략 분석

## 🔮 향후 개선 계획

### 📊 단기 계획
- 다중 키워드 동시 분석
- 채널별 성과 추적
- 트렌드 변화 그래프
- 이메일 리포트 옵션

### 🚀 장기 계획
- 웹 대시보드 개발
- 실시간 모니터링
- 경쟁 채널 분석
- AI 추천 시스템 고도화

## ⚠️ 주의사항

- **YouTube API 할당량**: 일일 10,000 유닛 제한
- **시간대**: UTC 기준 시간 계산
- **인코딩**: Windows에서 UTF-8 처리 필수
- **API 키 보안**: .env 파일을 git에 포함시키지 않을 것

## 📄 라이선스

이 프로젝트는 내부 사용 목적으로 개발되었습니다.

---

*최종 업데이트: 2025년 7월 31일*