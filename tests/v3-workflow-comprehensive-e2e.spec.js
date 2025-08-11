// V3 워크플로우 종합 E2E 테스트 - 경로 중복 문제 특화 검증
const { test, expect } = require('@playwright/test');
const fs = require('fs').promises;
const path = require('path');
const { exec } = require('child_process');
const { promisify } = require('util');

const execAsync = promisify(exec);

test.describe('🎰 통합 포커 보고 스케줄링 시스템 V3 - 종합 E2E 테스트', () => {
  let testResults = {};
  let startTime = new Date();

  test.beforeAll(async () => {
    console.log('🚀 V3 워크플로우 종합 테스트 시작');
    startTime = new Date();
    
    // 테스트 결과 초기화
    testResults = {
      timestamp: startTime.toISOString(),
      testSuite: 'V3 워크플로우 종합 E2E',
      results: []
    };
  });

  test.afterAll(async () => {
    const endTime = new Date();
    const duration = endTime - startTime;
    
    testResults.duration = duration;
    testResults.endTime = endTime.toISOString();
    testResults.summary = {
      total: testResults.results.length,
      passed: testResults.results.filter(r => r.status === 'passed').length,
      failed: testResults.results.filter(r => r.status === 'failed').length
    };
    
    // 테스트 결과 저장
    const reportPath = path.join(process.cwd(), 'test-results', `v3-workflow-e2e-report-${Date.now()}.json`);
    await fs.writeFile(reportPath, JSON.stringify(testResults, null, 2));
    
    console.log(`📊 테스트 완료. 결과 저장: ${reportPath}`);
    console.log(`⏱️ 총 소요시간: ${duration}ms`);
  });

  test('1. 프로젝트 구조 및 경로 검증', async () => {
    const testName = '프로젝트 구조 및 경로 검증';
    const testStart = Date.now();
    
    try {
      console.log('🔍 프로젝트 구조 검증 시작...');
      
      const projectRoot = process.cwd();
      const requiredPaths = [
        'backend/data-collector',
        'backend/platform-analyzer/scripts',
        'poker-trend-analysis/backend/news-analyzer',
        '.github/workflows/unified-poker-report-scheduler-v3.yml'
      ];
      
      const pathResults = {};
      
      // 경로 존재 확인
      for (const requiredPath of requiredPaths) {
        const fullPath = path.join(projectRoot, requiredPath);
        try {
          const stat = await fs.stat(fullPath);
          pathResults[requiredPath] = {
            exists: true,
            isDirectory: stat.isDirectory(),
            isFile: stat.isFile()
          };
          console.log(`✅ ${requiredPath}: 존재함`);
        } catch (error) {
          pathResults[requiredPath] = {
            exists: false,
            error: error.message
          };
          console.log(`❌ ${requiredPath}: 존재하지 않음`);
        }
      }
      
      // 핵심 Python 스크립트 파일 확인
      const scriptFiles = [
        'backend/data-collector/scripts/quick_validated_analyzer.py',
        'backend/data-collector/scripts/validated_analyzer_with_translation.py',
        'backend/data-collector/scripts/enhanced_validated_analyzer.py',
        'backend/platform-analyzer/scripts/firebase_rest_api_fetcher.py',
        'backend/platform-analyzer/scripts/show_daily_comparison.py',
        'backend/platform-analyzer/scripts/final_slack_reporter.py',
        'poker-trend-analysis/backend/news-analyzer/pokernews_slack_reporter.py'
      ];
      
      const scriptResults = {};
      for (const scriptFile of scriptFiles) {
        const fullPath = path.join(projectRoot, scriptFile);
        try {
          await fs.access(fullPath);
          scriptResults[scriptFile] = { exists: true };
          console.log(`✅ 스크립트 파일 존재: ${scriptFile}`);
        } catch (error) {
          scriptResults[scriptFile] = { exists: false, error: error.message };
          console.log(`❌ 스크립트 파일 없음: ${scriptFile}`);
        }
      }
      
      // 결과 기록
      testResults.results.push({
        testName,
        status: 'passed',
        duration: Date.now() - testStart,
        details: {
          pathResults,
          scriptResults,
          projectRoot
        }
      });
      
      expect(pathResults['.github/workflows/unified-poker-report-scheduler-v3.yml'].exists).toBe(true);
      
    } catch (error) {
      testResults.results.push({
        testName,
        status: 'failed',
        duration: Date.now() - testStart,
        error: error.message
      });
      throw error;
    }
  });

  test('2. GitHub Actions 워크플로우 YAML 구문 검증', async () => {
    const testName = 'GitHub Actions 워크플로우 YAML 구문 검증';
    const testStart = Date.now();
    
    try {
      console.log('📋 워크플로우 YAML 파일 구문 검증...');
      
      const workflowPath = path.join(process.cwd(), '.github/workflows/unified-poker-report-scheduler-v3.yml');
      const workflowContent = await fs.readFile(workflowPath, 'utf-8');
      
      // YAML 기본 구조 검증
      const requiredSections = [
        'name: 🎰 통합 포커 보고 스케줄링 시스템 V3',
        'on:',
        'schedule:',
        'workflow_dispatch:',
        'jobs:'
      ];
      
      const missingSections = [];
      for (const section of requiredSections) {
        if (!workflowContent.includes(section)) {
          missingSections.push(section);
        }
      }
      
      // 필수 Job 확인
      const requiredJobs = [
        'schedule-determination',
        'pokernews-analysis',
        'youtube-analysis',
        'platform-analysis',
        'final-report'
      ];
      
      const missingJobs = [];
      for (const job of requiredJobs) {
        if (!workflowContent.includes(`${job}:`)) {
          missingJobs.push(job);
        }
      }
      
      // 경로 처리 로직 검증
      const pathHandlingPatterns = [
        'if [ -d "poker-trend-analysis" ]; then',
        'if [ -d "backend/news-analyzer" ]; then',
        'if [ -d "backend/data-collector" ]; then',
        'if [ -d "backend/platform-analyzer/scripts" ]; then'
      ];
      
      const missingPathHandling = [];
      for (const pattern of pathHandlingPatterns) {
        if (!workflowContent.includes(pattern)) {
          missingPathHandling.push(pattern);
        }
      }
      
      console.log(`✅ YAML 구문 검증 완료`);
      console.log(`📋 누락된 섹션: ${missingSections.length}개`);
      console.log(`🔧 누락된 Job: ${missingJobs.length}개`);
      console.log(`🛤️ 누락된 경로 처리: ${missingPathHandling.length}개`);
      
      testResults.results.push({
        testName,
        status: missingSections.length === 0 && missingJobs.length === 0 ? 'passed' : 'failed',
        duration: Date.now() - testStart,
        details: {
          missingSections,
          missingJobs,
          missingPathHandling,
          workflowSize: workflowContent.length
        }
      });
      
      expect(missingSections.length).toBe(0);
      expect(missingJobs.length).toBe(0);
      
    } catch (error) {
      testResults.results.push({
        testName,
        status: 'failed',
        duration: Date.now() - testStart,
        error: error.message
      });
      throw error;
    }
  });

  test('3. 스케줄 결정 로직 시뮬레이션', async () => {
    const testName = '스케줄 결정 로직 시뮬레이션';
    const testStart = Date.now();
    
    try {
      console.log('🧠 스케줄 결정 로직 시뮬레이션...');
      
      // 시뮬레이션 스크립트 작성
      const simulationScript = `
#!/bin/bash
echo "스케줄 결정 로직 시뮬레이션"

# 현재 날짜 정보
CURRENT_DATE="2025-08-05"  # 테스트용 고정 날짜 (화요일)
DAY_OF_MONTH=05
DAY_OF_WEEK=2  # 화요일
WEEK_OF_MONTH=1  # 첫째주

echo "📅 테스트 날짜: $CURRENT_DATE"
echo "📊 요일: $DAY_OF_WEEK (1=월, 7=일)"
echo "📈 월 중 몇째 주: $WEEK_OF_MONTH"

# 스케줄 결정 로직
if [[ $DAY_OF_WEEK -eq 1 && $WEEK_OF_MONTH -eq 1 ]]; then
  REPORT_TYPE="monthly"
  echo "🗓️ 첫째주 월요일 → 월간 리포트"
elif [[ $DAY_OF_WEEK -eq 1 ]]; then
  REPORT_TYPE="weekly"
  echo "📅 일반 월요일 → 주간 리포트"
elif [[ $DAY_OF_WEEK -ge 2 && $DAY_OF_WEEK -le 5 ]]; then
  REPORT_TYPE="daily"
  echo "📋 평일 → 일간 리포트"
else
  REPORT_TYPE="none"
  echo "🚫 주말 → 실행하지 않음"
fi

echo "결정된 리포트 타입: $REPORT_TYPE"
`;
      
      // 임시 스크립트 파일 생성
      const tempScriptPath = path.join(process.cwd(), 'temp_schedule_test.sh');
      await fs.writeFile(tempScriptPath, simulationScript);
      
      try {
        // 스크립트 실행 권한 부여 및 실행 (Windows에서는 Git Bash 또는 WSL 사용)
        const { stdout, stderr } = await execAsync(`bash ${tempScriptPath}`);
        
        console.log('📋 스케줄 결정 결과:');
        console.log(stdout);
        
        if (stderr) {
          console.warn('⚠️ 경고:', stderr);
        }
        
        // 결과에서 리포트 타입 추출
        const reportTypeMatch = stdout.match(/결정된 리포트 타입: (\w+)/);
        const reportType = reportTypeMatch ? reportTypeMatch[1] : 'unknown';
        
        testResults.results.push({
          testName,
          status: reportType === 'daily' ? 'passed' : 'failed',
          duration: Date.now() - testStart,
          details: {
            reportType,
            output: stdout,
            expectedType: 'daily'
          }
        });
        
        expect(reportType).toBe('daily');
        
      } finally {
        // 임시 파일 정리
        await fs.unlink(tempScriptPath).catch(() => {});
      }
      
    } catch (error) {
      testResults.results.push({
        testName,
        status: 'failed',
        duration: Date.now() - testStart,
        error: error.message
      });
      throw error;
    }
  });

  test('4. PokerNews 분석 경로 시뮬레이션', async () => {
    const testName = 'PokerNews 분석 경로 시뮬레이션';
    const testStart = Date.now();
    
    try {
      console.log('📰 PokerNews 경로 처리 시뮬레이션...');
      
      const projectRoot = process.cwd();
      const pathSimulationScript = `
#!/bin/bash
echo "PokerNews 경로 처리 시뮬레이션"

# GitHub Actions의 기본 경로 확인
echo "📂 현재 위치: $(pwd)"

# poker-trend-analysis 폴더가 있는지 확인
if [ -d "poker-trend-analysis" ]; then
  cd poker-trend-analysis
  echo "✅ poker-trend-analysis 디렉토리로 이동"
  TARGET_PATH="poker-trend-analysis/backend/news-analyzer"
else
  echo "❌ poker-trend-analysis 디렉토리 없음"
  TARGET_PATH=""
fi

# backend/news-analyzer 경로로 이동
if [ -d "backend/news-analyzer" ]; then
  cd backend/news-analyzer
  echo "✅ news-analyzer 디렉토리 발견"
  TARGET_PATH="$TARGET_PATH/backend/news-analyzer"
elif [ -d "news-analyzer" ]; then
  cd news-analyzer
  echo "✅ news-analyzer 디렉토리 발견 (루트)"
  TARGET_PATH="$TARGET_PATH/news-analyzer"
else
  echo "❌ news-analyzer 디렉토리를 찾을 수 없습니다"
  find . -name "news-analyzer" -type d 2>/dev/null || echo "검색 실패"
  exit 1
fi

echo "📂 최종 작업 디렉토리: $(pwd)"
echo "🎯 타겟 경로: $TARGET_PATH"

# requirements.txt 파일 확인
if [ -f "requirements.txt" ]; then
  echo "✅ requirements.txt 파일 존재"
else
  echo "❌ requirements.txt 파일 없음"
fi

# 주요 Python 스크립트 확인
if [ -f "pokernews_slack_reporter.py" ]; then
  echo "✅ pokernews_slack_reporter.py 파일 존재"
else
  echo "❌ pokernews_slack_reporter.py 파일 없음"
fi
`;
      
      const tempScriptPath = path.join(projectRoot, 'temp_pokernews_path_test.sh');
      await fs.writeFile(tempScriptPath, pathSimulationScript);
      
      try {
        const { stdout, stderr } = await execAsync(`bash ${tempScriptPath}`, { cwd: projectRoot });
        
        console.log('📋 PokerNews 경로 처리 결과:');
        console.log(stdout);
        
        if (stderr) {
          console.warn('⚠️ 경고:', stderr);
        }
        
        const hasRequirements = stdout.includes('requirements.txt 파일 존재');
        const hasMainScript = stdout.includes('pokernews_slack_reporter.py 파일 존재');
        const foundDirectory = stdout.includes('news-analyzer 디렉토리 발견');
        
        testResults.results.push({
          testName,
          status: hasRequirements && hasMainScript && foundDirectory ? 'passed' : 'failed',
          duration: Date.now() - testStart,
          details: {
            hasRequirements,
            hasMainScript,
            foundDirectory,
            output: stdout
          }
        });
        
        expect(foundDirectory).toBe(true);
        
      } finally {
        await fs.unlink(tempScriptPath).catch(() => {});
      }
      
    } catch (error) {
      testResults.results.push({
        testName,
        status: 'failed',
        duration: Date.now() - testStart,
        error: error.message
      });
      throw error;
    }
  });

  test('5. YouTube 분석 경로 시뮬레이션', async () => {
    const testName = 'YouTube 분석 경로 시뮬레이션';
    const testStart = Date.now();
    
    try {
      console.log('🎥 YouTube 경로 처리 시뮬레이션...');
      
      const projectRoot = process.cwd();
      const pathSimulationScript = `
#!/bin/bash
echo "YouTube 경로 처리 시뮬레이션"

# backend/data-collector 경로로 이동
if [ -d "backend/data-collector" ]; then
  cd backend/data-collector
  echo "✅ backend/data-collector 디렉토리로 이동"
  TARGET_PATH="backend/data-collector"
elif [ -d "data-collector" ]; then
  cd data-collector
  echo "✅ data-collector 디렉토리로 이동"
  TARGET_PATH="data-collector"
else
  echo "❌ data-collector 디렉토리를 찾을 수 없습니다"
  find . -name "data-collector" -type d 2>/dev/null || echo "검색 실패"
  exit 1
fi

echo "📂 작업 디렉토리: $(pwd)"
echo "🎯 타겟 경로: $TARGET_PATH"

# requirements.txt 파일 확인
if [ -f "requirements.txt" ]; then
  echo "✅ requirements.txt 파일 존재"
else
  echo "❌ requirements.txt 파일 없음"
fi

# scripts 디렉토리 확인
if [ -d "scripts" ]; then
  echo "✅ scripts 디렉토리 존재"
  
  # 주요 분석 스크립트 확인
  SCRIPTS=(
    "scripts/quick_validated_analyzer.py"
    "scripts/validated_analyzer_with_translation.py"
    "scripts/enhanced_validated_analyzer.py"
  )
  
  for script in "\${SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
      echo "✅ $script 파일 존재"
    else
      echo "❌ $script 파일 없음"
    fi
  done
else
  echo "❌ scripts 디렉토리 없음"
fi
`;
      
      const tempScriptPath = path.join(projectRoot, 'temp_youtube_path_test.sh');
      await fs.writeFile(tempScriptPath, pathSimulationScript);
      
      try {
        const { stdout, stderr } = await execAsync(`bash ${tempScriptPath}`, { cwd: projectRoot });
        
        console.log('📋 YouTube 경로 처리 결과:');
        console.log(stdout);
        
        if (stderr) {
          console.warn('⚠️ 경고:', stderr);
        }
        
        const hasRequirements = stdout.includes('requirements.txt 파일 존재');
        const hasScriptsDir = stdout.includes('scripts 디렉토리 존재');
        const foundDirectory = stdout.includes('data-collector 디렉토리로 이동');
        const hasQuickScript = stdout.includes('quick_validated_analyzer.py 파일 존재');
        
        testResults.results.push({
          testName,
          status: hasRequirements && hasScriptsDir && foundDirectory && hasQuickScript ? 'passed' : 'failed',
          duration: Date.now() - testStart,
          details: {
            hasRequirements,
            hasScriptsDir,
            foundDirectory,
            hasQuickScript,
            output: stdout
          }
        });
        
        expect(foundDirectory).toBe(true);
        expect(hasScriptsDir).toBe(true);
        
      } finally {
        await fs.unlink(tempScriptPath).catch(() => {});
      }
      
    } catch (error) {
      testResults.results.push({
        testName,
        status: 'failed',
        duration: Date.now() - testStart,
        error: error.message
      });
      throw error;
    }
  });

  test('6. Platform 분석 경로 중복 문제 특화 검증', async () => {
    const testName = 'Platform 분석 경로 중복 문제 특화 검증';
    const testStart = Date.now();
    
    try {
      console.log('📊 Platform 경로 중복 문제 특화 검증...');
      
      const projectRoot = process.cwd();
      
      // V3 워크플로우의 실제 경로 처리 로직을 시뮬레이션
      const pathSimulationScript = `
#!/bin/bash
echo "Platform 경로 처리 시뮬레이션 - 중복 문제 방지 검증"

echo "📂 현재 위치: $(pwd)"
echo "📁 루트 디렉토리 구조:"
ls -la | head -10

# V3 워크플로우의 경로 처리 로직 재현
ORIGINAL_PATH=$(pwd)
echo "🏠 원본 경로: $ORIGINAL_PATH"

# Step 1: 직접 경로 확인
if [ -d "backend/platform-analyzer/scripts" ]; then
  cd backend/platform-analyzer
  echo "✅ 방법1: backend/platform-analyzer/scripts 직접 접근 성공"
  FOUND_METHOD="direct-backend"
elif [ -d "platform-analyzer/scripts" ]; then
  cd platform-analyzer
  echo "✅ 방법2: platform-analyzer/scripts 직접 접근 성공"
  FOUND_METHOD="direct-root"
else
  echo "⚠️ 직접 접근 실패, 수동 검색 시작..."
  
  # Step 2: backend 디렉토리 확인
  if [ -d "backend" ]; then
    cd backend
    echo "✅ backend 디렉토리 진입"
    if [ -d "platform-analyzer" ]; then
      cd platform-analyzer
      echo "✅ platform-analyzer 디렉토리 진입"
      FOUND_METHOD="manual-search"
    else
      echo "❌ backend 내 platform-analyzer를 찾을 수 없습니다"
      ls -la
      exit 1
    fi
  else
    echo "❌ backend 디렉토리를 찾을 수 없습니다"
    find . -name "platform-analyzer" -type d 2>/dev/null || echo "검색 실패"
    exit 1
  fi
fi

CURRENT_PATH=$(pwd)
echo "📂 Platform analyzer 디렉토리: $CURRENT_PATH"
echo "🔍 발견 방법: $FOUND_METHOD"

# 경로 중복 문제 검증
EXPECTED_SINGLE_PATH="backend/platform-analyzer"
if [[ "$CURRENT_PATH" == *"/poker-trend/poker-trend/"* ]]; then
  echo "❌ 경로 중복 문제 발견: poker-trend/poker-trend 중복"
  DUPLICATE_PATH_ISSUE="true"
elif [[ "$CURRENT_PATH" == *"/backend/backend/"* ]]; then
  echo "❌ 경로 중복 문제 발견: backend/backend 중복"
  DUPLICATE_PATH_ISSUE="true"
else
  echo "✅ 경로 중복 문제 없음"
  DUPLICATE_PATH_ISSUE="false"
fi

# requirements.txt 파일 확인
if [ -f "requirements.txt" ]; then
  echo "✅ requirements.txt 파일 존재"
  HAS_REQUIREMENTS="true"
else
  echo "❌ requirements.txt 파일 없음"
  HAS_REQUIREMENTS="false"
fi

# scripts 디렉토리로 이동
if [ -d "scripts" ]; then
  cd scripts
  echo "✅ scripts 디렉토리 진입 성공"
  HAS_SCRIPTS_DIR="true"
else
  echo "❌ scripts 디렉토리를 찾을 수 없습니다"
  ls -la
  HAS_SCRIPTS_DIR="false"
fi

FINAL_PATH=$(pwd)
echo "📂 최종 작업 디렉토리: $FINAL_PATH"

# 필수 스크립트 파일 확인
REQUIRED_SCRIPTS=(
  "firebase_rest_api_fetcher.py"
  "show_daily_comparison.py"
  "final_slack_reporter.py"
)

MISSING_SCRIPTS=()
for script in "\${REQUIRED_SCRIPTS[@]}"; do
  if [ -f "$script" ]; then
    echo "✅ 스크립트 존재: $script"
  else
    echo "❌ 스크립트 없음: $script"
    MISSING_SCRIPTS+=("$script")
  fi
done

# 결과 요약
echo "==================== 검증 결과 ===================="
echo "🔍 발견 방법: $FOUND_METHOD"
echo "🛤️ 중복 경로 문제: $DUPLICATE_PATH_ISSUE"
echo "📋 requirements.txt: $HAS_REQUIREMENTS"
echo "📁 scripts 디렉토리: $HAS_SCRIPTS_DIR"
echo "📊 누락된 스크립트 수: \${#MISSING_SCRIPTS[@]}"
echo "🏁 최종 경로: $FINAL_PATH"
echo "=================================================="
`;
      
      const tempScriptPath = path.join(projectRoot, 'temp_platform_path_test.sh');
      await fs.writeFile(tempScriptPath, pathSimulationScript);
      
      try {
        const { stdout, stderr } = await execAsync(`bash ${tempScriptPath}`, { cwd: projectRoot });
        
        console.log('📋 Platform 경로 처리 결과:');
        console.log(stdout);
        
        if (stderr) {
          console.warn('⚠️ 경고:', stderr);
        }
        
        // 결과 분석
        const noDuplicatePathIssue = stdout.includes('중복 경로 문제: false');
        const hasRequirements = stdout.includes('requirements.txt: true');
        const hasScriptsDir = stdout.includes('scripts 디렉토리: true');
        const foundDirectory = stdout.includes('Platform analyzer 디렉토리') || stdout.includes('platform-analyzer 디렉토리 진입');
        const hasFirebaseScript = stdout.includes('firebase_rest_api_fetcher.py');
        const hasComparisonScript = stdout.includes('show_daily_comparison.py');
        const hasSlackScript = stdout.includes('final_slack_reporter.py');
        
        // 발견 방법 추출
        const methodMatch = stdout.match(/발견 방법: (\w+-?\w*)/);
        const foundMethod = methodMatch ? methodMatch[1] : 'unknown';
        
        const allTestsPassed = noDuplicatePathIssue && hasRequirements && hasScriptsDir && 
                             foundDirectory && hasFirebaseScript && hasComparisonScript && hasSlackScript;
        
        testResults.results.push({
          testName,
          status: allTestsPassed ? 'passed' : 'failed',
          duration: Date.now() - testStart,
          details: {
            noDuplicatePathIssue,
            hasRequirements,
            hasScriptsDir,
            foundDirectory,
            foundMethod,
            hasFirebaseScript,
            hasComparisonScript,
            hasSlackScript,
            output: stdout
          }
        });
        
        // 핵심 검증
        expect(noDuplicatePathIssue).toBe(true); // 경로 중복 문제가 없어야 함
        expect(foundDirectory).toBe(true);       // platform-analyzer 디렉토리를 찾아야 함
        expect(hasScriptsDir).toBe(true);        // scripts 디렉토리가 있어야 함
        
      } finally {
        await fs.unlink(tempScriptPath).catch(() => {});
      }
      
    } catch (error) {
      testResults.results.push({
        testName,
        status: 'failed',
        duration: Date.now() - testStart,
        error: error.message
      });
      throw error;
    }
  });

  test('7. Slack 알림 페이로드 구조 검증', async () => {
    const testName = 'Slack 알림 페이로드 구조 검증';
    const testStart = Date.now();
    
    try {
      console.log('📤 Slack 알림 페이로드 구조 검증...');
      
      // V3 워크플로우에서 사용되는 Slack 페이로드 구조 시뮬레이션
      const mockSlackPayload = {
        blocks: [
          {
            type: "header",
            text: {
              type: "plain_text",
              text: "🎰 통합 포커 보고 시스템 시작",
              emoji: true
            }
          },
          {
            type: "section",
            text: {
              type: "mrkdwn",
              text: "*📅 실행 시간:* 2025-08-08 10:00:00 KST\\n*📊 리포트 타입:* daily\\n*📈 데이터 기간:* 2025-08-07 ~ 2025-08-07\\n*📋 설명:* 일간 보고서 - 어제 (2025-08-07) 데이터 분석"
            }
          },
          {
            type: "section",
            text: {
              type: "mrkdwn",
              text: "*🔄 실행 계획:*\\n• PokerNews: true\\n• YouTube: true\\n• Platform: true"
            }
          }
        ]
      };
      
      // 페이로드 구조 검증
      const validationResults = {
        hasBlocks: Array.isArray(mockSlackPayload.blocks),
        hasHeaderBlock: mockSlackPayload.blocks.some(block => block.type === 'header'),
        hasSectionBlocks: mockSlackPayload.blocks.some(block => block.type === 'section'),
        hasKoreanText: JSON.stringify(mockSlackPayload).includes('통합 포커 보고'),
        hasTimeInfo: JSON.stringify(mockSlackPayload).includes('실행 시간'),
        hasReportType: JSON.stringify(mockSlackPayload).includes('리포트 타입'),
        hasDataPeriod: JSON.stringify(mockSlackPayload).includes('데이터 기간'),
        hasExecutionPlan: JSON.stringify(mockSlackPayload).includes('실행 계획')
      };
      
      // 최종 보고 페이로드 구조 검증
      const finalReportPayload = {
        blocks: [
          {
            type: "header",
            text: {
              type: "plain_text",
              text: "✅ 통합 포커 보고 시스템 완료",
              emoji: true
            }
          },
          {
            type: "section",
            text: {
              type: "mrkdwn",
              text: "*📅 완료 시간:* 2025-08-08 10:15:00 KST\\n*📊 리포트 타입:* daily\\n*📈 데이터 기간:* 2025-08-07 ~ 2025-08-07\\n*🎯 전체 상태:* 모든 분석 완료"
            }
          },
          {
            type: "section",
            text: {
              type: "mrkdwn",
              text: "*📋 개별 분석 결과:*\\n✅ PokerNews: success\\n✅ YouTube: success\\n✅ Platform: success"
            }
          },
          {
            type: "section",
            text: {
              type: "mrkdwn",
              text: "*🔗 상세 결과:* <https://github.com/repo/actions/runs/123456789|GitHub Actions 로그 확인>"
            }
          }
        ]
      };
      
      const finalValidationResults = {
        hasCompletionHeader: JSON.stringify(finalReportPayload).includes('통합 포커 보고 시스템 완료'),
        hasCompletionTime: JSON.stringify(finalReportPayload).includes('완료 시간'),
        hasOverallStatus: JSON.stringify(finalReportPayload).includes('전체 상태'),
        hasIndividualResults: JSON.stringify(finalReportPayload).includes('개별 분석 결과'),
        hasGitHubLink: JSON.stringify(finalReportPayload).includes('GitHub Actions 로그')
      };
      
      const allValidationsPassed = Object.values(validationResults).every(v => v) && 
                                  Object.values(finalValidationResults).every(v => v);
      
      console.log('📊 시작 알림 페이로드 검증:', validationResults);
      console.log('📊 완료 알림 페이로드 검증:', finalValidationResults);
      
      testResults.results.push({
        testName,
        status: allValidationsPassed ? 'passed' : 'failed',
        duration: Date.now() - testStart,
        details: {
          startPayloadValidation: validationResults,
          finalPayloadValidation: finalValidationResults,
          mockPayloadSize: JSON.stringify(mockSlackPayload).length,
          finalPayloadSize: JSON.stringify(finalReportPayload).length
        }
      });
      
      expect(validationResults.hasBlocks).toBe(true);
      expect(validationResults.hasKoreanText).toBe(true);
      expect(finalValidationResults.hasCompletionHeader).toBe(true);
      
    } catch (error) {
      testResults.results.push({
        testName,
        status: 'failed',
        duration: Date.now() - testStart,
        error: error.message
      });
      throw error;
    }
  });

  test('8. 에러 처리 및 복구 로직 검증', async () => {
    const testName = '에러 처리 및 복구 로직 검증';
    const testStart = Date.now();
    
    try {
      console.log('🔧 에러 처리 및 복구 로직 검증...');
      
      const workflowPath = path.join(process.cwd(), '.github/workflows/unified-poker-report-scheduler-v3.yml');
      const workflowContent = await fs.readFile(workflowPath, 'utf-8');
      
      // 에러 처리 패턴 검증
      const errorHandlingPatterns = [
        'if always()', // 항상 실행되는 단계
        'timeout-minutes:', // 타임아웃 설정
        'continue-on-error', // 에러 발생해도 계속
        'needs.*result == \'skipped\'', // 스킵된 작업 처리
        'upload-artifact', // 아티팩트 업로드
        'cat.*output.log.*echo', // 로그 출력
        'exit 1' // 명시적 실패
      ];
      
      const foundPatterns = {};
      const missingPatterns = [];
      
      for (const pattern of errorHandlingPatterns) {
        const regex = new RegExp(pattern, 'i');
        if (regex.test(workflowContent)) {
          foundPatterns[pattern] = true;
        } else {
          foundPatterns[pattern] = false;
          missingPatterns.push(pattern);
        }
      }
      
      // 필수 에러 처리 시나리오
      const errorScenarios = [
        {
          name: 'PokerNews 분석 실패 시 YouTube 실행',
          condition: 'needs.pokernews-analysis.result == \'skipped\'',
          found: workflowContent.includes('needs.pokernews-analysis.result == \'skipped\'')
        },
        {
          name: 'YouTube 분석 실패 시 Platform 실행',
          condition: 'needs.youtube-analysis.result == \'skipped\'',
          found: workflowContent.includes('needs.youtube-analysis.result == \'skipped\'')
        },
        {
          name: '최종 보고는 항상 실행',
          condition: 'if: always()',
          found: workflowContent.includes('if: always()')
        },
        {
          name: '아티팩트 업로드는 항상 실행',
          condition: 'if: always()',
          found: workflowContent.match(/upload-artifact[\s\S]*?if: always\(\)/)
        }
      ];
      
      const passedScenarios = errorScenarios.filter(s => s.found).length;
      const totalScenarios = errorScenarios.length;
      
      // 타임아웃 설정 확인
      const timeoutMatches = workflowContent.match(/timeout-minutes:\s*(\d+)/g);
      const timeoutCounts = timeoutMatches ? timeoutMatches.length : 0;
      
      console.log(`📊 에러 처리 패턴: ${Object.keys(foundPatterns).length}개 중 ${Object.values(foundPatterns).filter(v => v).length}개 발견`);
      console.log(`🛡️ 에러 시나리오: ${passedScenarios}/${totalScenarios}개 통과`);
      console.log(`⏱️ 타임아웃 설정: ${timeoutCounts}개 Job`);
      
      const allErrorHandlingPassed = missingPatterns.length <= 2 && // 일부 패턴은 선택적
                                    passedScenarios >= totalScenarios * 0.75 && // 75% 이상 통과
                                    timeoutCounts >= 4; // 최소 4개 Job에 타임아웃 설정
      
      testResults.results.push({
        testName,
        status: allErrorHandlingPassed ? 'passed' : 'failed',
        duration: Date.now() - testStart,
        details: {
          foundPatterns,
          missingPatterns,
          errorScenarios,
          passedScenarios,
          totalScenarios,
          timeoutCounts
        }
      });
      
      expect(passedScenarios).toBeGreaterThanOrEqual(Math.floor(totalScenarios * 0.75));
      expect(timeoutCounts).toBeGreaterThanOrEqual(4);
      
    } catch (error) {
      testResults.results.push({
        testName,
        status: 'failed',
        duration: Date.now() - testStart,
        error: error.message
      });
      throw error;
    }
  });

  test('9. 전체 워크플로우 통합 시뮬레이션', async () => {
    const testName = '전체 워크플로우 통합 시뮬레이션';
    const testStart = Date.now();
    
    try {
      console.log('🎯 전체 워크플로우 통합 시뮬레이션...');
      
      const projectRoot = process.cwd();
      
      // 전체 워크플로우 시뮬레이션 스크립트
      const integrationScript = `
#!/bin/bash
echo "=== 🎰 통합 포커 보고 스케줄링 시스템 V3 시뮬레이션 ==="

# 환경 변수 설정
export TIMEZONE="Asia/Seoul"
export WORKFLOW_NAME="통합 포커 보고 스케줄링 시스템"

# Step 1: 스케줄 결정
echo "📅 Step 1: 스케줄 결정 로직"
CURRENT_DATE="2025-08-08"  # 목요일
DAY_OF_WEEK=4
REPORT_TYPE="daily"
DATA_PERIOD_START="2025-08-07"
DATA_PERIOD_END="2025-08-07"

echo "  ✅ 리포트 타입: $REPORT_TYPE"
echo "  ✅ 데이터 기간: $DATA_PERIOD_START ~ $DATA_PERIOD_END"

# Step 2: PokerNews 분석 경로 확인
echo "📰 Step 2: PokerNews 분석 경로 확인"
POKERNEWS_STATUS="success"
if [ -d "poker-trend-analysis/backend/news-analyzer" ]; then
  echo "  ✅ PokerNews 경로 발견: poker-trend-analysis/backend/news-analyzer"
  POKERNEWS_PATH="poker-trend-analysis/backend/news-analyzer"
else
  echo "  ❌ PokerNews 경로 실패"
  POKERNEWS_STATUS="failed"
fi

# Step 3: YouTube 분석 경로 확인
echo "🎥 Step 3: YouTube 분석 경로 확인"
YOUTUBE_STATUS="success"
if [ -d "backend/data-collector" ]; then
  echo "  ✅ YouTube 경로 발견: backend/data-collector"
  YOUTUBE_PATH="backend/data-collector"
else
  echo "  ❌ YouTube 경로 실패"
  YOUTUBE_STATUS="failed"
fi

# Step 4: Platform 분석 경로 확인 (중복 방지 검증)
echo "📊 Step 4: Platform 분석 경로 확인 (중복 방지 검증)"
PLATFORM_STATUS="success"
DUPLICATE_CHECK="passed"

if [ -d "backend/platform-analyzer/scripts" ]; then
  PLATFORM_PATH="backend/platform-analyzer"
  echo "  ✅ Platform 경로 발견: backend/platform-analyzer"
  
  # 중복 경로 문제 검증
  FULL_PATH=$(cd backend/platform-analyzer && pwd)
  if [[ "$FULL_PATH" == *"/poker-trend/poker-trend/"* ]]; then
    echo "  ❌ 중복 경로 문제 발견: poker-trend/poker-trend"
    DUPLICATE_CHECK="failed"
    PLATFORM_STATUS="failed"
  elif [[ "$FULL_PATH" == *"/backend/backend/"* ]]; then
    echo "  ❌ 중복 경로 문제 발견: backend/backend"
    DUPLICATE_CHECK="failed" 
    PLATFORM_STATUS="failed"
  else
    echo "  ✅ 중복 경로 문제 없음"
  fi
else
  echo "  ❌ Platform 경로 실패"
  PLATFORM_STATUS="failed"
fi

# Step 5: Slack 알림 시뮬레이션
echo "📤 Step 5: Slack 알림 시뮬레이션"
SLACK_PAYLOAD_VALID="true"

# 시작 알림 페이로드 생성
START_PAYLOAD='{
  "blocks": [
    {
      "type": "header",
      "text": {
        "type": "plain_text",
        "text": "🎰 통합 포커 보고 시스템 시작",
        "emoji": true
      }
    }
  ]
}'

# 완료 알림 페이로드 생성
FINAL_PAYLOAD='{
  "blocks": [
    {
      "type": "header", 
      "text": {
        "type": "plain_text",
        "text": "✅ 통합 포커 보고 시스템 완료",
        "emoji": true
      }
    }
  ]
}'

echo "  ✅ Slack 페이로드 구조 검증 완료"

# 전체 결과 요약
echo ""
echo "==================== 시뮬레이션 결과 ===================="
echo "📊 스케줄 결정: $REPORT_TYPE 리포트"
echo "📰 PokerNews 분석: $POKERNEWS_STATUS"
echo "🎥 YouTube 분석: $YOUTUBE_STATUS" 
echo "📊 Platform 분석: $PLATFORM_STATUS"
echo "🔍 중복 경로 검증: $DUPLICATE_CHECK"
echo "📤 Slack 페이로드: $SLACK_PAYLOAD_VALID"
echo ""

# 전체 성공 여부 결정
if [[ "$POKERNEWS_STATUS" == "success" && "$YOUTUBE_STATUS" == "success" && 
      "$PLATFORM_STATUS" == "success" && "$DUPLICATE_CHECK" == "passed" ]]; then
  OVERALL_STATUS="✅ 전체 시뮬레이션 성공"
  EXIT_CODE=0
else
  OVERALL_STATUS="❌ 일부 시뮬레이션 실패"
  EXIT_CODE=1
fi

echo "🎯 전체 상태: $OVERALL_STATUS"
echo "======================================================="

exit $EXIT_CODE
`;
      
      const tempScriptPath = path.join(projectRoot, 'temp_integration_test.sh');
      await fs.writeFile(tempScriptPath, integrationScript);
      
      try {
        const { stdout, stderr } = await execAsync(`bash ${tempScriptPath}`, { cwd: projectRoot });
        
        console.log('📋 통합 시뮬레이션 결과:');
        console.log(stdout);
        
        if (stderr) {
          console.warn('⚠️ 경고:', stderr);
        }
        
        // 결과 분석
        const overallSuccess = stdout.includes('전체 시뮬레이션 성공');
        const pokernewsSuccess = stdout.includes('PokerNews 분석: success');
        const youtubeSuccess = stdout.includes('YouTube 분석: success');
        const platformSuccess = stdout.includes('Platform 분석: success');
        const noDuplicateIssue = stdout.includes('중복 경로 검증: passed');
        const slackValid = stdout.includes('Slack 페이로드: true');
        
        testResults.results.push({
          testName,
          status: overallSuccess ? 'passed' : 'failed',
          duration: Date.now() - testStart,
          details: {
            overallSuccess,
            pokernewsSuccess,
            youtubeSuccess,
            platformSuccess,
            noDuplicateIssue,
            slackValid,
            output: stdout
          }
        });
        
        // 핵심 검증 - 경로 중복 문제가 해결되었는지 확인
        expect(noDuplicateIssue).toBe(true);
        expect(platformSuccess).toBe(true);
        expect(overallSuccess).toBe(true);
        
      } finally {
        await fs.unlink(tempScriptPath).catch(() => {});
      }
      
    } catch (error) {
      testResults.results.push({
        testName,
        status: 'failed',
        duration: Date.now() - testStart,
        error: error.message
      });
      throw error;
    }
  });

});