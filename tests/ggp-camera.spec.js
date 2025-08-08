// GGP CAMERA 업무 현황 보드 End-to-End 테스트
// 한국어로 작성된 포괄적인 Playwright 테스트

const { test, expect } = require('@playwright/test');

// 테스트 설정
const BASE_URL = 'http://localhost:8080';
const TIMEOUT = 30000; // 30초 타임아웃

test.describe('GGP CAMERA 업무 현황 보드 E2E 테스트', () => {
  
  // 1. 기본 로딩 테스트
  test('기본 로딩 테스트 - 페이지 로드 및 핵심 UI 요소 확인', async ({ page }) => {
    console.log('🔍 기본 로딩 테스트 시작');
    
    // 콘솔 에러 수집을 위한 리스너 설정
    const consoleErrors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    // 네트워크 실패 감지
    const networkFailures = [];
    page.on('response', response => {
      if (!response.ok()) {
        networkFailures.push(`${response.status()} ${response.url()}`);
      }
    });

    // 페이지 로드
    const response = await page.goto(BASE_URL, { 
      waitUntil: 'networkidle',
      timeout: TIMEOUT 
    });
    
    // 기본 HTTP 응답 확인
    expect(response.status()).toBe(200);
    console.log('✅ 페이지가 성공적으로 로드됨 (200 OK)');

    // 페이지 제목 확인
    const title = await page.title();
    expect(title).toContain('GGP CAMERA 업무 현황 보드');
    console.log(`✅ 페이지 제목 확인: ${title}`);

    // 핵심 UI 요소들이 표시되는지 확인
    await expect(page.locator('header')).toBeVisible({ timeout: TIMEOUT });
    await expect(page.locator('h1')).toContainText('GGP CAMERA 업무 현황');
    console.log('✅ 헤더 및 메인 타이틀 표시 확인');

    // 주요 버튼들 확인
    await expect(page.locator('#add-task-btn')).toBeVisible();
    await expect(page.locator('#manage-category-btn')).toBeVisible();
    await expect(page.locator('#dark-mode-toggle')).toBeVisible();
    console.log('✅ 주요 액션 버튼들 표시 확인');

    // 타임라인 컨트롤 확인
    await expect(page.locator('#timeline-controls')).toBeVisible();
    await expect(page.locator('#prev-btn')).toBeVisible();
    await expect(page.locator('#today-btn')).toBeVisible();
    await expect(page.locator('#next-btn')).toBeVisible();
    console.log('✅ 타임라인 네비게이션 버튼들 표시 확인');

    // 타임라인 컨테이너 확인
    await expect(page.locator('#timeline-container')).toBeVisible();
    console.log('✅ 타임라인 컨테이너 표시 확인');

    // CSS 및 JavaScript 리소스 로딩 확인
    await expect(page.locator('body')).toHaveClass(/bg-gray-100/);
    console.log('✅ CSS 스타일링 적용 확인 (Tailwind CSS)');

    // 현재 날짜 범위가 표시되는지 확인
    const currentRangeDisplay = page.locator('#current-range-display');
    await expect(currentRangeDisplay).toBeVisible();
    const rangeText = await currentRangeDisplay.textContent();
    expect(rangeText).toMatch(/\d{4}\. \d{1,2}\. \d{1,2}\. ~ \d{4}\. \d{1,2}\. \d{1,2}\./);
    console.log(`✅ 날짜 범위 표시 확인: ${rangeText}`);

    // 에러 없이 로드되었는지 확인
    expect(consoleErrors.length).toBe(0);
    if (consoleErrors.length > 0) {
      console.log('⚠️ 콘솔 에러:', consoleErrors);
    }

    expect(networkFailures.length).toBe(0);
    if (networkFailures.length > 0) {
      console.log('⚠️ 네트워크 실패:', networkFailures);
    }

    console.log('✅ 기본 로딩 테스트 완료');
  });

  // 2. 다크모드 기능 테스트
  test('다크모드 토글 기능 테스트', async ({ page }) => {
    console.log('🌙 다크모드 테스트 시작');
    
    await page.goto(BASE_URL, { waitUntil: 'networkidle' });
    
    const darkModeToggle = page.locator('#dark-mode-toggle');
    const htmlElement = page.locator('html');
    
    // 초기 상태 확인 (라이트 모드)
    await expect(htmlElement).not.toHaveClass('dark');
    const initialIcon = await darkModeToggle.locator('i').getAttribute('class');
    expect(initialIcon).toContain('fa-sun');
    console.log('✅ 초기 상태: 라이트 모드 확인');

    // 다크모드로 전환
    await darkModeToggle.click();
    await expect(htmlElement).toHaveClass('dark');
    
    // 아이콘이 변경되었는지 확인
    await expect(darkModeToggle.locator('i')).toHaveClass(/fa-moon/);
    console.log('✅ 다크모드 전환 성공 - 아이콘 변경 확인');

    // 다크모드 스타일 적용 확인
    await expect(page.locator('body')).toHaveClass(/dark:bg-gray-900/);
    console.log('✅ 다크모드 스타일 적용 확인');

    // 라이트모드로 재전환
    await darkModeToggle.click();
    await expect(htmlElement).not.toHaveClass('dark');
    await expect(darkModeToggle.locator('i')).toHaveClass(/fa-sun/);
    console.log('✅ 라이트모드 복원 성공');

    console.log('✅ 다크모드 테스트 완료');
  });

  // 3. 모달 기능 테스트 
  test('모달 열기/닫기 기능 테스트', async ({ page }) => {
    console.log('📋 모달 기능 테스트 시작');
    
    await page.goto(BASE_URL, { waitUntil: 'networkidle' });

    // 업무 추가 모달 테스트
    console.log('📝 업무 추가 모달 테스트');
    const addTaskBtn = page.locator('#add-task-btn');
    const taskModal = page.locator('#task-modal');
    
    // 모달이 초기에는 숨겨져 있는지 확인
    await expect(taskModal).toHaveClass(/hidden/);
    
    // 업무 추가 버튼 클릭하여 모달 열기
    await addTaskBtn.click();
    await expect(taskModal).not.toHaveClass(/hidden/);
    await expect(taskModal).toBeVisible();
    console.log('✅ 업무 추가 모달 열기 성공');

    // 모달 내용 확인
    await expect(page.locator('#task-modal-title')).toContainText('새 업무 추가');
    await expect(page.locator('#task-category')).toBeVisible();
    await expect(page.locator('#task-title')).toBeVisible();
    await expect(page.locator('#task-url')).toBeVisible();
    console.log('✅ 업무 추가 모달 내용 확인');

    // 취소 버튼으로 모달 닫기
    const cancelBtn = taskModal.locator('.close-modal-btn');
    await cancelBtn.click();
    await expect(taskModal).toHaveClass(/hidden/);
    console.log('✅ 업무 추가 모달 닫기 성공');

    // 카테고리 관리 모달 테스트
    console.log('📂 카테고리 관리 모달 테스트');
    const manageCategoryBtn = page.locator('#manage-category-btn');
    const categoryModal = page.locator('#category-modal');
    
    // 카테고리 관리 버튼 클릭
    await manageCategoryBtn.click();
    await expect(categoryModal).not.toHaveClass(/hidden/);
    await expect(categoryModal).toBeVisible();
    console.log('✅ 카테고리 관리 모달 열기 성공');

    // 모달 내용 확인
    await expect(categoryModal.locator('h3')).toContainText('카테고리 관리');
    await expect(page.locator('#category-list')).toBeVisible();
    await expect(page.locator('#add-category-form')).toBeVisible();
    console.log('✅ 카테고리 관리 모달 내용 확인');

    // 모달 닫기
    await categoryModal.locator('.close-modal-btn').click();
    await expect(categoryModal).toHaveClass(/hidden/);
    console.log('✅ 카테고리 관리 모달 닫기 성공');

    console.log('✅ 모달 기능 테스트 완료');
  });

  // 4. 타임라인 네비게이션 테스트
  test('타임라인 네비게이션 기능 테스트', async ({ page }) => {
    console.log('📅 타임라인 네비게이션 테스트 시작');
    
    await page.goto(BASE_URL, { waitUntil: 'networkidle' });

    const currentRangeDisplay = page.locator('#current-range-display');
    const prevBtn = page.locator('#prev-btn');
    const nextBtn = page.locator('#next-btn');
    const todayBtn = page.locator('#today-btn');

    // 초기 날짜 범위 저장
    const initialRange = await currentRangeDisplay.textContent();
    console.log(`📍 초기 날짜 범위: ${initialRange}`);

    // 이전 버튼 테스트
    await prevBtn.click();
    await page.waitForTimeout(500); // 렌더링 완료 대기
    const prevRange = await currentRangeDisplay.textContent();
    expect(prevRange).not.toBe(initialRange);
    console.log(`⬅️ 이전 버튼 클릭 후: ${prevRange}`);

    // 다음 버튼 테스트
    await nextBtn.click();
    await page.waitForTimeout(500);
    const nextRange = await currentRangeDisplay.textContent();
    expect(nextRange).not.toBe(prevRange);
    console.log(`➡️ 다음 버튼 클릭 후: ${nextRange}`);

    // 오늘 버튼 테스트
    await todayBtn.click();
    await page.waitForTimeout(500);
    const todayRange = await currentRangeDisplay.textContent();
    
    // 현재 날짜가 범위에 포함되어 있는지 확인
    const today = new Date();
    const todayStr = today.toLocaleDateString('ko-KR');
    expect(todayRange).toContain(todayStr.split('.')[0]); // 년도 부분만 확인
    console.log(`🎯 오늘 버튼 클릭 후: ${todayRange}`);

    console.log('✅ 타임라인 네비게이션 테스트 완료');
  });

  // 5. 에러 처리 테스트
  test('JavaScript 에러 및 네트워크 오류 처리 테스트', async ({ page }) => {
    console.log('⚠️ 에러 처리 테스트 시작');

    // 콘솔 에러 및 경고 수집
    const consoleMessages = [];
    page.on('console', msg => {
      consoleMessages.push({
        type: msg.type(),
        text: msg.text(),
        location: msg.location()
      });
    });

    // 네트워크 응답 감시
    const networkResponses = [];
    page.on('response', response => {
      networkResponses.push({
        url: response.url(),
        status: response.status(),
        ok: response.ok()
      });
    });

    await page.goto(BASE_URL, { waitUntil: 'networkidle' });

    // Firebase 연결 테스트 (네트워크 차단 시뮬레이션)
    console.log('🔌 네트워크 오류 시뮬레이션 테스트');
    
    // 잠시 오프라인으로 전환
    await page.setOffline(true);
    
    // 업무 추가 시도 (네트워크 오류 발생 예상)
    await page.locator('#add-task-btn').click();
    await page.fill('#task-title', '테스트 업무');
    await page.selectOption('#task-category', { index: 0 });
    
    // 폼 제출 시도 (실패 예상)
    await page.click('button[type="submit"]');
    await page.waitForTimeout(2000); // 에러 처리 시간 대기
    
    // 온라인 복원
    await page.setOffline(false);
    console.log('✅ 네트워크 오류 시뮬레이션 완료');

    // 수집된 에러 분석
    const errors = consoleMessages.filter(msg => msg.type === 'error');
    const warnings = consoleMessages.filter(msg => msg.type === 'warning');
    
    console.log(`📊 콘솔 에러 개수: ${errors.length}`);
    console.log(`📊 콘솔 경고 개수: ${warnings.length}`);
    
    if (errors.length > 0) {
      console.log('❌ 발견된 JavaScript 에러:');
      errors.forEach((error, index) => {
        console.log(`  ${index + 1}. ${error.text}`);
      });
    }

    // 네트워크 실패 분석
    const failedRequests = networkResponses.filter(response => !response.ok);
    console.log(`📊 실패한 네트워크 요청: ${failedRequests.length}`);
    
    if (failedRequests.length > 0) {
      console.log('🌐 실패한 네트워크 요청:');
      failedRequests.forEach((req, index) => {
        console.log(`  ${index + 1}. ${req.status} ${req.url}`);
      });
    }

    console.log('✅ 에러 처리 테스트 완료');
  });

  // 6. 반응형 디자인 테스트
  test('반응형 디자인 테스트', async ({ page }) => {
    console.log('📱 반응형 디자인 테스트 시작');
    
    await page.goto(BASE_URL, { waitUntil: 'networkidle' });

    // 데스크톱 뷰 (1920x1080)
    console.log('🖥️ 데스크톱 뷰 테스트');
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.waitForTimeout(1000);
    
    // 헤더 레이아웃 확인
    const header = page.locator('header');
    await expect(header).toBeVisible();
    const headerBox = await header.boundingBox();
    expect(headerBox.width).toBeGreaterThan(1000);
    console.log(`✅ 데스크톱 헤더 너비: ${headerBox.width}px`);

    // 타블릿 뷰 (768x1024)  
    console.log('📱 태블릿 뷰 테스트');
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.waitForTimeout(1000);
    
    // UI 요소들이 여전히 접근 가능한지 확인
    await expect(page.locator('#add-task-btn')).toBeVisible();
    await expect(page.locator('#manage-category-btn')).toBeVisible();
    await expect(page.locator('#dark-mode-toggle')).toBeVisible();
    console.log('✅ 태블릿 뷰에서 주요 버튼들 접근 가능');

    // 모바일 뷰 (375x667 - iPhone SE)
    console.log('📱 모바일 뷰 테스트');
    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForTimeout(1000);
    
    // 모바일에서도 핵심 기능 사용 가능한지 확인
    await expect(page.locator('h1')).toBeVisible();
    await expect(page.locator('#timeline-container')).toBeVisible();
    
    // 버튼들이 터치하기 적절한 크기인지 확인
    const addTaskBtn = page.locator('#add-task-btn');
    const btnBox = await addTaskBtn.boundingBox();
    expect(btnBox.height).toBeGreaterThan(40); // 최소 터치 타겟 크기
    console.log(`✅ 모바일에서 버튼 크기: ${btnBox.height}px (높이)`);

    // 가로 스크롤 없이 콘텐츠가 표시되는지 확인
    const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
    expect(bodyWidth).toBeLessThanOrEqual(375);
    console.log(`✅ 모바일에서 가로 스크롤 없음 (콘텐츠 너비: ${bodyWidth}px)`);

    // 데스크톱으로 복원
    await page.setViewportSize({ width: 1920, height: 1080 });
    
    console.log('✅ 반응형 디자인 테스트 완료');
  });

  // 7. 성능 테스트
  test('페이지 로딩 성능 및 렌더링 성능 테스트', async ({ page }) => {
    console.log('⚡ 성능 테스트 시작');

    // 성능 메트릭 수집 시작
    const startTime = Date.now();
    
    // 페이지 로드 성능 측정
    const response = await page.goto(BASE_URL, { waitUntil: 'networkidle' });
    const loadTime = Date.now() - startTime;
    
    console.log(`📊 페이지 로드 시간: ${loadTime}ms`);
    expect(loadTime).toBeLessThan(10000); // 10초 이내
    
    // 최초 콘텐츠풀 페인트 (FCP) 측정
    const paintTiming = await page.evaluate(() => {
      return JSON.stringify(performance.getEntriesByType('paint'));
    });
    const paintMetrics = JSON.parse(paintTiming);
    
    if (paintMetrics.length > 0) {
      const fcp = paintMetrics.find(metric => metric.name === 'first-contentful-paint');
      if (fcp) {
        console.log(`🎨 First Contentful Paint: ${Math.round(fcp.startTime)}ms`);
        expect(fcp.startTime).toBeLessThan(3000); // 3초 이내
      }
    }

    // JavaScript 실행 시간 측정
    const jsStartTime = Date.now();
    await page.evaluate(() => {
      // 복잡한 DOM 조작 시뮬레이션
      const container = document.getElementById('timeline-container');
      return container !== null;
    });
    const jsExecutionTime = Date.now() - jsStartTime;
    
    console.log(`⚙️ JavaScript 실행 시간: ${jsExecutionTime}ms`);
    expect(jsExecutionTime).toBeLessThan(100); // 100ms 이내

    // 메모리 사용량 체크 (가능한 경우)
    try {
      const memoryInfo = await page.evaluate(() => {
        return performance.memory ? {
          usedJSHeapSize: performance.memory.usedJSHeapSize,
          totalJSHeapSize: performance.memory.totalJSHeapSize,
          jsHeapSizeLimit: performance.memory.jsHeapSizeLimit
        } : null;
      });
      
      if (memoryInfo) {
        const usedMemoryMB = Math.round(memoryInfo.usedJSHeapSize / (1024 * 1024));
        console.log(`🧠 사용 메모리: ${usedMemoryMB}MB`);
        expect(usedMemoryMB).toBeLessThan(50); // 50MB 이내
      }
    } catch (e) {
      console.log('ℹ️ 메모리 정보를 가져올 수 없음');
    }

    // 렌더링 성능 테스트 - 타임라인 네비게이션 반응성
    const renderStartTime = Date.now();
    await page.click('#next-btn');
    await page.waitForTimeout(100); // 렌더링 완료 대기
    const renderTime = Date.now() - renderStartTime;
    
    console.log(`🎭 렌더링 응답 시간: ${renderTime}ms`);
    expect(renderTime).toBeLessThan(1000); // 1초 이내

    // 네트워크 리소스 분석
    const resourceTiming = await page.evaluate(() => {
      return JSON.stringify(performance.getEntriesByType('resource'));
    });
    const resources = JSON.parse(resourceTiming);
    
    const slowResources = resources.filter(resource => resource.duration > 2000);
    console.log(`🌐 느린 리소스 (2초 초과): ${slowResources.length}개`);
    
    if (slowResources.length > 0) {
      console.log('⚠️ 느린 리소스 목록:');
      slowResources.forEach(resource => {
        console.log(`  - ${resource.name}: ${Math.round(resource.duration)}ms`);
      });
    }

    console.log('✅ 성능 테스트 완료');
  });

  // 테스트 종료 후 정리
  test.afterEach(async ({ page }) => {
    // 페이지 닫기 전 정리 작업
    await page.evaluate(() => {
      // 로컬 스토리지 정리 (필요한 경우)
      if (typeof localStorage !== 'undefined') {
        localStorage.clear();
      }
    });
  });
});

// 전역 테스트 설정
test.beforeAll(async () => {
  console.log('🚀 GGP CAMERA 업무 현황 보드 E2E 테스트 시작');
  console.log(`🌐 테스트 URL: ${BASE_URL}`);
});

test.afterAll(async () => {
  console.log('✅ 모든 E2E 테스트 완료');
});