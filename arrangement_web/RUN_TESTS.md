# GGP CAMERA E2E 테스트 실행 가이드

## 🚀 빠른 시작

### 1. 환경 준비
```bash
# 의존성 설치
npm install

# Playwright 브라우저 설치
npx playwright install
```

### 2. 로컬 서버 시작
```bash
# 백그라운드에서 서버 시작
npm run start:local

# 또는 수동으로
cd arrangement_web
python -m http.server 8080
```

### 3. 테스트 실행
```bash
# 모든 브라우저에서 테스트
npm test

# Chrome만 테스트 (빠른 확인)
npm run test:chrome

# 헤드리스 모드 (브라우저 화면 보기)
npm run test:headed

# 디버그 모드 (단계별 실행)
npm run test:debug

# 모바일 전용 테스트
npm run test:mobile
```

## 📋 사용 가능한 스크립트

| 명령어 | 설명 |
|--------|------|
| `npm test` | 모든 브라우저에서 전체 테스트 실행 |
| `npm run test:chrome` | Chrome에서만 테스트 |
| `npm run test:firefox` | Firefox에서만 테스트 |
| `npm run test:webkit` | Safari WebKit에서만 테스트 |
| `npm run test:mobile` | 모바일 Chrome에서 테스트 |
| `npm run test:headed` | 브라우저 창을 보면서 테스트 |
| `npm run test:debug` | 디버그 모드로 단계별 실행 |
| `npm run test:report` | 테스트 결과 HTML 리포트 보기 |

## 📊 테스트 결과 확인

### HTML 리포트
```bash
# 테스트 실행 후 리포트 생성
npm run test:report

# 브라우저에서 자동으로 열림: test-results/html-report/index.html
```

### 실패한 테스트 디버깅
```bash
# 트레이스 파일 보기
npx playwright show-trace test-results/[test-name]/trace.zip

# 스크린샷 확인
# test-results/[test-name]/test-failed-1.png
```

## 🔧 설정 커스터마이징

### playwright.config.js 주요 설정

```javascript
// 브라우저 선택
projects: [
  { name: 'chromium' },  // Chrome/Edge
  { name: 'firefox' },   // Firefox  
  { name: 'webkit' },    // Safari
]

// 타임아웃 조정
timeout: 60000,           // 테스트당 60초
expect: { timeout: 10000 }, // expect 10초

// 실행 옵션
use: {
  screenshot: 'only-on-failure',
  video: 'retain-on-failure',
  trace: 'retain-on-failure',
}
```

## 🐛 문제 해결

### 자주 발생하는 문제

1. **포트 8080 사용 중 오류**
   ```bash
   # 포트 확인
   netstat -an | findstr :8080
   
   # 프로세스 종료
   taskkill /f /pid [PID]
   ```

2. **Playwright 설치 오류**
   ```bash
   # 완전 재설치
   npx playwright uninstall
   npx playwright install
   ```

3. **테스트 실행 느림**
   ```bash
   # 단일 브라우저만 사용
   npm run test:chrome
   
   # 병렬 실행 비활성화
   npx playwright test --workers=1
   ```

## 📝 테스트 케이스 추가

새로운 테스트를 추가하려면 `tests/ggp-camera.spec.js`에서:

```javascript
test('새로운 기능 테스트', async ({ page }) => {
  console.log('🧪 새로운 기능 테스트 시작');
  
  await page.goto(BASE_URL);
  
  // 테스트 로직 작성
  await expect(page.locator('#new-element')).toBeVisible();
  
  console.log('✅ 새로운 기능 테스트 완료');
});
```

## 📈 CI/CD 통합

### GitHub Actions 예시
```yaml
name: E2E Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: npm run start:local &
      - run: npm test
      - uses: actions/upload-artifact@v3
        if: always()
        with:
          name: playwright-report
          path: test-results/
```

## 🎯 테스트 결과 해석

### 성공한 테스트
- ✅ 초록색 체크마크
- 모든 expect 조건 통과
- 스크린샷/비디오 없음

### 실패한 테스트  
- ❌ 빨간색 X 마크
- 실패 지점의 스크린샷 저장
- 전체 실행 과정의 비디오 저장
- 디버깅용 trace 파일 생성

### 부분 성공
- ⚠️ 노란색 경고
- 일부 기능은 작동하지만 개선 필요
- 성능 임계값 초과 등

---

**도움이 필요하신가요?**
- 테스트 결과 리포트: `test-results/COMPREHENSIVE_E2E_TEST_REPORT.md`
- 기술적 분석: `test-results/TECHNICAL_ISSUES_ANALYSIS.md`  
- 요약 보고서: `test-results/EXECUTIVE_SUMMARY.md`