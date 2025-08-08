// 포커 트렌드 분석 플랫폼 E2E 테스트 - 전역 설정
const { expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

async function globalSetup(config) {
  console.log('🚀 포커 트렌드 분석 플랫폼 E2E 테스트 시작');
  
  // 테스트 결과 디렉토리 생성
  const resultsDir = path.join(__dirname, '..', 'test-results');
  if (!fs.existsSync(resultsDir)) {
    fs.mkdirSync(resultsDir, { recursive: true });
  }

  // 테스트 시작 시간 기록
  const startTime = new Date().toISOString();
  const testSession = {
    startTime,
    sessionId: `poker-e2e-${Date.now()}`,
    environment: {
      nodeVersion: process.version,
      platform: process.platform,
      arch: process.arch,
    }
  };

  // 세션 정보 저장
  fs.writeFileSync(
    path.join(resultsDir, 'test-session.json'),
    JSON.stringify(testSession, null, 2)
  );

  console.log(`📊 테스트 세션 ID: ${testSession.sessionId}`);
  console.log(`⏰ 테스트 시작 시간: ${startTime}`);

  // 필수 환경변수 검증
  const requiredEnvVars = [
    'GEMINI_API_KEY',
    'YOUTUBE_API_KEY', 
    'SLACK_WEBHOOK_URL'
  ];

  const missingEnvVars = requiredEnvVars.filter(envVar => !process.env[envVar]);
  
  if (missingEnvVars.length > 0) {
    console.warn(`⚠️  누락된 환경변수: ${missingEnvVars.join(', ')}`);
    console.warn('일부 테스트가 모킹될 수 있습니다.');
  } else {
    console.log('✅ 모든 필수 환경변수 확인');
  }

  // 시스템 상태 체크
  const systemCheck = {
    timestamp: new Date().toISOString(),
    pythonAvailable: await checkPythonAvailability(),
    nodeModules: fs.existsSync(path.join(__dirname, '..', 'node_modules')),
    testScripts: await checkTestScripts(),
  };

  console.log('🔍 시스템 상태 체크:');
  console.log(`   Python 사용 가능: ${systemCheck.pythonAvailable ? '✅' : '❌'}`);
  console.log(`   Node Modules: ${systemCheck.nodeModules ? '✅' : '❌'}`);
  console.log(`   테스트 스크립트: ${systemCheck.testScripts ? '✅' : '❌'}`);

  // 시스템 체크 결과 저장
  fs.writeFileSync(
    path.join(resultsDir, 'system-check.json'),
    JSON.stringify(systemCheck, null, 2)
  );

  return testSession;
}

async function checkPythonAvailability() {
  const { spawn } = require('child_process');
  
  return new Promise((resolve) => {
    const python = spawn('python', ['--version']);
    python.on('error', () => resolve(false));
    python.on('close', (code) => resolve(code === 0));
  });
}

async function checkTestScripts() {
  const scriptsDir = path.join(__dirname, '..', 'scripts');
  const requiredScripts = [
    'schedule_validator.py',
    'test_scheduling.bat',
    'test_scheduling.sh'
  ];

  return requiredScripts.every(script => 
    fs.existsSync(path.join(scriptsDir, script))
  );
}

module.exports = globalSetup;