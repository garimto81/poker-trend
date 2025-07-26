# 🚀 GitHub Pages 웹앱 배포 가이드

이 가이드는 `garimto81` 계정으로 Poker Trend 웹앱을 GitHub Pages에 배포하는 방법을 설명합니다.

## 📋 배포 준비사항

### 1. GitHub 저장소 생성
```bash
# GitHub에서 새 저장소 생성: poker-trend
# 로컬에서 리모트 추가
git remote add origin https://github.com/garimto81/poker-trend.git
```

### 2. 필수 파일 확인
- ✅ `.github/workflows/deploy.yml` - GitHub Actions CI/CD
- ✅ `frontend/public/CNAME` - 커스텀 도메인 설정
- ✅ `frontend/package.json` - GitHub Pages 설정
- ✅ `frontend/src/config/api.ts` - API 환경 설정

## 🔧 배포 과정

### Step 1: 코드 커밋 및 푸시
```bash
cd poker-trend
git add .
git commit -m "Initial commit: Poker Trend Web App"
git push -u origin main
```

### Step 2: GitHub Pages 활성화
1. GitHub 저장소 → **Settings** 탭
2. **Pages** 섹션으로 이동
3. **Source**: GitHub Actions 선택
4. **Custom domain**: `poker-trend.garimto81.com` 입력 (선택사항)

### Step 3: 도메인 설정 (선택사항)
도메인 제공업체에서 다음 DNS 레코드 추가:
```
Type: CNAME
Name: poker-trend
Value: garimto81.github.io
```

### Step 4: 자동 배포 확인
- 코드 푸시 시 GitHub Actions가 자동으로 빌드 및 배포
- **Actions** 탭에서 배포 상태 확인

## 🌐 접속 정보

### 배포 완료 후 접속 URL
- **GitHub Pages 기본**: https://garimto81.github.io/poker-trend
- **커스텀 도메인**: https://poker-trend.garimto81.com (설정 시)

### 데모 계정
- **아이디**: `admin`
- **비밀번호**: `admin`

## 📁 배포 구조

```
GitHub Pages 배포 구조:
├── index.html (메인 페이지)
├── static/ (CSS, JS, 이미지)
├── CNAME (커스텀 도메인)
└── 404.html (SPA 라우팅용)
```

## 🔄 CI/CD 파이프라인

### GitHub Actions 워크플로우
```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [ main ]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - Checkout code
      - Setup Node.js 18
      - Install dependencies
      - Build React app
      - Deploy to GitHub Pages
```

### 빌드 환경변수
```env
REACT_APP_API_URL=https://api.garimto81.com (실제 API 서버)
PUBLIC_URL=/poker-trend
NODE_ENV=production
```

## 🛠️ 개발 워크플로우

### 로컬 개발
```bash
cd frontend
npm install
npm start  # http://localhost:3000
```

### 프로덕션 빌드 테스트
```bash
cd frontend
npm run build
npx serve -s build  # 빌드된 앱 테스트
```

### 수동 배포 (필요시)
```bash
cd frontend
npm run deploy  # gh-pages 브랜치로 직접 배포
```

## 🔧 환경별 설정

### 개발 환경 (localhost)
- Mock 데이터 사용
- API 서버: http://localhost:3000
- 개발자 도구 활성화

### 스테이징 환경 (GitHub Pages)
- Mock 데이터 사용 (백엔드 없음)
- API 서버: 모의 API
- 프로덕션 빌드

### 프로덕션 환경 (실제 서비스)
- 실제 API 서버 연결
- API 서버: https://api.garimto81.com
- 최적화된 빌드

## 📊 모니터링

### 배포 상태 확인
1. **GitHub Actions** - 빌드/배포 로그 확인
2. **Repository Settings > Pages** - 배포 상태 확인
3. **웹사이트 접속** - 실제 동작 확인

### 에러 로그 확인
- 브라우저 개발자 도구 Console
- GitHub Actions 빌드 로그
- 웹사이트 네트워크 탭

## 🔒 보안 설정

### GitHub Repository 설정
- **Public repository** (GitHub Pages 무료 사용)
- **Branch protection rules** (main 브랜치 보호)
- **Required status checks** (빌드 성공 시에만 배포)

### 웹앱 보안
- HTTPS 강제 사용
- CSP (Content Security Policy) 헤더
- XSS 방지 설정

## 🚨 문제 해결

### 일반적인 문제들

1. **404 Error**
   - `public/404.html` 파일 확인
   - SPA 라우팅 설정 확인

2. **빌드 실패**
   - `package.json` 종속성 확인
   - GitHub Actions 로그 확인

3. **도메인 연결 실패**
   - DNS 설정 확인 (24-48시간 소요)
   - CNAME 파일 확인

4. **API 연결 오류**
   - 환경변수 설정 확인
   - CORS 설정 확인

### 디버깅 명령어
```bash
# 로컬 빌드 테스트
npm run build

# 정적 파일 서버 실행
npx serve -s build

# 종속성 문제 해결
npm audit fix

# 캐시 클리어
npm start -- --reset-cache
```

## 📈 성능 최적화

### 빌드 최적화
- Code splitting
- Tree shaking
- 이미지 최적화
- 번들 크기 분석

### 로딩 성능
- Lazy loading
- Service worker
- CDN 사용 (jsDelivr)
- 캐싱 전략

## 🔄 업데이트 프로세스

### 자동 배포 (권장)
1. 로컬에서 코드 수정
2. `git push origin main`
3. GitHub Actions 자동 빌드/배포
4. 웹사이트에서 변경사항 확인

### 수동 배포
1. `npm run build`
2. `npm run deploy`
3. GitHub Pages 업데이트 확인

---

**🎯 목표**: garimto81 계정으로 완전한 웹앱 서비스 제공  
**📧 지원**: GitHub Issues를 통한 문제 신고  
**📚 문서**: README.md 참조