# 🎰 Poker Trend Shorts 자동 제작 시스템

포커 관련 트렌드를 실시간으로 감지하고 자동으로 쇼츠 콘텐츠를 생성하는 GitHub Actions 기반 완전 자동화 시스템입니다.

## 🚀 주요 기능

- **실시간 트렌드 감지**: YouTube, TikTok, Twitter, Reddit 등에서 포커 트렌드 모니터링
- **일일 Slack 알림**: 매일 오전 10시 YouTube 포커 트렌드 분석 리포트 자동 전송
- **AI 스크립트 생성**: GPT-4를 활용한 자동 스크립트 작성
- **자동 영상 제작**: 클라우드 기반 영상 생성
- **멀티플랫폼 배포**: YouTube, TikTok, Instagram 동시 업로드
- **성과 분석**: 실시간 조회수, 좋아요, 댓글 분석

## 🏗️ 시스템 아키텍처 (GitHub 기반)

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  GitHub Pages   │    │ GitHub Actions  │    │ GitHub Releases │
│   (대시보드)     │◄──►│  (자동화 엔진)   │◄──►│  (콘텐츠 저장)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ External APIs   │
                    │ (YouTube, AI)   │
                    └─────────────────┘
```

## 🌐 라이브 데모

**웹사이트**: [https://poker-trend.garimto81.com](https://poker-trend.garimto81.com)

> GitHub Pages에서 호스팅되는 라이브 대시보드를 확인해보세요!
> 
> **데모 계정**: 
> - 아이디: `admin`
> - 비밀번호: `admin`

## 🤖 GitHub Actions 자동화

### YouTube 트렌드 자동 분석
매일 자동으로 YouTube 포커 트렌드를 분석하고 Slack으로 리포트를 전송합니다.

- **실행 시간**: 매일 오전 10시 (한국 시간)
- **분석 내용**: TOP 5 급상승 영상, 평균 조회수, 트렌드 분석
- **알림 방식**: Slack Webhook

### 필요한 GitHub Secrets
```
YOUTUBE_API_KEY     # YouTube Data API v3 키
SLACK_WEBHOOK_URL   # Slack Incoming Webhook URL
OPENAI_API_KEY      # OpenAI API 키
GEMINI_API_KEY      # Google Gemini API 키
```

### 설정 방법
1. GitHub Settings → Secrets and variables → Actions
2. 필요한 Secrets 추가
3. GitHub Actions에서 워크플로우 실행

자세한 내용은 [배포 가이드](DEPLOYMENT.md)를 참조하세요.

## 📋 시작하기

### 🚀 빠른 시작 (서버 불필요)

1. **저장소 Fork**: 이 저장소를 Fork
2. **Secrets 설정**: 필요한 API 키 설정
3. **Actions 활성화**: GitHub Actions 활성화
4. **Pages 활성화**: GitHub Pages 설정

### 🛠️ 로컬 개발 환경

#### 사전 요구사항
- Git
- Python 3.11+
- Node.js 18+
- VS Code (권장)

#### 환경 설정
1. **저장소 클론**
```bash
git clone https://github.com/garimto81/poker-trend.git
cd poker-trend
```

2. **Python 환경 설정**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **프론트엔드 설정**
```bash
cd frontend
npm install
npm start
```

## 📁 프로젝트 구조

```
poker-trend/
├── .github/
│   ├── workflows/           # GitHub Actions 워크플로우
│   └── scripts/            # 워크플로우 헬퍼 스크립트
├── scripts/                # Python 자동화 스크립트
│   ├── collectors/         # 데이터 수집 스크립트
│   ├── generators/         # 콘텐츠 생성 스크립트
│   └── uploaders/          # 플랫폼 업로드 스크립트
├── frontend/               # React 대시보드 (GitHub Pages)
├── data/                   # JSON 데이터 저장
│   ├── trends/            # 트렌드 데이터
│   └── reports/           # 분석 리포트
├── docs/                   # 프로젝트 문서
└── README.md
```

## 🔧 개발 가이드

### GitHub Actions 워크플로우

#### 데이터 수집 (매시간)
```yaml
name: Collect Trend Data
on:
  schedule:
    - cron: '0 * * * *'
```

#### 일일 리포트 (매일 오전 10시)
```yaml
name: Daily Trend Report
on:
  schedule:
    - cron: '0 1 * * *'  # UTC 1시 = KST 10시
```

#### 콘텐츠 생성 (트리거 기반)
```yaml
name: Generate Content
on:
  repository_dispatch:
    types: [trend-detected]
```

### 로컬 테스트

```bash
# 트렌드 수집 테스트
python scripts/collect_youtube_trends.py

# 리포트 생성 테스트
python scripts/generate_daily_report.py

# 워크플로우 실행
gh workflow run collect-trends.yml
```

## 🔄 개발 로드맵

### Phase 1: GitHub 인프라 구축 (✅ 완료)
- [x] GitHub Actions 워크플로우 설정
- [x] YouTube 데이터 수집 자동화
- [x] Slack 일일 알림 시스템
- [x] GitHub Pages 대시보드

### Phase 2: 자동화 파이프라인 (🔄 진행중)
- [ ] AI 스크립트 생성 워크플로우
- [ ] 클라우드 영상 생성
- [ ] 멀티플랫폼 업로드 자동화
- [ ] 성과 추적 시스템

### Phase 3: 최적화 및 확장 (📅 예정)
- [ ] A/B 테스트 프레임워크
- [ ] 예측 모델 구축
- [ ] 커뮤니티 기능
- [ ] GitHub Marketplace 앱

## 🧪 테스트

```bash
# Python 스크립트 테스트
pytest scripts/tests/

# 프론트엔드 테스트
cd frontend && npm test

# GitHub Actions 로컬 테스트
act -j collect
```

## 📊 모니터링

### GitHub Actions 모니터링
- **Actions 탭**: 워크플로우 실행 현황
- **실행 로그**: 각 단계별 상세 로그
- **사용량**: Settings → Billing → Actions usage

### 대시보드
- **라이브 URL**: https://poker-trend.garimto81.com
- **데이터 업데이트**: 매시간 자동
- **성과 추적**: Google Analytics 연동

## 🔐 보안

- **GitHub Secrets**: API 키 암호화 저장
- **Branch Protection**: main 브랜치 보호
- **CODEOWNERS**: 코드 리뷰 필수
- **Actions 권한**: 최소 권한 원칙

## 📈 성능 최적화

- **Actions 캐싱**: 의존성 캐싱으로 빌드 시간 단축
- **병렬 처리**: Matrix 전략으로 동시 실행
- **조건부 실행**: 필요한 경우에만 워크플로우 실행
- **외부 스토리지**: 대용량 파일은 GitHub Releases 활용

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

1. **워크플로우 실행 실패**
   - Actions 탭에서 에러 로그 확인
   - Secrets 설정 확인
   - API 할당량 확인

2. **GitHub Pages 404 에러**
   - Pages 설정에서 소스 브랜치 확인
   - 빌드 로그 확인

3. **API Rate Limit**
   - 캐싱 구현
   - 요청 최적화
   - 백오프 전략 적용

### 지원

- 이슈 제기: [GitHub Issues](https://github.com/garimto81/poker-trend/issues)
- 토론: [GitHub Discussions](https://github.com/garimto81/poker-trend/discussions)
- 위키: [프로젝트 Wiki](https://github.com/garimto81/poker-trend/wiki)

---

**🎯 목표**: 서버 인프라 없이 GitHub 서비스만으로 30분 내 트렌드 감지부터 쇼츠 배포까지 완전 자동화