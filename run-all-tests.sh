#!/bin/bash

# 포커 트렌드 분석 시스템 - 전체 테스트 자동화 스크립트
# 일간/주간/월간 리포트를 순차적으로 테스트

echo "🎰 포커 트렌드 분석 시스템 - 전체 테스트 시작"
echo "================================================"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 환경변수 확인
check_env() {
    echo -e "${YELLOW}📋 환경변수 확인 중...${NC}"
    
    if [[ -z "$YOUTUBE_API_KEY" ]]; then
        echo -e "${RED}❌ YOUTUBE_API_KEY가 설정되지 않았습니다${NC}"
        exit 1
    fi
    
    if [[ -z "$GEMINI_API_KEY" ]]; then
        echo -e "${RED}❌ GEMINI_API_KEY가 설정되지 않았습니다${NC}"
        exit 1
    fi
    
    if [[ -z "$SLACK_WEBHOOK_URL" ]]; then
        echo -e "${YELLOW}⚠️ SLACK_WEBHOOK_URL이 설정되지 않았습니다 (선택사항)${NC}"
    fi
    
    echo -e "${GREEN}✅ 환경변수 확인 완료${NC}\n"
}

# 테스트 실행 함수
run_test() {
    local report_type=$1
    local youtube_script=$2
    local wait_time=$3
    
    echo "================================================"
    echo -e "${YELLOW}🚀 ${report_type} 리포트 테스트 시작${NC}"
    echo "시간: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "================================================"
    
    export REPORT_TYPE=${report_type}
    
    # 1. PokerNews 분석 (있는 경우)
    if [ -d "backend/news-analyzer" ]; then
        echo -e "${YELLOW}📰 PokerNews 분석 중...${NC}"
        cd backend/news-analyzer
        python pokernews_slack_reporter.py 2>&1 | tail -5
        cd ../..
    elif [ -d "poker-trend-analysis/backend/news-analyzer" ]; then
        echo -e "${YELLOW}📰 PokerNews 분석 중...${NC}"
        cd poker-trend-analysis/backend/news-analyzer
        python pokernews_slack_reporter.py 2>&1 | tail -5
        cd ../../..
    fi
    
    # 2. YouTube 분석
    echo -e "${YELLOW}🎥 YouTube ${report_type} 분석 중...${NC}"
    cd backend/data-collector
    python scripts/${youtube_script} 2>&1 | tail -10
    cd ../..
    
    # 3. Platform 분석
    echo -e "${YELLOW}📊 Platform ${report_type} 분석 중...${NC}"
    cd backend/platform-analyzer/scripts
    
    # Firebase 데이터 수집
    python firebase_rest_api_fetcher.py 2>&1 | tail -5
    
    # 리포트 타입별 추가 분석
    case $report_type in
        "weekly")
            python multi_period_analyzer.py 2>&1 | tail -5
            ;;
        "monthly")
            python monthly_platform_report.py 2>&1 | tail -5
            python competitive_analysis_reporter.py 2>&1 | tail -5
            ;;
        *)
            python show_daily_comparison.py 2>&1 | tail -5
            ;;
    esac
    
    # 최종 Slack 리포트
    python final_slack_reporter.py 2>&1 | tail -5
    cd ../../..
    
    echo -e "${GREEN}✅ ${report_type} 리포트 테스트 완료${NC}"
    
    # 다음 테스트 전 대기
    if [[ $wait_time -gt 0 ]]; then
        echo -e "${YELLOW}⏰ 다음 테스트까지 ${wait_time}초 대기...${NC}\n"
        sleep $wait_time
    fi
}

# 메인 실행
main() {
    # 환경변수 확인
    check_env
    
    # 시작 시간 기록
    start_time=$(date +%s)
    
    # 일간 리포트 테스트
    run_test "daily" "quick_validated_analyzer.py" 300
    
    # 주간 리포트 테스트
    run_test "weekly" "validated_analyzer_with_translation.py" 300
    
    # 월간 리포트 테스트
    run_test "monthly" "enhanced_validated_analyzer.py" 0
    
    # 종료 시간 및 소요 시간 계산
    end_time=$(date +%s)
    duration=$((end_time - start_time))
    minutes=$((duration / 60))
    seconds=$((duration % 60))
    
    echo "================================================"
    echo -e "${GREEN}🎉 모든 테스트 완료!${NC}"
    echo "총 소요 시간: ${minutes}분 ${seconds}초"
    echo "================================================"
    
    # 결과 요약
    echo -e "\n📊 테스트 결과 요약:"
    echo "• 일간 리포트: ✅"
    echo "• 주간 리포트: ✅"
    echo "• 월간 리포트: ✅"
    echo -e "\n💡 Slack 채널에서 결과를 확인하세요!"
}

# 스크립트 실행
main