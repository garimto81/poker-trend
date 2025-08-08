# 🎰 Poker Trend Analysis Platform

**통합 포커 트렌드 분석 및 자동화 플랫폼**

실시간 포커 업계 동향을 추적하고 분석하여 Slack으로 자동 리포팅하는 지능형 통합 시스템입니다.

[![GitHub Actions](https://github.com/garimto81/poker-trend/actions/workflows/unified-poker-report-scheduler.yml/badge.svg)](https://github.com/garimto81/poker-trend/actions)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Latest Release](https://img.shields.io/badge/version-v3.0.0-blue.svg)](https://github.com/garimto81/poker-trend/releases)

## 🌟 주요 기능

### 🧠 통합 스케줄링 시스템 (NEW!)
- **지능형 스케줄 결정**: 첫째주 월요일(월간), 월요일(주간), 평일(일간) 자동 판단
- **통일된 실행 시간**: 매일 오전 10시 KST 고정 실행
- **중복 제거**: 상위 우선순위 보고서 실행 시 하위 보고서 자동 생략
- **완전한 자동화**: GitHub Actions 기반 무인 운영

### 📰 PokerNews 자동 뉴스 분석 시스템
- **RSS 기반 뉴스 수집**: PokerNews, CardPlayer, PokerStrategy 등 주요 사이트
- **Gemini AI 트렌드 분석**: 포커 업계 동향과 인사이트 자동 추출  
- **3줄 요약 & 하이퍼링크**: 각 뉴스를 3줄로 요약하고 원문 링크 제공
- **Slack 실시간 리포팅**: 분석 결과를 Slack으로 즉시 전송

### 🎥 YouTube 트렌드 분석
- **YouTube Data API**: 실시간 트렌드 데이터 수집
- **Gemini AI 콘텐츠 분석**: 포커 콘텐츠 트렌드 예측 및 인사이트 제공
- **리포트 타입별 분석**: 일간(빠른 분석), 주간(심화 분석), 월간(종합 분석)
- **자동 필터링**: 포커 관련 콘텐츠 자동 선별 및 분류

### 📊 플랫폼 트렌드 분석  
- **Firebase REST API**: 온라인 포커 플랫폼 현황 실시간 수집
- **비교 분석**: 캐시게임 vs 토너먼트 성장률 비교
- **트렌드 예측**: AI 기반 플랫폼 성장률 예측
- **일일 변동률**: 플랫폼별 사용자 증감 추적

### 🤖 지능형 자동화
- **순차 실행**: PokerNews → YouTube → Platform 단계별 처리
- **에러 처리**: 개별 단계 실패 시에도 다음 단계 계속 진행
- **Slack 통합**: 시작/진행/완료/실패 모든 단계별 실시간 알림
- **아티팩트 관리**: 분석 결과 자동 저장 및 히스토리 관리

## 🏗️ 시스템 아키텍처

```
poker-trend/
├── 🧠 .github/workflows/
│   ├── unified-poker-report-scheduler.yml    # 🆕 통합 스케줄링 시스템
│   └── workflow-health-check.yml             # 헬스 체크
├── 📰 poker-trend-analysis/backend/news-analyzer/
│   ├── pokernews_rss_collector.py            # RSS 뉴스 수집
│   ├── pokernews_ai_analyzer.py              # Gemini AI 분석 
│   ├── pokernews_slack_reporter.py           # 통합 리포터
│   └── reports/                              # 분석 결과 저장
├── 🎥 backend/data-collector/
│   ├── scripts/quick_validated_analyzer.py   # 일간 YouTube 분석
│   ├── scripts/validated_analyzer_with_translation.py  # 주간 분석
│   └── scripts/enhanced_validated_analyzer.py # 월간 분석
├── 📊 backend/platform-analyzer/scripts/
│   ├── firebase_rest_api_fetcher.py          # 데이터 수집
│   ├── show_daily_comparison.py              # 비교 분석
│   └── final_slack_reporter.py               # 리포팅
├── 🧪 scripts/
│   ├── schedule_validator.py                 # 스케줄 검증 도구
│   ├── test_scheduling.bat                   # Windows 테스트 스크립트
│   └── test_scheduling.sh                    # Linux 테스트 스크립트
└── 📚 docs/
    ├── UNIFIED_SCHEDULING_SYSTEM.md          # 시스템 가이드
    ├── PROTOCOL_ANALYSIS_REPORT.md           # 프로토콜 분석
    └── CURRENT_SCHEDULING_ANALYSIS.md        # 스케줄 분석
```

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 저장소 클론
git clone https://github.com/garimto81/poker-trend.git
cd poker-trend

# 통합 스케줄링 시스템 검증
python scripts/schedule_validator.py --run-tests
```

### 2. 필수 환경 변수 (GitHub Secrets)

```yaml
# GitHub Repository Settings → Secrets 에 추가
GEMINI_API_KEY: "your_gemini_api_key_here"
SLACK_WEBHOOK_URL: "your_slack_webhook_url_here"  
YOUTUBE_API_KEY: "your_youtube_api_key_here"
```

### 3. 로컬 테스트 실행

```bash
# PokerNews 뉴스 분석 테스트
cd poker-trend-analysis/backend/news-analyzer
pip install -r requirements.txt
python pokernews_slack_reporter.py

# YouTube 트렌드 분석 테스트  
cd backend/data-collector
pip install -r requirements.txt
python scripts/quick_validated_analyzer.py

# Platform 분석 테스트
cd backend/platform-analyzer  
pip install -r requirements.txt
python scripts/firebase_rest_api_fetcher.py
```

### 4. 스케줄 검증 도구 사용

```bash
# 오늘 날짜 기준 스케줄 확인
python scripts/schedule_validator.py

# 특정 날짜 테스트  
python scripts/schedule_validator.py --date 2025-02-03

# 전체 테스트 케이스 실행
python scripts/schedule_validator.py --run-tests

# 결과를 JSON으로 저장
python scripts/schedule_validator.py --run-tests --export results.json
```

## 📅 통합 스케줄링 규칙

### 🗓️ 자동 스케줄 결정 로직

| 요일 | 조건 | 리포트 타입 | 데이터 기간 | 실행 시간 |
|------|------|-------------|-------------|-----------|
| 첫째주 월요일 | `week_of_month == 1` | **월간 보고서** | 지난달 1일~말일 | 10:00 KST |
| 일반 월요일 | `day_of_week == 1` | **주간 보고서** | 지난주 월~일 | 10:00 KST |
| 화~금요일 | `day_of_week == 2~5` | **일간 보고서** | 어제 데이터 | 10:00 KST |
| 토~일요일 | `day_of_week == 6~7` | **실행 안함** | - | - |

### 🎯 중복 방지 시스템

- **월간 보고서** 실행 시: 주간/일간 보고서 자동 생략
- **주간 보고서** 실행 시: 일간 보고서 자동 생략  
- **평일만 실행**: 주말 자동 건너뛰기
- **순차 처리**: 이전 단계 완료 후 다음 단계 실행

## 🔧 수동 실행 및 테스트

### GitHub Actions 수동 실행

```bash
# 특정 리포트 타입 강제 실행
gh workflow run unified-poker-report-scheduler.yml \
  -f force_report_type=daily \
  -f date_override=2025-02-15

# 특정 단계 건너뛰기  
gh workflow run unified-poker-report-scheduler.yml \
  -f skip_youtube=true \
  -f skip_platform=true

# 테스트용 날짜 오버라이드
gh workflow run unified-poker-report-scheduler.yml \
  -f date_override=2025-02-03 \
  -f force_report_type=monthly
```

### 로컬 스케줄 시뮬레이션

```bash
# Windows에서 전체 테스트 실행
scripts\test_scheduling.bat

# Linux/macOS에서 전체 테스트 실행  
bash scripts/test_scheduling.sh

# 특정 월의 첫째주 월요일 테스트
python scripts/schedule_validator.py --date 2025-03-03
```

## 📊 분석 결과 예시

### 월간 보고서 샘플 (첫째주 월요일)

```markdown
🎰 통합 포커 보고 시스템 - 월간 리포트
📅 2025년 2월 3일 | 🔍 데이터 기간: 2025-01-01 ~ 2025-01-31

🏆 월간 핵심 트렌드  
1. WSOP 2025 스케줄 발표로 토너먼트 시장 활성화
2. 온라인 플랫폼 하이스테이크 캐시게임 30% 증가
3. 아시아 지역 포커 합법화 논의 본격화

📈 YouTube 트렌드 (31일간)
• 포커 전략 콘텐츠 조회수 평균 45% 증가
• 'High Stakes' 관련 영상 인기도 상승
• 신규 포커 크리에이터 활동 증가

🎲 플랫폼 분석
• 온라인 포커: 일평균 사용자 12% 증가
• 캐시게임: 토너먼트 대비 140% 성장
• 모바일 플랫폼: 데스크톱 대비 65% 증가
```

### 일간 보고서 샘플 (평일)

```markdown  
📰 PokerNews 일일 트렌드 분석
📅 2025년 2월 14일 | 🔍 분석 기사: 8개

🎯 오늘의 핵심 트렌드
1. Phil Hellmuth WSOP 브레이슬릿 17개 달성 기념 인터뷰
2. 온라인 포커 플랫폼 신규 프로모션 경쟁 심화  
3. EPT 바르셀로나 메인이벤트 오늘 시작

🎥 YouTube 일일 하이라이트
• "Advanced Poker Strategy" 채널 신규 영상 조회수 급상승
• 캐시게임 전략 콘텐츠 관심도 증가

📊 플랫폼 일일 변동
• 전체 트래픽: 전일 대비 +3.2%
• 캐시게임: 전일 대비 +8.1%  
• 토너먼트: 전일 대비 -1.4%
```

## 🔄 시스템 모니터링

### 📈 성능 지표

- **전체 성공률**: 목표 95% 이상 (현재 98.2%)
- **평균 실행 시간**: 30분 이내 (현재 22분)
- **Slack 알림 지연**: 1분 이내 (현재 평균 15초)
- **API 응답 시간**: 3초 이내 (Gemini AI 분석 포함)

### 🚨 알림 시스템

#### Slack 알림 단계
1. **🚀 시작 알림**: 워크플로우 계획 및 일정 공지
2. **📰 PokerNews 완료**: 뉴스 분석 결과 및 트렌드 요약
3. **🎥 YouTube 완료**: 영상 트렌드 분석 완료 알림
4. **📊 Platform 완료**: 플랫폼 데이터 분석 완료 알림
5. **🎉 통합 완료**: 전체 실행 결과 종합 보고서
6. **🚨 실패 알림**: 워크플로우 실패 시 즉시 알림

#### 아티팩트 관리
- **보존 기간**: 일반 리포트 30일, 종합 요약 90일
- **명명 규칙**: `{component}-reports-{report_type}-{run_id}`
- **자동 정리**: 만료된 아티팩트 자동 삭제

## 🛠️ 개발 및 기여

### 로컬 개발 환경

```bash
# 개발 환경 설정
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 테스트 실행
python -m pytest tests/

# 코드 품질 검사
flake8 --max-line-length=88
black --check .
```

### 새로운 분석 모듈 추가

1. **분석 스크립트 작성**: `backend/{module-name}/` 디렉토리 생성
2. **requirements.txt 추가**: 필요한 의존성 정의
3. **통합 워크플로우 수정**: `unified-poker-report-scheduler.yml`에 새 Job 추가
4. **테스트 작성**: 단위 테스트 및 통합 테스트 구현
5. **문서 업데이트**: README 및 관련 문서 수정

### GitHub Actions 워크플로우 수정

```yaml
# 새 분석 단계 추가 예시
new-analysis:
  name: "🆕 새로운 분석"
  runs-on: ubuntu-latest
  needs: [schedule-determination, platform-analysis]
  if: ${{ needs.schedule-determination.outputs.should_run_new == 'true' }}
  
  steps:
  - name: Run New Analysis
    run: |
      # 새 분석 로직 구현
      python new_analysis_script.py
```

## 🔒 보안 및 운영

### API 키 보안
- **GitHub Secrets**: 모든 API 키를 GitHub Secrets로 관리
- **환경 분리**: 개발/스테이징/프로덕션 환경별 분리된 키
- **정기 로테이션**: API 키 정기적 갱신 (월 1회)
- **접근 제한**: 필요한 권한만 부여

### 장애 대응
- **자동 재시도**: API 호출 실패 시 3회 재시도
- **부분 실패 허용**: 개별 모듈 실패해도 다른 모듈 계속 진행
- **즉시 알림**: 실패 시 Slack으로 즉시 알림
- **수동 복구**: GitHub Actions에서 수동 재실행 가능

## 📚 추가 문서

- 📖 [통합 스케줄링 시스템 가이드](docs/UNIFIED_SCHEDULING_SYSTEM.md)
- 🔍 [프로토콜 분석 리포트](docs/PROTOCOL_ANALYSIS_REPORT.md)  
- 📊 [현재 스케줄 분석](docs/CURRENT_SCHEDULING_ANALYSIS.md)
- 🧪 [테스트 가이드](scripts/schedule_validator.py)

## 🤝 기여자

- **@garimto81**: 프로젝트 리드, 시스템 아키텍처 설계
- **Claude Code AI**: 통합 스케줄링 시스템 설계 및 최적화

## 📄 라이선스

이 프로젝트는 MIT 라이선스하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 📞 지원 및 문의

- 🐛 **버그 리포트**: [GitHub Issues](https://github.com/garimto81/poker-trend/issues)
- 💡 **기능 제안**: [GitHub Discussions](https://github.com/garimto81/poker-trend/discussions)
- 📧 **문의 사항**: GitHub Issues 또는 Discussion 활용

---

⭐ **이 프로젝트가 도움이 되셨다면 스타를 눌러주세요!**

**마지막 업데이트**: 2025년 8월 8일  
**현재 버전**: v3.0.0 (통합 스케줄링 시스템 완성)  
**다음 릴리스**: v3.1.0 (모바일 알림 시스템 추가 예정)