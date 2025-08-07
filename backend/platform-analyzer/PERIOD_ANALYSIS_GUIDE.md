# 다기간 포커 시장 비교 분석 시스템

## 📊 시스템 개요

사용자 요구사항에 따라 구축된 포커 시장 비교 분석 시스템입니다:
- **일일 분석**: 전일과 오늘 비교
- **주간 분석**: 지난주와 이번주 비교  
- **월간 분석**: 지난달과 이번달 비교

## 🚀 빠른 시작

### 1. 전체 시스템 테스트
```bash
cd poker-trend/backend/platform-analyzer/scripts
python run_period_analysis.py
# 메뉴에서 7번 선택 → 모든 분석 실행
```

### 2. 개별 분석 실행
```bash
# 일일 분석
python daily_comparison_analyzer.py

# 주간 분석  
python weekly_comparison_analyzer.py

# 월간 분석
python monthly_comparison_analyzer.py
```

### 3. 보고서 생성
```bash
python report_generator.py
# Slack/Markdown/Plain Text 형식 지원
```

### 4. Slack 전송
```bash
# 환경변수 설정
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

python slack_report_sender.py
```

## 📁 시스템 구성

### 핵심 모듈

1. **multi_period_analyzer.py**
   - 기본 다기간 비교 분석 엔진
   - 데이터 조회, 통계 계산, 변화율 분석

2. **daily_comparison_analyzer.py**
   - 일일 비교 분석 (전일 vs 오늘)
   - 실시간 시장 변화 추적

3. **weekly_comparison_analyzer.py**
   - 주간 비교 분석 (지난주 vs 이번주)
   - 주간 트렌드 및 변동성 분석

4. **monthly_comparison_analyzer.py**
   - 월간 비교 분석 (지난달 vs 이번달)  
   - 장기 트렌드 및 전략적 인사이트

5. **report_generator.py**
   - 다양한 형식의 보고서 생성
   - Slack/Markdown/Plain Text 지원

6. **slack_report_sender.py**
   - Slack 워크스페이스 자동 보고서 전송
   - 채널별 맞춤 메시지 지원

### 지원 도구

- **run_period_analysis.py**: 통합 실행 스크립트
- **integrated_period_analysis_test.py**: 전체 시스템 테스트

## 📊 데이터 구조

### SQLite 데이터베이스 (poker_history.db)

#### daily_data 테이블
```sql
- date: 수집 날짜
- site_name: 포커 사이트명
- players_online: 온라인 플레이어 수
- cash_players: 캐시 게임 플레이어 수  
- peak_24h: 24시간 최고치
- seven_day_avg: 7일 평균
- data_quality: 데이터 품질 (normal/suspicious_history/firebase_import)
```

### 데이터 소스
- **로컬 수집**: PokerScout.com 실시간 크롤링
- **Firebase 통합**: poker-online-analyze 프로젝트 히스토리 데이터
- **데이터 검증**: 극단적 성장률 필터링 (>30,000% 방지)

## 📈 분석 기능

### 일일 분석
- 전일 vs 오늘 비교
- 총 플레이어 수 변화
- 시장 집중도 변화
- 상위 증가/감소 사이트

### 주간 분석
- 지난주 vs 이번주 비교
- 주간 성장률 계산
- 변동성 평가
- 주간 챔피언 및 주의 대상

### 월간 분석
- 지난달 vs 이번달 비교
- 월간 성과 평가
- 시장 성숙도 분석
- 계절적 효과 고려
- 경영진용 요약 보고서

## 🎯 주요 지표

### 성장률 계산
```python
change_pct = ((new_value - old_value) / old_value) * 100
```

### 시장 집중도
- 상위 3개 사이트의 총 점유율 비중

### 데이터 품질 분류
- `normal`: 정상 수집 데이터
- `firebase_import`: Firebase에서 가져온 히스토리 데이터
- `suspicious_history`: 검증 필요한 데이터

## 📋 보고서 형식

### Slack 형식
```
📅 *일일 포커 시장 분석 리포트*

*📊 기간:* 2025-08-06 vs 2025-08-07
*⏰ 분석 시간:* 2025-08-07 14:30

*🎯 핵심 지표*
• 총 플레이어: 150,000 → 160,000 (+6.7%)
• 평균 플레이어: 3,200 → 3,400 (+6.3%)
```

### Plain Text 형식
```
일일 포커 시장 분석 (2025-08-06 vs 2025-08-07)

주요 지표:
- 총 플레이어: +10,000명 (+6.7%)
- 평균 플레이어: +200명 (+6.3%)
```

## 🔧 환경 설정

### 필수 환경변수
```bash
# Slack 통합 (선택사항)
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

### 의존성 패키지
```bash
pip install sqlite3 requests datetime logging json
```

## 📅 자동화 설정

### Windows 작업 스케줄러
```batch
# 일일 분석 (매일 오전 9시)
schtasks /create /tn "DailyPokerAnalysis" /tr "python daily_comparison_analyzer.py" /sc daily /st 09:00

# 주간 분석 (월요일 오전 10시)  
schtasks /create /tn "WeeklyPokerAnalysis" /tr "python weekly_comparison_analyzer.py" /sc weekly /d MON /st 10:00

# 월간 분석 (매월 1일 오전 11시)
schtasks /create /tn "MonthlyPokerAnalysis" /tr "python monthly_comparison_analyzer.py" /sc monthly /d 1 /st 11:00
```

### Linux Cron
```bash
# 일일 분석 (매일 오전 9시)
0 9 * * * cd /path/to/scripts && python daily_comparison_analyzer.py

# 주간 분석 (월요일 오전 10시)
0 10 * * 1 cd /path/to/scripts && python weekly_comparison_analyzer.py  

# 월간 분석 (매월 1일 오전 11시)
0 11 1 * * cd /path/to/scripts && python monthly_comparison_analyzer.py
```

## 🧪 테스트 및 검증

### 통합 테스트
```bash
python integrated_period_analysis_test.py
```

**테스트 항목:**
1. 데이터베이스 상태 확인
2. 일일 분석 기능
3. 주간 분석 기능  
4. 월간 분석 기능
5. 보고서 생성
6. Slack 통합
7. 성능 벤치마크

### 성공 기준
- 모든 분석이 60초 이내 완료
- 데이터베이스에 100개 이상 레코드
- 10개 이상 사이트 추적
- 3일 이상 히스토리 데이터

## 🔍 문제 해결

### 데이터 부족
```bash
# Firebase 데이터 가져오기
python firebase_data_importer.py

# 일일 데이터 수집 실행
python daily_data_collector.py
```

### Slack 전송 실패
1. `SLACK_WEBHOOK_URL` 환경변수 확인
2. 네트워크 연결 상태 점검
3. Webhook URL 유효성 검증

### 성능 이슈
- 데이터베이스 인덱스 최적화
- 분석 대상 기간 조정
- 메모리 사용량 모니터링

## 📊 사용 예시

### 일일 시장 모니터링
```python
analyzer = DailyComparisonAnalyzer()
result = analyzer.run_daily_analysis()
insights = analyzer.get_trend_insights(result)

if insights['overall_trend'].find('성장') != -1:
    # 성장 시 알림 로직
    pass
```

### 주간 성과 리포트
```python
analyzer = WeeklyComparisonAnalyzer()
result = analyzer.run_weekly_analysis()
trends = analyzer.get_weekly_trends(result)

# 주간 성장률이 10% 이상이면 알림
changes = result['changes']
if changes['total_players']['change_pct'] > 10:
    # 고성장 알림
    pass
```

### 월간 전략 분석
```python
analyzer = MonthlyComparisonAnalyzer()
result = analyzer.run_monthly_analysis()
trends = analyzer.get_monthly_trends(result)

# 경영진 요약 보고서 생성
summary = analyzer.generate_monthly_executive_summary(result, trends)
```

## 💡 모범 사례

1. **정기적인 데이터 수집**: 매일 일정한 시간에 데이터 수집
2. **데이터 품질 모니터링**: 극단적 값이나 누락 데이터 주의
3. **히스토리 백업**: Firebase와 로컬 DB 이중화
4. **알림 설정**: 중요한 시장 변화 시 즉시 알림
5. **성능 최적화**: 분석 결과 캐싱 및 인덱스 활용

## 📞 지원

- **로그 파일**: 각 스크립트 실행 시 자동 생성
- **테스트 실행**: `python integrated_period_analysis_test.py`
- **데이터 확인**: `python data_integrity_test.py`

---

✅ **시스템 완성**: 전일/오늘, 지난주/이번주, 지난달/이번달 비교 분석 완료
🚀 **즉시 사용 가능**: `python run_period_analysis.py` 실행하여 전체 기능 확인