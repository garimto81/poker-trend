// 포커 트렌드 분석 플랫폼 E2E 테스트 설정
const { defineConfig, devices } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests',
  /* 병렬 테스트 실행 비활성화 - 시스템 리소스 보호 */
  fullyParallel: false,
  /* CI에서 재시도 금지 */
  forbidOnly: !!process.env.CI,
  /* CI에서 재시도 설정 */
  retries: process.env.CI ? 3 : 1,
  /* 병렬 실행자 수 */
  workers: process.env.CI ? 1 : undefined,
  /* 리포터 설정 */
  reporter: [
    ['html', { outputFolder: 'test-results/playwright-report' }],
    ['junit', { outputFile: 'test-results/junit.xml' }],
    ['json', { outputFile: 'test-results/test-results.json' }],
    ['list']
  ],
  /* 전역 테스트 설정 */
  use: {
    /* 스크린샷 설정 */
    screenshot: 'only-on-failure',
    
    /* 비디오 설정 */
    video: 'retain-on-failure',
    
    /* 트레이스 설정 */
    trace: 'retain-on-failure',
    
    /* 타임아웃 설정 - API 응답 대기 고려 */
    actionTimeout: 45000,
    navigationTimeout: 45000,
    
    /* 뷰포트 설정 */
    viewport: { width: 1920, height: 1080 },
    
    /* 기타 설정 */
    ignoreHTTPSErrors: true,
    
    /* 테스트 실행 전 대기 시간 */
    launchOptions: {
      slowMo: 200, // 액션 간 200ms 지연으로 안정성 확보
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
    {
      name: 'firefox',
      use: { 
        ...devices['Desktop Firefox'],
        locale: 'ko-KR',
        timezoneId: 'Asia/Seoul',
      },
    },
  ],

  /* 테스트 결과 디렉토리 */
  outputDir: 'test-results/',
  
  /* 테스트 타임아웃 - 긴 분석 작업 고려 */
  timeout: 180000, // 3분
  
  /* expect 타임아웃 */
  expect: {
    timeout: 15000, // 15초
  },

  /* 전역 설정 */
  globalSetup: require.resolve('./tests/global-setup.js'),
  globalTeardown: require.resolve('./tests/global-teardown.js'),
});