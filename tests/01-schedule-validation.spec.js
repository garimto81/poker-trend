// 포커 트렌드 분석 플랫폼 - 스케줄 검증 시스템 테스트
const { test, expect } = require('@playwright/test');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

test.describe('Schedule Validation System', () => {
  const scheduleValidatorPath = path.join(__dirname, '..', 'scripts', 'schedule_validator.py');
  
  test.beforeAll(async () => {
    // schedule_validator.py 파일 존재 확인
    expect(fs.existsSync(scheduleValidatorPath)).toBeTruthy();
  });

  test('스케줄 검증기 기본 실행 테스트', async () => {
    const result = await runScheduleValidator(['--help']);
    
    expect(result.code).toBe(0);
    expect(result.output).toContain('통합 포커 보고 스케줄링 시스템 검증 도구');
    expect(result.output).toContain('--date');
    expect(result.output).toContain('--force-type');
    expect(result.output).toContain('--run-tests');
  });

  test('첫째주 월요일 - 월간 보고서 스케줄 검증', async () => {
    const testDates = [
      '2024-01-01',  // 2024년 1월 첫째주 월요일
      '2024-02-05',  // 2024년 2월 첫째주 월요일
      '2024-07-01',  // 2024년 7월 첫째주 월요일
    ];

    for (const date of testDates) {
      const result = await runScheduleValidator(['--date', date, '--export', `test-results/schedule-${date}.json`]);
      
      expect(result.code).toBe(0);
      expect(result.output).toContain('월간 보고서');
      expect(result.output).toContain('지난달');
      expect(result.output).toContain('실행 우선순위: 3');
      
      // JSON 결과 파일 검증
      const jsonFile = path.join(__dirname, '..', 'test-results', `schedule-${date}.json`);
      if (fs.existsSync(jsonFile)) {
        const data = JSON.parse(fs.readFileSync(jsonFile, 'utf8'));
        expect(data.test_cases[0].report_type).toBe('monthly');
        expect(data.test_cases[0].execution_priority).toBe(3);
      }
    }
  });

  test('일반 월요일 - 주간 보고서 스케줄 검증', async () => {
    const testDates = [
      '2024-01-08',  // 2024년 1월 둘째주 월요일
      '2024-02-12',  // 2024년 2월 둘째주 월요일
      '2024-03-11',  // 2024년 3월 둘째주 월요일
    ];

    for (const date of testDates) {
      const result = await runScheduleValidator(['--date', date]);
      
      expect(result.code).toBe(0);
      expect(result.output).toContain('주간 보고서');
      expect(result.output).toContain('지난주');
      expect(result.output).toContain('실행 우선순위: 2');
    }
  });

  test('평일(화-금) - 일간 보고서 스케줄 검증', async () => {
    const testDates = [
      '2024-01-09',  // 화요일
      '2024-01-10',  // 수요일
      '2024-01-11',  // 목요일
      '2024-01-12',  // 금요일
    ];

    for (const date of testDates) {
      const result = await runScheduleValidator(['--date', date]);
      
      expect(result.code).toBe(0);
      expect(result.output).toContain('일간 보고서');
      expect(result.output).toContain('어제');
      expect(result.output).toContain('실행 우선순위: 1');
    }
  });

  test('주말 - 실행 건너뛰기 검증', async () => {
    const weekendDates = [
      '2024-01-13',  // 토요일
      '2024-01-14',  // 일요일
    ];

    for (const date of weekendDates) {
      const result = await runScheduleValidator(['--date', date]);
      
      expect(result.code).toBe(0);
      expect(result.output).toContain('주말로 인해 실행하지 않음');
    }
  });

  test('강제 타입 설정 검증', async () => {
    const testCases = [
      { date: '2024-01-13', forceType: 'daily', expected: '일간' },
      { date: '2024-01-14', forceType: 'weekly', expected: '주간' },
      { date: '2024-01-15', forceType: 'monthly', expected: '월간' },
    ];

    for (const { date, forceType, expected } of testCases) {
      const result = await runScheduleValidator(['--date', date, '--force-type', forceType]);
      
      expect(result.code).toBe(0);
      expect(result.output).toContain(`강제 설정: ${forceType}`);
      expect(result.output).toContain(`${expected}`);
    }
  });

  test('전체 테스트 케이스 실행 및 통계 검증', async () => {
    const result = await runScheduleValidator(['--run-tests']);
    
    expect(result.code).toBe(0);
    expect(result.output).toContain('통합 포커 보고 스케줄링 시스템 - 테스트 케이스 실행');
    expect(result.output).toContain('테스트 결과 요약');
    expect(result.output).toContain('월간 보고서:');
    expect(result.output).toContain('주간 보고서:');
    expect(result.output).toContain('일간 보고서:');
    expect(result.output).toContain('실행 안함 (주말):');
  });

  test('데이터 기간 계산 정확성 검증', async () => {
    // 특정 날짜의 데이터 기간이 올바르게 계산되는지 검증
    const result = await runScheduleValidator(['--date', '2024-07-01']);  // 첫째주 월요일
    
    expect(result.code).toBe(0);
    // 2024년 6월 데이터 기간이 표시되어야 함
    expect(result.output).toContain('2024-06-01 ~ 2024-06-30');
  });

  test('잘못된 날짜 형식 처리', async () => {
    const invalidDates = [
      'invalid-date',
      '2024-13-01',  // 잘못된 월
      '2024-02-30',  // 잘못된 일
    ];

    for (const date of invalidDates) {
      const result = await runScheduleValidator(['--date', date]);
      
      // 에러가 발생하거나 적절한 오류 메시지가 출력되어야 함
      expect(result.code !== 0 || result.output.includes('날짜 형식 오류')).toBeTruthy();
    }
  });

  test('JSON 내보내기 기능 검증', async () => {
    const exportFile = 'test-results/schedule-export-test.json';
    const result = await runScheduleValidator(['--run-tests', '--export', exportFile]);
    
    expect(result.code).toBe(0);
    expect(result.output).toContain('테스트 결과가');
    expect(result.output).toContain('에 저장되었습니다');
    
    // JSON 파일이 생성되었는지 확인
    const jsonPath = path.join(__dirname, '..', exportFile);
    expect(fs.existsSync(jsonPath)).toBeTruthy();
    
    // JSON 파일 내용 검증
    const jsonData = JSON.parse(fs.readFileSync(jsonPath, 'utf8'));
    expect(jsonData.test_timestamp).toBeDefined();
    expect(jsonData.total_test_cases).toBeGreaterThan(0);
    expect(jsonData.summary).toBeDefined();
    expect(jsonData.test_cases).toBeInstanceOf(Array);
  });
});

// Helper function: Python 스크립트 실행
async function runScheduleValidator(args) {
  const scriptPath = path.join(__dirname, '..', 'scripts', 'schedule_validator.py');
  
  return new Promise((resolve) => {
    const python = spawn('python', [scriptPath, ...args], {
      stdio: ['pipe', 'pipe', 'pipe']
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