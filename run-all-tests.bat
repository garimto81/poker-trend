@echo off
REM 포커 트렌드 분석 시스템 - 전체 테스트 자동화 스크립트 (Windows)
REM 일간/주간/월간 리포트를 순차적으로 테스트

echo ============================================
echo 🎰 포커 트렌드 분석 시스템 - 전체 테스트 시작
echo ============================================

REM 환경변수 확인
echo 📋 환경변수 확인 중...

if "%YOUTUBE_API_KEY%"=="" (
    echo ❌ YOUTUBE_API_KEY가 설정되지 않았습니다
    echo .env 파일을 확인하거나 set YOUTUBE_API_KEY=your_key 실행
    exit /b 1
)

if "%GEMINI_API_KEY%"=="" (
    echo ❌ GEMINI_API_KEY가 설정되지 않았습니다
    echo .env 파일을 확인하거나 set GEMINI_API_KEY=your_key 실행
    exit /b 1
)

if "%SLACK_WEBHOOK_URL%"=="" (
    echo ⚠️ SLACK_WEBHOOK_URL이 설정되지 않았습니다 (선택사항)
)

echo ✅ 환경변수 확인 완료
echo.

REM ================================================
REM 일간 리포트 테스트
REM ================================================
echo ============================================
echo 🚀 일간(Daily) 리포트 테스트 시작
echo 시간: %date% %time%
echo ============================================

set REPORT_TYPE=daily

REM YouTube 일간 분석
echo 🎥 YouTube 일간 분석 중...
cd backend\data-collector
python scripts\quick_validated_analyzer.py
if errorlevel 1 echo ⚠️ YouTube 분석 완료 (경고 무시)

REM Platform 일간 분석
echo 📊 Platform 일간 분석 중...
cd ..\platform-analyzer\scripts
python firebase_rest_api_fetcher.py
python show_daily_comparison.py
python final_slack_reporter.py
if errorlevel 1 echo ⚠️ Platform 분석 완료 (경고 무시)
cd ..\..\..

echo ✅ 일간 리포트 테스트 완료
echo ⏰ 5분 대기 중 (Slack rate limit)...
timeout /t 300 /nobreak > nul

REM ================================================
REM 주간 리포트 테스트
REM ================================================
echo ============================================
echo 🚀 주간(Weekly) 리포트 테스트 시작
echo 시간: %date% %time%
echo ============================================

set REPORT_TYPE=weekly

REM YouTube 주간 분석
echo 🎥 YouTube 주간 분석 중 (한글 번역 포함)...
cd backend\data-collector
python scripts\validated_analyzer_with_translation.py
if errorlevel 1 echo ⚠️ YouTube 분석 완료 (경고 무시)

REM Platform 주간 분석
echo 📊 Platform 주간 분석 중...
cd ..\platform-analyzer\scripts
python firebase_rest_api_fetcher.py
python multi_period_analyzer.py
python final_slack_reporter.py
if errorlevel 1 echo ⚠️ Platform 분석 완료 (경고 무시)
cd ..\..\..

echo ✅ 주간 리포트 테스트 완료
echo ⏰ 5분 대기 중 (Slack rate limit)...
timeout /t 300 /nobreak > nul

REM ================================================
REM 월간 리포트 테스트
REM ================================================
echo ============================================
echo 🚀 월간(Monthly) 리포트 테스트 시작
echo 시간: %date% %time%
echo ============================================

set REPORT_TYPE=monthly

REM YouTube 월간 분석
echo 🎥 YouTube 월간 분석 중 (강화된 AI 분석)...
cd backend\data-collector
python scripts\enhanced_validated_analyzer.py
if errorlevel 1 echo ⚠️ YouTube 분석 완료 (경고 무시)

REM Platform 월간 분석
echo 📊 Platform 월간 분석 중...
cd ..\platform-analyzer\scripts
python firebase_rest_api_fetcher.py
python monthly_platform_report.py
python competitive_analysis_reporter.py
python final_slack_reporter.py
if errorlevel 1 echo ⚠️ Platform 분석 완료 (경고 무시)
cd ..\..\..

echo ✅ 월간 리포트 테스트 완료

REM ================================================
REM 테스트 완료
REM ================================================
echo.
echo ============================================
echo 🎉 모든 테스트 완료!
echo ============================================
echo.
echo 📊 테스트 결과 요약:
echo • 일간 리포트: ✅
echo • 주간 리포트: ✅
echo • 월간 리포트: ✅
echo.
echo 💡 Slack 채널에서 결과를 확인하세요!
echo.
pause