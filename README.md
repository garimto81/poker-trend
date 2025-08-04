# 포커 트렌드 분석 플랫폼

## 프로젝트 개요
유튜브의 포커 관련 콘텐츠 트렌드를 분석하여 쇼츠 제작 아이디어를 제공하는 자동화 플랫폼입니다.

## 주요 기능
- **유튜브 트렌드 분석**: 지정된 포커 키워드로 유튜브 콘텐츠 분석
- **AI 기반 인사이트**: Gemini AI를 활용한 트렌드 분석 및 쇼츠 아이디어 제공
- **자동 보고서 생성**: 일/주/월 단위 자동 보고서 생성
- **슬랙 통합**: 보고서 자동 공유

## 분석 키워드
지정된 9개의 포커 관련 키워드만 사용:
- `wsop` - World Series of Poker
- `gg poker` - GG Poker
- `pokerstars` - PokerStars
- `ept` - European Poker Tour
- `wpt` - World Poker Tour
- `triton poker` - Triton Poker Series
- `hustler` - Hustler Casino Live
- `poker` - General Poker Content
- `holdem` - Texas Hold'em

## 보고서 스케줄
중복 보고 방지: 동일 기간에 대한 보고서는 한 번만 생성

### 일일 보고서
- **시간**: 평일 오전 10시 (주말 제외)
- **범위**: 당일(오늘) 데이터
- **내용**: 각 키워드별 조회수 상위 10개 콘텐츠

### 주간 보고서
- **시간**: 매주 월요일 정오 12시
- **범위**: 전주(지난주) 데이터
- **내용**: 주간 트렌드 분석 및 인사이트

### 월간 보고서
- **시간**: 매월 첫째주 월요일 오후 2시
- **범위**: 전월 데이터
- **내용**: 월간 종합 분석 및 쇼츠 전략

## 수집 데이터
- 콘텐츠 제목
- 설명
- 조회수
- 좋아요 수
- 댓글 수
- 유튜브 채널 정보

## 기술 스택
- **백엔드**: Python (FastAPI)
- **데이터 수집**: YouTube Data API v3
- **AI 분석**: Google Gemini AI
- **스케줄링**: APScheduler
- **알림**: Slack Webhook
- **데이터베이스**: PostgreSQL
- **캐싱**: Redis

## 프로젝트 구조
```
poker-trend/
├── src/
│   ├── api/              # API 엔드포인트
│   ├── services/         # 비즈니스 로직
│   ├── collectors/       # 데이터 수집
│   ├── analyzers/        # AI 분석
│   ├── reporters/        # 보고서 생성
│   └── schedulers/       # 작업 스케줄링
├── tests/                # 테스트 코드
├── docs/                 # 문서
└── config/              # 설정 파일
```

## 시작하기
자세한 설치 및 실행 방법은 [DEPLOYMENT.md](./DEPLOYMENT.md)를 참조하세요.

## 라이선스
Copyright (c) 2024. All rights reserved.