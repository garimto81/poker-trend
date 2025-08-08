@echo off
echo ================================================================================
echo 포커 플랫폼 일일 분석 리포트 프로세스
echo ================================================================================
echo 실행 시간: %date% %time%
echo.

cd /d "%~dp0"
if not exist "venv" (
    echo [ERROR] Python 가상환경이 없습니다. 설치를 먼저 진행하세요.
    pause
    exit /b 1
)

call venv\Scripts\activate

echo [STEP 1] Firebase 데이터 수집 및 동기화...
echo --------------------------------------------------------------------------------
python scripts/firebase_data_fetcher.py
if %errorlevel% neq 0 (
    echo [ERROR] Firebase 데이터 수집 실패
    pause
    exit /b 1
)
echo.

echo [STEP 2] 일일 비교 분석 실행...
echo --------------------------------------------------------------------------------
python scripts/show_daily_comparison.py
if %errorlevel% neq 0 (
    echo [ERROR] 일일 비교 분석 실패
    pause
    exit /b 1
)
echo.

echo [STEP 3] 경쟁 구도 분석...
echo --------------------------------------------------------------------------------
python scripts/competitive_analysis_reporter.py
if %errorlevel% neq 0 (
    echo [ERROR] 경쟁 구도 분석 실패
    pause
    exit /b 1
)
echo.

echo [STEP 4] Slack 통합 리포트 전송...
echo --------------------------------------------------------------------------------
python scripts/final_slack_reporter.py
if %errorlevel% neq 0 (
    echo [ERROR] Slack 리포트 전송 실패
    pause
    exit /b 1
)
echo.

echo ================================================================================
echo ✅ 일일 포커 플랫폼 분석 보고서 완료!
echo ================================================================================
echo 완료 시간: %date% %time%
echo.
echo 📊 생성된 파일들:
dir /b *.db 2>nul
dir /b scripts\*_%date:~0,4%%date:~5,2%%date:~8,2%*.json 2>nul
echo.

pause