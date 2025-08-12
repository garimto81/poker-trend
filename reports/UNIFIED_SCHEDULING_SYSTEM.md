# 통합 포커 보고 스케줄링 시스템

## 📋 개요

기존의 3개 개별 워크플로우를 통합하여 중복 제거와 일관성 있는 보고 체계를 구축한 지능형 스케줄링 시스템입니다.

## 🎯 새로운 스케줄링 규칙

### 1. 통일된 실행 시간
- **매일 오전 10시 (KST)** 고정 실행
- UTC 01:00에 실행 (KST -9시간)
- 평일만 실행 (토요일, 일요일 제외)

### 2. 지능형 리포트 타입 결정
```
if (첫째주 월요일):
  → 월간 보고서 (주간/일간 생략)
elif (월요일):
  → 주간 보고서 (일간 생략)
elif (평일):
  → 일간 보고서
else:
  → 실행하지 않음 (주말)
```

### 3. 데이터 기간 설정
- **월간**: 지난달 1일 ~ 말일
- **주간**: 지난주 월요일 ~ 일요일  
- **일간**: 어제 (전일)

## 🚀 워크플로우 구조

### 메인 워크플로우: `unified-poker-report-scheduler.yml`

#### Job 1: Schedule Determination (스케줄 결정)
- 현재 날짜/요일 분석
- 리포트 타입 자동 결정
- 데이터 기간 계산
- 실행할 분석 단계 결정

#### Job 2: PokerNews Analysis (뉴스 분석)
- 리포트 타입별 적절한 분석 실행
- Slack 알림 전송
- 결과 아티팩트 저장

#### Job 3: YouTube Analysis (YouTube 트렌드)
- PokerNews 완료 후 순차 실행
- 리포트 타입별 분석 스크립트 선택
- Rate limit 고려 (3초 대기)

#### Job 4: Platform Analysis (플랫폼 분석)
- YouTube 완료 후 순차 실행
- Firebase REST API 데이터 수집
- Rate limit 고려 (5초 대기)

#### Job 5: Completion Report (완료 보고)
- 전체 실행 결과 요약
- 성공률 계산 및 Slack 알림
- 상세 실행 로그 저장

#### Job 6: Failure Notification (실패 알림)
- 워크플로우 실패 시 즉시 알림
- 단계별 상태 정보 포함

## 📊 기존 워크플로우 처리

### Deprecated (비활성화됨)
- `integrated-daily-poker-report.yml`
- `poker-trend-scheduler.yml`
- `platform-trend-analyzer.yml`

**변경 사항:**
- 자동 스케줄 비활성화 (cron 주석 처리)
- 수동 실행(`workflow_dispatch`)만 유지
- 백업/테스트 목적으로 보존

## 🛠️ 수동 실행 옵션

### 강력한 수동 제어
```yaml
workflow_dispatch:
  inputs:
    force_report_type: [daily/weekly/monthly]  # 타입 강제 설정
    date_override: "2024-01-15"                # 날짜 오버라이드 (테스트용)
    skip_pokernews: true/false                 # PokerNews 건너뛰기
    skip_youtube: true/false                   # YouTube 건너뛰기  
    skip_platform: true/false                  # Platform 건너뛰기
```

## 📅 스케줄 예시

### 월간 보고서
- **언제**: 매월 첫째주 월요일
- **예시**: 2024년 1월 1일(월) → 월간 보고서
- **데이터**: 2023년 12월 1일 ~ 31일

### 주간 보고서  
- **언제**: 매주 월요일 (첫째주 제외)
- **예시**: 2024년 1월 8일(월) → 주간 보고서
- **데이터**: 2024년 1월 1일(월) ~ 7일(일)

### 일간 보고서
- **언제**: 화~금요일 
- **예시**: 2024년 1월 9일(화) → 일간 보고서
- **데이터**: 2024년 1월 8일(월)

### 실행하지 않음
- **언제**: 토요일, 일요일
- **동작**: 워크플로우 조기 종료

## 🔧 리포트 타입별 분석 스크립트

### PokerNews
- **월간**: `pokernews_slack_reporter.py` (기본 스크립트, 환경변수로 기간 제어)
- **주간**: `pokernews_slack_reporter.py`
- **일간**: `pokernews_slack_reporter.py`

### YouTube
- **월간**: `enhanced_validated_analyzer.py`
- **주간**: `validated_analyzer_with_translation.py`  
- **일간**: `quick_validated_analyzer.py`

### Platform
- **모든 타입**: 
  1. `firebase_rest_api_fetcher.py`
  2. `show_daily_comparison.py`
  3. `final_slack_reporter.py`

## 🎛️ 환경 변수

### 필수 환경 변수
- `SLACK_WEBHOOK_URL`: Slack 알림 전송
- `GEMINI_API_KEY`: AI 분석 (PokerNews, YouTube)
- `YOUTUBE_API_KEY`: YouTube 데이터 수집

### 자동 설정 환경 변수
- `REPORT_TYPE`: daily/weekly/monthly
- `DATA_PERIOD_START`: 분석 시작 날짜
- `DATA_PERIOD_END`: 분석 종료 날짜

## 📈 모니터링 및 로깅

### Slack 알림 단계
1. **시작 알림**: 워크플로우 시작 시 계획 공지
2. **단계별 알림**: 각 분석 완료 시 개별 알림
3. **완료 보고서**: 전체 실행 결과 요약 알림
4. **실패 알림**: 워크플로우 실패 시 즉시 알림

### 아티팩트 저장
- **보존 기간**: 30일 (요약 보고서는 90일)
- **명명 규칙**: `{component}-reports-{report_type}-{run_id}`
- **포함 내용**: JSON 보고서, 로그 파일, 실행 요약

## 🧪 테스트 시나리오

### 날짜별 테스트 케이스

#### 1. 첫째주 월요일 (월간 보고서)
```bash
# 수동 테스트
date_override: "2024-02-05"  # 2024년 2월 첫째주 월요일
예상 결과: REPORT_TYPE=monthly, 데이터 기간=2024-01-01~2024-01-31
```

#### 2. 일반 월요일 (주간 보고서)
```bash
date_override: "2024-02-12"  # 2024년 2월 둘째주 월요일  
예상 결과: REPORT_TYPE=weekly, 데이터 기간=2024-02-05~2024-02-11
```

#### 3. 평일 (일간 보고서)
```bash
date_override: "2024-02-13"  # 2024년 2월 13일 화요일
예상 결과: REPORT_TYPE=daily, 데이터 기간=2024-02-12
```

#### 4. 주말 (실행 안함)
```bash
date_override: "2024-02-10"  # 2024년 2월 10일 토요일
예상 결과: 조기 종료, 모든 분석 단계 스킵
```

### 검증 명령어
```bash
# GitHub Actions에서 수동 실행으로 테스트
gh workflow run unified-poker-report-scheduler.yml \
  -f force_report_type=daily \
  -f date_override=2024-02-13 \
  -f skip_youtube=true
```

## 🔒 보안 및 안정성

### Rate Limiting
- PokerNews → YouTube: 3초 대기
- YouTube → Platform: 5초 대기
- Slack API 호출 간격 확보

### 에러 처리
- 각 단계별 독립적 실패 처리
- 하나 실패해도 다음 단계 계속 진행 가능
- 상세 에러 로그 및 Slack 알림

### Timeout 설정
- Schedule Determination: 5분
- PokerNews Analysis: 15분
- YouTube Analysis: 20분
- Platform Analysis: 15분
- Completion Report: 5분

## 🚀 마이그레이션 가이드

### 기존 시스템에서 전환
1. ✅ 통합 워크플로우 배포 완료
2. ✅ 기존 워크플로우 자동 스케줄 비활성화
3. ✅ 수동 실행 옵션 백업용 유지
4. ⏳ 운영 모니터링 (1주일)
5. ⏳ 필요시 기존 워크플로우 완전 제거

### 롤백 계획
1. 통합 워크플로우 비활성화
2. 기존 워크플로우 cron 스케줄 복원
3. Slack 알림 중복 방지 설정

## 📞 문제 해결

### 일반적인 문제
1. **첫째주 월요일 인식 오류**
   - 날짜 계산 로직 확인
   - `date_override` 옵션으로 테스트

2. **Slack 알림 누락**  
   - `SLACK_WEBHOOK_URL` 시크릿 확인
   - Rate limiting 간격 조정

3. **분석 스크립트 실패**
   - API 키 및 권한 확인
   - 의존성 설치 상태 점검

### 로그 확인 방법
```bash
# GitHub Actions 로그 직접 접근
https://github.com/{repository}/actions/runs/{run_id}

# CLI를 통한 로그 확인
gh run view {run_id} --log
```

## 📊 성능 지표

### 목표 지표
- **성공률**: 95% 이상
- **실행 시간**: 평균 30분 이내
- **알림 지연**: 실행 완료 후 1분 이내

### 모니터링 대시보드
- GitHub Actions 실행 히스토리
- Slack 알림 로그
- 아티팩트 저장 상태

---

## 📋 체크리스트

### 배포 완료 항목
- [x] 통합 워크플로우 생성
- [x] 지능형 스케줄 결정 로직
- [x] 기존 워크플로우 비활성화  
- [x] Slack 알림 시스템 통합
- [x] 아티팩트 관리 표준화
- [x] 에러 처리 및 실패 알림
- [x] 수동 실행 옵션
- [x] 문서화 완료

### 운영 준비 항목
- [ ] 실제 스케줄에서 테스트 실행
- [ ] 모니터링 대시보드 구축
- [ ] 알람 설정 검토
- [ ] 백업 시스템 검증

---

**마지막 업데이트**: 2025-08-08  
**버전**: 1.0.0  
**담당자**: Claude Code Assistant