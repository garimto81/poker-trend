# 📊 YouTube 포커 트렌드 일일 분석 시스템

## 🎯 프로젝트 목표

YouTube에서 포커 관련 콘텐츠의 트렌드를 매일 분석하여, 주말을 제외한 평일 오전 10시에 Slack 특정 채널로 자동 리포트를 전송하는 시스템 구축

### 핵심 가치
- **정확성**: 데이터 기반의 객관적인 트렌드 분석
- **일관성**: 매일 같은 시간에 표준화된 리포트 제공
- **실용성**: 즉시 활용 가능한 인사이트 제공
- **자동화**: 100% 자동화된 무인 운영

## 📋 시스템 요구사항

### 1. 데이터 수집
```yaml
수집 대상:
  - YouTube 포커 관련 영상 (최근 24-48시간)
  - 8개 핵심 키워드 기반 검색
  - 영상 메타데이터 (조회수, 좋아요, 댓글 수)
  - 채널 정보 (구독자 수, 채널명)

수집 주기:
  - 매일 오전 9시 30분 (분석 시간 확보)
  - 데이터 검증 및 정제
```

### 2. 분석 항목
```yaml
기본 분석:
  - TOP 10 인기 영상 (조회수 기준)
  - 급상승 영상 (성장률 기준)
  - 채널별 영상 업로드 현황
  - 평균 조회수/참여율 통계

트렌드 분석:
  - 핫 토픽 키워드 추출
  - 카테고리별 분포 (토너먼트/교육/엔터테인먼트 등)
  - 시간대별 업로드 패턴
  - 전일 대비 변화율

AI 인사이트:
  - 주요 트렌드 요약 (1-2문장)
  - 주목할 만한 패턴 분석
  - 콘텐츠 기회 영역 제시
```

### 3. 리포트 형식
```yaml
Slack 메시지 구조:
  - 헤더: 날짜, 분석 영상 수
  - 섹션 1: 오늘의 트렌드 요약
  - 섹션 2: TOP 10 인기 영상 (링크 포함)
  - 섹션 3: 급상승 콘텐츠
  - 섹션 4: 채널 분석
  - 섹션 5: AI 인사이트
  - 푸터: 전체 통계 요약
```

## 🏗️ 시스템 아키텍처

### 심플한 3단계 파이프라인
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Data Collector │ --> │ Trend Analyzer  │ --> │ Slack Reporter  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        ↓                       ↓                       ↓
   YouTube API           Gemini AI API          Slack Webhook
```

### 기술 스택
```yaml
핵심 기술:
  - Python 3.11 (데이터 처리)
  - GitHub Actions (스케줄링/실행)
  - YouTube Data API v3 (데이터 수집)
  - Google Gemini API (AI 분석)
  - Slack Webhook (리포트 전송)

데이터 저장:
  - JSON 파일 (일일 데이터)
  - GitHub Repository (히스토리)
```

## 📅 일일 워크플로우

### 실행 스케줄
```yaml
09:30 KST: 데이터 수집 시작
  - YouTube API로 최근 48시간 영상 수집
  - 8개 키워드별 검색 수행
  - 영상 상세 정보 조회

09:45 KST: 데이터 분석
  - 통계 계산 및 순위 산정
  - 트렌드 패턴 분석
  - AI 인사이트 생성

10:00 KST: Slack 리포트 전송
  - 포맷팅 및 검증
  - 지정 채널로 전송
  - 전송 결과 로깅
```

### GitHub Actions 설정
```yaml
name: Daily Poker Trend Analysis

on:
  schedule:
    # 평일 오전 9시 30분 (UTC 0:30 = KST 9:30)
    - cron: '30 0 * * 1-5'
  workflow_dispatch:

jobs:
  analyze-and-report:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Collect YouTube Data
        env:
          YOUTUBE_API_KEY: ${{ secrets.YOUTUBE_API_KEY }}
        run: python scripts/collect_data.py
      
      - name: Analyze Trends
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        run: python scripts/analyze_trends.py
      
      - name: Send Slack Report
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
        run: python scripts/send_report.py
```

## 📊 리포트 예시

### Slack 메시지 형식
```
🎰 포커 트렌드 일일 분석 리포트
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 2025년 1월 15일 (수)
📊 분석 대상: 총 156개 영상

🔥 오늘의 트렌드
────────────────
"WSOP 메인 이벤트 관련 콘텐츠가 급증하며, 특히 블러프 플레이 
하이라이트 영상들이 높은 조회수를 기록하고 있습니다."

📺 TOP 10 인기 영상
────────────────
1. 🥇 Phil Ivey's INSANE Bluff at WSOP 2025!
   조회수: 385,234 | PokerGO
   https://youtube.com/watch?v=xxxxx

2. 🥈 $1,000,000 Pot - Biggest Cash Game Ever
   조회수: 298,567 | Hustler Casino Live
   https://youtube.com/watch?v=xxxxx

[... 3-10위 영상 ...]

📈 급상승 콘텐츠
────────────────
• "Triton Poker Series London" - 24시간 내 +2,450% 상승
• "GGPoker WSOP Online" - 48시간 내 +1,890% 상승
• "Doug Polk vs Daniel Negreanu" - 지속적 관심 증가

🎬 채널 분석
────────────────
가장 활발한 채널:
• PokerGO: 12개 영상 업로드
• Brad Owen: 8개 영상 업로드
• Rampage Poker: 6개 영상 업로드

💡 AI 인사이트
────────────────
1. 토너먼트 시즌 효과로 WSOP 관련 콘텐츠 수요 급증
2. 고액 캐시게임 영상의 평균 시청 시간이 일반 영상 대비 3배 높음
3. 교육 콘텐츠보다 엔터테인먼트 중심 콘텐츠가 더 높은 참여율 기록

📊 전체 통계
────────────────
• 평균 조회수: 45,678회
• 평균 좋아요율: 4.2%
• 가장 많이 사용된 태그: #WSOP #Poker #Holdem
• 최적 업로드 시간: 오후 2-4시 (EST)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💬 문의: poker-trends@company.com
```

## 🔧 구현 세부사항

### 1. 데이터 수집 스크립트 (`collect_data.py`)
```python
주요 기능:
- YouTube API 호출 최적화
- 페이지네이션 처리
- 중복 제거
- 에러 핸들링
- 데이터 검증
```

### 2. 트렌드 분석 스크립트 (`analyze_trends.py`)
```python
주요 기능:
- 통계 계산 (평균, 중앙값, 표준편차)
- 순위 알고리즘 (조회수 + 성장률 가중치)
- 카테고리 자동 분류
- Gemini AI 프롬프트 최적화
- 트렌드 스코어 계산
```

### 3. Slack 리포트 스크립트 (`send_report.py`)
```python
주요 기능:
- Slack 블록 포맷팅
- 하이퍼링크 처리
- 이모지 적절히 사용
- 에러 시 재시도
- 전송 확인 로깅
```

## 📈 성과 측정

### KPI (핵심 성과 지표)
```yaml
시스템 안정성:
  - 일일 실행 성공률: 99.9% 목표
  - 평균 실행 시간: 30분 이내
  - 에러 발생률: 0.1% 이하

데이터 품질:
  - 수집 영상 수: 100개 이상/일
  - 데이터 정확도: 98% 이상
  - 중복률: 1% 이하

사용자 만족도:
  - 리포트 활용률 추적
  - 피드백 수집 및 반영
  - 개선 요청 대응
```

## 🚀 향후 개선 계획

### Phase 1 (1개월)
- 주말 특별 리포트 (주간 요약)
- 더 많은 통계 지표 추가
- 시각화 차트 이미지 첨부

### Phase 2 (3개월)
- 웹 대시보드 연동
- 히스토리 데이터 분석
- 예측 모델 도입

### Phase 3 (6개월)
- 다국어 지원
- 맞춤형 알림 설정
- API 서비스 제공

## 🔐 보안 및 관리

### 환경 변수
```bash
YOUTUBE_API_KEY      # YouTube Data API v3
SLACK_WEBHOOK_URL    # Slack 웹훅 URL
GEMINI_API_KEY       # Google Gemini API
```

### 접근 권한
- GitHub Secrets로 API 키 관리
- Slack 웹훅 URL 보안 유지
- 정기적인 키 로테이션

## 📞 지원 및 문의

- 기술 문의: GitHub Issues
- 리포트 개선 제안: Slack #poker-trends-feedback
- 긴급 이슈: 담당자 직접 연락