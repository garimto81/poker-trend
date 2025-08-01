# 🚀 GitHub 기반 배포 가이드

이 가이드는 `garimto81` 계정의 Poker Trend 프로젝트를 GitHub 서비스만으로 배포하고 운영하는 방법을 설명합니다.

## 📋 시스템 개요

### GitHub 서비스 활용
- **GitHub Actions**: 자동화된 데이터 수집, 콘텐츠 생성, 배포
- **GitHub Pages**: 대시보드 웹 호스팅
- **GitHub Releases**: 생성된 콘텐츠 저장
- **GitHub Secrets**: API 키 및 인증 정보 관리

### 서버리스 아키텍처
- 별도 서버 인프라 불필요
- 100% GitHub 서비스로 운영
- 무료 티어로 시작 가능

## 🔧 초기 설정

### Step 1: GitHub Secrets 설정
1. 저장소 → **Settings** → **Secrets and variables** → **Actions**
2. 다음 시크릿 추가:

```yaml
# YouTube API
YOUTUBE_API_KEY: your_youtube_api_key_here

# Slack Integration  
SLACK_WEBHOOK_URL: https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# AI Services
OPENAI_API_KEY: your_openai_api_key_here
GEMINI_API_KEY: your_gemini_api_key_here

# Social Media APIs (선택사항)
TWITTER_BEARER_TOKEN: your_twitter_token_here
REDDIT_CLIENT_ID: your_reddit_client_id_here
REDDIT_CLIENT_SECRET: your_reddit_client_secret_here
```

### Step 2: GitHub Pages 활성화
1. **Settings** → **Pages**
2. **Source**: Deploy from a branch
3. **Branch**: `gh-pages` 선택 (또는 `master` + `/docs` 폴더)
4. **Custom domain**: `poker-trend.garimto81.com` (선택사항)

### Step 3: Actions 권한 설정
1. **Settings** → **Actions** → **General**
2. **Workflow permissions**: Read and write permissions 선택
3. **Allow GitHub Actions to create and approve pull requests** 체크

## 🌐 대시보드 배포

### GitHub Pages 자동 배포
```yaml
# .github/workflows/deploy-dashboard.yml
name: Deploy Dashboard
on:
  push:
    branches: [master]
  workflow_run:
    workflows: ["Collect Trend Data"]
    types: [completed]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
      - run: |
          cd frontend
          npm ci
          npm run build
      - uses: peaceiris/actions-gh-pages@v4
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./frontend/build
```

### 접속 정보
- **GitHub Pages URL**: https://garimto81.github.io/poker-trend
- **커스텀 도메인**: https://poker-trend.garimto81.com
- **데모 계정**: admin / admin

## 📊 자동화 워크플로우

### 1. 트렌드 데이터 수집 (매시간)
```yaml
# .github/workflows/collect-trends.yml
name: Collect Trend Data
on:
  schedule:
    - cron: '0 * * * *'  # 매시간
  workflow_dispatch:     # 수동 실행 가능

jobs:
  collect:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: |
          pip install -r requirements.txt
          python scripts/collect_youtube_trends.py
      - uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: 'Update trend data'
          file_pattern: 'data/trends/*.json'
```

### 2. Slack 일일 리포트 (오전 10시)
```yaml
# .github/workflows/daily-report.yml
name: Daily Trend Report
on:
  schedule:
    - cron: '0 1 * * *'  # UTC 1시 = KST 10시
  workflow_dispatch:

jobs:
  report:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: python scripts/generate_daily_report.py
      - run: |
          curl -X POST ${{ secrets.SLACK_WEBHOOK_URL }} \
            -H 'Content-Type: application/json' \
            -d @report.json
```

### 3. 콘텐츠 자동 생성
```yaml
# .github/workflows/generate-content.yml
name: Generate Content
on:
  repository_dispatch:
    types: [trend-detected]
  workflow_dispatch:
    inputs:
      trend_id:
        description: 'Trend ID to process'
        required: true

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Generate Script
        run: python scripts/generate_script.py --trend-id ${{ github.event.inputs.trend_id }}
      - name: Create Video
        run: python scripts/create_video.py
      - uses: softprops/action-gh-release@v2
        with:
          files: output/*.mp4
          tag_name: content-${{ github.run_number }}
```

## 📁 프로젝트 구조

```
poker-trend/
├── .github/
│   ├── workflows/         # GitHub Actions 워크플로우
│   │   ├── collect-trends.yml
│   │   ├── daily-report.yml
│   │   ├── generate-content.yml
│   │   └── deploy-dashboard.yml
│   └── scripts/          # 워크플로우 헬퍼 스크립트
├── scripts/              # Python 자동화 스크립트
│   ├── collect_youtube_trends.py
│   ├── generate_daily_report.py
│   ├── generate_script.py
│   └── create_video.py
├── frontend/             # React 대시보드 (GitHub Pages)
├── data/                 # JSON 데이터 저장
│   ├── trends/          # 트렌드 데이터
│   └── reports/         # 일일 리포트
└── docs/                # 프로젝트 문서
```

## 🔄 개발 워크플로우

### 로컬 개발
```bash
# 저장소 클론
git clone https://github.com/garimto81/poker-trend.git
cd poker-trend

# Python 환경 설정
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 프론트엔드 개발
cd frontend
npm install
npm start
```

### 워크플로우 테스트
```bash
# GitHub CLI로 워크플로우 실행
gh workflow run collect-trends.yml

# 특정 입력값으로 실행
gh workflow run generate-content.yml -f trend_id=12345

# 워크플로우 상태 확인
gh run list --workflow=collect-trends.yml
```

## 📊 모니터링

### GitHub Actions 모니터링
- **Actions 탭**: 워크플로우 실행 현황
- **실행 로그**: 각 단계별 상세 로그
- **사용량**: Settings > Billing > Actions usage

### 성과 추적
- **대시보드**: https://poker-trend.garimto81.com
- **GitHub Insights**: 저장소 활동 통계
- **API 사용량**: 각 서비스 대시보드에서 확인

## 🚨 문제 해결

### 일반적인 문제

1. **워크플로우 실행 실패**
   - Actions 탭에서 에러 로그 확인
   - Secrets 설정 확인
   - API 할당량 확인

2. **GitHub Pages 404 에러**
   - Pages 설정 확인
   - gh-pages 브랜치 존재 여부
   - 빌드 로그 확인

3. **API Rate Limit**
   - 캐싱 구현
   - 요청 최적화
   - 백오프 전략 적용

### 디버깅 팁
```bash
# 로컬에서 Actions 테스트
act -j collect

# 시크릿 확인 (마스킹됨)
gh secret list

# 워크플로우 로그 확인
gh run view <run-id> --log
```

## 📈 확장 계획

### 단기 (1-2개월)
- [ ] Twitter, Reddit 데이터 수집 추가
- [ ] AI 영상 생성 통합
- [ ] A/B 테스트 프레임워크

### 중기 (3-6개월)
- [ ] 멀티플랫폼 자동 업로드
- [ ] 실시간 성과 분석
- [ ] 커뮤니티 기능

### 장기 (6개월+)
- [ ] GitHub Marketplace 앱 출시
- [ ] 다국어 지원
- [ ] B2B 서비스 전환

## 🔒 보안 고려사항

### API 키 관리
- GitHub Secrets 사용 필수
- 최소 권한 원칙
- 정기적 키 로테이션

### 접근 제어
- Branch protection rules
- CODEOWNERS 파일 활용
- 2FA 활성화 권장

### 데이터 보호
- 민감 정보 커밋 금지
- .gitignore 활용
- 공개 저장소 주의사항

---

**🎯 목표**: 서버 인프라 없이 GitHub 서비스만으로 완전 자동화된 포커 트렌드 콘텐츠 시스템 운영  
**📧 지원**: GitHub Issues를 통한 문의  
**📚 문서**: 프로젝트 Wiki 참조