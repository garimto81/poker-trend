# 🎰 Poker Trend Shorts 자동 제작 시스템

포커 관련 트렌드를 실시간으로 감지하고 자동으로 쇼츠 콘텐츠를 생성하는 AI 기반 자동화 시스템입니다.

## 🚀 주요 기능

- **실시간 트렌드 감지**: YouTube, TikTok, Twitter, Reddit 등에서 포커 트렌드 모니터링
- **일일 Slack 알림**: 매일 오전 10시 YouTube 포커 트렌드 분석 리포트 자동 전송
- **AI 스크립트 생성**: GPT-4를 활용한 자동 스크립트 작성
- **자동 영상 제작**: FFmpeg 기반 템플릿 영상 생성
- **멀티플랫폼 배포**: YouTube, TikTok, Instagram 동시 업로드
- **성과 분석**: 실시간 조회수, 좋아요, 댓글 분석

## 🏗️ 시스템 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Server    │    │ Data Collector  │
│   (React)       │◄──►│   (Node.js)     │◄──►│   (Python)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                        │
                              ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│Content Generator│    │   PostgreSQL    │    │    MongoDB      │
│   (Python)      │    │   (메타데이터)   │    │  (콘텐츠 데이터) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🌐 라이브 데모

**웹사이트**: [https://poker-trend.garimto81.com](https://poker-trend.garimto81.com)

> GitHub Pages에서 호스팅되는 라이브 데모를 확인해보세요!
> 
> **데모 계정**: 
> - 아이디: `admin`
> - 비밀번호: `admin`

## 🤖 자동 실행 (GitHub Actions)

### YouTube 트렌드 자동 분석
매일 자동으로 YouTube 포커 트렌드를 분석하고 Slack으로 리포트를 전송합니다.

- **실행 시간**: 매일 오전 10시 (한국 시간)
- **분석 내용**: TOP 5 급상승 영상, 카테고리별 트렌드, 인기 채널
- **알림 채널**: Slack

### 설정 방법
1. GitHub Secrets에 필요한 API 키 설정
2. Slack Bot 설정 및 채널 추가
3. GitHub Actions 활성화

자세한 설정 방법은 [GitHub Actions 설정 가이드](docs/github-actions-setup.md)를 참조하세요.

## 📋 시작하기

### 🚀 빠른 시작 (GitHub Pages)

1. **웹사이트 접속**: [poker-trend.garimto81.com](https://poker-trend.garimto81.com)
2. **데모 계정으로 로그인**: admin / admin
3. **실시간 대시보드 체험**

### 🛠️ 로컬 개발 환경

#### 사전 요구사항
- Docker & Docker Compose
- Node.js 18+ (로컬 개발 시)
- Python 3.11+ (로컬 개발 시)

#### 환경 설정
1. **저장소 클론**
```bash
git clone https://github.com/garimto81/poker-trend.git
cd poker-trend
```

2. **환경 변수 설정**
```bash
cp .env.example .env
# .env 파일을 편집하여 API 키 설정
```

3. **Docker Compose로 실행**
```bash
docker-compose up -d
```

#### 서비스 접속
- **Frontend Dashboard**: http://localhost:3001
- **API Server**: http://localhost:3000
- **Data Collector**: http://localhost:8001
- **Content Generator**: http://localhost:8002

## 📁 프로젝트 구조

```
poker-trend/
├── backend/
│   ├── api-server/          # Node.js API 서버
│   ├── data-collector/      # Python 데이터 수집 서비스
│   └── content-generator/   # Python 콘텐츠 생성 서비스
├── frontend/                # React 대시보드
├── infrastructure/          # Docker, Nginx 설정
├── docs/                   # 문서
├── docker-compose.yml      # 개발 환경 설정
└── README.md
```

## 🔧 개발 가이드

### 로컬 개발 환경 설정

#### Backend API Server
```bash
cd backend/api-server
npm install
npm run dev
```

#### Data Collector
```bash
cd backend/data-collector
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

#### Content Generator
```bash
cd backend/content-generator
pip install -r requirements.txt
uvicorn main:app --reload --port 8002
```

#### Frontend
```bash
cd frontend
npm install
npm start
```

### API 키 설정

`.env` 파일에 다음 API 키들을 설정해야 합니다:

```env
# YouTube Data API
YOUTUBE_API_KEY=your_youtube_api_key

# Slack Integration
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
SLACK_CHANNEL_ID=C1234567890

# Twitter API v2
TWITTER_BEARER_TOKEN=your_twitter_bearer_token

# Reddit API
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret

# OpenAI API
OPENAI_API_KEY=your_openai_api_key
```

## 🔄 개발 워크플로우

### Phase 1: 기반 구축 (현재 단계)
- [x] 프로젝트 구조 설정
- [x] Docker 개발 환경
- [x] 기본 서비스 틀
- [x] 데이터베이스 스키마
- [x] YouTube 트렌드 분석 API
- [x] Slack 일일 알림 시스템
- [ ] 기본 API 엔드포인트 (진행중)

### Phase 2: 자동화 고도화 (예정)
- [ ] AI 스크립트 생성
- [ ] 실시간 트렌드 감지
- [ ] 자동 영상 제작
- [ ] 멀티플랫폼 업로드

### Phase 3: 최적화 및 확장 (예정)
- [ ] 성능 최적화
- [ ] A/B 테스트 시스템
- [ ] 분석 대시보드
- [ ] 모니터링 시스템

## 🧪 테스트

```bash
# API Server 테스트
cd backend/api-server
npm test

# Data Collector 테스트
cd backend/data-collector
pytest

# Content Generator 테스트
cd backend/content-generator
pytest

# Frontend 테스트
cd frontend
npm test
```

## 📊 모니터링

### Health Checks
- API Server: http://localhost:3000/health
- Data Collector: http://localhost:8001/health
- Content Generator: http://localhost:8002/health

### 로그 확인
```bash
# 모든 서비스 로그
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs -f api-server
docker-compose logs -f data-collector
```

## 🔐 보안

- JWT 기반 인증
- API 키 환경변수 관리
- Rate Limiting 적용
- CORS 설정
- 입력값 검증 및 SQL Injection 방지

## 📈 성능 최적화

- Redis 캐싱 시스템
- 데이터베이스 인덱싱
- API 응답 압축
- CDN 활용 (예정)
- 이미지 최적화

## 🤝 기여 가이드

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 라이선스

MIT License - 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🆘 문제 해결

### 자주 발생하는 문제

1. **Docker 컨테이너 시작 실패**
   ```bash
   docker-compose down -v
   docker-compose up -d --build
   ```

2. **데이터베이스 연결 오류**
   - `.env` 파일의 데이터베이스 URL 확인
   - Docker 네트워크 상태 점검

3. **API 키 오류**
   - `.env` 파일의 API 키 유효성 확인
   - API 키의 권한 및 할당량 점검

### 지원

- 이슈 제기: [GitHub Issues](https://github.com/your-repo/poker-trend/issues)
- 문서: [Wiki](https://github.com/your-repo/poker-trend/wiki)

---

**🎯 목표**: 30분 내 트렌드 감지부터 쇼츠 배포까지 완전 자동화