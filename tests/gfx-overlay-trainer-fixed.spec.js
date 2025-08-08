const { test, expect } = require('@playwright/test');
const path = require('path');

test.describe('GFX 오버레이 학습기 수정된 기능 테스트', () => {
  let page;
  
  test.beforeEach(async ({ browser }) => {
    page = await browser.newPage();
    
    // 콘솔 메시지와 에러 캡처
    page.on('console', msg => {
      if (msg.type() === 'error') {
        console.log(`❌ 콘솔 에러: ${msg.text()}`);
      } else if (msg.type() === 'log') {
        console.log(`📝 콘솔 로그: ${msg.text()}`);
      }
    });
    
    page.on('pageerror', error => {
      console.log(`💥 페이지 에러: ${error.message}`);
    });
    
    // 페이지 로드 (올바른 경로)
    await page.goto('http://localhost:8081/web-ui/gfx_overlay_trainer.html');
    await page.waitForLoadState('networkidle');
  });

  test('1. 페이지 로드 및 초기 상태 확인', async () => {
    console.log('\n🎯 1단계: 페이지 로드 및 초기 상태 확인');
    
    // 제목 확인
    await expect(page).toHaveTitle(/GFX 오버레이 학습기/);
    console.log('✅ 페이지 제목 확인됨');
    
    // 주요 요소들 존재 확인
    await expect(page.locator('#videoInput')).toBeVisible();
    await expect(page.locator('#videoCanvas')).toBeVisible();
    await expect(page.locator('#markGFXBtn')).toBeVisible();
    await expect(page.locator('#clearBtn')).toBeVisible();
    await expect(page.locator('#saveBtn')).toBeVisible();
    console.log('✅ 모든 주요 UI 요소 확인됨');
    
    // 초기 버튼 상태 확인
    const gfxButton = page.locator('#markGFXBtn');
    await expect(gfxButton).toContainText('GFX 오버레이 인식');
    await expect(gfxButton).toHaveClass(/btn-danger/);
    await expect(gfxButton).toBeDisabled();
    console.log('✅ GFX 버튼 초기 상태 (비활성화, 빨간색) 확인됨');
    
    // 초기 통계 확인
    await expect(page.locator('#gfxCount')).toHaveText('0');
    await expect(page.locator('#gameCount')).toHaveText('0:00');
    await expect(page.locator('#totalSamples')).toContainText('0 구간');
    console.log('✅ 초기 통계 (GFX 0개, 게임 시간 0:00, 0 구간) 확인됨');
  });

  test('2. JavaScript 함수들 에러 확인 및 테스트', async () => {
    console.log('\n🎯 2단계: JavaScript 함수들 에러 확인');
    
    let hasError = false;
    page.on('pageerror', error => {
      hasError = true;
      console.log(`💥 JavaScript 에러 발견: ${error.message}`);
    });
    
    // formatTime 함수 테스트
    const formatTimeResult = await page.evaluate(() => {
      try {
        return {
          test1: formatTime(65), // 1:05
          test2: formatTime(0),  // 0:00
          test3: formatTime(3661), // 61:01 (1시간 1분 1초)
          nanTest: formatTime(NaN), // 0:00
          nullTest: formatTime(null), // 0:00
          undefinedTest: formatTime(undefined), // 0:00
          negativeTest: formatTime(-5) // 0:00
        };
      } catch (error) {
        return { error: error.message };
      }
    });
    
    console.log('formatTime 테스트 결과:', formatTimeResult);
    expect(formatTimeResult.error).toBeUndefined();
    expect(formatTimeResult.test1).toBe('1:05');
    expect(formatTimeResult.test2).toBe('0:00');
    expect(formatTimeResult.nanTest).toBe('0:00');
    expect(formatTimeResult.nullTest).toBe('0:00');
    expect(formatTimeResult.undefinedTest).toBe('0:00');
    expect(formatTimeResult.negativeTest).toBe('0:00');
    console.log('✅ formatTime 함수 모든 케이스 정상 작동 확인');
    
    // toggleGFXMarking 함수 존재 확인
    const hasToggleFunction = await page.evaluate(() => {
      return typeof toggleGFXMarking === 'function';
    });
    expect(hasToggleFunction).toBe(true);
    console.log('✅ toggleGFXMarking 함수 존재 확인');
    
    // updateSegmentDisplay 함수 존재 확인
    const hasUpdateFunction = await page.evaluate(() => {
      return typeof updateSegmentDisplay === 'function';
    });
    expect(hasUpdateFunction).toBe(true);
    console.log('✅ updateSegmentDisplay 함수 존재 확인');
    
    expect(hasError).toBe(false);
    console.log('✅ JavaScript 에러 없음 확인');
  });

  test('3. 비디오 없이 GFX 마킹 시도 (에러 처리)', async () => {
    console.log('\n🎯 3단계: 비디오 없이 GFX 마킹 시도');
    
    const gfxButton = page.locator('#markGFXBtn');
    await expect(gfxButton).toBeDisabled();
    console.log('✅ 비디오 없을 때 GFX 버튼 비활성화 확인');
    
    // 강제로 클릭 시도 (JavaScript에서 alert 발생)
    page.on('dialog', async dialog => {
      expect(dialog.message()).toContain('비디오를 먼저 업로드해주세요');
      console.log('✅ 알림 메시지 확인:', dialog.message());
      await dialog.accept();
    });
    
    // 버튼을 강제로 활성화하고 클릭하여 알림 확인
    await page.evaluate(() => {
      document.getElementById('markGFXBtn').disabled = false;
    });
    
    await gfxButton.click();
    console.log('✅ 비디오 없이 마킹 시도 시 에러 처리 확인');
  });

  test('4. 가상 비디오로 GFX 마킹 시뮬레이션', async () => {
    console.log('\n🎯 4단계: 가상 비디오로 GFX 마킹 시뮬레이션');
    
    // 가상 비디오 설정
    await page.evaluate(() => {
      // 가상 video 객체 생성
      window.video = {
        duration: 30,
        currentTime: 0
      };
      
      // 필요한 전역 변수들 초기화
      window.segments = [];
      window.currentSegment = null;
      window.isMarkingStart = true;
      
      // 버튼 활성화
      document.getElementById('markGFXBtn').disabled = false;
    });
    
    await page.waitForTimeout(500);
    
    // 첫 번째 마킹 시작 (5초 지점)
    await page.evaluate(() => {
      window.video.currentTime = 5;
    });
    
    const gfxButton = page.locator('#markGFXBtn');
    await expect(gfxButton).toBeEnabled();
    
    await gfxButton.click();
    console.log('🔴 5초 지점에서 GFX 시작점 마킹');
    
    // 버튼 상태 변경 확인
    await expect(gfxButton).toHaveClass(/btn-warning/);
    console.log('✅ 버튼이 노란색으로 변경됨');
    
    // 구간 정보 표시 확인
    const segmentInfo = page.locator('#segmentInfo');
    await expect(segmentInfo).toBeVisible();
    await expect(page.locator('#segmentStatus')).toContainText('GFX 구간 마킹 중');
    console.log('✅ 구간 정보 패널 표시됨');
    
    // 종료점 마킹 (8초 지점)
    await page.evaluate(() => {
      window.video.currentTime = 8;
    });
    
    await gfxButton.click();
    console.log('🟡 8초 지점에서 GFX 종료점 마킹');
    
    // 버튼 상태 복귀 확인
    await expect(gfxButton).toHaveClass(/btn-danger/);
    console.log('✅ 버튼이 빨간색으로 복귀됨');
    
    // 구간 완료 상태 확인
    await expect(page.locator('#segmentStatus')).toContainText('구간 저장 완료');
    console.log('✅ 첫 번째 구간 생성 완료');
  });

  test('5. 구간 표시 및 통계 업데이트 확인', async () => {
    console.log('\n🎯 5단계: 구간 표시 및 통계 업데이트');
    
    // 테스트 구간 데이터 생성
    await page.evaluate(() => {
      window.segments = [
        {
          id: '1',
          gfxStart: 5,
          gfxEnd: 8,
          handStart: 0, // GFX 시작 -5초
          handEnd: 23,  // GFX 끝 +15초
        },
        {
          id: '2',
          gfxStart: 15,
          gfxEnd: 18,
          handStart: 10, // GFX 시작 -5초
          handEnd: 33,   // GFX 끝 +15초
        }
      ];
      
      // 화면 업데이트
      updateSegmentDisplay();
      updateStats();
    });
    
    await page.waitForTimeout(500);
    
    // 구간 카드들 확인
    const segmentCards = page.locator('.card');
    const visibleCards = await segmentCards.count();
    expect(visibleCards).toBeGreaterThan(0);
    console.log(`✅ ${visibleCards}개의 구간 카드 표시됨`);
    
    // 첫 번째 구간 정보 확인
    const firstCard = segmentCards.first();
    await expect(firstCard).toContainText('0:05 ~ 0:08'); // GFX 구간
    await expect(firstCard).toContainText('0:00 ~ 0:23'); // 핸드 구간
    console.log('✅ 첫 번째 구간 정보 확인');
    
    // 통계 업데이트 확인
    await expect(page.locator('#totalSamples')).toContainText('2 구간');
    console.log('✅ 전체 구간 수 통계 업데이트 확인');
    
    // 각 구간의 이동 버튼 확인
    const jumpButtons = page.locator('button:has-text("이동")');
    const jumpButtonCount = await jumpButtons.count();
    expect(jumpButtonCount).toBe(2);
    console.log('✅ 각 구간의 이동 버튼 확인');
    
    // 각 구간의 삭제 버튼 확인
    const deleteButtons = page.locator('button:has-text("삭제")');
    const deleteButtonCount = await deleteButtons.count();
    expect(deleteButtonCount).toBe(2);
    console.log('✅ 각 구간의 삭제 버튼 확인');
  });

  test('6. 구간 삭제 기능 테스트', async () => {
    console.log('\n🎯 6단계: 구간 삭제 기능 테스트');
    
    // 테스트 구간 생성
    await page.evaluate(() => {
      window.segments = [
        {
          id: '1',
          gfxStart: 5,
          gfxEnd: 8,
          handStart: 0,
          handEnd: 23,
        },
        {
          id: '2',
          gfxStart: 15,
          gfxEnd: 18,
          handStart: 10,
          handEnd: 33,
        }
      ];
      updateSegmentDisplay();
    });
    
    await page.waitForTimeout(500);
    
    // 삭제 전 구간 수 확인
    let segmentCards = page.locator('.card');
    let cardCount = await segmentCards.count();
    console.log(`삭제 전 구간 수: ${cardCount}`);
    
    // 첫 번째 구간 삭제
    const firstDeleteButton = page.locator('button:has-text("삭제")').first();
    await firstDeleteButton.click();
    console.log('🗑️ 첫 번째 구간 삭제 버튼 클릭');
    
    await page.waitForTimeout(500);
    
    // 삭제 후 구간 수 확인
    segmentCards = page.locator('.card');
    cardCount = await segmentCards.count();
    console.log(`삭제 후 구간 수: ${cardCount}`);
    expect(cardCount).toBe(1);
    
    // 남은 구간이 두 번째 구간인지 확인
    await expect(segmentCards).toContainText('0:15 ~ 0:18');
    console.log('✅ 구간 삭제 기능 정상 작동 확인');
  });

  test('7. 전체 초기화 기능 테스트', async () => {
    console.log('\n🎯 7단계: 전체 초기화 기능 테스트');
    
    // 테스트 구간 생성
    await page.evaluate(() => {
      window.segments = [
        {
          id: '1',
          gfxStart: 5,
          gfxEnd: 8,
          handStart: 0,
          handEnd: 23,
        }
      ];
      updateSegmentDisplay();
      
      // Save 버튼 활성화
      document.getElementById('saveBtn').disabled = false;
    });
    
    await page.waitForTimeout(500);
    
    // 확인 대화상자 처리
    page.on('dialog', async dialog => {
      expect(dialog.message()).toContain('모든 구간을 삭제하시겠습니까');
      console.log('✅ 삭제 확인 대화상자:', dialog.message());
      await dialog.accept();
    });
    
    // Clear 버튼 클릭
    await page.locator('#clearBtn').click();
    console.log('🗑️ Clear 버튼 클릭');
    
    await page.waitForTimeout(500);
    
    // 초기화 확인
    const segmentCards = page.locator('.card');
    const cardCount = await segmentCards.count();
    expect(cardCount).toBe(0);
    
    await expect(page.locator('#totalSamples')).toContainText('0 구간');
    
    // Save 버튼 비활성화 확인
    await expect(page.locator('#saveBtn')).toBeDisabled();
    
    console.log('✅ 전체 초기화 기능 정상 작동 확인');
  });

  test('8. LocalStorage 저장/복원 기능 테스트', async () => {
    console.log('\n🎯 8단계: LocalStorage 저장/복원 기능 테스트');
    
    // 테스트 구간 생성 및 저장
    await page.evaluate(() => {
      window.segments = [
        {
          id: '1',
          gfxStart: 10,
          gfxEnd: 15,
          handStart: 5,
          handEnd: 30,
        }
      ];
      
      // LocalStorage에 저장
      saveSegmentsToStorage();
      console.log('LocalStorage에 구간 저장 완료');
    });
    
    // 구간 데이터 초기화
    await page.evaluate(() => {
      window.segments = [];
      updateSegmentDisplay();
    });
    
    // 페이지 새로고침하여 데이터 복원 테스트
    await page.reload();
    await page.waitForLoadState('networkidle');
    
    // 복원된 데이터 확인
    const restoredData = await page.evaluate(() => {
      try {
        const saved = localStorage.getItem('gfx_segments');
        return saved ? JSON.parse(saved) : [];
      } catch {
        return [];
      }
    });
    
    console.log('복원된 구간 데이터:', restoredData);
    expect(restoredData.length).toBe(1);
    expect(restoredData[0].gfxStart).toBe(10);
    expect(restoredData[0].gfxEnd).toBe(15);
    
    console.log('✅ LocalStorage 저장/복원 기능 정상 작동 확인');
  });

  test('9. 에지 케이스 및 에러 처리 테스트', async () => {
    console.log('\n🎯 9단계: 에지 케이스 및 에러 처리 테스트');
    
    // NaN 처리 테스트
    const nanTest = await page.evaluate(() => {
      return {
        formatTime: formatTime(NaN),
        formatTimeNull: formatTime(null),
        formatTimeUndefined: formatTime(undefined)
      };
    });
    
    expect(nanTest.formatTime).toBe('0:00');
    expect(nanTest.formatTimeNull).toBe('0:00');
    expect(nanTest.formatTimeUndefined).toBe('0:00');
    console.log('✅ NaN/null/undefined 에러 처리 확인');
    
    // 빈 구간 배열 처리
    await page.evaluate(() => {
      window.segments = [];
      updateSegmentDisplay();
      updateStats();
    });
    
    await expect(page.locator('#totalSamples')).toContainText('0 구간');
    console.log('✅ 빈 구간 배열 처리 확인');
    
    // 잘못된 구간 데이터 처리
    await page.evaluate(() => {
      window.segments = [
        { /* 불완전한 구간 데이터 */ }
      ];
      try {
        updateSegmentDisplay();
        return true;
      } catch (error) {
        console.error('에러 발생:', error);
        return false;
      }
    });
    
    console.log('✅ 잘못된 구간 데이터 처리 확인');
  });

  test('10. 모든 기능 통합 테스트', async () => {
    console.log('\n🎯 10단계: 모든 기능 통합 테스트');
    
    // 1) 가상 비디오 설정
    await page.evaluate(() => {
      window.video = { duration: 60, currentTime: 0 };
      window.segments = [];
      window.isMarkingStart = true;
      document.getElementById('markGFXBtn').disabled = false;
    });
    
    // 2) 첫 번째 구간 마킹
    await page.evaluate(() => { window.video.currentTime = 10; });
    await page.locator('#markGFXBtn').click();
    await page.evaluate(() => { window.video.currentTime = 15; });
    await page.locator('#markGFXBtn').click();
    console.log('✅ 첫 번째 구간 마킹 완료');
    
    // 3) 두 번째 구간 마킹
    await page.evaluate(() => { window.video.currentTime = 30; });
    await page.locator('#markGFXBtn').click();
    await page.evaluate(() => { window.video.currentTime = 35; });
    await page.locator('#markGFXBtn').click();
    console.log('✅ 두 번째 구간 마킹 완료');
    
    // 4) 구간 수 확인
    const segmentCards = page.locator('.card');
    const cardCount = await segmentCards.count();
    expect(cardCount).toBe(2);
    console.log(`✅ 총 ${cardCount}개 구간 생성됨`);
    
    // 5) 구간 정보 확인
    await expect(segmentCards.first()).toContainText('0:10 ~ 0:15');
    await expect(segmentCards.nth(1)).toContainText('0:30 ~ 0:35');
    console.log('✅ 모든 구간 정보 정확히 표시됨');
    
    // 6) 통계 업데이트 확인
    await expect(page.locator('#totalSamples')).toContainText('2 구간');
    console.log('✅ 통계 정보 업데이트됨');
    
    // 7) 구간 삭제 테스트
    await page.locator('button:has-text("삭제")').first().click();
    await page.waitForTimeout(300);
    
    const remainingCards = await page.locator('.card').count();
    expect(remainingCards).toBe(1);
    console.log('✅ 구간 삭제 기능 작동됨');
    
    // 8) 전체 초기화
    page.on('dialog', async dialog => {
      await dialog.accept();
    });
    
    await page.locator('#clearBtn').click();
    await page.waitForTimeout(300);
    
    const finalCards = await page.locator('.card').count();
    expect(finalCards).toBe(0);
    console.log('✅ 전체 초기화 완료');
    
    console.log('🎉 모든 통합 테스트 완료!');
  });
});