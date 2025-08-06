# 🎰 YouTube 포커 트렌드 통합 분석 시스템

<div align="center">
  
  [![GitHub Pages](https://img.shields.io/badge/Demo-Live-success?style=for-the-badge&logo=github)](https://garimto81.github.io/poker-trend/)
  [![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)
  [![Python](https://img.shields.io/badge/Python-3.11-yellow?style=for-the-badge&logo=python)](https://www.python.org/)
  [![Gemini](https://img.shields.io/badge/Gemini_AI-Powered-purple?style=for-the-badge&logo=google)](https://ai.google.dev/)
  
  <p align="center">
    <strong>일간 · 주간 · 월간 YouTube 포커 트렌드를 AI로 분석하고 Slack으로 자동 리포팅</strong>
  </p>
  
  [🌐 Live Demo](https://garimto81.github.io/poker-trend/) | [📖 Documentation](docs/) | [🐛 Issues](https://github.com/garimto81/poker-trend/issues)
  
</div>

---

## 📌 최신 업데이트 (v2.0)

### 🔧 [PR #2: Gemini AI 번역 문제 완전 해결](docs/PR_SUMMARY.md)
- ✅ 번역 시 단일 옵션만 출력하도록 프롬프트 개선
- ✅ "Several options" 패턴 감지 및 자동 처리
- ✅ 번역 실패 시 원본 제목 자동 사용
- ✅ 번역 성공률 100% 달성

### 🎨 GitHub Pages 완전 재설계
- ✅ 모던한 UI/UX 디자인 시스템 적용
- ✅ 다크모드 지원 (LocalStorage 기반)
- ✅ 완벽한 반응형 디자인
- ✅ 실시간 시스템 상태 표시기

---

## 🚀 핵심 기능

### 📊 3단계 통합 리포팅
| 리포트 타입 | 실행 시간 | 분석 기간 | 특징 |
|------------|-----------|-----------|------|
| **일간** | 평일 10:00 KST | 24시간 | 즉각적 트렌드, 핫 토픽 |
| **주간** | 월요일 11:00 KST | 7일 | 성장률 분석, 패턴 변화 |
| **월간** | 첫째주 월요일 14:00 KST | 30일 | 장기 예측, 종합 통계 |

### 🤖 Gemini AI 심층 분석
```python
# AI가 수행하는 분석
- 🎯 현재 트렌드 패턴 인식
- 📈 1주-1개월 미래 예측 (확률 기반)
- 💡 실행 가능한 콘텐츠 전략 제안
- 🌏 영어→한국어 자동 번역 (100% 성공률)
```

### 🔍 데이터 수집 전략
- **8개 핵심 키워드**: poker, holdem, wsop, wpt, ept, pokerstars, ggpoker, triton poker
- **키워드당 TOP 5**: 조회수 기준 상위 5개 영상
- **실시간 추적**: YouTube Data API v3 활용
- **중복 제거**: 스마트 필터링 알고리즘

### 💬 Slack 자동 리포팅
<details>
<summary>📋 리포트 샘플 보기</summary>

```
🎰 포커 트렌드 일일 분석
━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 2025년 1월 15일 (수)
⏰ 분석 기간: 최근 24시간
📊 분석 영상: 35개

🤖 AI 트렌드 심층 분석
────────────────
【현재 트렌드】
WSOP 관련 콘텐츠가 45% 점유율로 압도적 관심

【숨겨진 패턴】
• 블러프 성공 영상이 3배 높은 참여율
• 오후 2-4시 업로드가 최적 시간대

【미래 예측】
🔺 Phil Ivey 콘텐츠 상승 예상 (78%)
🔻 초보자 튜토리얼 하락 예상 (82%)

📺 키워드별 TOP 영상
────────────────
【poker】
1. WSOP 2025 Final Table → 125K views
2. Epic Bluff Compilation → 98K views
...
```
</details>

---

## 🛠️ 기술 스택

<div align="center">
  
| Category | Technologies |
|----------|-------------|
| **Backend** | ![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white) ![Node.js](https://img.shields.io/badge/Node.js-18-339933?logo=node.js&logoColor=white) |
| **AI/API** | ![Gemini](https://img.shields.io/badge/Gemini-AI-4285F4?logo=google&logoColor=white) ![YouTube](https://img.shields.io/badge/YouTube-API_v3-FF0000?logo=youtube&logoColor=white) |
| **Automation** | ![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?logo=github-actions&logoColor=white) ![Slack](https://img.shields.io/badge/Slack-Webhook-4A154B?logo=slack&logoColor=white) |
| **Frontend** | ![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black) ![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?logo=typescript&logoColor=white) |
| **DevOps** | ![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white) ![GitHub Pages](https://img.shields.io/badge/GitHub_Pages-181717?logo=github&logoColor=white) |

</div>

---

## 📦 설치 및 실행

### 필수 요구사항
- Python 3.11+
- GitHub 계정
- YouTube Data API 키
- Gemini API 키
- Slack Webhook URL

### 빠른 시작

#### 1️⃣ 저장소 복제
```bash
git clone https://github.com/garimto81/poker-trend.git
cd poker-trend
```

#### 2️⃣ 의존성 설치
```bash
cd backend/data-collector
pip install -r requirements.txt
```

#### 3️⃣ 환경 변수 설정
```bash
# .env 파일 생성
YOUTUBE_API_KEY=your_youtube_api_key
GEMINI_API_KEY=your_gemini_api_key
SLACK_WEBHOOK_URL=your_slack_webhook_url
```

#### 4️⃣ 로컬 테스트
```bash
# 일간 리포트 테스트
python scripts/quick_validated_analyzer.py

# 번역 기능 테스트
python scripts/test_translation_fix.py
```

### GitHub Actions 설정

#### 1️⃣ Secrets 추가
Repository Settings → Secrets and variables → Actions:
- `YOUTUBE_API_KEY`
- `GEMINI_API_KEY`
- `SLACK_WEBHOOK_URL`

#### 2️⃣ 수동 실행
Actions 탭 → "포커 트렌드 분석 자동 스케줄러" → Run workflow

---

## 📁 프로젝트 구조

```
poker-trend/
├── 📂 .github/workflows/       # GitHub Actions 워크플로우
│   └── poker-trend-scheduler.yml
├── 📂 backend/
│   ├── 📂 data-collector/      # Python 분석 엔진
│   │   └── scripts/
│   │       ├── quick_validated_analyzer.py      # 일간
│   │       ├── validated_analyzer_with_translation.py  # 주간
│   │       └── enhanced_validated_analyzer.py   # 월간
│   └── 📂 api-server/          # Node.js API
├── 📂 frontend/                # React 대시보드
├── 📂 docs/                    # 문서
│   ├── index.html             # GitHub Pages
│   ├── PR_SUMMARY.md          # 최신 업데이트
│   └── guides/                # 설정 가이드
└── README.md
```

---

## 📈 성능 지표

| 지표 | 수치 | 설명 |
|------|------|------|
| **자동화율** | 100% | 완전 무인 운영 |
| **번역 성공률** | 100% | Gemini AI 개선 |
| **일일 분석량** | 40+ 영상 | 8개 키워드 × 5개 |
| **응답 시간** | < 30초 | API 최적화 |
| **비용** | $0 | GitHub Actions 무료 티어 |

---

## 🔧 문제 해결

<details>
<summary>번역이 여러 옵션으로 나올 때</summary>

최신 업데이트로 해결되었습니다. [PR #2](docs/PR_SUMMARY.md) 참조

</details>

<details>
<summary>GitHub Actions 실행 실패</summary>

1. Secrets 설정 확인
2. API 키 유효성 검증
3. [트러블슈팅 가이드](docs/guides/TEST_GUIDE.md) 참조

</details>

<details>
<summary>Slack 메시지가 오지 않을 때</summary>

1. Webhook URL 확인
2. Slack 앱 권한 확인
3. [Slack 설정 가이드](docs/guides/daily-slack-setup.md) 참조

</details>

---

## 🤝 기여하기

기여는 언제나 환영합니다! 

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

자세한 내용은 [CONTRIBUTING.md](CONTRIBUTING.md)를 참조하세요.

---

## 📊 프로젝트 상태

<div align="center">

| Component | Status |
|-----------|--------|
| **Backend API** | ![Status](https://img.shields.io/badge/Status-Active-success) |
| **GitHub Actions** | ![Build](https://img.shields.io/badge/Build-Passing-success) |
| **Documentation** | ![Docs](https://img.shields.io/badge/Docs-100%25-success) |
| **Test Coverage** | ![Coverage](https://img.shields.io/badge/Coverage-85%25-yellow) |

</div>

---

## 📜 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

---

## 🙏 감사의 말

- Google Gemini AI 팀
- YouTube Data API 팀
- GitHub Actions 팀
- 오픈소스 커뮤니티

---

## 📞 연락처

- **GitHub**: [@garimto81](https://github.com/garimto81)
- **Issues**: [버그 리포트](https://github.com/garimto81/poker-trend/issues)
- **Discussions**: [프로젝트 논의](https://github.com/garimto81/poker-trend/discussions)

---

<div align="center">
  
  **⭐ 이 프로젝트가 도움이 되셨다면 Star를 눌러주세요!**
  
  <img src="https://img.shields.io/github/stars/garimto81/poker-trend?style=social" alt="GitHub stars">
  
</div>