# 시스템 아키텍처

## 1. 전체 아키텍처 개요

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Scheduler     │────▶│   Core Engine   │────▶│  Slack Client   │
│  (APScheduler)  │     │   (FastAPI)     │     │   (Webhook)     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                    ┌──────────┼──────────┐
                    ▼          ▼          ▼
            ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
            │  YouTube    │ │  Gemini AI  │ │  PostgreSQL │
            │  Collector  │ │  Analyzer   │ │  Database   │
            └─────────────┘ └─────────────┘ └─────────────┘
                    │                              │
                    └──────────┬───────────────────┘
                               ▼
                        ┌─────────────┐
                        │    Redis    │
                        │   (Cache)   │
                        └─────────────┘
```

## 2. 컴포넌트 설명

### 2.1 Core Engine (FastAPI)
- **역할**: 중앙 제어 및 API 제공
- **주요 기능**:
  - RESTful API 엔드포인트
  - 비즈니스 로직 조정
  - 요청 라우팅
  - 에러 처리

### 2.2 Scheduler (APScheduler)
- **역할**: 자동 작업 스케줄링
- **주요 기능**:
  - Cron 기반 스케줄링
  - 작업 큐 관리
  - 실행 로그 추적
  - 중복 실행 방지

### 2.3 YouTube Collector
- **역할**: 유튜브 데이터 수집
- **주요 기능**:
  - YouTube Data API v3 연동
  - 키워드 검색
  - 데이터 정규화
  - API 할당량 관리

### 2.4 Gemini AI Analyzer
- **역할**: AI 기반 분석
- **주요 기능**:
  - 트렌드 패턴 분석
  - 인사이트 도출
  - 쇼츠 아이디어 생성
  - 자연어 처리

### 2.5 PostgreSQL Database
- **역할**: 영구 데이터 저장
- **주요 테이블**:
  - videos: 비디오 메타데이터
  - channels: 채널 정보
  - reports: 생성된 보고서
  - keywords: 키워드 관리
  - execution_logs: 실행 이력

### 2.6 Redis Cache
- **역할**: 임시 데이터 캐싱
- **주요 용도**:
  - API 응답 캐싱
  - 중복 요청 방지
  - 세션 관리
  - 작업 큐

### 2.7 Slack Client
- **역할**: 슬랙 알림 전송
- **주요 기능**:
  - Webhook 통합
  - 메시지 포맷팅
  - 파일 첨부
  - 에러 알림

## 3. 데이터 플로우

### 3.1 일일 보고서 생성 플로우
```
1. Scheduler가 매일 오전 10시 트리거
2. Core Engine이 YouTube Collector 호출
3. Collector가 각 키워드별 데이터 수집
4. 수집된 데이터 PostgreSQL 저장
5. Gemini AI Analyzer가 데이터 분석
6. 보고서 생성 및 저장
7. Slack Client로 보고서 전송
```

### 3.2 API 요청 플로우
```
1. 클라이언트가 API 엔드포인트 호출
2. Redis에서 캐시 확인
3. 캐시 미스 시 PostgreSQL 조회
4. 결과 반환 및 캐싱
```

## 4. 데이터베이스 스키마

### 4.1 videos 테이블
```sql
CREATE TABLE videos (
    id SERIAL PRIMARY KEY,
    video_id VARCHAR(50) UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    view_count INTEGER,
    like_count INTEGER,
    comment_count INTEGER,
    published_at TIMESTAMP,
    channel_id VARCHAR(50),
    keyword VARCHAR(50),
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (channel_id) REFERENCES channels(channel_id)
);
```

### 4.2 channels 테이블
```sql
CREATE TABLE channels (
    channel_id VARCHAR(50) PRIMARY KEY,
    channel_name VARCHAR(255),
    subscriber_count INTEGER,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4.3 reports 테이블
```sql
CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    report_type VARCHAR(20), -- daily, weekly, monthly
    period_start DATE,
    period_end DATE,
    content TEXT,
    ai_insights TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sent_to_slack BOOLEAN DEFAULT FALSE
);
```

## 5. API 설계

### 5.1 주요 엔드포인트
- `GET /api/v1/reports/{type}` - 보고서 조회
- `POST /api/v1/reports/generate` - 수동 생성
- `GET /api/v1/keywords` - 키워드 목록
- `GET /api/v1/videos/trending` - 트렌딩 비디오
- `GET /api/v1/health` - 헬스체크

### 5.2 인증 및 보안
- API Key 기반 인증
- Rate Limiting
- CORS 설정
- HTTPS 강제

## 6. 배포 아키텍처

### 6.1 컨테이너 구성
```yaml
services:
  app:
    - FastAPI 애플리케이션
    - Scheduler
    - 환경: Python 3.11
  
  postgres:
    - PostgreSQL 15
    - 볼륨 마운트
  
  redis:
    - Redis 7
    - 메모리 최적화
  
  nginx:
    - 리버스 프록시
    - SSL 종료
```

### 6.2 환경별 구성
- **개발**: Docker Compose
- **스테이징**: Kubernetes (미니멀)
- **프로덕션**: Kubernetes (HA 구성)

## 7. 모니터링 및 로깅

### 7.1 로깅 전략
- 구조화된 JSON 로그
- 로그 레벨별 분리
- ELK 스택 연동 가능

### 7.2 모니터링 지표
- API 응답 시간
- 에러율
- YouTube API 할당량
- 데이터베이스 연결 풀
- Redis 메모리 사용량

## 8. 확장성 고려사항

### 8.1 수평 확장
- 무상태 설계
- 로드 밸런서 지원
- 데이터베이스 읽기 복제

### 8.2 수직 확장
- 리소스 모니터링
- 자동 스케일링 정책
- 캐시 최적화