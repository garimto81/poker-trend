# 🎰 순차적 포커 트렌드 분석 워크플로우 가이드

## 📋 개요

이 워크플로우는 매일 오전 10시 (KST)에 자동으로 실행되어 포커 관련 트렌드를 순차적으로 분석하고 Slack으로 결과를 전송합니다.

## 🔄 실행 순서

```
1. PokerNews 분석 → Slack 전송
           ↓ (성공 시)
2. YouTube 트렌드 분석 → Slack 전송  
           ↓ (성공 시)
3. 플랫폼 트렌드 분석 → Slack 전송
           ↓ (항상 실행)
4. 워크플로우 완료 보고서 → Slack 전송
```

## ⚙️ 설정 방법

### 1. GitHub Secrets 설정

Repository Settings → Secrets and variables → Actions에서 다음 시크릿을 추가하세요:

| Secret Name | 설명 | 예시 |
|------------|------|------|
| `SLACK_WEBHOOK_URL` | Slack Incoming Webhook URL | `https://hooks.slack.com/services/...` |
| `YOUTUBE_API_KEY` | YouTube Data API v3 키 | `AIza...` |
| `GEMINI_API_KEY` | Google Gemini API 키 | `AIza...` |

### 2. API 키 발급 방법

#### 🔴 YouTube API Key
1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 프로젝트 생성 또는 선택
3. "APIs & Services" → "Library" → "YouTube Data API v3" 활성화
4. "Credentials" → "Create Credentials" → "API Key"

#### 🔴 Gemini API Key  
1. [Google AI Studio](https://aistudio.google.com/) 접속
2. "Get API Key" 클릭
3. API 키 생성 및 복사

#### 🔴 Slack Webhook URL
1. Slack 워크스페이스에서 앱 생성
2. "Incoming Webhooks" 활성화
3. 채널 선택 후 Webhook URL 생성

### 3. 워크플로우 파일 확인

다음 파일들이 올바른 위치에 있는지 확인하세요:

```
.github/
├── workflows/
│   ├── integrated-daily-poker-report.yml  # 메인 워크플로우
│   └── workflow-health-check.yml          # 헬스체크 워크플로우
```

## 🎯 주요 특징

### ✅ 의존성 관리
- 각 단계는 이전 단계 성공 후에만 실행
- `needs` 키워드로 Job 간 의존성 설정
- 실패 시 다음 단계 자동 건너뛰기

### ✅ Slack 전송 확인
- 각 분석 단계에서 HTTP 200 응답 확인
- 성공/실패 상태를 다음 Job으로 전달
- Slack API rate limit 고려한 대기 시간

### ✅ 에러 처리
- 각 단계별 타임아웃 설정 (15-20분)
- 실패 시 상세 에러 로그 출력
- 아티팩트로 결과 파일 업로드

### ✅ 모니터링
- 실행 로그를 통한 상태 추적
- 완료 보고서로 전체 결과 요약
- 아티팩트 보관 (7-30일)

## 📊 실행 결과

### 성공적인 실행 시

```
✅ PokerNews Analysis (10:00 KST)
   → Slack 메시지 전송 성공
   
✅ YouTube Trend Analysis (10:02 KST)
   → Slack 메시지 전송 성공
   
✅ Platform Trend Analysis (10:15 KST)
   → Slack 메시지 전송 성공
   
✅ Workflow Completion (10:18 KST)
   → 최종 요약 보고서 전송
```

### 부분 실패 시

```
✅ PokerNews Analysis
❌ YouTube Trend Analysis (실패)
⏭️ Platform Trend Analysis (건너뜀)
⚠️ Workflow Completion (부분 성공 보고)
```

## 🔧 수동 실행

### GitHub Actions 탭에서
1. Actions 탭 이동
2. "Daily Poker Report - Sequential Workflow" 선택
3. "Run workflow" 클릭
4. 옵션 선택 (특정 단계 건너뛰기 가능)

### 옵션 설명
- `skip_news`: PokerNews 분석 건너뛰기
- `skip_youtube`: YouTube 트렌드 분석 건너뛰기  
- `skip_platform`: 플랫폼 트렌드 분석 건너뛰기

## 🧪 테스트 방법

### 1. 헬스체크 워크플로우 실행
```bash
# Actions 탭에서 "Workflow Health Check" 실행
# 또는 수동으로:
python scripts/validate-workflow-setup.py
```

### 2. 개별 스크립트 테스트
```bash
# PokerNews 분석 테스트
cd poker-trend-analysis/backend/news-analyzer
python pokernews_slack_reporter.py

# YouTube 분석 테스트  
cd backend/data-collector
python scripts/validated_analyzer_with_translation.py

# 플랫폼 분석 테스트
cd backend/platform-analyzer/scripts
python final_slack_reporter.py
```

## 🚨 문제 해결

### 일반적인 문제들

#### 1. API 키 오류
```
❌ 403 Forbidden / Invalid API Key
```
**해결방법**: GitHub Secrets에서 API 키 재확인 및 갱신

#### 2. Slack 전송 실패
```
❌ Failed to send to Slack: 404
```
**해결방법**: Slack Webhook URL 유효성 확인

#### 3. 스크립트 실행 실패
```
❌ ModuleNotFoundError
```
**해결방법**: requirements.txt 파일 확인 및 의존성 설치

#### 4. 타임아웃 발생
```
❌ Job cancelled due to timeout
```
**해결방법**: 워크플로우 timeout-minutes 값 증가

### 로그 확인 방법

1. **GitHub Actions 로그**
   - Actions 탭 → 실행된 워크플로우 클릭
   - 각 Job별 상세 로그 확인

2. **아티팩트 다운로드**
   - 워크플로우 실행 페이지에서 Artifacts 섹션
   - 리포트 파일 다운로드 및 분석

3. **Slack 메시지 확인**
   - 설정된 Slack 채널에서 메시지 수신 여부 확인

## 📈 모니터링 및 최적화

### 성능 지표
- **실행 시간**: 전체 워크플로우 15-25분
- **성공률**: 목표 95% 이상
- **Slack 전송률**: 목표 100%

### 최적화 팁
1. **병렬 처리**: 독립적인 작업은 병렬 실행 고려
2. **캐싱**: pip cache, API 응답 캐싱 활용
3. **리트라이**: 중요한 API 호출에 재시도 로직 추가

## 📅 유지보수 계획

### 주기적 점검 (월 1회)
- [ ] API 키 유효성 확인
- [ ] Slack 채널 및 Webhook 상태 점검
- [ ] 워크플로우 성공률 분석
- [ ] 의존성 패키지 업데이트 확인

### 개선 사항 
- [ ] 실패 시 자동 재시도 로직 추가
- [ ] 더 상세한 에러 분류 및 알림
- [ ] 성능 최적화 및 실행 시간 단축
- [ ] 추가 데이터 소스 통합

## 🔗 관련 문서

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Slack Webhook API](https://api.slack.com/messaging/webhooks)  
- [YouTube Data API v3](https://developers.google.com/youtube/v3)
- [Google Gemini API](https://ai.google.dev/docs)

## 📞 지원

문제가 발생하거나 개선사항이 있으면 다음을 통해 연락하세요:

- **GitHub Issues**: 버그 리포트 및 기능 요청
- **Actions 로그**: 실행 오류 디버깅
- **헬스체크**: 시스템 상태 정기 점검

---

**마지막 업데이트**: 2025-08-08  
**워크플로우 버전**: v1.0.0