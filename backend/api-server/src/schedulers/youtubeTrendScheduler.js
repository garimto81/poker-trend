/**
 * YouTube 트렌드 분석 스케줄러
 * 매일 오전 10시에 실행되며, 실시간 모니터링도 수행합니다.
 */

const cron = require('node-cron');
const axios = require('axios');
const SlackNotifier = require('../services/slackNotifier');
const logger = require('../utils/logger');
const db = require('../config/database');

class YouTubeTrendScheduler {
  constructor() {
    this.slackNotifier = new SlackNotifier();
    this.dataCollectorUrl = process.env.DATA_COLLECTOR_URL || 'http://localhost:8001';
    this.isRunning = false;
    this.lastAnalysisTime = null;
  }
  
  /**
   * 스케줄러 시작
   */
  start() {
    // 매일 오전 10시 정기 분석
    this.scheduleDailyAnalysis();
    
    // 4시간마다 실시간 모니터링
    this.scheduleRealtimeMonitoring();
    
    // 시작 시 즉시 한 번 실행 (개발 편의)
    if (process.env.NODE_ENV === 'development') {
      this.runAnalysis('manual');
    }
    
    logger.info('YouTube Trend Scheduler started');
  }
  
  /**
   * 일일 분석 스케줄 설정
   */
  scheduleDailyAnalysis() {
    const schedule = process.env.TREND_ANALYSIS_SCHEDULE || '0 10 * * *';
    const timezone = process.env.TREND_ANALYSIS_TIMEZONE || 'Asia/Seoul';
    
    cron.schedule(schedule, async () => {
      await this.runAnalysis('scheduled');
    }, {
      timezone: timezone
    });
    
    logger.info(`Daily analysis scheduled at ${schedule} (${timezone})`);
  }
  
  /**
   * 실시간 모니터링 스케줄 설정
   */
  scheduleRealtimeMonitoring() {
    // 4시간마다 실행
    cron.schedule('0 */4 * * *', async () => {
      await this.checkForTrendingVideos();
    });
    
    logger.info('Realtime monitoring scheduled every 4 hours');
  }
  
  /**
   * 트렌드 분석 실행
   */
  async runAnalysis(triggerType = 'scheduled') {
    if (this.isRunning) {
      logger.warn('Analysis already running, skipping...');
      return;
    }
    
    this.isRunning = true;
    const startTime = new Date();
    
    try {
      logger.info(`Starting YouTube trend analysis (${triggerType})...`);
      
      // 1. 데이터 수집 요청
      const collectionResult = await this.collectYouTubeData();
      
      // 2. 트렌드 분석 요청
      const analysisResult = await this.analyzeTrends(collectionResult.videos);
      
      // 3. 데이터베이스 저장
      await this.saveAnalysisResults(analysisResult);
      
      // 4. Slack 리포트 전송
      await this.slackNotifier.sendDailyReport(analysisResult);
      
      // 5. 통계 업데이트
      const duration = new Date() - startTime;
      logger.info(`Analysis completed in ${duration}ms`);
      
      this.lastAnalysisTime = startTime;
      
    } catch (error) {
      logger.error('Analysis failed:', error);
      await this.slackNotifier.sendErrorNotification(error, 'YouTubeTrendScheduler.runAnalysis');
      
    } finally {
      this.isRunning = false;
    }
  }
  
  /**
   * YouTube 데이터 수집
   */
  async collectYouTubeData() {
    try {
      const response = await axios.post(`${this.dataCollectorUrl}/api/youtube/collect`, {
        hours_back: 24,
        max_results: 200
      });
      
      return response.data;
      
    } catch (error) {
      logger.error('Data collection failed:', error);
      throw new Error(`Failed to collect YouTube data: ${error.message}`);
    }
  }
  
  /**
   * 트렌드 분석
   */
  async analyzeTrends(videos) {
    try {
      const response = await axios.post(`${this.dataCollectorUrl}/api/youtube/analyze`, {
        videos: videos
      });
      
      return response.data;
      
    } catch (error) {
      logger.error('Trend analysis failed:', error);
      throw new Error(`Failed to analyze trends: ${error.message}`);
    }
  }
  
  /**
   * 분석 결과 저장
   */
  async saveAnalysisResults(analysisResult) {
    const client = await db.getClient();
    
    try {
      await client.query('BEGIN');
      
      // 트렌드 리포트 저장
      const reportQuery = `
        INSERT INTO trend_reports (report_date, total_videos, avg_views, trending_count, report_data)
        VALUES ($1, $2, $3, $4, $5)
        ON CONFLICT (report_date) DO UPDATE
        SET total_videos = $2, avg_views = $3, trending_count = $4, report_data = $5
      `;
      
      await client.query(reportQuery, [
        new Date().toISOString().split('T')[0],
        analysisResult.summary.total_videos,
        analysisResult.summary.avg_views,
        analysisResult.summary.trending_count,
        JSON.stringify(analysisResult)
      ]);
      
      // 개별 비디오 정보 저장
      for (const video of analysisResult.trending_videos) {
        const videoQuery = `
          INSERT INTO youtube_trends (
            video_id, title, channel_name, channel_id, view_count, 
            like_count, comment_count, published_at, trend_score, 
            category, thumbnail_url, video_url
          ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
          ON CONFLICT (video_id) DO UPDATE
          SET view_count = $5, like_count = $6, comment_count = $7, 
              trend_score = $9, collected_at = CURRENT_TIMESTAMP
        `;
        
        await client.query(videoQuery, [
          video.video_id,
          video.title,
          video.channel_name,
          video.channel_id,
          video.view_count,
          video.like_count,
          video.comment_count,
          video.published_at,
          video.trend_score,
          video.category,
          video.thumbnail_url,
          video.video_url
        ]);
      }
      
      await client.query('COMMIT');
      logger.info('Analysis results saved to database');
      
    } catch (error) {
      await client.query('ROLLBACK');
      throw error;
    } finally {
      client.release();
    }
  }
  
  /**
   * 급상승 비디오 확인 (실시간 모니터링)
   */
  async checkForTrendingVideos() {
    try {
      logger.info('Checking for trending videos...');
      
      // 최근 4시간 데이터 수집
      const result = await this.collectYouTubeData();
      const analysis = await this.analyzeTrends(result.videos);
      
      // 이전 데이터와 비교하여 급상승 감지
      const trendingAlerts = await this.detectRapidGrowth(analysis.trending_videos);
      
      // 급상승 알림 전송
      for (const video of trendingAlerts) {
        await this.slackNotifier.sendTrendingAlert(video);
      }
      
      logger.info(`Found ${trendingAlerts.length} rapidly trending videos`);
      
    } catch (error) {
      logger.error('Trending check failed:', error);
    }
  }
  
  /**
   * 급성장 비디오 감지
   */
  async detectRapidGrowth(currentVideos) {
    const client = await db.getClient();
    const alerts = [];
    
    try {
      for (const video of currentVideos) {
        // 이전 데이터 조회
        const previousQuery = `
          SELECT view_count, collected_at 
          FROM youtube_trends 
          WHERE video_id = $1 
          ORDER BY collected_at DESC 
          LIMIT 1
        `;
        
        const result = await client.query(previousQuery, [video.video_id]);
        
        if (result.rows.length > 0) {
          const previous = result.rows[0];
          const timeDiff = (new Date() - new Date(previous.collected_at)) / 3600000; // hours
          const viewDiff = video.view_count - previous.view_count;
          const growthRate = (viewDiff / previous.view_count) * 100;
          
          // 급상승 조건: 4시간 내 50% 이상 증가 또는 10만 뷰 이상 증가
          if ((growthRate > 50 && timeDiff <= 4) || viewDiff > 100000) {
            alerts.push({
              ...video,
              growth_rate: growthRate.toFixed(1),
              view_increase: viewDiff
            });
          }
        }
      }
      
    } finally {
      client.release();
    }
    
    return alerts;
  }
  
  /**
   * 스케줄러 상태 조회
   */
  getStatus() {
    return {
      isRunning: this.isRunning,
      lastAnalysisTime: this.lastAnalysisTime,
      nextDailyRun: this.getNextDailyRun()
    };
  }
  
  /**
   * 다음 일일 실행 시간 계산
   */
  getNextDailyRun() {
    const now = new Date();
    const next = new Date(now);
    next.setHours(10, 0, 0, 0);
    
    if (next <= now) {
      next.setDate(next.getDate() + 1);
    }
    
    return next;
  }
}

// 싱글톤 인스턴스
const scheduler = new YouTubeTrendScheduler();

module.exports = scheduler;