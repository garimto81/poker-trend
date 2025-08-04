# API 설계 문서

## 1. API 개요

### 기본 정보
- **Base URL**: `https://api.poker-trend.com`
- **버전**: v1
- **형식**: RESTful JSON API
- **인증**: API Key (헤더: `X-API-Key`)
- **타임존**: 모든 시간은 KST (UTC+9) 기준

### 응답 형식
```json
{
  "success": true,
  "data": {},
  "error": null,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 에러 응답
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error description",
    "details": {}
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## 2. 엔드포인트 명세

### 2.1 보고서 관련

#### GET /api/v1/reports/daily
일일 보고서 조회

**Query Parameters:**
- `date` (optional): YYYY-MM-DD 형식, 기본값은 오늘 (KST 기준)

**Response:**
```json
{
  "success": true,
  "data": {
    "report_id": "rep_123456",
    "type": "daily",
    "date": "2024-01-01",
    "keywords": [
      {
        "keyword": "wsop",
        "top_videos": [
          {
            "video_id": "abc123",
            "title": "WSOP Main Event Final Table",
            "view_count": 1500000,
            "like_count": 25000,
            "comment_count": 3000,
            "channel_name": "PokerGO",
            "published_at": "2024-01-01T10:00:00Z"
          }
        ],
        "total_views": 5000000,
        "avg_engagement_rate": 0.035
      }
    ],
    "ai_insights": {
      "trends": ["토너먼트 하이라이트 인기 상승"],
      "shorts_ideas": [
        {
          "title": "올인 순간 모음집",
          "description": "WSOP 메인 이벤트의 짜릿한 올인 순간들",
          "estimated_views": "100K-500K"
        }
      ]
    },
    "created_at": "2024-01-01T10:00:00Z"
  }
}
```

#### GET /api/v1/reports/weekly
주간 보고서 조회

**Query Parameters:**
- `start_date` (optional): YYYY-MM-DD 형식
- `end_date` (optional): YYYY-MM-DD 형식

**Response:** 일일 보고서와 동일한 구조

#### GET /api/v1/reports/monthly
월간 보고서 조회

**Query Parameters:**
- `year` (optional): YYYY 형식
- `month` (optional): MM 형식

**Response:** 일일 보고서와 동일한 구조 + 월간 트렌드 분석

#### POST /api/v1/reports/generate
수동 보고서 생성

**Request Body:**
```json
{
  "type": "daily|weekly|monthly",
  "start_date": "2024-01-01",
  "end_date": "2024-01-07",
  "keywords": ["wsop", "gg poker"],  // optional, 기본값은 전체
  "send_to_slack": false
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "job_id": "job_789012",
    "status": "processing",
    "estimated_time": 300
  }
}
```

### 2.2 키워드 관련

#### GET /api/v1/keywords
키워드 목록 조회

**Response:**
```json
{
  "success": true,
  "data": {
    "keywords": [
      {
        "id": "kw_001",
        "name": "wsop",
        "display_name": "WSOP",
        "description": "World Series of Poker",
        "active": true,
        "priority": 1
      },
      {
        "id": "kw_002",
        "name": "gg poker",
        "display_name": "GG Poker",
        "description": "GG Poker Platform",
        "active": true,
        "priority": 2
      }
    ]
  }
}
```

#### POST /api/v1/keywords
키워드 추가 (관리자 전용)

**Request Body:**
```json
{
  "name": "new_keyword",
  "display_name": "New Keyword",
  "description": "Description",
  "priority": 10
}
```

### 2.3 비디오 관련

#### GET /api/v1/videos/trending
트렌딩 비디오 조회

**Query Parameters:**
- `keyword` (optional): 특정 키워드 필터
- `period` (optional): today|week|month
- `limit` (optional): 기본값 10

**Response:**
```json
{
  "success": true,
  "data": {
    "videos": [
      {
        "video_id": "xyz789",
        "title": "Epic Poker Bluff",
        "view_count": 2000000,
        "growth_rate": 0.25,
        "channel": {
          "channel_id": "ch_123",
          "name": "Poker Channel",
          "subscriber_count": 500000
        },
        "metrics": {
          "engagement_rate": 0.045,
          "comment_sentiment": "positive"
        }
      }
    ]
  }
}
```

#### GET /api/v1/videos/{video_id}
특정 비디오 상세 정보

**Response:**
```json
{
  "success": true,
  "data": {
    "video_id": "xyz789",
    "title": "Epic Poker Bluff",
    "description": "Full description...",
    "view_count": 2000000,
    "like_count": 50000,
    "dislike_count": 1000,
    "comment_count": 5000,
    "duration": "PT15M30S",
    "tags": ["poker", "bluff", "wsop"],
    "channel": {
      "channel_id": "ch_123",
      "name": "Poker Channel",
      "subscriber_count": 500000
    },
    "collected_at": "2024-01-01T10:00:00Z"
  }
}
```

### 2.4 분석 관련

#### GET /api/v1/analytics/trends
트렌드 분석 데이터

**Query Parameters:**
- `period`: week|month|quarter
- `keywords[]`: 키워드 배열

**Response:**
```json
{
  "success": true,
  "data": {
    "period": {
      "start": "2024-01-01",
      "end": "2024-01-31"
    },
    "trends": [
      {
        "keyword": "wsop",
        "growth_rate": 0.15,
        "peak_day": "2024-01-15",
        "popular_topics": ["final table", "bad beat"],
        "audience_insights": {
          "peak_hours": ["20:00-22:00 UTC"],
          "engagement_pattern": "weekend_heavy"
        }
      }
    ]
  }
}
```

### 2.5 시스템 관련

#### GET /api/v1/health
시스템 상태 확인

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "version": "1.0.0",
    "services": {
      "database": "connected",
      "redis": "connected",
      "youtube_api": "healthy",
      "gemini_api": "healthy",
      "slack": "connected"
    },
    "api_quotas": {
      "youtube": {
        "used": 3500,
        "limit": 10000,
        "reset_at": "2024-01-02T00:00:00Z"
      },
      "gemini": {
        "used": 45,
        "limit": 60,
        "reset_at": "2024-01-01T11:00:00Z"
      }
    }
  }
}
```

#### GET /api/v1/logs
실행 로그 조회 (관리자 전용)

**Query Parameters:**
- `type`: scheduler|api|error
- `start_date`: YYYY-MM-DD
- `end_date`: YYYY-MM-DD
- `limit`: 기본값 100

## 3. 인증 및 권한

### 3.1 API Key 인증
```
Headers:
X-API-Key: your-api-key-here
```

### 3.2 권한 레벨
- **Public**: 기본 읽기 권한
- **Admin**: 전체 권한

## 4. Rate Limiting

### 4.1 제한 정책
- Public: 100 requests/hour
- Admin: 1000 requests/hour

### 4.2 Rate Limit 헤더
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1609459200
```

## 5. 에러 코드

| 코드 | 설명 |
|------|------|
| AUTH_001 | Invalid API key |
| AUTH_002 | Insufficient permissions |
| RATE_001 | Rate limit exceeded |
| DATA_001 | Resource not found |
| DATA_002 | Invalid request data |
| API_001 | YouTube API error |
| API_002 | Gemini API error |
| SYS_001 | Internal server error |

## 6. Webhook

### 6.1 Slack Webhook 형식
```json
{
  "text": "📊 일일 포커 트렌드 보고서",
  "attachments": [
    {
      "color": "good",
      "title": "2024년 1월 1일 보고서",
      "fields": [
        {
          "title": "총 조회수",
          "value": "5,000,000",
          "short": true
        }
      ],
      "footer": "Poker Trend Analyzer",
      "ts": 1609459200
    }
  ]
}