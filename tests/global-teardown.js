// 포커 트렌드 분석 플랫폼 E2E 테스트 - 전역 정리
const fs = require('fs');
const path = require('path');

async function globalTeardown() {
  console.log('🧹 테스트 환경 정리 시작...');
  
  const resultsDir = path.join(__dirname, '..', 'test-results');
  
  try {
    // 테스트 세션 정보 로드
    const sessionPath = path.join(resultsDir, 'test-session.json');
    if (fs.existsSync(sessionPath)) {
      const sessionData = JSON.parse(fs.readFileSync(sessionPath, 'utf8'));
      const startTime = new Date(sessionData.startTime);
      const endTime = new Date();
      const duration = Math.round((endTime - startTime) / 1000);
      
      // 테스트 완료 정보 업데이트
      const completionData = {
        ...sessionData,
        endTime: endTime.toISOString(),
        duration: `${duration}초`,
        completedAt: endTime.toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' }),
        status: 'completed'
      };
      
      fs.writeFileSync(sessionPath, JSON.stringify(completionData, null, 2));
      
      console.log(`⏱️ 전체 테스트 실행 시간: ${duration}초`);
      console.log(`🏁 테스트 완료 시간: ${completionData.completedAt}`);
    }

    // 테스트 결과 요약 생성
    await generateTestSummary(resultsDir);
    
    // 임시 파일 정리
    cleanupTempFiles(resultsDir);
    
    console.log('✅ 테스트 환경 정리 완료');
    console.log(`📄 상세 결과는 test-results/ 디렉토리를 확인하세요`);
    
  } catch (error) {
    console.error('❌ 테스트 환경 정리 중 오류:', error.message);
  }
}

async function generateTestSummary(resultsDir) {
  try {
    const summaryPath = path.join(resultsDir, 'test-summary.md');
    const timestamp = new Date().toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' });
    
    let summary = `# 포커 트렌드 분석 플랫폼 E2E 테스트 요약\n\n`;
    summary += `생성 시간: ${timestamp}\n\n`;
    
    // JSON 결과 파일이 있으면 파싱하여 요약
    const jsonResultPath = path.join(resultsDir, 'test-results.json');
    if (fs.existsSync(jsonResultPath)) {
      const results = JSON.parse(fs.readFileSync(jsonResultPath, 'utf8'));
      summary += `## 테스트 실행 결과\n\n`;
      summary += `- 총 테스트 수: ${results.suites?.reduce((sum, suite) => sum + (suite.tests?.length || 0), 0) || 0}\n`;
      summary += `- 성공한 테스트: ${results.stats?.passed || 0}\n`;
      summary += `- 실패한 테스트: ${results.stats?.failed || 0}\n`;
      summary += `- 건너뛴 테스트: ${results.stats?.skipped || 0}\n\n`;
    }
    
    summary += `## 테스트 파일 위치\n\n`;
    summary += `- HTML 리포트: [playwright-report/index.html](./playwright-report/index.html)\n`;
    summary += `- JUnit 결과: [junit.xml](./junit.xml)\n`;
    summary += `- 시스템 체크: [system-check.json](./system-check.json)\n`;
    summary += `- 세션 정보: [test-session.json](./test-session.json)\n\n`;
    
    summary += `---\n포커 트렌드 분석 플랫폼 © 2025\n`;
    
    fs.writeFileSync(summaryPath, summary);
    console.log('📋 테스트 요약 생성 완료');
  } catch (error) {
    console.warn('⚠️ 테스트 요약 생성 실패:', error.message);
  }
}

function cleanupTempFiles(resultsDir) {
  try {
    // .tmp 파일들 정리
    const files = fs.readdirSync(resultsDir);
    const tempFiles = files.filter(file => file.endsWith('.tmp'));
    
    tempFiles.forEach(file => {
      fs.unlinkSync(path.join(resultsDir, file));
    });
    
    if (tempFiles.length > 0) {
      console.log(`🗑️ ${tempFiles.length}개의 임시 파일 정리 완료`);
    }
  } catch (error) {
    console.warn('⚠️ 임시 파일 정리 실패:', error.message);
  }
}

module.exports = globalTeardown;