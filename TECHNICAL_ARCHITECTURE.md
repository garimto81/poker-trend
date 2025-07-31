# 포커 트렌드 분석기 기술 아키텍처

## 시스템 아키텍처 개요

```
┌─────────────────────────────────────────────────────────────┐
│                     프론트엔드 (대시보드)                      │
│                   React + TypeScript + D3.js                  │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                         API Gateway                           │
│                      FastAPI + Redis                          │
└─────────────────────────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│  데이터 수집기   │   │   분석 엔진     │   │  보고서 생성기   │
│  Python Scripts  │   │  ML/NLP Models  │   │  Report Builder  │
└─────────────────┘   └─────────────────┘   └─────────────────┘
        │                       │                       │
        └───────────────────────┴───────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                      데이터베이스 계층                         │
│              MongoDB (문서) + PostgreSQL (관계형)             │
└─────────────────────────────────────────────────────────────┘
```

## 1. 데이터 수집 모듈

### 1.1 소셜 미디어 크롤러

```python
# collectors/reddit_collector.py
import praw
from datetime import datetime
import asyncio
from typing import List, Dict

class RedditCollector:
    def __init__(self, client_id: str, client_secret: str):
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent="PokerTrendAnalyzer/1.0"
        )
        self.target_subreddits = ['poker', 'poker_theory']
        
    async def collect_posts(self, limit: int = 100) -> List[Dict]:
        """Reddit 게시물 수집"""
        posts = []
        
        for subreddit_name in self.target_subreddits:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # 인기 게시물
            for post in subreddit.hot(limit=limit//2):
                posts.append(self._extract_post_data(post))
            
            # 신규 게시물
            for post in subreddit.new(limit=limit//2):
                posts.append(self._extract_post_data(post))
                
        return posts
    
    def _extract_post_data(self, post) -> Dict:
        return {
            'id': post.id,
            'title': post.title,
            'author': str(post.author) if post.author else 'deleted',
            'created_utc': datetime.fromtimestamp(post.created_utc),
            'score': post.score,
            'num_comments': post.num_comments,
            'url': post.url,
            'selftext': post.selftext,
            'subreddit': post.subreddit.display_name,
            'platform': 'reddit',
            'collected_at': datetime.now()
        }
```

### 1.2 트위터/X 수집기

```python
# collectors/twitter_collector.py
import tweepy
from typing import List, Dict

class TwitterCollector:
    def __init__(self, api_key: str, api_secret: str, 
                 access_token: str, access_secret: str):
        auth = tweepy.OAuthHandler(api_key, api_secret)
        auth.set_access_token(access_token, access_secret)
        self.api = tweepy.API(auth, wait_on_rate_limit=True)
        
        self.target_accounts = [
            'DNegreanu', 'phil_hellmuth', 'LexVeldhuis',
            'Stapes', 'JaimeStaples', 'PokerNews'
        ]
        
        self.poker_hashtags = [
            '#poker', '#WSOP', '#WPT', '#pokerlife',
            '#onlinepoker', '#pokerplayer'
        ]
    
    async def collect_tweets(self) -> List[Dict]:
        """트윗 수집"""
        tweets = []
        
        # 타겟 계정의 최신 트윗
        for username in self.target_accounts:
            user_tweets = self.api.user_timeline(
                screen_name=username, 
                count=10, 
                tweet_mode='extended'
            )
            tweets.extend([self._extract_tweet_data(t) for t in user_tweets])
        
        # 해시태그 검색
        for hashtag in self.poker_hashtags:
            search_tweets = self.api.search_tweets(
                q=hashtag, 
                count=20, 
                tweet_mode='extended'
            )
            tweets.extend([self._extract_tweet_data(t) for t in search_tweets])
            
        return tweets
    
    def _extract_tweet_data(self, tweet) -> Dict:
        return {
            'id': tweet.id_str,
            'text': tweet.full_text,
            'author': tweet.user.screen_name,
            'created_at': tweet.created_at,
            'retweet_count': tweet.retweet_count,
            'favorite_count': tweet.favorite_count,
            'platform': 'twitter',
            'collected_at': datetime.now()
        }
```

### 1.3 전문 사이트 스크레이퍼

```python
# collectors/specialized_scraper.py
import aiohttp
from bs4 import BeautifulSoup
import asyncio

class PokerNewsScraper:
    def __init__(self):
        self.base_url = "https://www.pokernews.com"
        self.headers = {
            'User-Agent': 'PokerTrendAnalyzer/1.0'
        }
    
    async def scrape_latest_news(self) -> List[Dict]:
        """PokerNews 최신 기사 스크레이핑"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/news/", 
                headers=self.headers
            ) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                articles = []
                for article in soup.find_all('article', limit=20):
                    articles.append(self._extract_article_data(article))
                    
                return articles
    
    def _extract_article_data(self, article) -> Dict:
        return {
            'title': article.find('h2').text.strip(),
            'url': self.base_url + article.find('a')['href'],
            'summary': article.find('p').text.strip() if article.find('p') else '',
            'published_at': self._parse_date(article.find('time')['datetime']),
            'platform': 'pokernews',
            'collected_at': datetime.now()
        }
```

## 2. 분석 엔진

### 2.1 NLP 분석 모듈

```python
# analysis/nlp_analyzer.py
from transformers import pipeline
import spacy
from typing import List, Dict
from collections import Counter

class NLPAnalyzer:
    def __init__(self):
        # 감성 분석 모델
        self.sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model="cardiffnlp/twitter-roberta-base-sentiment"
        )
        
        # SpaCy 모델 (개체명 인식)
        self.nlp = spacy.load("en_core_web_sm")
        
        # 포커 전문 용어 사전
        self.poker_terms = {
            'strategic': ['GTO', 'exploitative', 'range', 'equity', 'EV'],
            'emotional': ['tilt', 'bad beat', 'cooler', 'suckout', 'rigged'],
            'technical': ['3bet', 'c-bet', 'check-raise', 'float', 'donk']
        }
        
    def analyze_sentiment(self, text: str) -> Dict:
        """감성 분석"""
        result = self.sentiment_analyzer(text[:512])[0]  # 최대 512 토큰
        
        # 포커 특화 감정 분석
        poker_emotion = self._detect_poker_emotion(text)
        
        return {
            'sentiment': result['label'],
            'confidence': result['score'],
            'poker_emotion': poker_emotion
        }
    
    def extract_entities(self, text: str) -> Dict:
        """개체명 추출"""
        doc = self.nlp(text)
        
        entities = {
            'players': [],
            'tournaments': [],
            'sites': [],
            'money': []
        }
        
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                entities['players'].append(ent.text)
            elif ent.label_ == "ORG":
                # 토너먼트나 사이트 구분
                if any(term in ent.text.lower() for term in ['wsop', 'wpt', 'ept']):
                    entities['tournaments'].append(ent.text)
                else:
                    entities['sites'].append(ent.text)
            elif ent.label_ == "MONEY":
                entities['money'].append(ent.text)
                
        return entities
    
    def _detect_poker_emotion(self, text: str) -> str:
        """포커 특화 감정 감지"""
        text_lower = text.lower()
        
        if any(term in text_lower for term in ['bad beat', 'suckout', 'rigged']):
            return 'frustration'
        elif any(term in text_lower for term in ['ship it', 'bink', 'crushing']):
            return 'excitement'
        elif any(term in text_lower for term in ['tilt', 'tilted', 'steaming']):
            return 'tilt'
        else:
            return 'neutral'
```

### 2.2 트렌드 스코어링 엔진

```python
# analysis/trend_scorer.py
import numpy as np
from datetime import datetime, timedelta

class TrendScorer:
    def __init__(self):
        self.weights = {
            'engagement_velocity': 0.4,
            'sentiment_intensity': 0.3,
            'narrative_potential': 0.2,
            'visual_availability': 0.1
        }
    
    def calculate_content_potential(self, trend_data: Dict) -> float:
        """콘텐츠 잠재력 점수 계산"""
        scores = {
            'engagement_velocity': self._calc_engagement_velocity(trend_data),
            'sentiment_intensity': self._calc_sentiment_intensity(trend_data),
            'narrative_potential': self._calc_narrative_potential(trend_data),
            'visual_availability': self._calc_visual_availability(trend_data)
        }
        
        # 가중 평균 계산
        total_score = sum(
            scores[key] * self.weights[key] 
            for key in scores
        )
        
        return round(total_score, 2)
    
    def _calc_engagement_velocity(self, data: Dict) -> float:
        """참여 속도 계산 (0-1)"""
        recent_engagement = data.get('recent_engagement', 0)
        previous_engagement = data.get('previous_engagement', 1)
        
        if previous_engagement == 0:
            return 1.0 if recent_engagement > 0 else 0.0
            
        velocity = (recent_engagement - previous_engagement) / previous_engagement
        return min(max(velocity, 0), 1)  # 0-1 범위로 정규화
    
    def _calc_sentiment_intensity(self, data: Dict) -> float:
        """감성 강도 계산 (0-1)"""
        sentiment_scores = data.get('sentiment_scores', [])
        if not sentiment_scores:
            return 0.0
            
        # 표준편차가 클수록 강한 감정
        std_dev = np.std(sentiment_scores)
        return min(std_dev * 2, 1)  # 0-1 범위로 정규화
```

### 2.3 토픽 모델링

```python
# analysis/topic_modeling.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import numpy as np

class TopicModeler:
    def __init__(self, n_topics=10):
        self.n_topics = n_topics
        self.vectorizer = TfidfVectorizer(
            max_features=100,
            stop_words='english',
            ngram_range=(1, 3)  # 1-3 단어 조합
        )
        self.lda = LatentDirichletAllocation(
            n_components=n_topics,
            random_state=42
        )
        
    def extract_topics(self, documents: List[str]) -> List[Dict]:
        """문서 집합에서 주요 토픽 추출"""
        # TF-IDF 벡터화
        doc_term_matrix = self.vectorizer.fit_transform(documents)
        
        # LDA 모델 학습
        self.lda.fit(doc_term_matrix)
        
        # 각 토픽의 주요 단어 추출
        feature_names = self.vectorizer.get_feature_names_out()
        topics = []
        
        for topic_idx, topic in enumerate(self.lda.components_):
            top_words_idx = topic.argsort()[-10:][::-1]
            top_words = [feature_names[i] for i in top_words_idx]
            
            topics.append({
                'topic_id': topic_idx,
                'keywords': top_words,
                'weight': float(topic.sum())
            })
            
        return topics
```

## 3. 보고서 생성 시스템

### 3.1 일일 브리핑 생성기

```python
# reporting/daily_briefing.py
from jinja2 import Template
from datetime import datetime
import json

class DailyBriefingGenerator:
    def __init__(self):
        self.template = Template("""
# 포커 트렌드 일일 브리핑
## {{ date }}

### 🎯 오늘의 스포트라이트
**{{ spotlight.title }}**
- 콘텐츠 잠재력: {{ spotlight.score }}/10
- 카테고리: {{ spotlight.category }}
- 핵심 요약: {{ spotlight.summary }}

### 📰 Top 3 중시(Meso) 트렌드
{% for trend in meso_trends %}
{{ loop.index }}. **{{ trend.title }}**
   - 출처: {{ trend.source }}
   - 참여도: {{ trend.engagement }}
   - [상세보기]({{ trend.url }})
{% endfor %}

### 🎮 Top 3 미시(Micro) 전략 토론
{% for discussion in micro_trends %}
{{ loop.index }}. **{{ discussion.topic }}**
   - 주요 논점: {{ discussion.key_points }}
   - 커뮤니티 반응: {{ discussion.sentiment }}
{% endfor %}

### 🔥 Top 3 나노(Nano) 바이럴 순간
{% for viral in nano_trends %}
{{ loop.index }}. **{{ viral.title }}**
   - 플랫폼: {{ viral.platform }}
   - 조회수: {{ viral.views }}
   - 감정: {{ viral.emotion }}
{% endfor %}

### 📊 데이터 대시보드
- 총 수집 데이터: {{ stats.total_collected }}
- 긍정/부정 비율: {{ stats.sentiment_ratio }}
- 가장 언급된 플레이어: {{ stats.top_players }}
        """)
    
    def generate_briefing(self, analysis_results: Dict) -> str:
        """분석 결과를 바탕으로 일일 브리핑 생성"""
        briefing_data = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'spotlight': self._select_spotlight(analysis_results),
            'meso_trends': self._extract_meso_trends(analysis_results),
            'micro_trends': self._extract_micro_trends(analysis_results),
            'nano_trends': self._extract_nano_trends(analysis_results),
            'stats': self._calculate_stats(analysis_results)
        }
        
        return self.template.render(**briefing_data)
```

### 3.2 콘텐츠 매트릭스 생성기

```python
# reporting/content_matrix.py
class ContentMatrixGenerator:
    def __init__(self):
        self.content_formats = [
            '60초 뉴스 플래시',
            '핫테이크/리액션',
            '전략 해설',
            'TOP 5 카운트다운',
            '미신 타파',
            'Before & After'
        ]
        
        self.format_templates = {
            '60초 뉴스 플래시': {
                'hook': '속보! {event}',
                'structure': '육하원칙 요약',
                'cta': '더 자세한 내용은...'
            },
            '핫테이크/리액션': {
                'hook': '이건 정말 {emotion}!',
                'structure': '개인 의견 + 근거',
                'cta': '여러분 생각은?'
            },
            # ... 기타 템플릿
        }
    
    def generate_content_ideas(self, trend: Dict) -> List[Dict]:
        """트렌드를 기반으로 콘텐츠 아이디어 생성"""
        ideas = []
        
        for format_name in self.content_formats:
            if self._is_format_suitable(trend, format_name):
                idea = {
                    'format': format_name,
                    'title': self._generate_title(trend, format_name),
                    'hook': self._generate_hook(trend, format_name),
                    'script_outline': self._generate_outline(trend, format_name),
                    'estimated_duration': self._estimate_duration(format_name)
                }
                ideas.append(idea)
                
        return ideas
```

## 4. API 및 대시보드

### 4.1 FastAPI 백엔드

```python
# api/main.py
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Poker Trend Analyzer API")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/trends/latest")
async def get_latest_trends():
    """최신 트렌드 조회"""
    # MongoDB에서 최신 분석 결과 조회
    trends = await db.trends.find().sort("created_at", -1).limit(10).to_list()
    return {"trends": trends}

@app.get("/api/briefing/today")
async def get_today_briefing():
    """오늘의 브리핑 조회"""
    briefing = await db.briefings.find_one(
        {"date": datetime.now().strftime("%Y-%m-%d")}
    )
    return briefing

@app.post("/api/analyze/trigger")
async def trigger_analysis(background_tasks: BackgroundTasks):
    """수동 분석 트리거"""
    background_tasks.add_task(run_analysis_pipeline)
    return {"message": "Analysis triggered"}

@app.get("/api/content/suggestions/{trend_id}")
async def get_content_suggestions(trend_id: str):
    """트렌드 기반 콘텐츠 제안"""
    trend = await db.trends.find_one({"_id": trend_id})
    if not trend:
        raise HTTPException(404, "Trend not found")
    
    matrix_generator = ContentMatrixGenerator()
    suggestions = matrix_generator.generate_content_ideas(trend)
    return {"suggestions": suggestions}
```

### 4.2 React 대시보드

```typescript
// dashboard/src/components/TrendDashboard.tsx
import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';

interface Trend {
  id: string;
  title: string;
  score: number;
  category: string;
  sentiment: string;
  engagement: number;
}

const TrendDashboard: React.FC = () => {
  const [trends, setTrends] = useState<Trend[]>([]);
  const [selectedTrend, setSelectedTrend] = useState<Trend | null>(null);
  
  useEffect(() => {
    fetchLatestTrends();
    const interval = setInterval(fetchLatestTrends, 60000); // 1분마다 갱신
    return () => clearInterval(interval);
  }, []);
  
  const fetchLatestTrends = async () => {
    const response = await fetch('/api/trends/latest');
    const data = await response.json();
    setTrends(data.trends);
  };
  
  return (
    <div className="dashboard">
      <h1>포커 트렌드 실시간 대시보드</h1>
      
      <div className="trend-grid">
        {trends.map(trend => (
          <TrendCard 
            key={trend.id}
            trend={trend}
            onClick={() => setSelectedTrend(trend)}
          />
        ))}
      </div>
      
      {selectedTrend && (
        <TrendDetail 
          trend={selectedTrend}
          onClose={() => setSelectedTrend(null)}
        />
      )}
    </div>
  );
};
```

## 5. 자동화 및 스케줄링

### 5.1 데이터 수집 스케줄러

```python
# scheduler/data_collector_scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio

class DataCollectionScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.collectors = {
            'reddit': RedditCollector(),
            'twitter': TwitterCollector(),
            'pokernews': PokerNewsScraper()
        }
        
    def setup_schedules(self):
        """스케줄 설정"""
        # 5분마다 소셜 미디어 수집
        self.scheduler.add_job(
            self.collect_social_media,
            'interval',
            minutes=5,
            id='social_media_collection'
        )
        
        # 30분마다 뉴스 사이트 스크레이핑
        self.scheduler.add_job(
            self.scrape_news_sites,
            'interval',
            minutes=30,
            id='news_scraping'
        )
        
        # 매일 오전 8시 일일 브리핑 생성
        self.scheduler.add_job(
            self.generate_daily_briefing,
            'cron',
            hour=8,
            minute=0,
            id='daily_briefing'
        )
        
    async def collect_social_media(self):
        """소셜 미디어 데이터 수집"""
        tasks = []
        for platform, collector in self.collectors.items():
            if platform in ['reddit', 'twitter']:
                tasks.append(collector.collect_data())
        
        results = await asyncio.gather(*tasks)
        await self.save_to_database(results)
```

## 6. 배포 및 운영

### 6.1 Docker 컨테이너화

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# SpaCy 모델 다운로드
RUN python -m spacy download en_core_web_sm

# 애플리케이션 복사
COPY . .

# 환경 변수 설정
ENV PYTHONUNBUFFERED=1

# 실행
CMD ["python", "main.py"]
```

### 6.2 Docker Compose 설정

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MONGODB_URL=mongodb://mongodb:27017/poker_trends
      - REDIS_URL=redis://redis:6379
    depends_on:
      - mongodb
      - redis
    
  mongodb:
    image: mongo:5.0
    volumes:
      - mongo_data:/data/db
    ports:
      - "27017:27017"
    
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    
  dashboard:
    build: ./dashboard
    ports:
      - "3000:3000"
    depends_on:
      - api

volumes:
  mongo_data:
```

## 7. 모니터링 및 로깅

### 7.1 로깅 설정

```python
# utils/logging_config.py
import logging
from pythonjsonlogger import jsonlogger

def setup_logging():
    """구조화된 로깅 설정"""
    logHandler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter()
    logHandler.setFormatter(formatter)
    
    logger = logging.getLogger()
    logger.addHandler(logHandler)
    logger.setLevel(logging.INFO)
    
    return logger

# 사용 예시
logger = setup_logging()
logger.info("trend_detected", extra={
    "trend_id": "123",
    "score": 8.5,
    "category": "tournament",
    "platform": "reddit"
})
```

### 7.2 성능 모니터링

```python
# monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# 메트릭 정의
trends_collected = Counter(
    'poker_trends_collected_total',
    'Total number of trends collected',
    ['platform', 'category']
)

analysis_duration = Histogram(
    'poker_analysis_duration_seconds',
    'Time spent analyzing trends'
)

active_trends = Gauge(
    'poker_active_trends',
    'Number of currently active trends',
    ['category']
)
```

이 기술 아키텍처는 확장 가능하고 유지보수가 용이하도록 설계되었으며, 실시간 데이터 수집부터 분석, 보고서 생성까지 전체 파이프라인을 자동화합니다.