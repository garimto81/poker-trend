# 🎲 온라인 포커 플랫폼 트렌드 분석 시스템

## 📌 개요

`poker-online-analyze` 프로젝트에서 수집한 Firebase 데이터를 활용하여 온라인 포커 플랫폼의 트렌드를 분석하는 독립적인 시스템입니다.

### 🎯 주요 기능

- **실시간 트래픽 분석**: 59개 온라인 포커 사이트의 플레이어 트래픽 분석
- **트렌드 감지**: 성장/하락 플랫폼 자동 식별
- **시장 점유율 분석**: 플랫폼별 시장 점유율 변화 추적
- **AI 인사이트**: Gemini AI를 활용한 심층 분석
- **자동 리포팅**: Slack으로 일간/주간/월간 리포트 전송

## 🏗️ 시스템 구조

```
platform-analyzer/
├── scripts/
│   ├── online_platform_trend_analyzer.py    # 메인 분석기
│   ├── weekly_platform_analysis.py          # 주간 심층 분석
│   └── monthly_platform_report.py           # 월간 종합 리포트
├── reports/                                 # 분석 결과 저장
├── requirements.txt                         # Python 의존성
└── README.md                                # 문서
```

## 📊 데이터 소스

- **Firebase Firestore**: `poker-online-analyze` 프로젝트의 실시간 데이터
  - `sites` 컬렉션: 플랫폼 정보
  - `daily_stats` 서브컬렉션: 일일 통계
- **PokerScout.com**: 원본 데이터 출처 (간접)

## 🔄 분석 프로세스

### 1. 데이터 수집
```python
# Firebase에서 최근 7일간 데이터 수집
platform_data = fetch_platform_data()
```

### 2. 트렌드 분석
- **성장률 계산**: 7일간 플레이어 수 변화율
- **변동성 분석**: 일일 변화 패턴
- **피크 시간 감지**: 최대 동시 접속자 시간

### 3. 시장 분석
- **시장 점유율**: 전체 시장 대비 각 플랫폼 비중
- **순위 변동**: 플랫폼별 순위 변화
- **카테고리별 분석**: 네트워크/지역별 그룹화

### 4. AI 인사이트
```python
# Gemini AI로 패턴 분석 및 예측
ai_insights = generate_ai_insights(trends, market_share)
```

### 5. 리포팅
- **Slack 알림**: 자동 포맷팅된 리포트
- **JSON 저장**: 상세 분석 데이터 보관
- **Firebase 백업**: 클라우드 저장 (선택)

## 🚀 설치 및 실행

### 환경 설정

1. **Python 환경 준비**
```bash
cd backend/platform-analyzer
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **환경 변수 설정**
```bash
# .env 파일 생성
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY=your-private-key
FIREBASE_CLIENT_EMAIL=your-client-email
GEMINI_API_KEY=your-gemini-key
SLACK_WEBHOOK_URL=your-slack-webhook
```

3. **Firebase 서비스 계정 키**
- Firebase Console > 프로젝트 설정 > 서비스 계정
- 새 비공개 키 생성 → `firebase-key.json`으로 저장

### 실행 방법

#### 일간 분석
```bash
python scripts/online_platform_trend_analyzer.py
```

#### 주간 분석
```bash
python scripts/weekly_platform_analysis.py
```

#### 월간 분석
```bash
python scripts/monthly_platform_report.py
```

## ⏰ 자동화 스케줄

GitHub Actions를 통한 자동 실행:

| 분석 타입 | 실행 시간 (KST) | 주기 | 워크플로우 |
|----------|----------------|------|-----------|
| **일간** | 매일 10:30 | 매일 | `platform-trend-analyzer.yml` |
| **주간** | 월요일 11:30 | 매주 | 동일 워크플로우 |
| **월간** | 1일 15:00 | 매월 | 동일 워크플로우 |

## 📈 분석 지표

### 트렌드 지표
- **성장률**: `(현재 - 7일전) / 7일전 * 100`
- **변동성**: 일일 변화율의 표준편차
- **안정성**: 변동성의 역수

### 트렌드 분류
| 분류 | 기준 | 아이콘 |
|------|------|--------|
| 급성장 | +20% 이상 | 🚀 |
| 성장 | +10% ~ +20% | 📈 |
| 안정 | -5% ~ +5% | ➡️ |
| 하락 | -10% ~ -5% | 📉 |
| 급락 | -20% 이하 | ⚠️ |

## 📊 리포트 형식

### Slack 리포트 예시
```
🎰 온라인 포커 플랫폼 트렌드 분석
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 분석 기간: 최근 7일
📊 총 활성 플레이어: 125,340명

🏆 TOP 10 플랫폼 현황
1. GGNetwork 🔺
   현재: 45,230명 | 점유율: 36.1% | 성장률: +15.3%
   
2. PokerStars ➖
   현재: 38,120명 | 점유율: 30.4% | 성장률: +2.1%

🔥 주목할 변화
• 🚀 Natural8이 23.5% 급성장!
• ⚠️ PartyPoker가 18.2% 급락!

🤖 AI 트렌드 분석
현재 아시아 중심 플랫폼들이 강세를 보이고 있으며...
```

## 🔧 커스터마이징

### 새로운 분석 추가

1. **새 분석 스크립트 생성**
```python
# scripts/custom_analysis.py
from online_platform_trend_analyzer import OnlinePlatformTrendAnalyzer

class CustomAnalyzer(OnlinePlatformTrendAnalyzer):
    def custom_analysis(self):
        # 커스텀 분석 로직
        pass
```

2. **워크플로우에 추가**
```yaml
# .github/workflows/platform-trend-analyzer.yml
- name: 커스텀 분석 실행
  run: python scripts/custom_analysis.py
```

### 분석 파라미터 조정

```python
# 분석 기간 변경
analyzer = OnlinePlatformTrendAnalyzer()
analyzer.analysis_period_days = 14  # 14일 분석

# 상위 플랫폼 수 조정
analyzer.top_platforms_count = 20  # TOP 20 분석
```

## 🔐 보안 고려사항

- Firebase 서비스 계정 키는 절대 커밋하지 않음
- GitHub Secrets에 민감한 정보 저장
- Slack Webhook URL 노출 방지
- API 키 정기적 로테이션

## 📝 로그 및 디버깅

### 로그 레벨 설정
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 에러 처리
- 모든 Firebase 연결 오류는 자동 재시도
- API 실패 시 fallback 메커니즘 작동
- 에러 발생 시 Slack으로 알림

## 🤝 연관 프로젝트

- **데이터 수집**: [poker-online-analyze](https://github.com/garimto81/poker-online-analyze)
- **YouTube 분석**: 기존 poker-trend 시스템
- **대시보드**: https://garimto81.github.io/poker-online-analyze

## 📞 문의 및 지원

- **이슈**: GitHub Issues 활용
- **개선 제안**: Pull Request 환영
- **문서**: 지속적 업데이트 중

---

최종 업데이트: 2025-08-07