@echo off
echo 🧪 통합 포커 보고 스케줄링 시스템 - 테스트 실행
echo ===============================================

REM Python 가상환경 확인
if exist "venv\Scripts\activate.bat" (
    echo 📦 Python 가상환경 활성화...
    call venv\Scripts\activate.bat
) else (
    echo ⚠️ 가상환경이 없습니다. 시스템 Python 사용...
)

REM 스크립트 디렉토리로 이동
cd /d "%~dp0"

echo.
echo 📅 1. 오늘 날짜 기준 스케줄 확인
python schedule_validator.py

echo.
echo 🧪 2. 전체 테스트 케이스 실행
python schedule_validator.py --run-tests

echo.
echo 📄 3. 테스트 결과를 JSON으로 내보내기
python schedule_validator.py --run-tests --export test_results.json

echo.
echo 🔍 4. 특정 날짜 테스트 예시
echo    - 첫째주 월요일 (월간 보고서):
python schedule_validator.py --date 2024-02-05

echo    - 일반 월요일 (주간 보고서):
python schedule_validator.py --date 2024-02-12

echo    - 평일 (일간 보고서):
python schedule_validator.py --date 2024-02-13

echo    - 주말 (실행 안함):
python schedule_validator.py --date 2024-02-10

echo.
echo ✅ 모든 테스트가 완료되었습니다!
echo 📊 테스트 결과는 test_results.json 파일에서 확인할 수 있습니다.

pause