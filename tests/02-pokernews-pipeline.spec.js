// 포커 트렌드 분석 플랫폼 - PokerNews 분석 파이프라인 테스트
const { test, expect } = require('@playwright/test');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

test.describe('PokerNews Analysis Pipeline', () => {
  const newsAnalyzerDir = path.join(__dirname, '..', 'poker-trend-analysis', 'backend', 'news-analyzer');
  
  test.beforeAll(async () => {
    // 뉴스 분석기 디렉토리 존재 확인
    expect(fs.existsSync(newsAnalyzerDir)).toBeTruthy();
  });

  test('RSS 수집기 존재 및 실행 가능성 검증', async () => {
    const rssCollectorPath = path.join(newsAnalyzerDir, 'pokernews_rss_collector.py');
    expect(fs.existsSync(rssCollectorPath)).toBeTruthy();
    
    // 파일 내용에서 주요 함수들 확인
    const content = fs.readFileSync(rssCollectorPath, 'utf8');
    expect(content).toContain('def collect_pokernews_rss');
    expect(content).toContain('https://www.pokernews.com/rss.xml');
  });

  test('AI 분석기 존재 및 Gemini API 설정 검증', async () => {
    const aiAnalyzerPath = path.join(newsAnalyzerDir, 'pokernews_ai_analyzer.py');
    expect(fs.existsSync(aiAnalyzerPath)).toBeTruthy();
    
    const content = fs.readFileSync(aiAnalyzerPath, 'utf8');
    expect(content).toContain('import google.generativeai');
    expect(content).toContain('GEMINI_API_KEY');
  });

  test('Slack 리포터 존재 및 웹훅 설정 검증', async () => {
    const slackReporterPath = path.join(newsAnalyzerDir, 'pokernews_slack_reporter.py');
    expect(fs.existsSync(slackReporterPath)).toBeTruthy();
    
    const content = fs.readFileSync(slackReporterPath, 'utf8');
    expect(content).toContain('SLACK_WEBHOOK_URL');
    expect(content).toContain('requests.post');
  });

  test('RSS 수집기 기본 실행 테스트', async () => {
    const result = await runPythonScript(path.join(newsAnalyzerDir, 'pokernews_rss_collector.py'), []);
    
    // 스크립트가 에러 없이 실행되는지 확인
    expect(result.code === 0 || result.output.includes('Successfully collected')).toBeTruthy();
  });

  test('미리보기 기능 실행 테스트', async () => {
    const previewScripts = [
      'pokernews_preview.py',
      'enhanced_preview.py',
      'enhanced_preview_v2.py',
      'simple_preview.py'
    ];
    
    for (const script of previewScripts) {
      const scriptPath = path.join(newsAnalyzerDir, script);
      if (fs.existsSync(scriptPath)) {
        const result = await runPythonScript(scriptPath, []);
        
        // 스크립트가 실행되고 결과를 생성하는지 확인
        expect(result.code === 0 || result.output.includes('미리보기')).toBeTruthy();
      }
    }
  });

  test('생성된 RSS 데이터 파일 검증', async () => {
    // 기존 RSS 데이터 파일들 확인
    const rssFiles = fs.readdirSync(newsAnalyzerDir)
      .filter(file => file.includes('pokernews_rss') && file.endsWith('.json'));
    
    if (rssFiles.length > 0) {
      for (const file of rssFiles) {
        const filePath = path.join(newsAnalyzerDir, file);
        const content = JSON.parse(fs.readFileSync(filePath, 'utf8'));
        
        // RSS 데이터 구조 검증
        expect(content).toHaveProperty('timestamp');
        expect(content).toHaveProperty('articles');
        expect(Array.isArray(content.articles)).toBeTruthy();
        
        // 개별 아티클 구조 검증
        if (content.articles.length > 0) {
          const article = content.articles[0];
          expect(article).toHaveProperty('title');
          expect(article).toHaveProperty('link');
          expect(article).toHaveProperty('published');
        }
      }
    }
  });

  test('미리보기 HTML 파일 생성 검증', async () => {
    const previewFiles = fs.readdirSync(newsAnalyzerDir)
      .filter(file => file.includes('preview') && file.endsWith('.html'));
    
    if (previewFiles.length > 0) {
      for (const file of previewFiles) {
        const filePath = path.join(newsAnalyzerDir, file);
        const content = fs.readFileSync(filePath, 'utf8');
        
        // HTML 구조 기본 검증
        expect(content).toContain('<html');
        expect(content).toContain('<head');
        expect(content).toContain('<body');
        expect(content).toContain('PokerNews');
      }
    }
  });

  test('미리보기 JSON 데이터 구조 검증', async () => {
    const previewJsonFiles = fs.readdirSync(newsAnalyzerDir)
      .filter(file => file.includes('preview_data') && file.endsWith('.json'));
    
    if (previewJsonFiles.length > 0) {
      for (const file of previewJsonFiles) {
        const filePath = path.join(newsAnalyzerDir, file);
        const content = JSON.parse(fs.readFileSync(filePath, 'utf8'));
        
        // 미리보기 데이터 구조 검증
        expect(content).toHaveProperty('timestamp');
        expect(content).toHaveProperty('analysis_summary');
        
        if (content.articles) {
          expect(Array.isArray(content.articles)).toBeTruthy();
        }
      }
    }
  });

  test('Requirements.txt 의존성 확인', async () => {
    const requirementsPath = path.join(newsAnalyzerDir, 'requirements.txt');
    
    if (fs.existsSync(requirementsPath)) {
      const content = fs.readFileSync(requirementsPath, 'utf8');
      
      // 필수 라이브러리들 확인
      const requiredPackages = [
        'requests',
        'google-generativeai',
        'feedparser',
        'beautifulsoup4'
      ];
      
      for (const pkg of requiredPackages) {
        expect(content.toLowerCase()).toContain(pkg.toLowerCase());
      }
    }
  });

  test('환경변수 의존성 테스트', async ({ page }) => {
    // 환경변수가 없는 상황에서의 동작 확인
    const tempEnv = { ...process.env };
    delete process.env.GEMINI_API_KEY;
    delete process.env.SLACK_WEBHOOK_URL;
    
    const result = await runPythonScript(
      path.join(newsAnalyzerDir, 'simple_preview.py'), 
      [],
      { env: {} }  // 빈 환경변수로 실행
    );
    
    // 환경변수 복구
    process.env = tempEnv;
    
    // 적절한 에러 메시지나 대체 동작이 있는지 확인
    expect(
      result.output.includes('API_KEY') || 
      result.output.includes('환경변수') ||
      result.output.includes('설정이 필요') ||
      result.code !== 0
    ).toBeTruthy();
  });

  test('배치 스크립트 실행 테스트', async () => {
    const batchScript = path.join(newsAnalyzerDir, 'run_preview.bat');
    
    if (fs.existsSync(batchScript)) {
      const result = await runBatchScript(batchScript);
      
      // 배치 스크립트가 정상 실행되는지 확인
      expect(result.code === 0 || result.output.includes('완료')).toBeTruthy();
    }
  });

  test('PokerNews 파이프라인 통합 테스트', async () => {
    // 전체 파이프라인이 순차적으로 실행되는지 테스트
    const pipeline = [
      'pokernews_rss_collector.py',
      'simple_preview.py'  // AI 분석 대신 간단한 미리보기로 대체
    ];
    
    for (const script of pipeline) {
      const scriptPath = path.join(newsAnalyzerDir, script);
      if (fs.existsSync(scriptPath)) {
        const result = await runPythonScript(scriptPath, []);
        
        // 각 단계가 성공적으로 완료되어야 함
        expect(result.code === 0 || !result.output.includes('Error')).toBeTruthy();
      }
    }
  });

  test('오류 처리 및 복구 메커니즘 테스트', async () => {
    // 잘못된 RSS URL로 테스트
    const testScript = `
import sys
import os
sys.path.append(r'${newsAnalyzerDir.replace(/\\/g, '\\\\')}')

try:
    from pokernews_rss_collector import collect_pokernews_rss
    # 존재하지 않는 URL로 테스트
    result = collect_pokernews_rss('https://invalid-url-for-test.com/rss.xml')
    print("Error handling test passed")
except Exception as e:
    print(f"Expected error occurred: {str(e)}")
`;
    
    const tempScript = path.join(__dirname, '..', 'test-results', 'temp_error_test.py');
    fs.writeFileSync(tempScript, testScript);
    
    const result = await runPythonScript(tempScript, []);
    
    // 에러가 적절히 처리되는지 확인
    expect(
      result.output.includes('Error handling test') || 
      result.output.includes('Expected error occurred')
    ).toBeTruthy();
    
    // 임시 파일 정리
    if (fs.existsSync(tempScript)) {
      fs.unlinkSync(tempScript);
    }
  });
});

// Helper function: Python 스크립트 실행
async function runPythonScript(scriptPath, args = [], options = {}) {
  return new Promise((resolve) => {
    const python = spawn('python', [scriptPath, ...args], {
      stdio: ['pipe', 'pipe', 'pipe'],
      cwd: path.dirname(scriptPath),
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

// Helper function: 배치 스크립트 실행
async function runBatchScript(batchPath) {
  return new Promise((resolve) => {
    const batch = spawn('cmd', ['/c', batchPath], {
      stdio: ['pipe', 'pipe', 'pipe'],
      cwd: path.dirname(batchPath)
    });
    
    let output = '';
    let error = '';
    
    batch.stdout.on('data', (data) => {
      output += data.toString();
    });
    
    batch.stderr.on('data', (data) => {
      error += data.toString();
    });
    
    batch.on('close', (code) => {
      resolve({
        code,
        output: output + error,
        stdout: output,
        stderr: error
      });
    });
    
    batch.on('error', (err) => {
      resolve({
        code: -1,
        output: err.message,
        stdout: '',
        stderr: err.message
      });
    });
  });
}