# 특정 키워드 포커 트렌드 분석기 구현 가이드

## 🎯 구현 개요

사용자 요청에 따라 다음 키워드에 대한 YouTube 비디오 분석 시스템을 구현했습니다:
- **Holdem, WSOP, Cashgame, PokerStars, GGPoker, GTO, WPT**

각 키워드당 상위 50개 비디오를 수집하여 제목과 설명을 추출하고, Gemini AI로 트렌드를 추론합니다.

## 📁 구현 파일 구조

```
poker-trend/
├── specific_keyword_trend_analyzer.py  # 🎯 메인 분석기 (핵심)
├── setup_and_run.py                   # 🚀 설정 및 실행 도우미
├── requirements.txt                   # 📦 필수 라이브러리 목록
├── .env.example                       # 🔑 API 키 설정 템플릿
└── IMPLEMENTATION_GUIDE.md            # 📖 이 구현 가이드
```

## 🔧 핵심 구현 기능

### 1. 키워드별 비디오 수집 (YouTube Data API v3)
```python
# 각 키워드에 대해 확장된 검색 쿼리 사용
keyword_queries = {
    "Holdem": ["Texas Holdem", "Hold'em poker", "Holdem strategy"],
    "WSOP": ["World Series of Poker", "WSOP 2024", "WSOP bracelet"],
    "Cashgame": ["Cash game poker", "Live cash game", "Online cash"],
    "PokerStars": ["PokerStars tournament", "PokerStars live", "PS poker"],
    "GGPoker": ["GG Poker online", "GGPoker tournament", "GG network"],
    "GTO": ["GTO poker", "Game theory optimal", "GTO solver"],
    "WPT": ["World Poker Tour", "WPT tournament", "WPT final table"]
}
```

### 2. 관련성 점수 계산 알고리즘
```python
def _calculate_relevance_score(self, text: str, keyword: str) -> float:
    # 기본 점수 + 포커 용어 보너스 + 제목 포함 보너스
    base_score = 0.5 if keyword_lower in text_lower else 0.0
    bonus_score = sum(0.05 for term in poker_terms if term in text_lower)
    title_bonus = 0.3 if keyword_lower in text_lower[:100] else 0.0
    return min(1.0, base_score + bonus_score + title_bonus)
```

### 3. Gemini AI 트렌드 분석
- 50개 비디오의 제목과 설명을 종합 분석
- 4계층 트렌드 프레임워크 적용 (Nano/Micro/Meso/Macro)
- JSON 형식으로 구조화된 결과 제공

### 4. 비동기 처리로 성능 최적화
```python
# 모든 키워드를 동시에 검색하여 처리 시간 단축
tasks = []
for keyword in self.target_keywords:
    task = self.collect_videos_for_keyword(keyword, 50)
    tasks.append(task)

results = await asyncio.gather(*tasks, return_exceptions=True)
```

## 🚀 실행 방법

### 방법 1: 자동 설정 및 실행 (권장)
```bash
# 모든 설정을 자동으로 처리
python setup_and_run.py
```

### 방법 2: 수동 설정 및 실행
```bash
# 1. 라이브러리 설치
pip install -r requirements.txt

# 2. 환경 변수 설정
cp .env.example .env
# .env 파일에서 API 키 설정

# 3. 분석기 실행
python specific_keyword_trend_analyzer.py
```

## 🔑 필수 API 키

### YouTube Data API v3
1. [Google Cloud Console](https://console.developers.google.com/) 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. YouTube Data API v3 활성화
4. API 키 생성

### Gemini AI API
1. [Google AI Studio](https://makersuite.google.com/app/apikey) 접속
2. API 키 생성

## 📊 분석 결과 구조

### 생성되는 파일들
- `poker_trend_analysis_YYYYMMDD_HHMMSS.json` - 상세 분석 결과
- `poker_trend_analyzer.log` - 실행 로그

### JSON 결과 구조
```json
{
  "metadata": {
    "analysis_time": "2025-01-30T...",
    "target_keywords": ["Holdem", "WSOP", ...],
    "total_videos_collected": 50
  },
  "videos": [
    {
      "video_id": "abc123",
      "title": "비디오 제목",
      "description": "비디오 설명...",
      "view_count": 12345,
      "like_count": 567,
      "keyword_matched": "WSOP",
      "relevance_score": 0.85,
      "url": "https://www.youtube.com/watch?v=abc123"
    }
  ],
  "gemini_analysis": {
    "trends": [
      {
        "trend_title": "트렌드 제목",
        "trend_description": "상세 설명",
        "confidence_score": 0.85,
        "trend_category": "emerging",
        "impact_level": "meso",
        "content_potential": "높음"
      }
    ],
    "keyword_insights": {
      "most_trending": "GTO",
      "emerging_themes": ["AI solver"],
      "declining_themes": ["live tournaments"]
    },
    "content_recommendations": [
      "GTO 솔버 사용법 가이드 제작",
      "WSOP 2024 하이라이트 편집"
    ]
  }
}
```

## 🎯 트렌드 분석 기준

### 4계층 프레임워크 적용
- **Nano**: 바이럴 순간, 밈 (수시간-수일)
- **Micro**: 전략/기술 토론 (가변적)
- **Meso**: 토너먼트/인물 뉴스 (수일-수주)  
- **Macro**: 산업 변화 (6-24개월)

### 트렌드 분류
- **emerging**: 새로 떠오르는 트렌드
- **stable**: 안정적으로 지속되는 트렌드
- **declining**: 줄어드는 트렌드

## 🔧 커스터마이징 옵션

### 키워드 변경
```python
# specific_keyword_trend_analyzer.py 파일에서 수정
self.target_keywords = [
    "새키워드1", "새키워드2", "새키워드3"
]
```

### 수집 비디오 수 조정
```python
# collect_all_videos() 메서드에서 수정
self.collected_videos = self.collected_videos[:원하는수]
```

### Gemini AI 프롬프트 수정
```python
# prepare_gemini_prompt() 메서드에서 프롬프트 내용 수정
```

## 🛠️ 문제 해결

### 일반적인 오류

1. **API 키 오류**
   ```
   ❌ YouTube API 키가 설정되지 않았습니다.
   ```
   → `.env` 파일에서 API 키 확인

2. **API 할당량 초과**
   ```
   HttpError 403: quotaExceeded
   ```
   → 다음 날까지 대기 또는 다른 API 키 사용

3. **Gemini AI 분석 오류**
   → 폴백 메커니즘으로 기본 분석 결과 제공

### 로그 확인
```bash
tail -f poker_trend_analyzer.log
```

## 📈 성능 최적화

### 비동기 처리
- 모든 키워드 검색을 동시에 실행
- API 호출 간 적절한 지연 시간 적용

### 중복 제거
- video_id 기준으로 중복 비디오 자동 제거
- 관련성 점수 기준으로 상위 50개 선택

### 캐싱 (향후 구현 예정)
- Redis 또는 파일 기반 캐싱
- API 응답 결과 임시 저장

## 🔄 향후 확장 계획

1. **실시간 모니터링**: 스케줄러를 통한 자동 실행
2. **웹 대시보드**: FastAPI 기반 결과 시각화
3. **다국어 지원**: 한국어 포커 콘텐츠 분석
4. **소셜 미디어 확장**: Twitter, Reddit 데이터 추가
5. **AI 모델 개선**: 포커 특화 NLP 모델 구축

## 💡 사용 팁

1. **처음 실행**: `setup_and_run.py` 사용으로 설정 자동화
2. **정기 실행**: cron job 또는 Task Scheduler 활용
3. **결과 활용**: JSON 결과를 다른 도구로 가져와서 추가 분석
4. **키워드 최적화**: 수집 결과를 보고 키워드 조정
5. **콘텐츠 제작**: 분석 결과의 content_recommendations 활용

이 구현으로 사용자의 요구사항인 "특정 키워드 기반 YouTube 상위 50개 비디오 수집 → 제목/설명 추출 → Gemini AI 트렌드 분석"을 완전히 충족합니다.