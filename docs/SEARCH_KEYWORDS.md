# 🔍 YouTube 검색 키워드 설정

## 📌 검색 키워드 목록

### 지정된 검색 키워드 (8개)
```
poker
holdem
wsop
wpt
ept
pokerstars
ggpoker
triton poker
```

## ⚙️ 검색 설정

### 언어 설정
- **검색 언어**: 영어 전용 (English Only)
- 한글 키워드 사용 안함

### 검색 지역
- **검색 범위**: Global (전 세계)
- 특정 국가/지역 제한 없음

### 검색 기간
- **기본 설정**: 최근 48시간 이내 업로드된 영상
- **리포트 타입별**:
  - 일간 리포트: 48시간
  - 주간 리포트: 7일
  - 월간 리포트: 30일

## 📝 구현 가이드

### Python 코드에서의 적용
```python
self.search_terms = [
    'poker',
    'holdem', 
    'wsop',
    'wpt',
    'ept',
    'pokerstars',
    'ggpoker',
    'triton poker'
]
```

### YouTube API 파라미터
```python
# 검색 파라미터
params = {
    'q': search_term,              # 위 키워드 중 하나
    'regionCode': None,            # Global 검색 (지역 제한 없음)
    'relevanceLanguage': 'en',     # 영어 콘텐츠 우선
    'type': 'video',
    'order': 'viewCount',          # 조회수 순 정렬
    'publishedAfter': published_after
}
```

## 🚀 업데이트 방법

1. 이 파일의 키워드 목록을 수정
2. `backend/data-collector/scripts/youtube_trend_webhook_enhanced.py` 파일의 `search_terms` 업데이트
3. GitHub에 커밋 및 푸시
4. GitHub Actions가 자동으로 새 키워드로 검색 시작

## 📅 최종 업데이트
- **날짜**: 2025-08-05
- **작성자**: Claude Code
- **버전**: 1.0