#!/bin/bash

echo "==============================================="
echo " 포커 트렌드 분석 시스템 테스트"
echo "==============================================="
echo

# Python 버전 확인
echo "Python 버전:"
python3 --version
echo

# 가상환경 활성화 (있는 경우)
if [ -d "venv" ]; then
    echo "가상환경을 활성화합니다..."
    source venv/bin/activate
fi

# 필요한 패키지 설치
echo "필요한 패키지를 설치합니다..."
pip install -r requirements.txt
echo

# 테스트 스크립트 실행
echo "테스트를 시작합니다..."
cd scripts
python3 test_integrated_analyzer.py

echo
echo "테스트가 완료되었습니다."