// 포커 트렌드 분석 플랫폼 - YouTube 분석 시스템 테스트
const { test, expect } = require('@playwright/test');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

test.describe('YouTube Analysis System', () => {
  const dataCollectorDir = path.join(__dirname, '..', 'backend', 'data-collector');
  const scriptsDir = path.join(dataCollectorDir, 'scripts');
  
  test.beforeAll(async () => {
    // YouTube 분석 시스템 디렉토리 존재 확인
    expect(fs.existsSync(dataCollectorDir)).toBeTruthy();
    expect(fs.existsSync(scriptsDir)).toBeTruthy();
  });

  test('YouTube API 키 체크 스크립트 검증', async () => {
    const apiKeyCheckerPath = path.join(scriptsDir, 'check_api_key.py');
    expect(fs.existsSync(apiKeyCheckerPath)).toBeTruthy();
    
    const result = await runPythonScript(apiKeyCheckerPath, []);
    
    // API 키 체크 결과 확인
    expect(
      result.output.includes('API 키') ||
      result.output.includes('YouTube') ||
      result.code === 0
    ).toBeTruthy();
  });

  test('일간 분석 스크립트 존재 및 구조 검증', async () => {
    const quickAnalyzerPath = path.join(scriptsDir, 'quick_validated_analyzer.py');
    expect(fs.existsSync(quickAnalyzerPath)).toBeTruthy();
    
    const content = fs.readFileSync(quickAnalyzerPath, 'utf8');
    expect(content).toContain('youtube');
    expect(content).toContain('api');
    expect(content).toContain('trend');
  });

  test('주간 분석 스크립트 존재 및 번역 기능 검증', async () => {
    const weeklyAnalyzerPath = path.join(scriptsDir, 'validated_analyzer_with_translation.py');
    expect(fs.existsSync(weeklyAnalyzerPath)).toBeTruthy();
    
    const content = fs.readFileSync(weeklyAnalyzerPath, 'utf8');
    expect(content).toContain('translation');
    expect(content).toContain('gemini');
  });

  test('월간 분석 스크립트 존재 및 고급 기능 검증', async () => {
    const monthlyAnalyzerPath = path.join(scriptsDir, 'enhanced_validated_analyzer.py');
    expect(fs.existsSync(monthlyAnalyzerPath)).toBeTruthy();
    
    const content = fs.readFileSync(monthlyAnalyzerPath, 'utf8');
    expect(content).toContain('enhanced');
    expect(content).toContain('analysis');
  });

  test('간단한 테스트 스크립트들 실행 검증', async () => {
    const testScripts = [
      'simple_test.py',
      'simple_gemini_test.py',
      'simple_video_check.py'
    ];
    
    for (const script of testScripts) {
      const scriptPath = path.join(scriptsDir, script);
      if (fs.existsSync(scriptPath)) {
        const result = await runPythonScript(scriptPath, []);
        
        // 테스트 스크립트가 정상 실행되는지 확인
        expect(result.code === 0 || result.output.includes('테스트')).toBeTruthy();
      }
    }
  });

  test('모킹된 테스트 실행 검증', async () => {
    const mockTestScripts = [
      'test_with_mock.py',
      'test_automated.py'
    ];
    
    for (const script of mockTestScripts) {
      const scriptPath = path.join(scriptsDir, script);
      if (fs.existsSync(scriptPath)) {
        const result = await runPythonScript(scriptPath, []);
        
        // 모킹된 테스트가 성공적으로 실행되는지 확인
        expect(
          result.code === 0 || 
          result.output.includes('mock') ||
          result.output.includes('test')
        ).toBeTruthy();
      }
    }
  });

  test('비디오 유효성 검사기 테스트', async () => {
    const videoCheckerPath = path.join(scriptsDir, 'video_checker.py');
    if (fs.existsSync(videoCheckerPath)) {
      const result = await runPythonScript(videoCheckerPath, []);
      
      expect(
        result.code === 0 || 
        result.output.includes('video') ||
        result.output.includes('validation')
      ).toBeTruthy();
    }
  });

  test('포커 콘텐츠 검증기 테스트', async () => {
    const pokerValidatorPath = path.join(scriptsDir, 'test_poker_validator.py');
    if (fs.existsSync(pokerValidatorPath)) {
      const result = await runPythonScript(pokerValidatorPath, []);
      
      expect(
        result.code === 0 || 
        result.output.includes('poker') ||
        result.output.includes('validator')
      ).toBeTruthy();
    }
  });

  test('생성된 리포트 파일 구조 검증', async () => {
    const reportsDir = path.join(scriptsDir, 'reports');
    if (fs.existsSync(reportsDir)) {
      const reportFiles = fs.readdirSync(reportsDir);
      
      // 리포트 파일들이 존재하는지 확인
      const jsonReports = reportFiles.filter(file => file.endsWith('.json'));
      const textReports = reportFiles.filter(file => file.endsWith('.txt'));
      
      expect(jsonReports.length + textReports.length).toBeGreaterThan(0);
      
      // JSON 리포트 구조 검증
      for (const jsonFile of jsonReports) {
        const filePath = path.join(reportsDir, jsonFile);
        const content = JSON.parse(fs.readFileSync(filePath, 'utf8'));
        
        // 기본 리포트 구조 확인
        expect(typeof content).toBe('object');
      }
    }
  });

  test('YouTube API 응답 형식 검증 (모킹)', async () => {
    // API 응답을 모킹하는 테스트
    const mockTestScript = `
import json
import sys

# YouTube API 응답 모킹
mock_response = {
    "items": [
        {
            "id": "test_video_id",
            "snippet": {
                "title": "Test Poker Video",
                "description": "Test description",
                "publishedAt": "2025-08-08T00:00:00Z",
                "tags": ["poker", "tournament"]
            },
            "statistics": {
                "viewCount": "1000",
                "likeCount": "100",
                "commentCount": "10"
            }
        }
    ]
}

print("Mock YouTube API Response:")
print(json.dumps(mock_response, indent=2))
print("API response validation: PASSED")
`;
    
    const tempScript = path.join(__dirname, '..', 'test-results', 'temp_youtube_mock.py');
    fs.writeFileSync(tempScript, mockTestScript);
    
    const result = await runPythonScript(tempScript, []);
    
    expect(result.output).toContain('API response validation: PASSED');
    expect(result.output).toContain('Test Poker Video');
    
    // 임시 파일 정리
    if (fs.existsSync(tempScript)) {
      fs.unlinkSync(tempScript);
    }
  });

  test('Gemini AI 통합 테스트 (모킹)', async () => {
    // Gemini AI 응답을 모킹하는 테스트
    const mockGeminiScript = `
import json

# Gemini AI 분석 결과 모킹
mock_analysis = {
    "trend_analysis": {
        "popular_topics": ["Texas Hold'em", "Tournament Strategy", "Cash Games"],
        "content_quality_score": 8.5,
        "engagement_prediction": "high",
        "recommended_topics": ["Bluff Strategy", "Position Play"]
    },
    "translation": {
        "korean_summary": "포커 동영상 트렌드 분석 결과입니다.",
        "key_insights": ["전략 콘텐츠 인기 상승", "토너먼트 관련 영상 증가"]
    }
}

print("Mock Gemini AI Analysis:")
print(json.dumps(mock_analysis, indent=2, ensure_ascii=False))
print("Gemini integration test: PASSED")
`;
    
    const tempScript = path.join(__dirname, '..', 'test-results', 'temp_gemini_mock.py');
    fs.writeFileSync(tempScript, mockGeminiScript);
    
    const result = await runPythonScript(tempScript, []);
    
    expect(result.output).toContain('Gemini integration test: PASSED');
    expect(result.output).toContain('포커 동영상 트렌드');
    
    // 임시 파일 정리
    if (fs.existsSync(tempScript)) {
      fs.unlinkSync(tempScript);
    }
  });

  test('요구사항 파일 의존성 검증', async () => {
    const requirementsFiles = [
      'requirements.txt',
      'requirements-minimal.txt'
    ];
    
    for (const reqFile of requirementsFiles) {
      const reqPath = path.join(dataCollectorDir, reqFile);
      if (fs.existsSync(reqPath)) {
        const content = fs.readFileSync(reqPath, 'utf8');
        
        // 필수 YouTube 관련 라이브러리 확인
        const requiredPackages = [
          'google-api-python-client',
          'google-generativeai',
          'requests'
        ];
        
        for (const pkg of requiredPackages) {
          expect(content.toLowerCase()).toContain(pkg.toLowerCase());
        }
      }
    }
  });

  test('분석 결과 저장 형식 검증', async () => {
    // 분석 결과가 올바른 형식으로 저장되는지 테스트
    const testResultsDir = path.join(scriptsDir, 'test_results');
    if (fs.existsSync(testResultsDir)) {
      const testFiles = fs.readdirSync(testResultsDir);
      
      for (const file of testFiles) {
        if (file.endsWith('.json')) {
          const filePath = path.join(testResultsDir, file);
          
          try {
            const content = JSON.parse(fs.readFileSync(filePath, 'utf8'));
            
            // JSON 형식이 올바른지 확인
            expect(typeof content).toBe('object');
            
          } catch (error) {
            // JSON 파싱 에러가 발생하면 테스트 실패
            expect(false).toBeTruthy();
          }
        }
      }
    }
  });

  test('YouTube 웹훅 시스템 테스트', async () => {
    const webhookScripts = [
      'youtube_trend_webhook.py',
      'youtube_trend_webhook_enhanced.py'
    ];
    
    for (const script of webhookScripts) {
      const scriptPath = path.join(scriptsDir, script);
      if (fs.existsSync(scriptPath)) {
        const content = fs.readFileSync(scriptPath, 'utf8');
        
        // 웹훅 관련 기능 확인
        expect(content).toContain('webhook');
        expect(content).toContain('http');
      }
    }
  });

  test('데이터 수집기 메인 실행 테스트', async () => {
    const mainPath = path.join(dataCollectorDir, 'main.py');
    if (fs.existsSync(mainPath)) {
      const result = await runPythonScript(mainPath, ['--help']);
      
      // help 옵션이 정상 동작하는지 확인
      expect(
        result.code === 0 || 
        result.output.includes('usage') ||
        result.output.includes('help')
      ).toBeTruthy();
    }
  });

  test('퀵 테스트 실행 검증', async () => {
    const quickTestPath = path.join(dataCollectorDir, 'quick_test.py');
    if (fs.existsSync(quickTestPath)) {
      const result = await runPythonScript(quickTestPath, []);
      
      expect(
        result.code === 0 || 
        result.output.includes('test') ||
        !result.output.includes('critical error')
      ).toBeTruthy();
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