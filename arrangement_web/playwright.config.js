// GFX 오버레이 학습기 전용 Playwright 테스트 설정
const { defineConfig, devices } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests',
  /* 병렬 테스트 실행 */
  fullyParallel: false, // 단일 페이지이므로 순차 실행
  /* CI에서 재시도 금지 */
  forbidOnly: !!process.env.CI,
  /* CI에서 재시도 설정 */
  retries: process.env.CI ? 2 : 0,
  /* 병렬 실행자 수 */
  workers: process.env.CI ? 1 : undefined,
  /* 리포터 설정 */
  reporter: [
    ['html', { outputFolder: 'test-results/playwright-report' }],
    ['junit', { outputFile: 'test-results/junit.xml' }],
    ['list']
  ],
  /* 전역 테스트 설정 */
  use: {
    /* 베이스 URL */
    baseURL: 'http://localhost:8082',
    
    /* 스크린샷 설정 */
    screenshot: 'only-on-failure',
    
    /* 비디오 설정 */
    video: 'retain-on-failure',
    
    /* 트레이스 설정 */
    trace: 'retain-on-failure',
    
    /* 타임아웃 설정 */
    actionTimeout: 30000,
    navigationTimeout: 30000,
    
    /* 뷰포트 설정 */
    viewport: { width: 1280, height: 720 },
    
    /* 기타 설정 */
    ignoreHTTPSErrors: true,
    
    /* 테스트 실행 전 대기 시간 */
    launchOptions: {
      slowMo: 100, // 액션 간 100ms 지연
    },
  },

  /* 다양한 브라우저 환경에서 테스트 */
  projects: [
    {
      name: 'chromium',
      use: { 
        ...devices['Desktop Chrome'],
        // 한국어 설정
        locale: 'ko-KR',
        timezoneId: 'Asia/Seoul',
      },
    },
  ],

  /* 테스트 결과 디렉토리 */
  outputDir: 'test-results/',
  
  /* 테스트 타임아웃 */
  timeout: 60000, // 60초
  
  /* expect 타임아웃 */
  expect: {
    timeout: 10000, // 10초
  },
});