require('dotenv').config();
const { google } = require('googleapis');

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

// Google Docs 인증
async function authenticateDocs() {
  try {
    const serviceAccountKey = JSON.parse(process.env.GOOGLE_SERVICE_ACCOUNT_KEY);
    
    const auth = new google.auth.GoogleAuth({
      credentials: serviceAccountKey,
      scopes: ['https://www.googleapis.com/auth/documents']
    });
    
    return google.docs({ version: 'v1', auth });
  } catch (error) {
    console.error('❌ 인증 오류: Google 서비스 계정 키가 올바르지 않습니다.');
    console.log('\n💡 해결 방법:');
    console.log('1. .env 파일에 GOOGLE_SERVICE_ACCOUNT_KEY가 설정되어 있는지 확인');
    console.log('2. 서비스 계정 JSON 전체가 작은따옴표로 감싸져 있는지 확인');
    console.log("   예: GOOGLE_SERVICE_ACCOUNT_KEY='{\"type\":\"service_account\",...}'");
    throw error;
  }
}

// 테이블 셀에서 텍스트 추출
function getTextFromTableCell(cell) {
  if (!cell || !cell.content) return '';
  
  let text = '';
  for (const element of cell.content) {
    if (element.paragraph && element.paragraph.elements) {
      for (const textElement of element.paragraph.elements) {
        if (textElement.textRun && textElement.textRun.content) {
          text += textElement.textRun.content;
        }
      }
    }
  }
  return text.trim();
}

// 문서에서 파트 데이터 찾기
async function findAllParts() {
  try {
    console.log('🔍 Google Docs에서 파트 데이터를 찾는 중...\n');
    
    const docs = await authenticateDocs();
    const documentId = process.env.GOOGLE_DOC_ID || '1QvLn7yJJ1c3xtwF8bd4lK_k6FL4hmcT5TiGvoeGRPow';
    
    const todayDate = getTodayDateKST();
    console.log(`📅 오늘 날짜 (한국시간): ${todayDate}\n`);
    
    // 문서 가져오기
    const document = await docs.documents.get({ documentId });
    const content = document.data.body.content;
    
    // 문서에 탭 정보가 있는지 확인
    if (document.data.tabs) {
      console.log('📑 탭 형식 문서입니다.');
      
      // 탭 이름에서 오늘 날짜 찾기
      const tabs = document.data.tabs;
      let targetTab = null;
      
      for (const [tabId, tab] of Object.entries(tabs)) {
        if (tab.tabProperties && tab.tabProperties.title) {
          const tabTitle = tab.tabProperties.title;
          console.log(`  - 탭 확인: "${tabTitle}"`);
          
          if (tabTitle.includes(todayDate) || tabTitle === todayDate) {
            targetTab = tab;
            console.log(`✅ ${todayDate} 탭을 찾았습니다!`);
            break;
          }
        }
      }
      
      if (!targetTab) {
        console.log(`\n❌ ${todayDate} 탭을 찾을 수 없습니다.`);
        console.log('💡 탭 이름이 YYMMDD 형식인지 확인해주세요.');
        return;
      }
      
      // 탭의 content 사용
      content = targetTab.documentTab.body.content;
    }
    
    // 테이블 찾기
    let foundParts = false;
    let tableCount = 0;
    
    for (const element of content) {
      if (element.table) {
        tableCount++;
        const tableRows = element.table.tableRows;
        
        // 첫 번째 행이 헤더인지 확인
        if (tableRows.length > 0) {
          const headerRow = tableRows[0];
          if (headerRow.tableCells && headerRow.tableCells.length > 0) {
            const firstHeaderCell = getTextFromTableCell(headerRow.tableCells[0]);
            
            // "파트" 헤더 확인
            if (firstHeaderCell.includes('파트') || firstHeaderCell.toLowerCase().includes('part')) {
              console.log(`📊 테이블 ${tableCount}: 파트 헤더를 찾았습니다!\n`);
              console.log('='.repeat(80));
              
              // 헤더 출력
              console.log('헤더:');
              let headers = [];
              for (let i = 0; i < headerRow.tableCells.length; i++) {
                const headerText = getTextFromTableCell(headerRow.tableCells[i]);
                headers.push(headerText);
                console.log(`  [${i}] ${headerText}`);
              }
              console.log('');
              
              // 데이터 행 출력
              console.log('파트 데이터:');
              console.log('-'.repeat(80));
              
              for (let rowIndex = 1; rowIndex < tableRows.length; rowIndex++) {
                const row = tableRows[rowIndex];
                if (row.tableCells && row.tableCells.length > 0) {
                  const partName = getTextFromTableCell(row.tableCells[0]);
                  
                  if (partName.trim()) { // 빈 행 제외
                    console.log(`\n행 ${rowIndex}:`);
                    console.log(`  파트: ${partName}`);
                    
                    // 다른 열 데이터도 출력
                    for (let cellIndex = 1; cellIndex < row.tableCells.length && cellIndex < headers.length; cellIndex++) {
                      const cellText = getTextFromTableCell(row.tableCells[cellIndex]);
                      if (cellText.trim()) {
                        console.log(`  ${headers[cellIndex]}: ${cellText}`);
                      }
                    }
                  }
                }
              }
              console.log('\n' + '='.repeat(80) + '\n');
              foundParts = true;
            }
          }
        }
      }
    }
    
    if (!foundParts) {
      console.log('❌ 파트 헤더가 있는 테이블을 찾을 수 없습니다.');
    } else {
      console.log('✅ 모든 파트 데이터를 찾았습니다!');
    }
    
  } catch (error) {
    console.error('❌ 오류 발생:', error.message);
    if (error.response && error.response.data) {
      console.error('상세 오류:', error.response.data);
    }
  }
}

// 실행
findAllParts();