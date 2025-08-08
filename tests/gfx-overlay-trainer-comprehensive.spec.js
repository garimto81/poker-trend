const { test, expect } = require('@playwright/test');
const path = require('path');

test.describe('GFX 오버레이 학습기 포괄적 테스트', () => {
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
    
    // 페이지 로드 (올바른 경로로 수정)
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
    await expect(gfxButton).toHaveText('GFX 시작점 마킹');
    await expect(gfxButton).toHaveClass(/btn-danger/);
    await expect(gfxButton).toBeDisabled();
    console.log('✅ GFX 버튼 초기 상태 (비활성화, 빨간색) 확인됨');
    
    // 초기 통계 확인
    await expect(page.locator('#gfxCount')).toHaveText('0');
    await expect(page.locator('#gameCount')).toHaveText('0:00');
    await expect(page.locator('#totalSamples')).toContainText('0 구간');
    console.log('✅ 초기 통계 (GFX 0개, 게임 시간 0:00, 0 구간) 확인됨');
  });

  test('2. JavaScript 콘솔 에러 확인', async () => {
    console.log('\n🎯 2단계: JavaScript 콘솔 에러 확인');
    
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
          test3: formatTime(3661) // 1:01:01
        };
      } catch (error) {
        return { error: error.message };
      }
    });
    
    console.log('formatTime 테스트 결과:', formatTimeResult);
    expect(formatTimeResult.error).toBeUndefined();
    expect(formatTimeResult.test1).toBe('1:05');
    expect(formatTimeResult.test2).toBe('0:00');
    console.log('✅ formatTime 함수 정상 작동 확인');
    
    expect(hasError).toBe(false);
    console.log('✅ JavaScript 에러 없음 확인');
  });

  test('3. 테스트 비디오 업로드 및 기본 기능', async () => {
    console.log('\n🎯 3단계: 테스트 비디오 업로드');
    
    // 테스트용 더미 비디오 파일 생성 (실제로는 작은 MP4 파일이 필요)
    // 여기서는 파일 선택 인터페이스만 테스트
    const fileInput = page.locator('#fileInput');
    
    // 파일 입력 요소에 change 이벤트 시뮬레이션
    await page.evaluate(() => {
      const video = document.getElementById('videoPlayer');
      const gfxButton = document.getElementById('gfxButton');
      
      // 비디오가 로드된 것처럼 시뮬레이션
      video.duration = 30; // 30초 비디오
      video.currentTime = 0;
      
      // 비디오 로드 이벤트 발생
      const event = new Event('loadedmetadata');
      video.dispatchEvent(event);
      
      return { duration: video.duration };
    });
    
    console.log('✅ 테스트 비디오 메타데이터 로드 시뮬레이션 완료');
    
    // 버튼 활성화 확인
    await expect(page.locator('#gfxButton')).toBeEnabled();
    console.log('✅ 비디오 로드 후 GFX 버튼 활성화 확인');
  });

  test('4. GFX 마킹 첫 번째 시나리오 (5초-8초)', async () => {
    console.log('\n🎯 4단계: 첫 번째 GFX 마킹 시나리오');
    
    // 비디오 로드 시뮬레이션
    await page.evaluate(() => {
      const video = document.getElementById('videoPlayer');
      video.duration = 30;
      video.currentTime = 0;
      const event = new Event('loadedmetadata');
      video.dispatchEvent(event);
    });
    
    await page.waitForTimeout(500);
    
    // 5초 지점으로 이동
    await page.evaluate(() => {
      document.getElementById('videoPlayer').currentTime = 5;
    });
    console.log('📍 비디오 시간을 5초로 설정');
    
    // 시작점 마킹
    const gfxButton = page.locator('#gfxButton');
    await expect(gfxButton).toHaveText('GFX 시작점 마킹');
    await expect(gfxButton).toHaveClass(/btn-danger/);
    
    await gfxButton.click();
    console.log('🔴 GFX 시작점 마킹 클릭');
    
    // 버튼 상태 변경 확인 (빨간색 → 노란색)
    await expect(gfxButton).toHaveText('GFX 종료점 마킹');
    await expect(gfxButton).toHaveClass(/btn-warning/);
    console.log('✅ 버튼이 노란색으로 변경됨 (종료점 마킹 모드)');
    
    // 8초 지점으로 이동
    await page.evaluate(() => {
      document.getElementById('videoPlayer').currentTime = 8;
    });
    console.log('📍 비디오 시간을 8초로 설정');
    
    // 종료점 마킹
    await gfxButton.click();
    console.log('🟡 GFX 종료점 마킹 클릭');
    
    // 버튼 상태 복귀 확인 (노란색 → 빨간색)
    await expect(gfxButton).toHaveText('GFX 시작점 마킹');
    await expect(gfxButton).toHaveClass(/btn-danger/);
    console.log('✅ 버튼이 빨간색으로 복귀됨');
    
    // 구간 정보 표시 확인
    const segmentInfo = await page.locator('#segmentInfo').textContent();
    console.log('📊 구간 정보:', segmentInfo);
    expect(segmentInfo).toContain('0:05~0:08');
    expect(segmentInfo).toContain('핸드 구간');
    
    // 통계 업데이트 확인
    await expect(page.locator('#segmentCount')).toHaveText('1');
    await expect(page.locator('#totalHandTime')).toHaveText('0:03');
    console.log('✅ 첫 번째 구간 저장 및 통계 업데이트 확인');
  });

  test('5. GFX 마킹 두 번째 시나리오 (15초-18초)', async () => {
    console.log('\n🎯 5단계: 두 번째 GFX 마킹 시나리오');
    
    // 비디오 로드 및 첫 번째 구간 생성
    await page.evaluate(() => {
      const video = document.getElementById('videoPlayer');
      video.duration = 30;
      video.currentTime = 0;
      const event = new Event('loadedmetadata');
      video.dispatchEvent(event);
      
      // 첫 번째 구간 추가
      window.gfxSegments = [{
        start: 5,
        end: 8,
        duration: 3
      }];
      updateSegmentDisplay();
    });
    
    await page.waitForTimeout(500);
    
    // 15초 지점으로 이동하여 두 번째 구간 시작
    await page.evaluate(() => {
      document.getElementById('videoPlayer').currentTime = 15;
    });
    console.log('📍 비디오 시간을 15초로 설정');
    
    const gfxButton = page.locator('#gfxButton');
    await gfxButton.click();
    console.log('🔴 두 번째 구간 시작점 마킹');
    
    // 18초 지점으로 이동
    await page.evaluate(() => {
      document.getElementById('videoPlayer').currentTime = 18;
    });
    console.log('📍 비디오 시간을 18초로 설정');
    
    await gfxButton.click();
    console.log('🟡 두 번째 구간 종료점 마킹');
    
    // 구간 정보에 두 구간이 모두 표시되는지 확인
    const segmentInfo = await page.locator('#segmentInfo').textContent();
    console.log('📊 업데이트된 구간 정보:', segmentInfo);
    expect(segmentInfo).toContain('0:05~0:08');
    expect(segmentInfo).toContain('0:15~0:18');
    
    // 통계 업데이트 확인 (2개 구간, 총 6초)
    await expect(page.locator('#segmentCount')).toHaveText('2');
    await expect(page.locator('#totalHandTime')).toHaveText('0:06');
    console.log('✅ 두 번째 구간 저장 및 통계 업데이트 확인');
  });

  test('6. 구간 목록 카드 표시 및 삭제 기능', async () => {
    console.log('\n🎯 6단계: 구간 목록 카드 및 삭제 기능');
    
    // 테스트 구간들 생성
    await page.evaluate(() => {
      const video = document.getElementById('videoPlayer');
      video.duration = 30;
      
      window.gfxSegments = [
        { start: 5, end: 8, duration: 3 },
        { start: 15, end: 18, duration: 3 }
      ];
      updateSegmentDisplay();
    });
    
    await page.waitForTimeout(500);
    
    // 구간 카드들이 표시되는지 확인
    const segmentCards = page.locator('.segment-card');
    await expect(segmentCards).toHaveCount(2);
    console.log('✅ 2개의 구간 카드가 표시됨');
    
    // 첫 번째 구간 카드의 내용 확인
    const firstCard = segmentCards.first();
    await expect(firstCard).toContainText('핸드 #1');
    await expect(firstCard).toContainText('0:05 ~ 0:08');
    await expect(firstCard).toContainText('지속시간: 0:03');
    console.log('✅ 첫 번째 구간 카드 내용 확인');
    
    // 두 번째 구간 카드의 내용 확인
    const secondCard = segmentCards.nth(1);
    await expect(secondCard).toContainText('핸드 #2');
    await expect(secondCard).toContainText('0:15 ~ 0:18');
    await expect(secondCard).toContainText('지속시간: 0:03');
    console.log('✅ 두 번째 구간 카드 내용 확인');
    
    // 첫 번째 구간 삭제 테스트
    const deleteButton = firstCard.locator('.btn-sm.btn-outline-danger');
    await expect(deleteButton).toBeVisible();
    await deleteButton.click();
    console.log('🗑️ 첫 번째 구간 삭제 버튼 클릭');
    
    // 구간 카드가 하나로 줄었는지 확인
    await expect(segmentCards).toHaveCount(1);
    await expect(page.locator('#segmentCount')).toHaveText('1');
    await expect(page.locator('#totalHandTime')).toHaveText('0:03');
    console.log('✅ 구간 삭제 후 카드 수와 통계 업데이트 확인');
  });

  test('7. JSON 내보내기 기능', async () => {
    console.log('\n🎯 7단계: JSON 내보내기 기능');
    
    // 테스트 구간들 생성
    await page.evaluate(() => {
      window.gfxSegments = [
        { start: 5, end: 8, duration: 3 },
        { start: 15, end: 18, duration: 3 }
      ];
      updateSegmentDisplay();
    });
    
    // 다운로드 이벤트 감지를 위한 설정
    const downloadPromise = page.waitForEvent('download');
    
    // Export 버튼 클릭
    await page.locator('#exportButton').click();
    console.log('📥 Export 버튼 클릭');
    
    const download = await downloadPromise;
    console.log('✅ 다운로드 이벤트 감지됨');
    
    // 다운로드된 파일 이름 확인
    expect(download.suggestedFilename()).toMatch(/gfx_segments_\d{8}_\d{6}\.json/);
    console.log('✅ 다운로드 파일명 형식 확인');
  });

  test('8. LocalStorage 저장/복원 기능', async () => {
    console.log('\n🎯 8단계: LocalStorage 저장/복원 기능');
    
    // 초기 구간 생성 및 저장
    await page.evaluate(() => {
      window.gfxSegments = [
        { start: 10, end: 15, duration: 5 },
        { start: 20, end: 25, duration: 5 }
      ];
      saveToLocalStorage();
    });
    
    console.log('💾 구간 데이터를 LocalStorage에 저장');
    
    // 페이지 새로고침 후 데이터 복원 확인
    await page.reload();
    await page.waitForLoadState('networkidle');
    
    // 비디오 로드 시뮬레이션 (복원을 위해 필요)
    await page.evaluate(() => {
      const video = document.getElementById('videoPlayer');
      video.duration = 30;
      const event = new Event('loadedmetadata');
      video.dispatchEvent(event);
    });
    
    await page.waitForTimeout(1000);
    
    // 복원된 데이터 확인
    const segmentCount = await page.locator('#segmentCount').textContent();
    const totalTime = await page.locator('#totalHandTime').textContent();
    const segmentInfo = await page.locator('#segmentInfo').textContent();
    
    console.log('📊 복원된 데이터:');
    console.log('- 구간 수:', segmentCount);
    console.log('- 총 시간:', totalTime);
    console.log('- 구간 정보:', segmentInfo);
    
    expect(segmentCount).toBe('2');
    expect(totalTime).toBe('0:10');
    expect(segmentInfo).toContain('0:10~0:15');
    expect(segmentInfo).toContain('0:20~0:25');
    
    console.log('✅ LocalStorage 데이터 복원 완료');
  });

  test('9. 전체 초기화 기능', async () => {
    console.log('\n🎯 9단계: 전체 초기화 기능');
    
    // 테스트 구간들 생성
    await page.evaluate(() => {
      window.gfxSegments = [
        { start: 5, end: 10, duration: 5 },
        { start: 15, end: 20, duration: 5 }
      ];
      updateSegmentDisplay();
    });
    
    // Clear 버튼 클릭
    await page.locator('#clearButton').click();
    console.log('🗑️ Clear 버튼 클릭');
    
    // 초기화 확인
    await expect(page.locator('#segmentCount')).toHaveText('0');
    await expect(page.locator('#totalHandTime')).toHaveText('0:00');
    
    const segmentInfo = await page.locator('#segmentInfo').textContent();
    expect(segmentInfo.trim()).toBe('구간이 없습니다.');
    
    // 구간 카드들이 모두 제거되었는지 확인
    await expect(page.locator('.segment-card')).toHaveCount(0);
    
    console.log('✅ 전체 데이터 초기화 완료');
  });

  test('10. 에지 케이스 및 에러 처리', async () => {
    console.log('\n🎯 10단계: 에지 케이스 및 에러 처리');
    
    // 비디오 없이 GFX 마킹 시도
    await page.evaluate(() => {
      const video = document.getElementById('videoPlayer');
      video.duration = NaN; // 잘못된 duration
    });
    
    const gfxButton = page.locator('#gfxButton');
    await expect(gfxButton).toBeDisabled();
    console.log('✅ 잘못된 비디오 상태에서 버튼 비활성화 확인');
    
    // 올바른 비디오 설정 후 시간 관련 에지 케이스
    await page.evaluate(() => {
      const video = document.getElementById('videoPlayer');
      video.duration = 30;
      video.currentTime = 0;
      const event = new Event('loadedmetadata');
      video.dispatchEvent(event);
    });
    
    await page.waitForTimeout(500);
    
    // 0초에서 시작점 마킹
    await page.evaluate(() => {
      document.getElementById('videoPlayer').currentTime = 0;
    });
    
    await gfxButton.click();
    console.log('🔴 0초에서 시작점 마킹');
    
    // 같은 시간에 종료점 마킹 시도
    await gfxButton.click();
    console.log('🟡 같은 시간(0초)에 종료점 마킹 시도');
    
    // 에러 처리 확인 (구간이 생성되지 않아야 함)
    await expect(page.locator('#segmentCount')).toHaveText('0');
    console.log('✅ 잘못된 구간(길이 0) 생성 방지 확인');
    
    // formatTime 함수의 NaN 처리 확인
    const formatResult = await page.evaluate(() => {
      try {
        return {
          nanTest: formatTime(NaN),
          undefinedTest: formatTime(undefined),
          negativeTest: formatTime(-5)
        };
      } catch (error) {
        return { error: error.message };
      }
    });
    
    console.log('formatTime 에지 케이스 결과:', formatResult);
    expect(formatResult.nanTest).toBe('0:00');
    expect(formatResult.undefinedTest).toBe('0:00');
    expect(formatResult.negativeTest).toBe('0:00');
    console.log('✅ formatTime 함수의 에러 처리 확인');
  });
});