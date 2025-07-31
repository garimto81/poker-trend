# 포커 트렌드 분석기 빠른 시작 가이드

## 🚀 30분 안에 시작하기

### Step 1: 필수 계정 및 API 키 준비 (10분)

#### 필요한 계정
1. **Reddit 개발자 계정**
   - https://www.reddit.com/prefs/apps 접속
   - "Create App" 클릭
   - Script 타입 선택
   - Client ID와 Secret 저장

2. **Twitter/X 개발자 계정**
   - https://developer.twitter.com 가입
   - API 키, API Secret 키 생성
   - Bearer Token 저장

3. **무료 모니터링 도구 (선택 1)**
   - Google Alerts 설정 (무료)
   - TweetDeck 설정 (무료)
   - 또는 유료 도구 무료 체험 시작

### Step 2: 기본 환경 설정 (10분)

```bash
# 프로젝트 디렉토리 생성
mkdir poker-trend-analyzer
cd poker-trend-analyzer

# Python 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 필수 패키지 설치
pip install praw tweepy beautifulsoup4 pandas nltk fastapi uvicorn
```

### Step 3: 최소 실행 가능 버전 (MVP) 코드 (10분)

```python
# quick_start.py
import praw
import json
from datetime import datetime
from collections import Counter

# Reddit 설정
reddit = praw.Reddit(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    user_agent="PokerTrends/1.0"
)

def get_poker_trends():
    """간단한 트렌드 수집"""
    posts = []
    
    # r/poker에서 핫 포스트 10개 가져오기
    for post in reddit.subreddit("poker").hot(limit=10):
        posts.append({
            'title': post.title,
            'score': post.score,
            'comments': post.num_comments,
            'created': datetime.fromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M'),
            'url': f"https://reddit.com{post.permalink}"
        })
    
    # 간단한 키워드 분석
    all_words = ' '.join([p['title'] for p in posts]).lower().split()
    common_words = Counter(all_words).most_common(10)
    
    # 결과 출력
    print("\n🎯 오늘의 포커 트렌드 (Reddit)\n")
    print("=" * 50)
    
    for i, post in enumerate(posts[:5], 1):
        print(f"\n{i}. {post['title']}")
        print(f"   💬 {post['comments']} comments | ⬆️ {post['score']} upvotes")
        print(f"   🔗 {post['url']}")
    
    print("\n\n📊 자주 언급된 키워드:")
    for word, count in common_words[:5]:
        if len(word) > 3:  # 짧은 단어 제외
            print(f"   - {word}: {count}회")
    
    # JSON 파일로 저장
    with open(f"trends_{datetime.now().strftime('%Y%m%d')}.json", 'w') as f:
        json.dump({
            'date': datetime.now().isoformat(),
            'posts': posts,
            'keywords': dict(common_words)
        }, f, indent=2)

if __name__ == "__main__":
    get_poker_trends()
```

## 📋 첫 주 실행 계획

### Day 1-2: 데이터 수집 테스트
- [ ] Reddit API로 데이터 수집 확인
- [ ] 수동으로 PokerNews 헤드라인 확인
- [ ] 첫 번째 간단한 브리핑 작성

### Day 3-4: 분석 기능 추가
- [ ] 감성 분석 라이브러리 테스트
- [ ] 키워드 빈도 분석 구현
- [ ] 트렌드 점수 계산 시작

### Day 5-7: 콘텐츠 제작
- [ ] 첫 번째 쇼츠 제작 (수동)
- [ ] 템플릿 기반 스크립트 작성
- [ ] 성과 측정 및 개선

## 🛠️ 점진적 개선 로드맵

### Phase 1 (Week 1-2): 수동 + 반자동
- Google Sheets에 일일 트렌드 기록
- 간단한 Python 스크립트로 Reddit 모니터링
- 수동으로 콘텐츠 아이디어 도출

### Phase 2 (Week 3-4): 자동화 시작
- 스케줄러 추가 (매시간 실행)
- 데이터베이스 연동 (SQLite 시작)
- 자동 리포트 생성 (HTML/Markdown)

### Phase 3 (Month 2): 고급 기능
- NLP 감성 분석 통합
- 다중 플랫폼 수집
- 대시보드 구축

### Phase 4 (Month 3): 완전 자동화
- 클라우드 배포
- 실시간 알림
- AI 기반 콘텐츠 제안

## 💡 즉시 사용 가능한 도구들

### 1. 무료 소셜 모니터링
- **Google Alerts**: "poker", "WSOP", "Daniel Negreanu" 등 설정
- **IFTTT**: Reddit → Google Sheets 자동화
- **Hootsuite Free**: 기본 소셜 모니터링

### 2. 콘텐츠 제작 도구
- **Canva**: 쇼츠 템플릿
- **CapCut**: 모바일 편집
- **DaVinci Resolve**: 무료 전문 편집

### 3. 분석 도구
- **Google Trends**: 포커 관련 검색어 트렌드
- **Reddit Insight**: 서브레딧 분석
- **Social Blade**: 유튜브 경쟁 채널 분석

## 📊 첫 달 목표 KPI

### 시스템 목표
- [ ] 일일 트렌드 수집: 95% 이상
- [ ] 자동 브리핑 생성: 80% 이상
- [ ] 분석 정확도: 70% 이상

### 콘텐츠 목표
- [ ] 일일 쇼츠 게시: 1-2개
- [ ] 평균 조회수: 1,000+
- [ ] 완성률: 50% 이상

## 🆘 문제 해결 가이드

### API 한계 도달
```python
# Rate limit 처리
import time

def safe_api_call(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except RateLimitException:
        print("Rate limit 도달, 60초 대기...")
        time.sleep(60)
        return func(*args, **kwargs)
```

### 트렌드 부족
- 예비 콘텐츠 뱅크 활용
- 해외 포커 커뮤니티 확인
- 과거 인기 콘텐츠 리메이크

### 낮은 참여율
- A/B 테스트 실행
- 댓글 분석으로 피드백 수집
- 경쟁 채널 벤치마킹

## 🎯 성공을 위한 핵심 팁

1. **일관성이 최우선**: 완벽한 시스템보다 꾸준한 실행
2. **작게 시작하기**: MVP로 시작해서 점진적 개선
3. **피드백 루프**: 매일 결과 측정하고 개선
4. **커뮤니티 참여**: 직접 포커 커뮤니티에 참여
5. **자동화는 천천히**: 먼저 수동으로 프로세스 검증

## 📞 추가 지원

### 커뮤니티
- Python 포커 개발자 Discord
- r/poker 모더레이터와 연결
- 포커 콘텐츠 크리에이터 네트워크

### 학습 자료
- "Automate the Boring Stuff with Python"
- YouTube Analytics 마스터클래스
- 포커 전략 기초 과정

이 가이드를 따라 시작하면 30분 안에 첫 트렌드 분석을 실행하고, 
한 달 안에 자동화된 시스템의 기초를 구축할 수 있습니다!

**시작이 반입니다. 지금 바로 Step 1부터 시작하세요! 🚀**