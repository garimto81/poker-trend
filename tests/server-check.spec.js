const { test, expect } = require('@playwright/test');

test('서버 경로 확인', async ({ page }) => {
  // 다양한 경로로 GFX 오버레이 페이지 접근 시도
  const possiblePaths = [
    'http://localhost:8080/web-ui/gfx_overlay_trainer.html',
    'http://localhost:8080/archive-mam/web-ui/gfx_overlay_trainer.html',
    'http://localhost:8080/gfx_overlay_trainer.html',
    'http://localhost:8080/archive-mam/gfx_overlay_trainer.html'
  ];

  for (const url of possiblePaths) {
    console.log(`테스트 중: ${url}`);
    try {
      const response = await page.goto(url, { waitUntil: 'load', timeout: 5000 });
      if (response.status() === 200) {
        console.log(`성공: ${url}`);
        const title = await page.title();
        console.log(`페이지 제목: ${title}`);
        
        // 테스트 성공시 실제 URL 저장
        if (title.includes('GFX 오버레이')) {
          console.log(`올바른 경로 발견: ${url}`);
          return;
        }
      }
    } catch (error) {
      console.log(`실패: ${url} - ${error.message}`);
    }
  }
});