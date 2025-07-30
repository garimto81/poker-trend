-- YouTube 포커 트렌드 분석 데이터베이스 스키마

-- 데이터베이스 생성
CREATE DATABASE IF NOT EXISTS poker_trend;
USE poker_trend;

-- YouTube 트렌드 데이터 테이블
CREATE TABLE IF NOT EXISTS youtube_trends (
    id SERIAL PRIMARY KEY,
    video_id VARCHAR(50) UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    channel_name VARCHAR(255),
    channel_id VARCHAR(50),
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    comment_count INTEGER DEFAULT 0,
    published_at TIMESTAMP,
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    trend_score FLOAT,
    category VARCHAR(50),
    tags TEXT[],
    thumbnail_url TEXT,
    video_url TEXT,
    duration INTEGER, -- seconds
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 생성
CREATE INDEX idx_youtube_trends_video_id ON youtube_trends(video_id);
CREATE INDEX idx_youtube_trends_published_at ON youtube_trends(published_at);
CREATE INDEX idx_youtube_trends_trend_score ON youtube_trends(trend_score);
CREATE INDEX idx_youtube_trends_category ON youtube_trends(category);
CREATE INDEX idx_youtube_trends_collected_at ON youtube_trends(collected_at);

-- 트렌드 리포트 테이블
CREATE TABLE IF NOT EXISTS trend_reports (
    id SERIAL PRIMARY KEY,
    report_date DATE UNIQUE NOT NULL,
    total_videos INTEGER DEFAULT 0,
    avg_views FLOAT DEFAULT 0,
    trending_count INTEGER DEFAULT 0,
    report_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 채널 정보 테이블
CREATE TABLE IF NOT EXISTS youtube_channels (
    id SERIAL PRIMARY KEY,
    channel_id VARCHAR(50) UNIQUE NOT NULL,
    channel_name VARCHAR(255),
    subscriber_count INTEGER DEFAULT 0,
    video_count INTEGER DEFAULT 0,
    description TEXT,
    thumbnail_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 키워드 분석 테이블
CREATE TABLE IF NOT EXISTS keyword_trends (
    id SERIAL PRIMARY KEY,
    keyword VARCHAR(100) NOT NULL,
    date DATE NOT NULL,
    frequency INTEGER DEFAULT 0,
    videos_count INTEGER DEFAULT 0,
    total_views INTEGER DEFAULT 0,
    avg_engagement FLOAT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(keyword, date)
);

-- 알림 로그 테이블
CREATE TABLE IF NOT EXISTS notification_logs (
    id SERIAL PRIMARY KEY,
    notification_type VARCHAR(50) NOT NULL, -- 'daily_report', 'trending_alert', 'error'
    channel VARCHAR(50), -- 'slack', 'discord', 'email'
    recipient VARCHAR(255),
    content TEXT,
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'sent', 'failed'
    error_message TEXT,
    sent_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 급상승 알림 기록
CREATE TABLE IF NOT EXISTS trending_alerts (
    id SERIAL PRIMARY KEY,
    video_id VARCHAR(50) NOT NULL,
    alert_type VARCHAR(50), -- 'rapid_growth', 'high_engagement', 'viral'
    growth_rate FLOAT,
    view_increase INTEGER,
    previous_views INTEGER,
    current_views INTEGER,
    alert_sent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (video_id) REFERENCES youtube_trends(video_id)
);

-- 분석 메트릭 테이블
CREATE TABLE IF NOT EXISTS analysis_metrics (
    id SERIAL PRIMARY KEY,
    metric_date DATE NOT NULL,
    metric_type VARCHAR(50) NOT NULL, -- 'collection', 'analysis', 'notification'
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    avg_processing_time FLOAT, -- milliseconds
    total_items_processed INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(metric_date, metric_type)
);

-- 스케줄러 실행 로그
CREATE TABLE IF NOT EXISTS scheduler_logs (
    id SERIAL PRIMARY KEY,
    job_name VARCHAR(100) NOT NULL,
    execution_time TIMESTAMP NOT NULL,
    status VARCHAR(20) NOT NULL, -- 'started', 'completed', 'failed'
    duration INTEGER, -- milliseconds
    videos_collected INTEGER,
    trends_detected INTEGER,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 업데이트 트리거 함수
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 업데이트 트리거 적용
CREATE TRIGGER update_youtube_trends_updated_at BEFORE UPDATE ON youtube_trends
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_youtube_channels_updated_at BEFORE UPDATE ON youtube_channels
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 뷰 생성: 일일 트렌드 요약
CREATE VIEW daily_trend_summary AS
SELECT 
    DATE(collected_at) as date,
    COUNT(DISTINCT video_id) as total_videos,
    SUM(view_count) as total_views,
    AVG(view_count) as avg_views,
    AVG(trend_score) as avg_trend_score,
    COUNT(CASE WHEN trend_score >= 0.8 THEN 1 END) as high_trending_count
FROM youtube_trends
GROUP BY DATE(collected_at);

-- 뷰 생성: 채널별 성과
CREATE VIEW channel_performance AS
SELECT 
    channel_id,
    channel_name,
    COUNT(DISTINCT video_id) as video_count,
    SUM(view_count) as total_views,
    AVG(view_count) as avg_views,
    AVG(trend_score) as avg_trend_score,
    MAX(collected_at) as last_collected
FROM youtube_trends
GROUP BY channel_id, channel_name;

-- 뷰 생성: 카테고리별 통계
CREATE VIEW category_statistics AS
SELECT 
    category,
    COUNT(DISTINCT video_id) as video_count,
    SUM(view_count) as total_views,
    AVG(view_count) as avg_views,
    AVG(like_count) as avg_likes,
    AVG(comment_count) as avg_comments,
    AVG(trend_score) as avg_trend_score
FROM youtube_trends
WHERE category IS NOT NULL
GROUP BY category;