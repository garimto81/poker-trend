// 한국 시간으로 오늘 날짜 가져오기
function getTodayDateKST() {
  const now = new Date();
  const kstOffset = 9 * 60; // KST는 UTC+9
  const kstTime = new Date(now.getTime() + (now.getTimezoneOffset() + kstOffset) * 60 * 1000);
  
  const year = String(kstTime.getFullYear()).slice(-2);
  const month = String(kstTime.getMonth() + 1).padStart(2, '0');
  const day = String(kstTime.getDate()).padStart(2, '0');
  
  return `${year}${month}${day}`;
}

// Google Docs에서 찾을 수 있는 파트 데이터 시뮬레이션
function simulatePartsData() {
  const todayDate = getTodayDateKST();
  
  console.log('🔍 Google Docs 파트 데이터 검색 시뮬레이션\n');
  console.log(`📅 오늘 날짜 (한국시간): ${todayDate}`);
  console.log(`📄 문서 ID: 1QvLn7yJJ1c3xtwF8bd4lK_k6FL4hmcT5TiGvoeGRPow\n`);
  
  console.log('='.repeat(80));
  console.log(`📑 "${todayDate}" 탭에서 찾은 파트 데이터:`);
  console.log('='.repeat(80));
  
  // 예상되는 테이블 구조
  console.log('\n📊 테이블 1: 일일 업무 보고서');
  console.log('-'.repeat(80));
  console.log('헤더: [파트] [진행 중인 업무 명칭] [핵심 내용(방향성)] [진행사항]\n');
  
  // 예상되는 파트 데이터들
  const expectedParts = [
    {
      part: '카메라 Aiden Kim',
      task: 'AI 쇼츠 자동 제작 앱',
      content: '고객 납품 관련 업무로 긴급도가 매우 높음',
      progress: '90%'
    },
    {
      part: '카메라',
      subPart: 'Aiden Kim',
      task: '영상 편집 자동화 프로세스',
      content: '편집 시간 단축을 위한 워크플로우 개선',
      progress: '진행중'
    },
    {
      part: '개발팀',
      task: '신규 기능 개발',
      content: '사용자 인터페이스 개선',
      progress: '50%'
    },
    {
      part: '마케팅',
      task: '캠페인 기획',
      content: 'Q4 마케팅 전략 수립',
      progress: '기획중'
    },
    {
      part: '디자인',
      task: 'UI/UX 리뉴얼',
      content: '모바일 앱 디자인 개선',
      progress: '70%'
    }
  ];
  
  console.log('찾은 파트 데이터:');
  expectedParts.forEach((data, index) => {
    console.log(`\n행 ${index + 1}:`);
    if (data.subPart) {
      console.log(`  파트: ${data.part}`);
      console.log(`        ${data.subPart}`);
    } else {
      console.log(`  파트: ${data.part}`);
    }
    console.log(`  진행 중인 업무 명칭: ${data.task}`);
    console.log(`  핵심 내용(방향성): ${data.content}`);
    console.log(`  진행사항: ${data.progress}`);
  });
  
  console.log('\n' + '='.repeat(80));
  console.log('\n🔍 검색 패턴 분석:');
  console.log('1. "카메라 Aiden Kim" - 전체 문자열 매치');
  console.log('2. "카메라" + 다음 행에 "Aiden Kim" - 계층적 구조');
  console.log('3. 다른 파트들: "개발팀", "마케팅", "디자인" 등');
  
  console.log('\n📌 시스템이 찾는 방식:');
  console.log('- 첫 번째 열이 "파트"로 시작하는 테이블 검색');
  console.log('- 각 행의 첫 번째 셀(파트 이름) 확인');
  console.log('- 빈 행은 자동으로 건너뜀');
  console.log('- 카메라 파트의 경우 특별히 "Aiden Kim" 포함 여부 확인');
}

// 실행
simulatePartsData();