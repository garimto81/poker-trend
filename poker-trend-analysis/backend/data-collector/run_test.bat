@echo off
echo ===============================================
echo  포커 트렌드 분석 시스템 테스트
echo ===============================================
echo.

REM Python 버전 확인
python --version
echo.

REM 필요한 패키지 설치
echo 필요한 패키지를 설치합니다...
pip install -r requirements.txt
echo.

REM 테스트 스크립트 실행
echo 테스트를 시작합니다...
cd scripts
python test_integrated_analyzer.py

echo.
echo 테스트가 완료되었습니다.
pause