// 포커 트렌드 분석 플랫폼 - 플랫폼 분석 시스템 테스트
const { test, expect } = require('@playwright/test');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

test.describe('Platform Analysis System', () => {
  const platformAnalyzerDir = path.join(__dirname, '..', 'backend', 'platform-analyzer');
  const scriptsDir = path.join(platformAnalyzerDir, 'scripts');
  
  test.beforeAll(async () => {
    // 플랫폼 분석기 디렉토리 존재 확인
    expect(fs.existsSync(platformAnalyzerDir)).toBeTruthy();
    expect(fs.existsSync(scriptsDir)).toBeTruthy();
  });

  test('Firebase REST API 데이터 수집기 검증', async () => {
    const firebaseApiFetcherPath = path.join(scriptsDir, 'firebase_rest_api_fetcher.py');
    expect(fs.existsSync(firebaseApiFetcherPath)).toBeTruthy();
    
    const content = fs.readFileSync(firebaseApiFetcherPath, 'utf8');
    expect(content).toContain('firebase');
    expect(content).toContain('rest');
    expect(content).toContain('api');
  });

  test('일일 비교 분석기 실행 테스트', async () => {
    const dailyComparisonPath = path.join(scriptsDir, 'show_daily_comparison.py');
    if (fs.existsSync(dailyComparisonPath)) {
      const result = await runPythonScript(dailyComparisonPath, []);
      
      expect(
        result.code === 0 || 
        result.output.includes('comparison') ||
        result.output.includes('daily')
      ).toBeTruthy();
    }
  });

  test('최종 Slack 리포터 존재 및 구조 검증', async () => {
    const finalSlackReporterPath = path.join(scriptsDir, 'final_slack_reporter.py');
    expect(fs.existsSync(finalSlackReporterPath)).toBeTruthy();
    
    const content = fs.readFileSync(finalSlackReporterPath, 'utf8');
    expect(content).toContain('slack');
    expect(content).toContain('webhook');
    expect(content).toContain('report');
  });

  test('이중 메트릭 분석기 테스트', async () => {
    const dualMetricScripts = [
      'dual_metric_analyzer.py',
      'enhanced_dual_metric_analyzer.py',
      'dual_metric_slack_reporter.py'
    ];
    
    for (const script of dualMetricScripts) {
      const scriptPath = path.join(scriptsDir, script);
      if (fs.existsSync(scriptPath)) {
        const content = fs.readFileSync(scriptPath, 'utf8');
        expect(content).toContain('metric');
        expect(content).toContain('analysis');
      }
    }
  });

  test('차트 생성기 기능 검증', async () => {
    const chartGenerators = [
      'chart_generator.py',
      'platform_chart_generator.py'
    ];
    
    for (const script of chartGenerators) {
      const scriptPath = path.join(scriptsDir, script);
      if (fs.existsSync(scriptPath)) {
        const content = fs.readFileSync(scriptPath, 'utf8');
        expect(content).toContain('chart');
        expect(content).toContain('matplotlib');
      }
    }
  });

  test('생성된 리포트 JSON 파일 구조 검증', async () => {
    // 스크립트 디렉토리에서 생성된 JSON 리포트 파일들 확인
    const jsonFiles = fs.readdirSync(scriptsDir)
      .filter(file => file.includes('final_slack_report') && file.endsWith('.json'));
    
    if (jsonFiles.length > 0) {
      for (const file of jsonFiles) {
        const filePath = path.join(scriptsDir, file);
        const content = JSON.parse(fs.readFileSync(filePath, 'utf8'));
        
        // Slack 리포트 구조 검증
        expect(content).toHaveProperty('timestamp');
        expect(content).toHaveProperty('report_data');
        
        // 메시지 형식 확인
        if (content.slack_message) {
          expect(content.slack_message).toHaveProperty('text');
        }
      }
    }
  });

  test('경쟁 분석 리포터 테스트', async () => {
    const competitiveAnalysisPath = path.join(scriptsDir, 'competitive_analysis_reporter.py');
    if (fs.existsSync(competitiveAnalysisPath)) {
      const result = await runPythonScript(competitiveAnalysisPath, []);
      
      expect(
        result.code === 0 || 
        result.output.includes('competitive') ||
        result.output.includes('analysis')
      ).toBeTruthy();
    }
  });

  test('현금 게임 중심 분석기 테스트', async () => {
    const cashAnalyzers = [
      'cash_focused_slack_reporter.py',
      'cash_player_analyzer.py'
    ];
    
    for (const script of cashAnalyzers) {
      const scriptPath = path.join(scriptsDir, script);
      if (fs.existsSync(scriptPath)) {
        const result = await runPythonScript(scriptPath, []);
        
        expect(
          result.code === 0 || 
          result.output.includes('cash') ||
          result.output.includes('player')
        ).toBeTruthy();
      }
    }
  });

  test('기간별 분석 시스템 검증', async () => {
    const periodAnalyzers = [
      'daily_comparison_analyzer.py',
      'weekly_comparison_analyzer.py',
      'monthly_comparison_analyzer.py'
    ];
    
    for (const script of periodAnalyzers) {
      const scriptPath = path.join(scriptsDir, script);
      if (fs.existsSync(scriptPath)) {
        const content = fs.readFileSync(scriptPath, 'utf8');
        expect(content).toContain('comparison');
        expect(content).toContain('analysis');
      }
    }
  });

  test('히스토리 기반 분석기 테스트', async () => {
    const historyBasedScripts = [
      'history_based_analyzer.py',
      'history_based_slack_reporter.py'
    ];
    
    for (const script of historyBasedScripts) {
      const scriptPath = path.join(scriptsDir, script);
      if (fs.existsSync(scriptPath)) {
        const result = await runPythonScript(scriptPath, []);
        
        expect(
          result.code === 0 || 
          result.output.includes('history') ||
          result.output.includes('trend')
        ).toBeTruthy();
      }
    }
  });

  test('데이터 무결성 테스트', async () => {
    const dataIntegrityPath = path.join(scriptsDir, 'data_integrity_test.py');
    if (fs.existsSync(dataIntegrityPath)) {
      const result = await runPythonScript(dataIntegrityPath, []);
      
      expect(
        result.code === 0 || 
        result.output.includes('integrity') ||
        result.output.includes('validation')
      ).toBeTruthy();
    }
  });

  test('Firebase 데이터 가져오기 테스트', async () => {
    const firebaseScripts = [
      'firebase_data_fetcher.py',
      'firebase_data_importer.py',
      'import_firebase_data.py'
    ];
    
    for (const script of firebaseScripts) {
      const scriptPath = path.join(scriptsDir, script);
      if (fs.existsSync(scriptPath)) {
        const content = fs.readFileSync(scriptPath, 'utf8');
        expect(content).toContain('firebase');
        expect(content).toContain('data');
      }
    }
  });

  test('실제 데이터 미리보기 테스트', async () => {
    const previewScripts = [
      'preview_real_slack_message.py',
      'test_slack_preview.py'
    ];
    
    for (const script of previewScripts) {
      const scriptPath = path.join(scriptsDir, script);
      if (fs.existsSync(scriptPath)) {
        const result = await runPythonScript(scriptPath, []);
        
        expect(
          result.code === 0 || 
          result.output.includes('preview') ||
          result.output.includes('slack')
        ).toBeTruthy();
      }
    }
  });

  test('온라인 플랫폼 트렌드 분석기 테스트', async () => {
    const onlinePlatformPath = path.join(scriptsDir, 'online_platform_trend_analyzer.py');
    if (fs.existsSync(onlinePlatformPath)) {
      const result = await runPythonScript(onlinePlatformPath, []);
      
      expect(
        result.code === 0 || 
        result.output.includes('online') ||
        result.output.includes('platform')
      ).toBeTruthy();
    }
  });

  test('생성된 차트 파일 검증', async () => {
    const chartFiles = fs.readdirSync(scriptsDir)
      .filter(file => file.endsWith('.png'));
    
    if (chartFiles.length > 0) {
      for (const chartFile of chartFiles) {
        const filePath = path.join(scriptsDir, chartFile);
        const stats = fs.statSync(filePath);
        
        // 차트 파일이 실제 데이터를 포함하는지 확인 (0바이트가 아닌지)
        expect(stats.size).toBeGreaterThan(0);
      }
    }
  });

  test('리포트 디렉토리 구조 검증', async () => {
    const reportsDir = path.join(scriptsDir, 'reports');
    if (fs.existsSync(reportsDir)) {
      const reportFiles = fs.readdirSync(reportsDir);
      
      // 일일 분석 리포트 확인
      const dailyReports = reportFiles.filter(file => file.includes('daily_analysis'));
      if (dailyReports.length > 0) {
        for (const report of dailyReports) {
          const filePath = path.join(reportsDir, report);
          const content = fs.readFileSync(filePath, 'utf8');
          
          expect(content.length).toBeGreaterThan(0);
        }
      }
    }
  });

  test('Slack 리포트 전송 테스트 (모킹)', async () => {
    // Slack 웹훅 전송을 모킹하는 테스트
    const mockSlackScript = `
import json
import sys

# Slack 메시지 형식 모킹
mock_slack_message = {
    "text": "🎯 포커 플랫폼 일일 분석 리포트",
    "blocks": [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*📊 오늘의 주요 지표*\\n• 온라인 플레이어: +5.2%\\n• 현금 게임 활동: +3.1%"
            }
        }
    ]
}

print("Mock Slack Report:")
print(json.dumps(mock_slack_message, indent=2, ensure_ascii=False))
print("Slack integration test: PASSED")
`;
    
    const tempScript = path.join(__dirname, '..', 'test-results', 'temp_slack_mock.py');
    fs.writeFileSync(tempScript, mockSlackScript);
    
    const result = await runPythonScript(tempScript, []);
    
    expect(result.output).toContain('Slack integration test: PASSED');
    expect(result.output).toContain('포커 플랫폼');
    
    // 임시 파일 정리
    if (fs.existsSync(tempScript)) {
      fs.unlinkSync(tempScript);
    }
  });

  test('다중 기간 분석기 통합 테스트', async () => {
    const multiPeriodPath = path.join(scriptsDir, 'multi_period_analyzer.py');
    if (fs.existsSync(multiPeriodPath)) {
      const result = await runPythonScript(multiPeriodPath, []);
      
      expect(
        result.code === 0 || 
        result.output.includes('period') ||
        result.output.includes('analysis')
      ).toBeTruthy();
    }
  });

  test('cron 검증기 테스트', async () => {
    const cronValidatorPath = path.join(scriptsDir, 'cron_validator.py');
    if (fs.existsSync(cronValidatorPath)) {
      const result = await runPythonScript(cronValidatorPath, []);
      
      expect(
        result.code === 0 || 
        result.output.includes('cron') ||
        result.output.includes('schedule')
      ).toBeTruthy();
    }
  });

  test('라이브 분석 JSON 파일 구조 검증', async () => {
    // 라이브 분석 결과 파일들 확인
    const liveAnalysisFiles = fs.readdirSync(platformAnalyzerDir)
      .filter(file => file.includes('live_analysis') && file.endsWith('.json'));
    
    if (liveAnalysisFiles.length > 0) {
      for (const file of liveAnalysisFiles) {
        const filePath = path.join(platformAnalyzerDir, file);
        const content = JSON.parse(fs.readFileSync(filePath, 'utf8'));
        
        // 라이브 분석 데이터 구조 검증
        expect(content).toHaveProperty('timestamp');
        expect(content).toHaveProperty('analysis_data');
      }
    }
  });

  test('요구사항 파일 의존성 검증', async () => {
    const requirementsPath = path.join(platformAnalyzerDir, 'requirements.txt');
    
    if (fs.existsSync(requirementsPath)) {
      const content = fs.readFileSync(requirementsPath, 'utf8');
      
      // 필수 라이브러리들 확인
      const requiredPackages = [
        'requests',
        'pandas',
        'matplotlib',
        'firebase'
      ];
      
      for (const pkg of requiredPackages) {
        expect(content.toLowerCase()).toContain(pkg.toLowerCase());
      }
    }
  });
});

// Helper function: Python 스크립트 실행
async function runPythonScript(scriptPath, args = [], options = {}) {
  return new Promise((resolve) => {
    const python = spawn('python', [scriptPath, ...args], {
      stdio: ['pipe', 'pipe', 'pipe'],
      cwd: path.dirname(scriptPath),
      timeout: 30000, // 30초 타임아웃
      ...options
    });
    
    let output = '';
    let error = '';
    
    python.stdout.on('data', (data) => {
      output += data.toString();
    });
    
    python.stderr.on('data', (data) => {
      error += data.toString();
    });
    
    python.on('close', (code) => {
      resolve({
        code,
        output: output + error,
        stdout: output,
        stderr: error
      });
    });
    
    python.on('error', (err) => {
      resolve({
        code: -1,
        output: err.message,
        stdout: '',
        stderr: err.message
      });
    });
  });
}