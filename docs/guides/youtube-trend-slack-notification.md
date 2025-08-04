# YouTube 포커 트렌드 일일 Slack 알림 시스템

**구현 완료**: 2025-01-30
**버전**: 1.0.0

## 1. 시스템 개요

매일 오전 10시에 YouTube 포커 트렌드를 자동으로 분석하고 Slack 채널에 업데이트하는 시스템입니다.

### 주요 기능
- YouTube API를 통한 포커 관련 영상 데이터 수집
- 트렌드 분석 및 인사이트 도출
- 일일 리포트 생성 및 Slack 전송
- 급상승 트렌드 실시간 알림

## 2. 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                     Scheduler Service                        │
│                    (Node.js + node-cron)                    │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                YouTube Trend Analyzer                        │
│               (Python + YouTube API)                         │
├─────────────────────────────────────────────────────────────┤
│ • Data Collection Module                                     │
│ • Trend Analysis Engine                                      │
│ • Report Generator                                          │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                   Slack Integration                          │
│                  (Slack Web API)                            │
└─────────────────────────────────────────────────────────────┘
```

## 3. 데이터 수집 전략

### 3.1 YouTube API 검색 파라미터
```python
search_params = {
    'q': 'poker OR 포커 OR holdem OR 홀덤',
    'type': 'video',
    'part': 'snippet,statistics',
    'maxResults': 50,
    'order': 'viewCount',  # 조회수 기준
    'publishedAfter': '24시간 전',
    'relevanceLanguage': 'ko',  # 한국어 우선
    'regionCode': 'KR'
}
```

### 3.2 수집 데이터 항목
- 영상 제목, 설명, 태그
- 조회수, 좋아요, 댓글 수
- 업로드 시간, 채널 정보
- 썸네일 URL
- 영상 길이

## 4. 트렌드 분석 알고리즘

### 4.1 트렌드 스코어 계산
```python
def calculate_trend_score(video_data):
    """
    트렌드 스코어 = (조회수 증가율 × 0.4) + 
                   (참여율 × 0.3) + 
                   (시간당 조회수 × 0.2) + 
                   (키워드 관련성 × 0.1)
    """
    view_growth_rate = calculate_view_growth(video_data)
    engagement_rate = (likes + comments) / views
    views_per_hour = views / hours_since_upload
    keyword_relevance = calculate_keyword_score(title, description)
    
    return (view_growth_rate * 0.4 + 
            engagement_rate * 0.3 + 
            views_per_hour * 0.2 + 
            keyword_relevance * 0.1)
```

### 4.2 카테고리별 분류
- **토너먼트**: WSOP, WPT, EPT 관련
- **온라인 포커**: 포커스타즈, GGPoker 등
- **교육 콘텐츠**: 전략, 팁, 강의
- **엔터테인먼트**: 하이라이트, 재미있는 순간
- **프로 선수**: 유명 선수 관련 콘텐츠

## 5. Slack 메시지 포맷

### 5.1 일일 리포트 구조
```json
{
  "blocks": [
    {
      "type": "header",
      "text": {
        "type": "plain_text",
        "text": "🎰 오늘의 포커 YouTube 트렌드 (2024.01.30)"
      }
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*📊 전체 요약*\n• 총 분석 영상: 150개\n• 신규 트렌드: 5개\n• 평균 조회수: 25,000회"
      }
    },
    {
      "type": "divider"
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*🔥 TOP 5 급상승 영상*"
      }
    },
    {
      "type": "section",
      "fields": [
        {
          "type": "mrkdwn",
          "text": "*1. [제목]*\n채널: 포커TV\n조회수: 150K (↑300%)\n<링크|바로가기>"
        }
      ]
    }
  ]
}
```

### 5.2 실시간 알림 조건
- 1시간 내 조회수 10만 돌파
- 24시간 내 조회수 증가율 500% 이상
- 유명 프로 선수 신규 영상
- 주요 토너먼트 하이라이트

## 6. 구현 세부사항

### 6.1 스케줄러 설정 (Node.js)
```javascript
// backend/api-server/src/schedulers/youtubeTrendScheduler.js
const cron = require('node-cron');
const { analyzeYouTubeTrends } = require('../services/youtubeAnalyzer');
const { sendSlackNotification } = require('../services/slackNotifier');

// 매일 오전 10시 실행
cron.schedule('0 10 * * *', async () => {
  console.log('Starting YouTube trend analysis...');
  
  try {
    const trendData = await analyzeYouTubeTrends();
    const report = generateDailyReport(trendData);
    await sendSlackNotification(report);
    
    // 데이터베이스에 저장
    await saveTrendData(trendData);
  } catch (error) {
    console.error('Trend analysis failed:', error);
    await sendSlackError(error);
  }
}, {
  timezone: "Asia/Seoul"
});
```

### 6.2 YouTube 데이터 수집 (Python)
```python
# backend/data-collector/src/collectors/youtube_trend_collector.py
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import pandas as pd

class YouTubeTrendCollector:
    def __init__(self, api_key):
        self.youtube = build('youtube', 'v3', developerKey=api_key)
        
    def collect_poker_videos(self):
        """포커 관련 영상 수집"""
        search_terms = ['poker', '포커', 'holdem', '홀덤', 'WSOP', 'WPT']
        videos = []
        
        for term in search_terms:
            request = self.youtube.search().list(
                q=term,
                part='snippet',
                type='video',
                maxResults=50,
                order='viewCount',
                publishedAfter=(datetime.now() - timedelta(days=1)).isoformat() + 'Z'
            )
            response = request.execute()
            videos.extend(response['items'])
            
        return self.enrich_video_data(videos)
    
    def enrich_video_data(self, videos):
        """비디오 상세 정보 추가"""
        video_ids = [v['id']['videoId'] for v in videos]
        
        stats_request = self.youtube.videos().list(
            part='statistics,contentDetails',
            id=','.join(video_ids)
        )
        stats_response = stats_request.execute()
        
        # 통계 정보 병합
        return self.merge_video_data(videos, stats_response['items'])
```

### 6.3 트렌드 분석 엔진
```python
# backend/data-collector/src/analyzers/trend_analyzer.py
class PokerTrendAnalyzer:
    def analyze_trends(self, videos_data):
        """트렌드 분석 및 인사이트 도출"""
        df = pd.DataFrame(videos_data)
        
        # 트렌드 스코어 계산
        df['trend_score'] = df.apply(self.calculate_trend_score, axis=1)
        
        # 카테고리 분류
        df['category'] = df.apply(self.categorize_video, axis=1)
        
        # 급상승 영상 식별
        trending_videos = df[df['trend_score'] > 0.8].sort_values(
            'trend_score', ascending=False
        )
        
        # 카테고리별 통계
        category_stats = df.groupby('category').agg({
            'viewCount': ['sum', 'mean'],
            'likeCount': 'sum',
            'commentCount': 'sum'
        })
        
        return {
            'trending_videos': trending_videos.to_dict('records'),
            'category_stats': category_stats.to_dict(),
            'total_videos': len(df),
            'avg_views': df['viewCount'].mean(),
            'top_channels': self.get_top_channels(df)
        }
```

### 6.4 Slack 통합
```javascript
// backend/api-server/src/services/slackNotifier.js
const { WebClient } = require('@slack/web-api');

class SlackNotifier {
  constructor(token, channel) {
    this.client = new WebClient(token);
    this.channel = channel;
  }
  
  async sendDailyReport(trendData) {
    const blocks = this.formatDailyReport(trendData);
    
    await this.client.chat.postMessage({
      channel: this.channel,
      blocks: blocks,
      text: '오늘의 포커 YouTube 트렌드 리포트'
    });
  }
  
  formatDailyReport(data) {
    return [
      {
        type: "header",
        text: {
          type: "plain_text",
          text: `🎰 오늘의 포커 YouTube 트렌드 (${new Date().toLocaleDateString('ko-KR')})`
        }
      },
      {
        type: "section",
        text: {
          type: "mrkdwn",
          text: `*📊 전체 요약*\n` +
                `• 총 분석 영상: ${data.total_videos}개\n` +
                `• 평균 조회수: ${this.formatNumber(data.avg_views)}회\n` +
                `• 급상승 영상: ${data.trending_videos.length}개`
        }
      },
      ...this.formatTrendingVideos(data.trending_videos),
      ...this.formatCategoryStats(data.category_stats)
    ];
  }
}
```

## 7. 데이터베이스 스키마

### 7.1 YouTube 트렌드 데이터
```sql
-- PostgreSQL
CREATE TABLE youtube_trends (
    id SERIAL PRIMARY KEY,
    video_id VARCHAR(50) UNIQUE NOT NULL,
    title TEXT NOT NULL,
    channel_name VARCHAR(255),
    channel_id VARCHAR(50),
    view_count INTEGER,
    like_count INTEGER,
    comment_count INTEGER,
    published_at TIMESTAMP,
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    trend_score FLOAT,
    category VARCHAR(50),
    tags TEXT[],
    thumbnail_url TEXT,
    video_url TEXT,
    duration INTEGER -- seconds
);

CREATE TABLE trend_reports (
    id SERIAL PRIMARY KEY,
    report_date DATE UNIQUE NOT NULL,
    total_videos INTEGER,
    avg_views FLOAT,
    trending_count INTEGER,
    report_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 8. 환경 변수 설정

```env
# YouTube API
YOUTUBE_API_KEY=your_youtube_api_key

# Slack
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
SLACK_CHANNEL_ID=C1234567890
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Schedule
TREND_ANALYSIS_SCHEDULE="0 10 * * *"  # 매일 오전 10시
TREND_ANALYSIS_TIMEZONE="Asia/Seoul"

# Analysis Settings
TREND_THRESHOLD=0.8
MAX_VIDEOS_PER_SEARCH=50
LOOKBACK_HOURS=24
```

## 9. 모니터링 및 에러 처리

### 9.1 에러 알림
```javascript
async function sendSlackError(error) {
  await slackClient.chat.postMessage({
    channel: process.env.SLACK_ERROR_CHANNEL,
    text: `⚠️ YouTube 트렌드 분석 오류 발생`,
    blocks: [
      {
        type: "section",
        text: {
          type: "mrkdwn",
          text: `*Error:* ${error.message}\n*Time:* ${new Date().toISOString()}`
        }
      }
    ]
  });
}
```

### 9.2 성능 모니터링
- API 할당량 추적
- 분석 소요 시간 측정
- 데이터 수집 성공률 모니터링

## 10. 확장 가능성

### 10.1 추가 기능
- 경쟁 채널 분석
- 키워드별 트렌드 추적
- 주간/월간 리포트
- 실시간 알림 강화

### 10.2 다른 플랫폼 연동
- TikTok 트렌드 분석
- Twitch 스트리밍 데이터
- Twitter 언급 분석