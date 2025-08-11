/**
 * Slack 알림 서비스
 * YouTube 포커 트렌드 분석 결과를 Slack으로 전송합니다.
 */

const { WebClient } = require('@slack/web-api');
const { IncomingWebhook } = require('@slack/webhook');

class SlackNotifier {
  constructor() {
    this.token = process.env.SLACK_BOT_TOKEN;
    this.channel = process.env.SLACK_CHANNEL_ID || '#poker-trends';
    this.webhookUrl = process.env.SLACK_WEBHOOK_URL;
    
    if (this.token) {
      this.client = new WebClient(this.token);
    }
    
    if (this.webhookUrl) {
      this.webhook = new IncomingWebhook(this.webhookUrl);
    }
  }
  
  /**
   * 일일 트렌드 리포트 전송
   */
  async sendDailyReport(trendData) {
    const blocks = this.formatDailyReport(trendData);
    
    try {
      if (this.client) {
        await this.client.chat.postMessage({
          channel: this.channel,
          blocks: blocks,
          text: '오늘의 포커 YouTube 트렌드 리포트'
        });
      } else if (this.webhook) {
        await this.webhook.send({
          blocks: blocks,
          text: '오늘의 포커 YouTube 트렌드 리포트'
        });
      }
      
      console.log('Daily report sent successfully');
    } catch (error) {
      console.error('Error sending daily report:', error);
      throw error;
    }
  }
  
  /**
   * 실시간 급상승 알림
   */
  async sendTrendingAlert(video) {
    const blocks = this.formatTrendingAlert(video);
    
    try {
      await this.client.chat.postMessage({
        channel: this.channel,
        blocks: blocks,
        text: `🔥 급상승 영상 감지: ${video.title}`
      });
    } catch (error) {
      console.error('Error sending trending alert:', error);
    }
  }
  
  /**
   * 에러 알림
   */
  async sendErrorNotification(error, context = '') {
    const errorChannel = process.env.SLACK_ERROR_CHANNEL || this.channel;
    
    try {
      await this.client.chat.postMessage({
        channel: errorChannel,
        text: '⚠️ 포커 트렌드 분석 오류',
        blocks: [
          {
            type: 'header',
            text: {
              type: 'plain_text',
              text: '⚠️ 시스템 오류 발생'
            }
          },
          {
            type: 'section',
            text: {
              type: 'mrkdwn',
              text: `*오류 내용:* ${error.message}\n*발생 위치:* ${context}\n*시간:* ${new Date().toLocaleString('ko-KR')}`
            }
          },
          {
            type: 'section',
            text: {
              type: 'mrkdwn',
              text: `\`\`\`${error.stack}\`\`\``
            }
          }
        ]
      });
    } catch (notifyError) {
      console.error('Error sending error notification:', notifyError);
    }
  }
  
  /**
   * 일일 리포트 포맷팅
   */
  formatDailyReport(data) {
    const now = new Date();
    const dateStr = now.toLocaleDateString('ko-KR');
    
    const blocks = [
      {
        type: 'header',
        text: {
          type: 'plain_text',
          text: `🎰 오늘의 포커 YouTube 트렌드 (${dateStr})`,
          emoji: true
        }
      },
      {
        type: 'divider'
      },
      // 전체 요약
      {
        type: 'section',
        text: {
          type: 'mrkdwn',
          text: '*📊 전체 요약*'
        },
        fields: [
          {
            type: 'mrkdwn',
            text: `*총 분석 영상*\n${data.summary.total_videos}개`
          },
          {
            type: 'mrkdwn',
            text: `*총 조회수*\n${this.formatNumber(data.summary.total_views)}회`
          },
          {
            type: 'mrkdwn',
            text: `*평균 조회수*\n${this.formatNumber(data.summary.avg_views)}회`
          },
          {
            type: 'mrkdwn',
            text: `*급상승 영상*\n${data.summary.trending_count}개`
          }
        ]
      },
      {
        type: 'divider'
      }
    ];
    
    // TOP 5 급상승 영상
    if (data.trending_videos && data.trending_videos.length > 0) {
      blocks.push({
        type: 'section',
        text: {
          type: 'mrkdwn',
          text: '*🔥 TOP 5 급상승 영상*'
        }
      });
      
      data.trending_videos.slice(0, 5).forEach((video, index) => {
        blocks.push({
          type: 'section',
          text: {
            type: 'mrkdwn',
            text: `*${index + 1}. ${this.escapeMarkdown(video.title)}*\n` +
                  `채널: ${video.channel_name}\n` +
                  `조회수: ${this.formatNumber(video.view_count)} (시간당 ${this.formatNumber(video.views_per_hour)}회)\n` +
                  `참여율: ${(video.engagement_rate * 100).toFixed(1)}%\n` +
                  `<${video.video_url}|영상 보기>`
          },
          accessory: {
            type: 'image',
            image_url: video.thumbnail_url,
            alt_text: video.title
          }
        });
      });
      
      blocks.push({ type: 'divider' });
    }
    
    // 카테고리별 통계
    if (data.category_breakdown) {
      blocks.push({
        type: 'section',
        text: {
          type: 'mrkdwn',
          text: '*📑 카테고리별 분석*'
        }
      });
      
      const categoryEmojis = {
        tournament: '🏆',
        online: '💻',
        education: '📚',
        entertainment: '🎭',
        pro_player: '⭐',
        general: '🎲'
      };
      
      const categoryNames = {
        tournament: '토너먼트',
        online: '온라인 포커',
        education: '교육/전략',
        entertainment: '엔터테인먼트',
        pro_player: '프로 선수',
        general: '일반'
      };
      
      const categoryFields = Object.entries(data.category_breakdown)
        .filter(([_, stats]) => stats.count > 0)
        .map(([category, stats]) => ({
          type: 'mrkdwn',
          text: `${categoryEmojis[category] || '🎯'} *${categoryNames[category] || category}*\n` +
                `영상 ${stats.count}개 | 평균 ${this.formatNumber(stats.avg_views)}회`
        }));
      
      if (categoryFields.length > 0) {
        blocks.push({
          type: 'section',
          fields: categoryFields
        });
      }
      
      blocks.push({ type: 'divider' });
    }
    
    // 인기 채널
    if (data.top_channels && data.top_channels.length > 0) {
      blocks.push({
        type: 'section',
        text: {
          type: 'mrkdwn',
          text: '*🏅 인기 채널 TOP 3*'
        }
      });
      
      const channelText = data.top_channels.slice(0, 3).map((channel, index) =>
        `${index + 1}. *${channel.channel_name}* - ${channel.video_count}개 영상, 총 ${this.formatNumber(channel.total_views)}회`
      ).join('\n');
      
      blocks.push({
        type: 'section',
        text: {
          type: 'mrkdwn',
          text: channelText
        }
      });
      
      blocks.push({ type: 'divider' });
    }
    
    // 키워드 트렌드
    if (data.keyword_analysis && Object.keys(data.keyword_analysis).length > 0) {
      const topKeywords = Object.entries(data.keyword_analysis)
        .slice(0, 10)
        .map(([keyword, count]) => `\`${keyword}\` (${count})`)
        .join(', ');
      
      blocks.push({
        type: 'section',
        text: {
          type: 'mrkdwn',
          text: `*🔤 인기 키워드*\n${topKeywords}`
        }
      });
    }
    
    // 푸터
    blocks.push({
      type: 'context',
      elements: [
        {
          type: 'mrkdwn',
          text: `📅 분석 시간: ${now.toLocaleString('ko-KR')} | 🤖 Poker Trend Bot v1.0`
        }
      ]
    });
    
    return blocks;
  }
  
  /**
   * 급상승 알림 포맷팅
   */
  formatTrendingAlert(video) {
    return [
      {
        type: 'section',
        text: {
          type: 'mrkdwn',
          text: '🚨 *급상승 영상 감지!*'
        }
      },
      {
        type: 'section',
        text: {
          type: 'mrkdwn',
          text: `*${this.escapeMarkdown(video.title)}*\n` +
                `채널: ${video.channel_name}\n` +
                `현재 조회수: ${this.formatNumber(video.view_count)}회\n` +
                `1시간 전 대비: +${video.growth_rate}%\n` +
                `<${video.video_url}|지금 확인하기>`
        },
        accessory: {
          type: 'image',
          image_url: video.thumbnail_url,
          alt_text: video.title
        }
      }
    ];
  }
  
  /**
   * 숫자 포맷팅 (천 단위 구분)
   */
  formatNumber(num) {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  }
  
  /**
   * Markdown 이스케이프
   */
  escapeMarkdown(text) {
    return text
      .replace(/[*_~`]/g, '\\$&')
      .replace(/\n/g, ' ');
  }
}

module.exports = SlackNotifier;