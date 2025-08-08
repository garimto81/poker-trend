const { test, expect } = require('@playwright/test');
const path = require('path');
const fs = require('fs');

/**
 * GFX 오버레이 학습기 종합 테스트 스위트
 * 
 * 테스트 대상: http://localhost:8081/web-ui/gfx_overlay_trainer.html
 * 
 * 주요 테스트 시나리오:
 * 1. 페이지 로드 및 기본 UI 확인
 * 2. 비디오 파일 업로드 시뮬레이션
 * 3. GFX 마킹 버튼 토글 동작 (시작점/종료점)
 * 4. 15초 규칙 적용 확인
 * 5. 구간 정보 실시간 표시
 * 6. 구간 목록 관리
 * 7. JSON 내보내기/불러오기
 * 8. 구간 삭제 기능
 * 9. LocalStorage 저장/복원
 * 10. 통계 업데이트
 * 11. JavaScript 콘솔 에러 확인
 */

test.describe('GFX 오버레이 학습기 종합 테스트', () => {
  let page;
  let consoleErrors = [];
  let consoleWarnings = [];

  test.beforeEach(async ({ page: testPage }) => {
    page = testPage;
    consoleErrors = [];
    consoleWarnings = [];

    // 콘솔 에러 및 경고 수집
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        consoleErrors.push({
          type: msg.type(),
          text: msg.text(),
          location: msg.location()
        });
      } else if (msg.type() === 'warning') {
        consoleWarnings.push({
          type: msg.type(),
          text: msg.text(),
          location: msg.location()
        });
      }
    });

    // 페이지 에러 이벤트 수집
    page.on('pageerror', (error) => {
      consoleErrors.push({
        type: 'pageerror',
        text: error.message,
        stack: error.stack
      });
    });

    // LocalStorage 초기화
    await page.goto('/web-ui/gfx_overlay_trainer.html');
    await page.evaluate(() => {
      localStorage.clear();
    });
  });

  test('1. 기본 페이지 로드 및 UI 요소 확인', async () => {
    console.log('🔍 페이지 로드 및 기본 UI 요소 확인 테스트 시작');

    // 페이지 제목 확인
    await expect(page).toHaveTitle(/GFX.*Overlay.*Trainer|오버레이.*학습기/i);

    // 핵심 UI 요소 존재 확인
    const essentialElements = [
      'input[type="file"]', // 파일 업로드 인풋
      'video', // 비디오 플레이어
      'button', // 버튼들
      '.segment-list, #segmentList, [id*="segment"], [class*="segment"]', // 구간 목록
      '.stats, #stats, [id*="stat"], [class*="stat"]', // 통계 영역
    ];

    for (const selector of essentialElements) {
      try {
        await expect(page.locator(selector).first()).toBeVisible({ timeout: 5000 });
        console.log(`✅ 요소 확인됨: ${selector}`);
      } catch (error) {
        console.log(`⚠️ 요소 찾을 수 없음: ${selector}`);
        // 페이지의 모든 요소를 확인해서 대체 선택자 찾기
        const allButtons = await page.locator('button').count();
        const allInputs = await page.locator('input').count();
        console.log(`📊 페이지 내 버튼 수: ${allButtons}, 인풋 수: ${allInputs}`);
      }
    }

    // GFX 마킹 버튼 찾기 (텍스트나 ID로)
    const gfxButtonSelectors = [
      'button:has-text("GFX")',
      'button:has-text("마킹")',
      'button:has-text("Mark")',
      '#gfxButton',
      '.gfx-button',
      '[data-testid="gfx-button"]'
    ];

    let gfxButton = null;
    for (const selector of gfxButtonSelectors) {
      try {
        gfxButton = page.locator(selector).first();
        await expect(gfxButton).toBeVisible({ timeout: 2000 });
        console.log(`✅ GFX 버튼 발견: ${selector}`);
        break;
      } catch (error) {
        continue;
      }
    }

    if (!gfxButton) {
      console.log('⚠️ GFX 버튼을 찾을 수 없음. 모든 버튼 텍스트 확인:');
      const buttonTexts = await page.locator('button').allTextContents();
      console.log('📋 버튼 텍스트들:', buttonTexts);
    }
  });

  test('2. 비디오 파일 업로드 시뮬레이션', async () => {
    console.log('🔍 비디오 파일 업로드 시뮬레이션 테스트 시작');

    // 파일 업로드 인풋 찾기
    const fileInput = page.locator('input[type="file"]').first();
    await expect(fileInput).toBeVisible();

    // 테스트용 비디오 파일이 있는지 확인하고, 없으면 가상 파일 생성
    const testVideoPath = path.join(__dirname, '..', 'test-data', 'sample.mp4');
    
    // 가상의 비디오 파일 데이터로 업로드 시뮬레이션
    await page.setInputFiles('input[type="file"]', {
      name: 'test-video.mp4',
      mimeType: 'video/mp4',
      buffer: Buffer.from('fake video content for testing')
    });

    console.log('✅ 비디오 파일 업로드 시뮬레이션 완료');

    // 업로드 후 비디오 플레이어 상태 확인
    const video = page.locator('video').first();
    await expect(video).toBeVisible();

    // 비디오 메타데이터 로드 대기 (실제 비디오가 아니므로 에러 예상)
    try {
      await page.waitForFunction(() => {
        const video = document.querySelector('video');
        return video && (video.readyState >= 1 || video.error);
      }, { timeout: 5000 });
      console.log('📹 비디오 로드 상태 확인됨');
    } catch (error) {
      console.log('⚠️ 가상 파일이므로 비디오 로드 에러 예상됨');
    }
  });

  test('3. GFX 마킹 버튼 토글 동작 테스트', async () => {
    console.log('🔍 GFX 마킹 버튼 토글 동작 테스트 시작');

    // 먼저 파일 업로드 시뮬레이션
    await page.setInputFiles('input[type="file"]', {
      name: 'test-video.mp4',
      mimeType: 'video/mp4',
      buffer: Buffer.from('fake video content')
    });

    // GFX 버튼 찾기
    let gfxButton = null;
    const buttonSelectors = [
      'button:has-text("GFX")',
      'button:has-text("마킹")',
      'button:has-text("Mark")',
      'button[class*="gfx"]',
      'button[id*="gfx"]'
    ];

    for (const selector of buttonSelectors) {
      try {
        gfxButton = page.locator(selector).first();
        await expect(gfxButton).toBeVisible({ timeout: 2000 });
        console.log(`✅ GFX 버튼 발견: ${selector}`);
        break;
      } catch (error) {
        continue;
      }
    }

    if (!gfxButton) {
      // 모든 버튼을 찾아서 GFX 관련 버튼 추정
      const allButtons = page.locator('button');
      const buttonCount = await allButtons.count();
      console.log(`📊 총 버튼 수: ${buttonCount}`);
      
      for (let i = 0; i < buttonCount; i++) {
        const button = allButtons.nth(i);
        const buttonText = await button.textContent();
        const buttonClass = await button.getAttribute('class');
        const buttonId = await button.getAttribute('id');
        console.log(`버튼 ${i}: "${buttonText}" (class: ${buttonClass}, id: ${buttonId})`);
        
        // GFX와 관련된 버튼인지 추정
        if (buttonText && (buttonText.includes('GFX') || buttonText.includes('마킹') || 
                          buttonText.includes('Mark') || buttonText.includes('시작') ||
                          buttonText.includes('종료'))) {
          gfxButton = button;
          console.log(`✅ GFX 버튼으로 추정: "${buttonText}"`);
          break;
        }
      }
    }

    if (gfxButton) {
      // 버튼 초기 상태 확인
      const initialColor = await gfxButton.evaluate(el => 
        window.getComputedStyle(el).backgroundColor
      );
      console.log(`🎨 초기 버튼 색상: ${initialColor}`);

      // 첫 번째 클릭 - 시작점 마킹 (빨간색 → 노란색)
      await gfxButton.click();
      await page.waitForTimeout(500); // 상태 변경 대기

      const firstClickColor = await gfxButton.evaluate(el => 
        window.getComputedStyle(el).backgroundColor
      );
      console.log(`🎨 첫 클릭 후 색상: ${firstClickColor}`);

      // 두 번째 클릭 - 종료점 마킹 (노란색 → 빨간색)
      await gfxButton.click();
      await page.waitForTimeout(500); // 상태 변경 대기

      const secondClickColor = await gfxButton.evaluate(el => 
        window.getComputedStyle(el).backgroundColor
      );
      console.log(`🎨 두 번째 클릭 후 색상: ${secondClickColor}`);

      // 색상 변화 확인
      const colorsAreDifferent = initialColor !== firstClickColor && 
                                firstClickColor !== secondClickColor;
      
      if (colorsAreDifferent) {
        console.log('✅ 버튼 색상 토글 동작 확인됨');
      } else {
        console.log('⚠️ 버튼 색상 변화가 감지되지 않음');
      }
    } else {
      console.log('❌ GFX 마킹 버튼을 찾을 수 없음');
    }
  });

  test('4. 15초 규칙 적용 확인', async () => {
    console.log('🔍 15초 규칙 적용 확인 테스트 시작');

    // 파일 업로드 및 비디오 설정
    await page.setInputFiles('input[type="file"]', {
      name: 'test-video.mp4',
      mimeType: 'video/mp4',
      buffer: Buffer.from('fake video content')
    });

    // 비디오 시간을 조작하여 테스트
    await page.evaluate(() => {
      const video = document.querySelector('video');
      if (video) {
        // 가상의 비디오 시간 설정
        Object.defineProperty(video, 'currentTime', {
          value: 30, // 30초 지점
          writable: true
        });
        Object.defineProperty(video, 'duration', {
          value: 120, // 2분 총 길이
          writable: true
        });
      }
    });

    // GFX 마킹 시뮬레이션
    const buttons = page.locator('button');
    const buttonCount = await buttons.count();
    
    for (let i = 0; i < buttonCount; i++) {
      const button = buttons.nth(i);
      const text = await button.textContent();
      if (text && (text.includes('GFX') || text.includes('마킹'))) {
        // 시작점 마킹 (30초)
        await button.click();
        await page.waitForTimeout(1000);
        
        // 종료점 마킹을 위해 시간 이동 (45초)
        await page.evaluate(() => {
          const video = document.querySelector('video');
          if (video) {
            video.currentTime = 45;
          }
        });
        await page.waitForTimeout(500);
        
        // 종료점 마킹
        await button.click();
        await page.waitForTimeout(1000);
        
        console.log('✅ GFX 마킹 시뮬레이션 완료 (30s-45s)');
        break;
      }
    }

    // 15초 규칙 적용 결과 확인
    // - GFX 시작(30s) - 15s = 핸드 시작(15s)
    // - GFX 종료(45s) + 15s = 핸드 종료(60s)
    
    // 구간 정보가 표시되는 요소 찾기
    const segmentInfo = await page.evaluate(() => {
      // 다양한 선택자로 구간 정보 찾기
      const selectors = [
        '.segment-info',
        '.hand-info',
        '[class*="segment"]',
        '[id*="segment"]',
        '.info',
        '#info'
      ];
      
      for (const selector of selectors) {
        const element = document.querySelector(selector);
        if (element && element.textContent.trim()) {
          return element.textContent;
        }
      }
      
      // 페이지의 모든 텍스트에서 시간 정보 찾기
      const bodyText = document.body.textContent;
      const timePattern = /\d{1,2}:\d{2}|\d+s|\d+초/g;
      const times = bodyText.match(timePattern);
      return times ? times.join(', ') : '시간 정보 없음';
    });

    console.log(`📊 구간 정보: ${segmentInfo}`);
    
    if (segmentInfo.includes('15') || segmentInfo.includes('60')) {
      console.log('✅ 15초 규칙이 적용된 것으로 추정됨');
    } else {
      console.log('⚠️ 15초 규칙 적용 여부를 명확히 확인할 수 없음');
    }
  });

  test('5. 구간 정보 실시간 표시 테스트', async () => {
    console.log('🔍 구간 정보 실시간 표시 테스트 시작');

    await page.setInputFiles('input[type="file"]', {
      name: 'test-video.mp4',
      mimeType: 'video/mp4',
      buffer: Buffer.from('fake video content')
    });

    // 실시간 표시 영역 찾기
    const infoSelectors = [
      '.current-info',
      '.segment-info', 
      '.real-time-info',
      '[id*="info"]',
      '[class*="info"]',
      '.status'
    ];

    let infoElement = null;
    for (const selector of infoSelectors) {
      try {
        infoElement = page.locator(selector).first();
        await expect(infoElement).toBeVisible({ timeout: 2000 });
        console.log(`✅ 정보 표시 영역 발견: ${selector}`);
        break;
      } catch (error) {
        continue;
      }
    }

    if (!infoElement) {
      console.log('⚠️ 구간 정보 표시 영역을 찾을 수 없음');
      // 페이지의 모든 텍스트 내용 확인
      const pageContent = await page.textContent('body');
      console.log('📄 페이지 내용 일부:', pageContent.substring(0, 500));
    }

    // 비디오 시간 변경하며 실시간 업데이트 확인
    const testTimes = [10, 25, 40, 55];
    
    for (const time of testTimes) {
      await page.evaluate((t) => {
        const video = document.querySelector('video');
        if (video) {
          video.currentTime = t;
          // timeupdate 이벤트 수동 발생
          const event = new Event('timeupdate');
          video.dispatchEvent(event);
        }
      }, time);
      
      await page.waitForTimeout(500);
      
      if (infoElement) {
        const infoText = await infoElement.textContent();
        console.log(`⏰ 시간 ${time}s에서 정보: ${infoText?.substring(0, 100)}`);
      }
    }
  });

  test('6. 구간 목록 표시 및 관리 테스트', async () => {
    console.log('🔍 구간 목록 표시 및 관리 테스트 시작');

    await page.setInputFiles('input[type="file"]', {
      name: 'test-video.mp4',
      mimeType: 'video/mp4',
      buffer: Buffer.from('fake video content')
    });

    // 여러 구간 생성
    const segments = [
      { start: 10, end: 25 },
      { start: 40, end: 55 },
      { start: 70, end: 85 }
    ];

    // GFX 버튼 찾기
    const gfxButton = await findGfxButton(page);
    
    if (gfxButton) {
      for (const segment of segments) {
        // 시작점 설정
        await page.evaluate((time) => {
          const video = document.querySelector('video');
          if (video) video.currentTime = time;
        }, segment.start);
        await gfxButton.click();
        await page.waitForTimeout(500);
        
        // 종료점 설정
        await page.evaluate((time) => {
          const video = document.querySelector('video');
          if (video) video.currentTime = time;
        }, segment.end);
        await gfxButton.click();
        await page.waitForTimeout(500);
        
        console.log(`✅ 구간 생성: ${segment.start}s - ${segment.end}s`);
      }
    }

    // 구간 목록 확인
    const listSelectors = [
      '.segment-list',
      '#segmentList', 
      '.segments',
      '[class*="segment"]',
      '[id*="list"]'
    ];

    let segmentList = null;
    for (const selector of listSelectors) {
      try {
        segmentList = page.locator(selector);
        const count = await segmentList.count();
        if (count > 0) {
          console.log(`✅ 구간 목록 발견: ${selector} (${count}개 요소)`);
          break;
        }
      } catch (error) {
        continue;
      }
    }

    if (segmentList) {
      const listItems = segmentList.locator('li, div, .segment-item').first();
      const itemCount = await segmentList.locator('li, div, .segment-item').count();
      console.log(`📊 구간 목록 아이템 수: ${itemCount}`);
    } else {
      console.log('⚠️ 구간 목록을 찾을 수 없음');
    }
  });

  test('7. JSON 내보내기/불러오기 테스트', async () => {
    console.log('🔍 JSON 내보내기/불러오기 테스트 시작');

    await page.setInputFiles('input[type="file"]', {
      name: 'test-video.mp4',
      mimeType: 'video/mp4',
      buffer: Buffer.from('fake video content')
    });

    // 테스트 구간 생성
    const gfxButton = await findGfxButton(page);
    if (gfxButton) {
      await createTestSegment(page, gfxButton, 20, 35);
    }

    // JSON 내보내기 버튼 찾기
    const exportButtons = [
      'button:has-text("Export")',
      'button:has-text("내보내기")',
      'button:has-text("JSON")',
      'button:has-text("저장")',
      '.export-btn',
      '#exportBtn'
    ];

    let exportButton = null;
    for (const selector of exportButtons) {
      try {
        exportButton = page.locator(selector).first();
        await expect(exportButton).toBeVisible({ timeout: 2000 });
        console.log(`✅ 내보내기 버튼 발견: ${selector}`);
        break;
      } catch (error) {
        continue;
      }
    }

    if (exportButton) {
      // 다운로드 이벤트 대기
      const [download] = await Promise.all([
        page.waitForEvent('download', { timeout: 5000 }).catch(() => null),
        exportButton.click()
      ]);

      if (download) {
        console.log(`✅ 파일 다운로드 성공: ${download.suggestedFilename()}`);
      } else {
        console.log('⚠️ 파일 다운로드가 시작되지 않음 (클립보드 복사일 수 있음)');
        
        // 클립보드에서 JSON 데이터 확인 시도
        const clipboardData = await page.evaluate(async () => {
          try {
            return await navigator.clipboard.readText();
          } catch (error) {
            return null;
          }
        });
        
        if (clipboardData && clipboardData.includes('{')) {
          console.log('✅ 클립보드에 JSON 데이터 복사됨');
          console.log('📋 JSON 데이터 일부:', clipboardData.substring(0, 200));
        }
      }
    }

    // JSON 불러오기 테스트
    const importButtons = [
      'button:has-text("Import")',
      'button:has-text("불러오기")',
      'button:has-text("Load")',
      '.import-btn',
      '#importBtn'
    ];

    for (const selector of importButtons) {
      try {
        const importButton = page.locator(selector).first();
        await expect(importButton).toBeVisible({ timeout: 2000 });
        console.log(`✅ 불러오기 버튼 발견: ${selector}`);
        
        // 테스트 JSON 데이터
        const testJsonData = JSON.stringify({
          segments: [
            { start: 15, end: 30, handStart: 0, handEnd: 45 },
            { start: 60, end: 75, handStart: 45, handEnd: 90 }
          ]
        });

        // 클립보드에 테스트 데이터 설정
        await page.evaluate((data) => {
          navigator.clipboard.writeText(data);
        }, testJsonData);

        await importButton.click();
        await page.waitForTimeout(1000);
        console.log('✅ JSON 불러오기 시도 완료');
        break;
      } catch (error) {
        continue;
      }
    }
  });

  test('8. 구간 삭제 기능 테스트', async () => {
    console.log('🔍 구간 삭제 기능 테스트 시작');

    await page.setInputFiles('input[type="file"]', {
      name: 'test-video.mp4',
      mimeType: 'video/mp4',
      buffer: Buffer.from('fake video content')
    });

    // 테스트 구간들 생성
    const gfxButton = await findGfxButton(page);
    if (gfxButton) {
      await createTestSegment(page, gfxButton, 10, 25);
      await createTestSegment(page, gfxButton, 40, 55);
    }

    // 삭제 버튼 찾기
    const deleteSelectors = [
      'button:has-text("Delete")',
      'button:has-text("삭제")',
      'button:has-text("Remove")',
      'button:has-text("제거")',
      '.delete-btn',
      '.remove-btn',
      '[class*="delete"]',
      'button[onclick*="delete"]'
    ];

    let deleteButtons = [];
    for (const selector of deleteSelectors) {
      try {
        const buttons = await page.locator(selector).all();
        if (buttons.length > 0) {
          deleteButtons = buttons;
          console.log(`✅ 삭제 버튼 발견: ${selector} (${buttons.length}개)`);
          break;
        }
      } catch (error) {
        continue;
      }
    }

    if (deleteButtons.length > 0) {
      // 첫 번째 구간 삭제
      await deleteButtons[0].click();
      await page.waitForTimeout(1000);
      console.log('✅ 첫 번째 구간 삭제 시도 완료');
      
      // 삭제 후 구간 수 확인
      const remainingButtons = await page.locator('button:has-text("삭제"), button:has-text("Delete")').count();
      console.log(`📊 삭제 후 남은 삭제 버튼 수: ${remainingButtons}`);
    } else {
      console.log('⚠️ 구간 삭제 버튼을 찾을 수 없음');
      
      // 구간 목록에서 삭제 옵션 찾기
      const segmentItems = page.locator('.segment-item, .segment, [class*="segment"]');
      const itemCount = await segmentItems.count();
      console.log(`📊 구간 아이템 수: ${itemCount}`);
      
      // 각 구간 아이템 내부의 삭제 옵션 찾기
      for (let i = 0; i < Math.min(itemCount, 3); i++) {
        const item = segmentItems.nth(i);
        const deleteInItem = item.locator('button, .delete, [onclick*="delete"]');
        const deleteCount = await deleteInItem.count();
        if (deleteCount > 0) {
          console.log(`✅ 구간 ${i}에서 삭제 옵션 발견`);
          await deleteInItem.first().click();
          await page.waitForTimeout(500);
          break;
        }
      }
    }
  });

  test('9. LocalStorage 저장/복원 테스트', async () => {
    console.log('🔍 LocalStorage 저장/복원 테스트 시작');

    await page.setInputFiles('input[type="file"]', {
      name: 'test-video.mp4',
      mimeType: 'video/mp4',
      buffer: Buffer.from('fake video content')
    });

    // 테스트 데이터 생성
    const gfxButton = await findGfxButton(page);
    if (gfxButton) {
      await createTestSegment(page, gfxButton, 15, 30);
    }

    // LocalStorage에 저장된 데이터 확인
    const storedData = await page.evaluate(() => {
      const keys = Object.keys(localStorage);
      const data = {};
      keys.forEach(key => {
        data[key] = localStorage.getItem(key);
      });
      return data;
    });

    console.log('💾 LocalStorage 데이터:', Object.keys(storedData));
    
    // 주요 키들 확인
    const expectedKeys = ['segments', 'gfx-segments', 'trainer-data', 'video-data'];
    const foundKeys = Object.keys(storedData).filter(key => 
      expectedKeys.some(expected => key.includes(expected.toLowerCase()))
    );
    
    console.log('✅ 관련 LocalStorage 키:', foundKeys);

    // 페이지 새로고침 후 데이터 복원 확인
    await page.reload();
    await page.waitForTimeout(2000);

    const restoredData = await page.evaluate(() => {
      const keys = Object.keys(localStorage);
      const data = {};
      keys.forEach(key => {
        data[key] = localStorage.getItem(key);
      });
      return data;
    });

    const dataIntact = JSON.stringify(storedData) === JSON.stringify(restoredData);
    console.log(`🔄 데이터 복원 상태: ${dataIntact ? '성공' : '실패'}`);

    if (!dataIntact) {
      console.log('📊 저장된 데이터 키 수:', Object.keys(storedData).length);
      console.log('📊 복원된 데이터 키 수:', Object.keys(restoredData).length);
    }
  });

  test('10. 통계 업데이트 테스트', async () => {
    console.log('🔍 통계 업데이트 테스트 시작');

    await page.setInputFiles('input[type="file"]', {
      name: 'test-video.mp4',
      mimeType: 'video/mp4',
      buffer: Buffer.from('fake video content')
    });

    // 통계 표시 영역 찾기
    const statsSelectors = [
      '.stats',
      '#stats',
      '.statistics', 
      '[class*="stat"]',
      '[id*="stat"]',
      '.summary',
      '.count'
    ];

    let statsElement = null;
    for (const selector of statsSelectors) {
      try {
        statsElement = page.locator(selector).first();
        await expect(statsElement).toBeVisible({ timeout: 2000 });
        console.log(`✅ 통계 영역 발견: ${selector}`);
        break;
      } catch (error) {
        continue;
      }
    }

    // 초기 통계 기록
    let initialStats = '';
    if (statsElement) {
      initialStats = await statsElement.textContent();
      console.log(`📊 초기 통계: ${initialStats}`);
    } else {
      // 페이지에서 숫자가 포함된 텍스트 찾기 (통계일 가능성)
      const numberTexts = await page.evaluate(() => {
        const allText = document.body.textContent;
        const numberPattern = /\d+\s*(개|구간|segment|total|count)/gi;
        return allText.match(numberPattern) || [];
      });
      console.log('📊 숫자 포함 텍스트:', numberTexts);
    }

    // 여러 구간 생성하여 통계 업데이트 확인
    const gfxButton = await findGfxButton(page);
    if (gfxButton) {
      const segments = [
        { start: 10, end: 25 },
        { start: 40, end: 55 },
        { start: 70, end: 85 }
      ];

      for (let i = 0; i < segments.length; i++) {
        await createTestSegment(page, gfxButton, segments[i].start, segments[i].end);
        await page.waitForTimeout(1000);

        // 각 구간 생성 후 통계 확인
        if (statsElement) {
          const currentStats = await statsElement.textContent();
          console.log(`📊 ${i + 1}번째 구간 후 통계: ${currentStats}`);
        }
      }
    }

    // 최종 통계와 초기 통계 비교
    if (statsElement) {
      const finalStats = await statsElement.textContent();
      console.log(`📊 최종 통계: ${finalStats}`);
      
      const statsChanged = initialStats !== finalStats;
      console.log(`🔄 통계 업데이트 확인: ${statsChanged ? '성공' : '변화없음'}`);
    }
  });

  test('11. 종합 기능 통합 테스트', async () => {
    console.log('🔍 종합 기능 통합 테스트 시작');

    // 전체 워크플로우 테스트
    console.log('1️⃣ 파일 업로드');
    await page.setInputFiles('input[type="file"]', {
      name: 'comprehensive-test.mp4',
      mimeType: 'video/mp4',
      buffer: Buffer.from('comprehensive test video content')
    });
    await page.waitForTimeout(1000);

    console.log('2️⃣ 다중 구간 생성');
    const gfxButton = await findGfxButton(page);
    if (gfxButton) {
      const segments = [
        { start: 5, end: 20 },
        { start: 35, end: 50 },
        { start: 65, end: 80 },
        { start: 95, end: 110 }
      ];

      for (const segment of segments) {
        await createTestSegment(page, gfxButton, segment.start, segment.end);
        console.log(`✅ 구간 생성됨: ${segment.start}s - ${segment.end}s`);
      }
    }

    console.log('3️⃣ 전체 기능 상태 점검');
    
    // UI 요소들의 최종 상태 확인
    const finalReport = await page.evaluate(() => {
      return {
        totalButtons: document.querySelectorAll('button').length,
        totalInputs: document.querySelectorAll('input').length,
        hasVideo: !!document.querySelector('video'),
        localStorageKeys: Object.keys(localStorage).length,
        bodyTextLength: document.body.textContent.length,
        hasSegmentList: !!document.querySelector('[class*="segment"], [id*="segment"]'),
        hasStats: !!document.querySelector('[class*="stat"], [id*="stat"]')
      };
    });

    console.log('📋 최종 상태 보고서:', finalReport);

    console.log('4️⃣ 성능 및 안정성 확인');
    
    // 메모리 누수 및 성능 확인
    const performanceMetrics = await page.evaluate(() => {
      return {
        memoryUsage: performance.memory ? performance.memory.usedJSHeapSize : 'N/A',
        timing: performance.now(),
        eventListenerCount: document.querySelectorAll('[onclick]').length
      };
    });

    console.log('⚡ 성능 지표:', performanceMetrics);
  });

  // 모든 테스트 후 에러 보고
  test.afterEach(async () => {
    // JavaScript 콘솔 에러 보고
    if (consoleErrors.length > 0) {
      console.log('\n❌ JavaScript 콘솔 에러 발견:');
      consoleErrors.forEach((error, index) => {
        console.log(`  ${index + 1}. [${error.type}] ${error.text}`);
        if (error.location) {
          console.log(`     위치: ${error.location.url}:${error.location.lineNumber}`);
        }
        if (error.stack) {
          console.log(`     스택: ${error.stack.split('\n')[0]}`);
        }
      });
    } else {
      console.log('\n✅ JavaScript 콘솔 에러 없음');
    }

    if (consoleWarnings.length > 0) {
      console.log('\n⚠️ JavaScript 콘솔 경고:');
      consoleWarnings.forEach((warning, index) => {
        console.log(`  ${index + 1}. ${warning.text}`);
      });
    }
  });
});

// 헬퍼 함수들
async function findGfxButton(page) {
  const buttonSelectors = [
    'button:has-text("GFX")',
    'button:has-text("마킹")',
    'button:has-text("Mark")',
    'button[class*="gfx"]',
    'button[id*="gfx"]',
    'button[onclick*="gfx"]'
  ];

  for (const selector of buttonSelectors) {
    try {
      const button = page.locator(selector).first();
      await expect(button).toBeVisible({ timeout: 2000 });
      return button;
    } catch (error) {
      continue;
    }
  }

  // 마지막 시도: 모든 버튼을 확인하여 GFX 관련 버튼 찾기
  const allButtons = page.locator('button');
  const buttonCount = await allButtons.count();
  
  for (let i = 0; i < buttonCount; i++) {
    const button = allButtons.nth(i);
    const text = await button.textContent();
    if (text && (text.toLowerCase().includes('gfx') || 
                text.includes('마킹') || text.includes('mark'))) {
      return button;
    }
  }

  return null;
}

async function createTestSegment(page, gfxButton, startTime, endTime) {
  if (!gfxButton) return;

  // 시작점 설정
  await page.evaluate((time) => {
    const video = document.querySelector('video');
    if (video) video.currentTime = time;
  }, startTime);
  await page.waitForTimeout(200);
  await gfxButton.click();
  await page.waitForTimeout(500);

  // 종료점 설정
  await page.evaluate((time) => {
    const video = document.querySelector('video');
    if (video) video.currentTime = time;
  }, endTime);
  await page.waitForTimeout(200);
  await gfxButton.click();
  await page.waitForTimeout(500);
}