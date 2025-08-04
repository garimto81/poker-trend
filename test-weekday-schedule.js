// 평일 스케줄링 테스트 스크립트
const cron = require('node-cron');

console.log('🧪 평일 스케줄링 테스트 시작\n');

// 요일별 테스트 케이스
const testCases = [
  { date: new Date('2025-01-04'), expected: false }, // 토요일
  { date: new Date('2025-01-05'), expected: false }, // 일요일
  { date: new Date('2025-01-06'), expected: true },  // 월요일
  { date: new Date('2025-01-07'), expected: true },  // 화요일
  { date: new Date('2025-01-08'), expected: true },  // 수요일
  { date: new Date('2025-01-09'), expected: true },  // 목요일
  { date: new Date('2025-01-10'), expected: true },  // 금요일
];

// 요일 이름 배열
const dayNames = ['일요일', '월요일', '화요일', '수요일', '목요일', '금요일', '토요일'];

console.log('📅 요일별 실행 테스트:');
console.log('─'.repeat(50));

testCases.forEach(testCase => {
  const dayOfWeek = testCase.date.getDay();
  const shouldRun = !(dayOfWeek === 0 || dayOfWeek === 6);
  const dayName = dayNames[dayOfWeek];
  const dateStr = testCase.date.toISOString().split('T')[0];
  
  console.log(`${dateStr} (${dayName}): ${shouldRun ? '✅ 실행' : '❌ 실행 안함'} ${shouldRun === testCase.expected ? '✓' : '✗ 오류!'}`);
});

console.log('\n📊 Cron 표현식 검증:');
console.log('─'.repeat(50));

// Cron 표현식 테스트
const cronExpression = '0 1 * * 1-5';
console.log(`Cron 표현식: ${cronExpression}`);
console.log('의미: 월-금 UTC 01:00 (한국시간 10:00)에 실행\n');

// Cron 표현식 유효성 검증
const isValid = cron.validate(cronExpression);
console.log(`Cron 표현식 유효성: ${isValid ? '✅ 유효함' : '❌ 유효하지 않음'}`);

// 다음 실행 시간 계산 (시뮬레이션)
console.log('\n🕐 다음 실행 예정 시간:');
console.log('─'.repeat(50));

const now = new Date();
const currentDay = now.getDay();
let daysUntilNext = 0;

if (currentDay === 0) { // 일요일
  daysUntilNext = 1;
} else if (currentDay === 6) { // 토요일
  daysUntilNext = 2;
} else if (currentDay >= 1 && currentDay <= 5) { // 평일
  // 현재 시간이 오전 10시 이전이면 오늘, 이후면 다음 평일
  const currentHour = now.getHours();
  if (currentHour < 10) {
    daysUntilNext = 0;
  } else {
    daysUntilNext = currentDay === 5 ? 3 : 1; // 금요일이면 월요일로, 아니면 다음날
  }
}

const nextRun = new Date(now);
nextRun.setDate(now.getDate() + daysUntilNext);
nextRun.setHours(10, 0, 0, 0);

console.log(`현재: ${now.toLocaleString('ko-KR')}`);
console.log(`다음 실행: ${nextRun.toLocaleString('ko-KR')} (${dayNames[nextRun.getDay()]})`);

console.log('\n✅ 테스트 완료!');