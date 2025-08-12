# 🧪 포커 트렌드 분석 시스템 - 전체 테스트 가이드

## 📌 테스트 준비사항

### 1. 환경변수 확인
```bash
# .env 파일에 다음 키들이 설정되어 있는지 확인
YOUTUBE_API_KEY=your_key
GEMINI_API_KEY=your_key  
SLACK_WEBHOOK_URL=your_webhook
```

### 2. 의존성 설치 확인
```bash
# YouTube 분석 의존성
cd backend/data-collector
pip install -r requirements.txt

# Platform 분석 의존성
cd ../platform-analyzer
pip install -r requirements.txt

# PokerNews 의존성 (있는 경우)
cd ../news-analyzer
pip install -r requirements.txt
```

---

## 🚀 테스트 실행 순서

### **방법 1: GitHub Actions 웹 인터페이스 (권장)**

#### 1️⃣ **일간 리포트 테스트**
1. GitHub 저장소 → Actions 탭
2. `unified-poker-report-scheduler` 워크플로우 선택
3. `Run workflow` 클릭
4. 다음 옵션 설정:
   - **force_report_type**: `daily`
   - **skip_pokernews**: `false`
   - **skip_youtube**: `false`
   - **skip_platform**: `false`
   - **debug_mode**: `true`
5. `Run workflow` 버튼 클릭
6. 실행 로그 모니터링 (약 5-10분)

#### 2️⃣ **주간 리포트 테스트**
1. 일간 테스트 완료 후 5분 대기 (Slack rate limit)
2. 동일한 방법으로 워크플로우 실행
3. 옵션 설정:
   - **force_report_type**: `weekly`
   - 나머지 동일
4. 실행 및 모니터링 (약 10-15분)

#### 3️⃣ **월간 리포트 테스트**
1. 주간 테스트 완료 후 5분 대기
2. 동일한 방법으로 워크플로우 실행
3. 옵션 설정:
   - **force_report_type**: `monthly`
   - 나머지 동일
4. 실행 및 모니터링 (약 15-20분)

---

### **방법 2: 로컬 명령줄 테스트**

#### 🔹 일간 리포트 테스트
```bash
# 1. 환경변수 설정
export REPORT_TYPE=daily

# 2. PokerNews 분석 (선택적)
cd backend/news-analyzer
python pokernews_slack_reporter.py

# 3. YouTube 일간 분석
cd ../data-collector
python scripts/quick_validated_analyzer.py

# 4. Platform 일간 분석
cd ../platform-analyzer/scripts
python firebase_rest_api_fetcher.py
python show_daily_comparison.py
python final_slack_reporter.py

echo "✅ 일간 리포트 테스트 완료"
```

#### 🔹 주간 리포트 테스트
```bash
# 1. 환경변수 설정
export REPORT_TYPE=weekly

# 2. PokerNews 분석
cd backend/news-analyzer
python pokernews_slack_reporter.py

# 3. YouTube 주간 분석 (한글 번역 포함)
cd ../data-collector
python scripts/validated_analyzer_with_translation.py

# 4. Platform 주간 분석
cd ../platform-analyzer/scripts
python firebase_rest_api_fetcher.py
python multi_period_analyzer.py
python final_slack_reporter.py

echo "✅ 주간 리포트 테스트 완료"
```

#### 🔹 월간 리포트 테스트
```bash
# 1. 환경변수 설정
export REPORT_TYPE=monthly

# 2. PokerNews 분석
cd backend/news-analyzer
python pokernews_slack_reporter.py

# 3. YouTube 월간 분석 (강화된 AI 분석)
cd ../data-collector
python scripts/enhanced_validated_analyzer.py

# 4. Platform 월간 분석
cd ../platform-analyzer/scripts
python firebase_rest_api_fetcher.py
python monthly_platform_report.py
python competitive_analysis_reporter.py
python final_slack_reporter.py

echo "✅ 월간 리포트 테스트 완료"
```

---

## 📊 테스트 검증 체크리스트

### ✅ 각 테스트별 확인사항

#### **일간 리포트 검증**
- [ ] Slack에 3개 메시지 수신 (PokerNews, YouTube, Platform)
- [ ] YouTube TOP 5 영상 표시
- [ ] Platform 전일 대비 변화율 표시
- [ ] 실행 시간 10분 이내

#### **주간 리포트 검증**
- [ ] Slack에 3개 메시지 수신
- [ ] YouTube TOP 10 영상 + 한글 번역
- [ ] Platform 주간 성장률 그래프
- [ ] 캐시게임 vs 토너먼트 비교
- [ ] 실행 시간 15분 이내

#### **월간 리포트 검증**
- [ ] Slack에 3개 메시지 수신
- [ ] YouTube TOP 15-20 영상
- [ ] AI 생성 콘텐츠 아이디어
- [ ] Platform 월간 시장 점유율
- [ ] GGNetwork 독점 상황 분석
- [ ] 실행 시간 20분 이내

---

## 🔍 로그 확인 위치

### GitHub Actions
```
Actions 탭 → 워크플로우 실행 → 각 Job 클릭
- schedule-determination: 리포트 타입 결정
- pokernews-analysis: 뉴스 분석 로그
- youtube-analysis: YouTube 분석 로그
- platform-analysis: Platform 분석 로그
- completion-report: 최종 상태
```

### 로컬 실행
```bash
# YouTube 로그
backend/data-collector/scripts/reports/*.json
backend/data-collector/scripts/reports/*.txt

# Platform 로그
backend/platform-analyzer/scripts/*.json
backend/platform-analyzer/reports/*.txt
```

---

## ⚠️ 주의사항

1. **API 할당량**
   - YouTube API: 일일 10,000 유닛
   - Gemini API: 분당 60 요청
   - Slack: 분당 1 메시지

2. **테스트 간격**
   - 각 테스트 사이 5분 대기 권장
   - Slack rate limit 방지

3. **데이터 기간**
   - 일간: 어제 데이터
   - 주간: 지난 7일
   - 월간: 지난달 전체

---

## 📝 트러블슈팅

### 문제: YouTube 분석 실패
```bash
# import 오류 확인
cd backend/data-collector
python -c "from src.validators.poker_content_validator import PokerContentValidator"

# PYTHONPATH 설정
export PYTHONPATH=$PWD
```

### 문제: Platform 데이터 없음
```bash
# Firebase 연결 확인
cd backend/platform-analyzer/scripts
python firebase_rest_api_fetcher.py

# 캐시 데이터 사용
python test_firebase_preview.py
```

### 문제: Slack 메시지 미수신
```bash
# Webhook URL 테스트
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"테스트 메시지"}' \
  $SLACK_WEBHOOK_URL
```

---

## 🎯 예상 결과

### 성공적인 테스트 완료 시:
1. **Slack 채널에 총 9개 메시지**
   - 일간: 3개 (PokerNews, YouTube, Platform)
   - 주간: 3개
   - 월간: 3개

2. **각 메시지 포함 내용**
   - 리포트 타입 명시
   - 데이터 기간 표시
   - 분석 결과 요약
   - 상세 링크 (있는 경우)

3. **GitHub Actions 상태**
   - 모든 Job 녹색 체크
   - 완료 보고서에 정확한 상태 표시

---

## 📞 지원

문제 발생 시:
1. GitHub Actions 로그 확인
2. 로컬 테스트로 개별 스크립트 검증
3. 환경변수 및 API 키 재확인