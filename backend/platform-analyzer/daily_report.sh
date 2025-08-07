#!/bin/bash

echo "================================================================================"
echo "포커 플랫폼 일일 분석 리포트 프로세스"
echo "================================================================================"
echo "실행 시간: $(date '+%Y-%m-%d %H:%M:%S')"
echo

# 스크립트 위치로 이동
cd "$(dirname "$0")"

# Python 가상환경 확인
if [ ! -d "venv" ]; then
    echo "[ERROR] Python 가상환경이 없습니다. 설치를 먼저 진행하세요."
    exit 1
fi

source venv/bin/activate

echo "[STEP 1] Firebase 데이터 수집 및 동기화..."
echo "--------------------------------------------------------------------------------"
python scripts/firebase_data_fetcher.py
if [ $? -ne 0 ]; then
    echo "[ERROR] Firebase 데이터 수집 실패"
    exit 1
fi
echo

echo "[STEP 2] 일일 비교 분석 실행..."
echo "--------------------------------------------------------------------------------"
python scripts/show_daily_comparison.py
if [ $? -ne 0 ]; then
    echo "[ERROR] 일일 비교 분석 실패"
    exit 1
fi
echo

echo "[STEP 3] 경쟁 구도 분석..."
echo "--------------------------------------------------------------------------------"
python scripts/competitive_analysis_reporter.py
if [ $? -ne 0 ]; then
    echo "[ERROR] 경쟁 구도 분석 실패"
    exit 1
fi
echo

echo "[STEP 4] Slack 통합 리포트 전송..."
echo "--------------------------------------------------------------------------------"
python scripts/final_slack_reporter.py
if [ $? -ne 0 ]; then
    echo "[ERROR] Slack 리포트 전송 실패"
    exit 1
fi
echo

echo "================================================================================"
echo "✅ 일일 포커 플랫폼 분석 보고서 완료!"
echo "================================================================================"
echo "완료 시간: $(date '+%Y-%m-%d %H:%M:%S')"
echo

echo "📊 생성된 파일들:"
ls -la *.db 2>/dev/null
ls -la scripts/*_$(date '+%Y%m%d')*.json 2>/dev/null
echo

echo "Press any key to continue..."
read -n 1