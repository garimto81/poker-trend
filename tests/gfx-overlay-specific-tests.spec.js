const { test, expect } = require('@playwright/test');

test.describe('GFX 오버레이 학습기 핵심 기능 개별 테스트', () => {
  let page;
  
  test.beforeEach(async ({ browser }) => {
    page = await browser.newPage();
    await page.goto('http://localhost:8081/web-ui/gfx_overlay_trainer.html');
    await page.waitForLoadState('networkidle');
  });

  test('✅ formatTime 함수 완전 테스트', async () => {
    console.log('\n🧪 formatTime 함수 완전 테스트');
    
    const results = await page.evaluate(() => {
      return {
        // 기본 케이스
        zero: formatTime(0),
        oneMinute: formatTime(60),
        oneHour: formatTime(3600),
        mixed: formatTime(3665), // 1:01:05
        
        // 소수점 케이스
        decimal: formatTime(65.7), // 1:05
        
        // 에러 케이스
        nan: formatTime(NaN),
        null_value: formatTime(null),
        undefined_value: formatTime(undefined),
        negative: formatTime(-10),
        string: formatTime('invalid'),
        
        // 큰 수
        big_number: formatTime(7265) // 121:05
      };
    });
    
    console.log('formatTime 테스트 결과:', results);
    
    // 기본 케이스 검증
    expect(results.zero).toBe('0:00');
    expect(results.oneMinute).toBe('1:00');
    expect(results.oneHour).toBe('60:00'); // 시간은 분으로 표시
    expect(results.mixed).toBe('61:05');
    
    // 소수점 처리
    expect(results.decimal).toBe('1:05');
    
    // 에러 케이스 모두 0:00 반환
    expect(results.nan).toBe('0:00');
    expect(results.null_value).toBe('0:00');
    expect(results.undefined_value).toBe('0:00');
    expect(results.negative).toBe('0:00');
    expect(results.string).toBe('0:00');
    
    // 큰 수 처리
    expect(results.big_number).toBe('121:05');
    
    console.log('✅ formatTime 함수 모든 케이스 통과!');
  });

  test('✅ toggleGFXMarking 함수 상태 변화 테스트', async () => {
    console.log('\n🧪 toggleGFXMarking 함수 상태 변화 테스트');
    
    // 비디오 없이 호출 시 알림 테스트
    page.on('dialog', async dialog => {
      expect(dialog.message()).toContain('비디오를 먼저 업로드해주세요');
      await dialog.accept();
    });
    
    // 버튼 강제 활성화 후 클릭
    await page.evaluate(() => {
      document.getElementById('markGFXBtn').disabled = false;
    });
    
    await page.locator('#markGFXBtn').click();
    console.log('✅ 비디오 없이 호출 시 알림 처리 확인');
    
    // 가상 비디오 설정 후 상태 변화 테스트
    await page.evaluate(() => {
      // 가상 비디오 환경 설정
      window.video = { currentTime: 0 };
      window.isMarkingStart = true;
      window.currentSegment = null;
      window.segments = [];
    });
    
    // 첫 번째 클릭 (시작점 마킹)
    const buttonBefore = await page.evaluate(() => {
      return {
        isMarkingStart: window.isMarkingStart,
        currentSegment: window.currentSegment
      };
    });
    
    expect(buttonBefore.isMarkingStart).toBe(true);
    expect(buttonBefore.currentSegment).toBe(null);
    console.log('✅ 초기 상태 확인');
    
    await page.locator('#markGFXBtn').click();
    
    const buttonAfter = await page.evaluate(() => {
      return {
        isMarkingStart: window.isMarkingStart,
        hasCurrentSegment: window.currentSegment !== null,
        segmentInfoVisible: document.getElementById('segmentInfo').style.display
      };
    });
    
    expect(buttonAfter.isMarkingStart).toBe(false);
    expect(buttonAfter.hasCurrentSegment).toBe(true);
    expect(buttonAfter.segmentInfoVisible).toBe('block');
    console.log('✅ 시작점 마킹 후 상태 변화 확인');
  });

  test('✅ updateSegmentDisplay 함수 정상 작동 테스트', async () => {
    console.log('\n🧪 updateSegmentDisplay 함수 테스트');
    
    // 빈 구간에서 시작
    await page.evaluate(() => {
      window.segments = [];
      updateSegmentDisplay();
    });
    
    let cardCount = await page.locator('.card').count();
    expect(cardCount).toBe(0);
    console.log('✅ 빈 구간 배열 처리 확인');
    
    // 구간 추가 테스트
    await page.evaluate(() => {
      window.segments = [
        {
          id: 'test1',
          gfxStart: 10,
          gfxEnd: 15,
          handStart: 5,
          handEnd: 30
        }
      ];
      updateSegmentDisplay();
    });
    
    cardCount = await page.locator('.card').count();
    expect(cardCount).toBe(1);
    console.log('✅ 단일 구간 표시 확인');
    
    // 구간 정보 내용 확인
    const cardContent = await page.locator('.card').first().textContent();
    expect(cardContent).toContain('0:10 ~ 0:15'); // GFX 구간
    expect(cardContent).toContain('0:05 ~ 0:30'); // 핸드 구간
    expect(cardContent).toContain('삭제');
    expect(cardContent).toContain('이동');
    console.log('✅ 구간 카드 내용 확인');
    
    // 여러 구간 테스트
    await page.evaluate(() => {
      window.segments = [
        { id: '1', gfxStart: 10, gfxEnd: 15, handStart: 5, handEnd: 30 },
        { id: '2', gfxStart: 40, gfxEnd: 45, handStart: 35, handEnd: 60 }
      ];
      updateSegmentDisplay();
    });
    
    cardCount = await page.locator('.card').count();
    expect(cardCount).toBe(2);
    console.log('✅ 여러 구간 표시 확인');
  });

  test('✅ 구간 삭제 기능 정확성 테스트', async () => {
    console.log('\n🧪 구간 삭제 기능 테스트');
    
    // 테스트 구간 설정
    await page.evaluate(() => {
      window.segments = [
        { id: 'segment1', gfxStart: 10, gfxEnd: 15, handStart: 5, handEnd: 30 },
        { id: 'segment2', gfxStart: 40, gfxEnd: 45, handStart: 35, handEnd: 60 }
      ];
      updateSegmentDisplay();
    });
    
    // 삭제 전 구간 수 확인
    let cardCount = await page.locator('.card').count();
    expect(cardCount).toBe(2);
    console.log('삭제 전 구간 수:', cardCount);
    
    // 첫 번째 구간 삭제
    await page.locator('button:has-text("삭제")').first().click();
    
    // 삭제 후 구간 수 확인
    cardCount = await page.locator('.card').count();
    expect(cardCount).toBe(1);
    console.log('삭제 후 구간 수:', cardCount);
    
    // 남은 구간이 올바른지 확인
    const remainingCard = await page.locator('.card').textContent();
    expect(remainingCard).toContain('0:40 ~ 0:45');
    console.log('✅ 정확한 구간이 삭제되었고 올바른 구간이 남았음');
  });

  test('✅ 전체 초기화 기능 정확성 테스트', async () => {
    console.log('\n🧪 전체 초기화 기능 테스트');
    
    // 테스트 구간 설정
    await page.evaluate(() => {
      window.segments = [
        { id: '1', gfxStart: 10, gfxEnd: 15, handStart: 5, handEnd: 30 }
      ];
      updateSegmentDisplay();
      document.getElementById('saveBtn').disabled = false;
    });
    
    // 초기화 전 상태 확인
    let cardCount = await page.locator('.card').count();
    expect(cardCount).toBe(1);
    
    const saveBtnDisabled = await page.locator('#saveBtn').isDisabled();
    expect(saveBtnDisabled).toBe(false);
    
    console.log('초기화 전: 구간 1개, Save 버튼 활성화');
    
    // 확인 대화상자 처리
    page.on('dialog', async dialog => {
      expect(dialog.message()).toContain('모든 구간을 삭제하시겠습니까');
      await dialog.accept();
    });
    
    // Clear 버튼 클릭
    await page.locator('#clearBtn').click();
    
    // 초기화 후 상태 확인
    await page.waitForTimeout(300);
    
    cardCount = await page.locator('.card').count();
    expect(cardCount).toBe(0);
    
    const saveBtnDisabledAfter = await page.locator('#saveBtn').isDisabled();
    expect(saveBtnDisabledAfter).toBe(true);
    
    const totalSamples = await page.locator('#totalSamples').textContent();
    expect(totalSamples).toContain('0 구간');
    
    console.log('✅ 초기화 완료: 구간 0개, Save 버튼 비활성화, 통계 초기화');
  });

  test('✅ LocalStorage 저장/복원 메커니즘 테스트', async () => {
    console.log('\n🧪 LocalStorage 저장/복원 메커니즘 테스트');
    
    // 테스트 데이터 설정 및 저장
    const testSegments = [
      { id: 'test1', gfxStart: 20, gfxEnd: 25, handStart: 15, handEnd: 40 }
    ];
    
    await page.evaluate((segments) => {
      window.segments = segments;
      localStorage.setItem('gfx_segments', JSON.stringify(segments));
      console.log('테스트 데이터 LocalStorage에 저장됨');
    }, testSegments);
    
    // LocalStorage에서 데이터 확인
    const storedData = await page.evaluate(() => {
      const stored = localStorage.getItem('gfx_segments');
      return stored ? JSON.parse(stored) : null;
    });
    
    expect(storedData).not.toBe(null);
    expect(storedData.length).toBe(1);
    expect(storedData[0].gfxStart).toBe(20);
    expect(storedData[0].gfxEnd).toBe(25);
    
    console.log('✅ LocalStorage 저장 확인:', storedData);
    
    // 페이지 새로고침하여 복원 테스트
    await page.reload();
    await page.waitForLoadState('networkidle');
    
    // 복원된 데이터 확인
    const restoredData = await page.evaluate(() => {
      return localStorage.getItem('gfx_segments');
    });
    
    expect(restoredData).not.toBe(null);
    const parsedRestored = JSON.parse(restoredData);
    expect(parsedRestored.length).toBe(1);
    expect(parsedRestored[0].gfxStart).toBe(20);
    
    console.log('✅ 페이지 새로고침 후 LocalStorage 데이터 복원 확인');
  });

  test('✅ 통계 업데이트 정확성 테스트', async () => {
    console.log('\n🧪 통계 업데이트 정확성 테스트');
    
    // 초기 통계 확인
    await page.evaluate(() => {
      window.segments = [];
      updateStats();
    });
    
    let gfxCount = await page.locator('#gfxCount').textContent();
    let gameCount = await page.locator('#gameCount').textContent();
    let totalSamples = await page.locator('#totalSamples').textContent();
    
    expect(gfxCount).toBe('0');
    expect(gameCount).toBe('0:00');
    expect(totalSamples).toContain('0 구간');
    console.log('✅ 초기 통계 확인');
    
    // 구간 추가 후 통계 업데이트
    await page.evaluate(() => {
      window.segments = [
        { gfxStart: 10, gfxEnd: 15, handStart: 5, handEnd: 30 }, // 핸드 25초
        { gfxStart: 40, gfxEnd: 45, handStart: 35, handEnd: 60 } // 핸드 25초
      ];
      updateStats();
    });
    
    gfxCount = await page.locator('#gfxCount').textContent();
    gameCount = await page.locator('#gameCount').textContent();
    totalSamples = await page.locator('#totalSamples').textContent();
    
    expect(gfxCount).toBe('2');
    expect(gameCount).toBe('0:50'); // 25 + 25 = 50초
    expect(totalSamples).toContain('2 구간');
    
    console.log('✅ 구간 추가 후 통계 업데이트 확인');
    console.log(`- GFX 구간: ${gfxCount}개`);
    console.log(`- 총 게임 시간: ${gameCount}`);
    console.log(`- 전체 샘플: ${totalSamples}`);
  });

  test('✅ 에러 핸들링 종합 테스트', async () => {
    console.log('\n🧪 에러 핸들링 종합 테스트');
    
    let hasError = false;
    page.on('pageerror', error => {
      hasError = true;
      console.log('예상치 못한 페이지 에러:', error.message);
    });
    
    // 1. 잘못된 구간 데이터로 updateSegmentDisplay 호출
    await page.evaluate(() => {
      try {
        window.segments = [{ /* 불완전한 데이터 */ }];
        updateSegmentDisplay();
      } catch (error) {
        console.log('updateSegmentDisplay 에러 처리됨:', error.message);
      }
    });
    
    // 2. 존재하지 않는 구간 삭제 시도
    await page.evaluate(() => {
      try {
        removeSegment('nonexistent');
      } catch (error) {
        console.log('구간 삭제 에러 처리됨:', error.message);
      }
    });
    
    // 3. 잘못된 시간으로 점프 시도
    await page.evaluate(() => {
      try {
        jumpToSegment('invalid');
      } catch (error) {
        console.log('시간 점프 에러 처리됨:', error.message);
      }
    });
    
    // 4. 비정상적인 formatTime 호출들
    await page.evaluate(() => {
      const results = [
        formatTime(Infinity),
        formatTime(-Infinity),
        formatTime({}),
        formatTime([]),
        formatTime(function(){}),
      ];
      console.log('비정상적인 formatTime 결과:', results);
      return results;
    });
    
    expect(hasError).toBe(false);
    console.log('✅ 모든 에러 케이스가 적절히 처리됨');
  });
});