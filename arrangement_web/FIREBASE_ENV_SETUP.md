# 🔥 Firebase 환경 변수 설정 가이드

## 📋 현재 상황

현재 코드에서 사용 중인 Firebase 설정:
```javascript
// 개발용 설정 (현재 하드코딩된 값)
const firebaseConfig = {
    apiKey: "AIzaSyD6LVOtT0x30CQNZDt5aSUEBKT8vXPhM6k",
    authDomain: "ggp-camera.firebaseapp.com",
    projectId: "ggp-camera",
    storageBucket: "ggp-camera.appspot.com",
    messagingSenderId: "906682771595",
    appId: "1:906682771595:web:431b539435f4a0ca294c8e",
    measurementId: "G-JLR9TMLSS1"
};
```

## 🛡️ 보안 개선 방안

### 방법 1: HTML에서 환경변수 직접 설정 (가장 간단)

`index.html` 파일의 `<head>` 섹션에 추가:

```html
<script>
    // 운영 환경에서는 서버에서 동적으로 생성하거나 빌드 시 주입
    window.FIREBASE_API_KEY = "AIzaSyD6LVOtT0x30CQNZDt5aSUEBKT8vXPhM6k";
    window.FIREBASE_AUTH_DOMAIN = "ggp-camera.firebaseapp.com";
    window.FIREBASE_PROJECT_ID = "ggp-camera";
    window.FIREBASE_STORAGE_BUCKET = "ggp-camera.appspot.com";
    window.FIREBASE_MESSAGING_SENDER_ID = "906682771595";
    window.FIREBASE_APP_ID = "1:906682771595:web:431b539435f4a0ca294c8e";
    window.FIREBASE_MEASUREMENT_ID = "G-JLR9TMLSS1";
</script>
```

### 방법 2: 별도 환경 설정 파일 생성

`firebase-env.js` 파일 생성:
```javascript
// firebase-env.js
window.FIREBASE_CONFIG = {
    development: {
        apiKey: "AIzaSyD6LVOtT0x30CQNZDt5aSUEBKT8vXPhM6k",
        authDomain: "ggp-camera.firebaseapp.com",
        projectId: "ggp-camera",
        storageBucket: "ggp-camera.appspot.com",
        messagingSenderId: "906682771595",
        appId: "1:906682771595:web:431b539435f4a0ca294c8e",
        measurementId: "G-JLR9TMLSS1"
    },
    production: {
        // 운영 환경용 설정 (다른 Firebase 프로젝트 사용 권장)
        apiKey: "YOUR_PROD_API_KEY",
        authDomain: "your-prod-project.firebaseapp.com",
        projectId: "your-prod-project",
        // ... 기타 설정
    }
};
```

### 방법 3: 서버 사이드에서 환경변수 주입 (가장 보안적)

#### Node.js/Express 서버 예시:
```javascript
// server.js
app.get('/', (req, res) => {
    const html = `
    <!DOCTYPE html>
    <html>
    <head>
        <script>
            window.FIREBASE_API_KEY = "${process.env.FIREBASE_API_KEY}";
            window.FIREBASE_AUTH_DOMAIN = "${process.env.FIREBASE_AUTH_DOMAIN}";
            // ... 기타 환경변수
        </script>
    </head>
    // ... 나머지 HTML
    `;
    res.send(html);
});
```

## 🔧 실제 적용 방법

### 단계 1: 현재 env-config.js 수정

현재 `env-config.js` 파일을 다음과 같이 수정하세요:

```javascript
// env-config.js
window.ENV_CONFIG = {
    DEVELOPMENT: {
        FIREBASE_API_KEY: "AIzaSyD6LVOtT0x30CQNZDt5aSUEBKT8vXPhM6k",
        FIREBASE_AUTH_DOMAIN: "ggp-camera.firebaseapp.com", 
        FIREBASE_PROJECT_ID: "ggp-camera",
        FIREBASE_STORAGE_BUCKET: "ggp-camera.appspot.com",
        FIREBASE_MESSAGING_SENDER_ID: "906682771595",
        FIREBASE_APP_ID: "1:906682771595:web:431b539435f4a0ca294c8e",
        FIREBASE_MEASUREMENT_ID: "G-JLR9TMLSS1",
        DEBUG_MODE: true
    },
    PRODUCTION: {
        // 실제 운영환경에서는 이 값들을 서버에서 주입
        FIREBASE_API_KEY: window.FIREBASE_API_KEY || "AIzaSyD6LVOtT0x30CQNZDt5aSUEBKT8vXPhM6k",
        FIREBASE_AUTH_DOMAIN: window.FIREBASE_AUTH_DOMAIN || "ggp-camera.firebaseapp.com",
        FIREBASE_PROJECT_ID: window.FIREBASE_PROJECT_ID || "ggp-camera", 
        FIREBASE_STORAGE_BUCKET: window.FIREBASE_STORAGE_BUCKET || "ggp-camera.appspot.com",
        FIREBASE_MESSAGING_SENDER_ID: window.FIREBASE_MESSAGING_SENDER_ID || "906682771595",
        FIREBASE_APP_ID: window.FIREBASE_APP_ID || "1:906682771595:web:431b539435f4a0ca294c8e",
        FIREBASE_MEASUREMENT_ID: window.FIREBASE_MEASUREMENT_ID || "G-JLR9TMLSS1",
        DEBUG_MODE: false
    }
};

// 현재 환경 감지
window.CURRENT_ENV = (
    window.location.hostname === 'localhost' || 
    window.location.hostname.includes('127.0.0.1') ||
    window.location.hostname.includes('github.io') // GitHub Pages용
) ? 'DEVELOPMENT' : 'PRODUCTION';

if (window.ENV_CONFIG[window.CURRENT_ENV].DEBUG_MODE) {
    console.log(`🔥 Firebase Environment: ${window.CURRENT_ENV}`);
}
```

### 단계 2: GitHub Pages 배포용 환경변수 설정

GitHub Pages에 배포할 경우, Repository Settings에서 환경변수 설정:

1. GitHub Repository → Settings → Secrets and variables → Actions
2. 다음 환경변수들 추가:
   - `FIREBASE_API_KEY`
   - `FIREBASE_AUTH_DOMAIN`  
   - `FIREBASE_PROJECT_ID`
   - `FIREBASE_STORAGE_BUCKET`
   - `FIREBASE_MESSAGING_SENDER_ID`
   - `FIREBASE_APP_ID`
   - `FIREBASE_MEASUREMENT_ID`

### 단계 3: GitHub Actions 워크플로우 (자동 배포)

`.github/workflows/deploy.yml`:
```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Setup Node.js
      uses: actions/setup-node@v2
      with:
        node-version: '16'
    
    - name: Create environment config
      run: |
        cat > arrangement_web/firebase-runtime-config.js << EOF
        window.FIREBASE_API_KEY = "${{ secrets.FIREBASE_API_KEY }}";
        window.FIREBASE_AUTH_DOMAIN = "${{ secrets.FIREBASE_AUTH_DOMAIN }}";
        window.FIREBASE_PROJECT_ID = "${{ secrets.FIREBASE_PROJECT_ID }}";
        window.FIREBASE_STORAGE_BUCKET = "${{ secrets.FIREBASE_STORAGE_BUCKET }}";
        window.FIREBASE_MESSAGING_SENDER_ID = "${{ secrets.FIREBASE_MESSAGING_SENDER_ID }}";
        window.FIREBASE_APP_ID = "${{ secrets.FIREBASE_APP_ID }}";
        window.FIREBASE_MEASUREMENT_ID = "${{ secrets.FIREBASE_MEASUREMENT_ID }}";
        EOF
    
    - name: Deploy to GitHub Pages
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./arrangement_web
```

## 🔒 보안 권장사항

### 1. Firebase 보안 규칙 설정
```javascript
// Firestore Security Rules
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // 인증된 사용자만 읽기/쓰기 허용
    match /{document=**} {
      allow read, write: if request.auth != null;
    }
  }
}
```

### 2. API 키 도메인 제한
Firebase Console → 프로젝트 설정 → API 키에서:
- HTTP 리퍼러 제한 설정
- 허용 도메인 목록에 실제 운영 도메인만 추가

### 3. 개발/운영 환경 분리
```javascript
// 환경별 다른 Firebase 프로젝트 사용 권장
const configs = {
    development: {
        projectId: "ggp-camera-dev",
        // ... 개발용 설정
    },
    production: {
        projectId: "ggp-camera-prod", 
        // ... 운영용 설정
    }
};
```

## 🚀 즉시 적용 방법

**가장 간단한 방법 (지금 바로 적용 가능):**

1. `index.html` 파일의 `<head>` 섹션에 추가:
```html
<!-- Firebase 환경변수 (운영 시 서버에서 동적 생성) -->
<script>
    window.FIREBASE_API_KEY = "AIzaSyD6LVOtT0x30CQNZDt5aSUEBKT8vXPhM6k";
    window.FIREBASE_AUTH_DOMAIN = "ggp-camera.firebaseapp.com";
    window.FIREBASE_PROJECT_ID = "ggp-camera";
    window.FIREBASE_STORAGE_BUCKET = "ggp-camera.appspot.com";
    window.FIREBASE_MESSAGING_SENDER_ID = "906682771595";
    window.FIREBASE_APP_ID = "1:906682771595:web:431b539435f4a0ca294c8e";
    window.FIREBASE_MEASUREMENT_ID = "G-JLR9TMLSS1";
</script>
```

2. 기존 `env-config.js` 파일은 그대로 두고 위 스크립트만 추가하면 완료!

## ❓ 추가 질문이나 도움이 필요한 경우

- Firebase 프로젝트 새로 생성하는 방법
- 보안 규칙 상세 설정
- CI/CD 파이프라인 구축
- 도메인별 환경 분리 전략

언제든지 문의해주세요!