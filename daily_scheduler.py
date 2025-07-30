# -*- coding: utf-8 -*-
"""
포커 트렌드 분석기 일일 자동 실행 및 슬랙 업데이트
"""

import os
import json
import asyncio
import schedule
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import traceback
import logging

from dotenv import load_dotenv
load_dotenv()

# 기존 분석기 import
from quantitative_analyzer import QuantitativePokerAnalyzer

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('daily_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SlackNotifier:
    """슬랙 알림 전송 클래스"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    def send_message(self, message: str, blocks: Optional[list] = None) -> bool:
        """슬랙 메시지 전송"""
        try:
            payload = {
                "text": message,
                "username": "포커트렌드봇",
                "icon_emoji": ":game_die:"
            }
            
            if blocks:
                payload["blocks"] = blocks
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"슬랙 메시지 전송 실패: {e}")
            return False
    
    def create_analysis_blocks(self, analysis_data: Dict[str, Any]) -> list:
        """분석 결과를 슬랙 블록 형식으로 변환"""
        basic_stats = analysis_data.get('basic_statistics', {})
        keyword_analysis = analysis_data.get('keyword_analysis', {})
        top_performers = analysis_data.get('top_performers', [])
        insights = analysis_data.get('quantitative_insights', [])
        
        # 키워드를 바이럴 점수로 정렬
        sorted_keywords = sorted(
            keyword_analysis.items(),
            key=lambda x: x[1]['avg_viral_score'],
            reverse=True
        )
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🎯 포커 트렌드 일일 분석 리포트 - {datetime.now().strftime('%Y-%m-%d')}"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*📊 총 분석 비디오*\n{basic_stats.get('total_videos', 0):,}개"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*👀 총 조회수*\n{basic_stats.get('total_views', 0):,}회"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*👍 총 좋아요*\n{basic_stats.get('total_likes', 0):,}개"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*💬 평균 참여율*\n{basic_stats.get('avg_engagement_rate', 0):.3f}"
                    }
                ]
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🏆 키워드별 성과 순위 (바이럴 점수 기준)*"
                }
            }
        ]
        
        # 상위 5개 키워드만 표시
        for rank, (keyword, stats) in enumerate(sorted_keywords[:5], 1):
            medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"{rank}위"
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{medal} {keyword}*\n"
                            f"바이럴점수: {stats['avg_viral_score']:.1f} | "
                            f"평균조회수: {stats['avg_views']:,.0f} | "
                            f"참여율: {stats['avg_engagement_rate']:.3f}"
                }
            })
        
        # 핵심 인사이트
        if insights:
            blocks.extend([
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*💡 핵심 인사이트*"
                    }
                }
            ])
            
            insight_names = {
                'performance_leader': '최고 성과',
                'momentum_leader': '최고 모멘텀', 
                'engagement_leader': '최고 참여도',
                'market_leader': '시장 점유율 1위'
            }
            
            for insight in insights[:3]:  # 상위 3개만 표시
                name = insight_names.get(insight['type'], insight['type'])
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"• *{name}*: {insight['keyword']} (신뢰도: {insight['confidence']:.0%})"
                    }
                })
        
        # 상위 성과 비디오
        if top_performers:
            blocks.extend([
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*🎬 오늘의 TOP 성과 비디오*"
                    }
                }
            ])
            
            top_video = top_performers[0]
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"🏆 *{top_video['keyword']}* 카테고리\n"
                            f"조회수: {top_video['views']:,} | "
                            f"참여율: {top_video['engagement_rate']:.3f} | "
                            f"바이럴점수: {top_video['viral_score']:.1f}"
                }
            })
        
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"분석 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
                            f"정량적 분석 모델 v3.0"
                }
            ]
        })
        
        return blocks

class DailyAnalysisScheduler:
    """일일 분석 스케줄러"""
    
    def __init__(self):
        self.youtube_api_key = os.getenv('YOUTUBE_API_KEY')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        
        if not all([self.youtube_api_key, self.gemini_api_key, self.slack_webhook_url]):
            raise ValueError("필수 환경 변수가 설정되지 않았습니다. YOUTUBE_API_KEY, GEMINI_API_KEY, SLACK_WEBHOOK_URL 확인 필요")
        
        self.slack_notifier = SlackNotifier(self.slack_webhook_url)
        self.analyzer = None
        
    async def run_daily_analysis(self) -> Optional[Dict[str, Any]]:
        """일일 분석 실행"""
        logger.info("일일 포커 트렌드 분석 시작")
        
        try:
            # 분석기 초기화
            self.analyzer = QuantitativePokerAnalyzer(
                self.youtube_api_key, 
                self.gemini_api_key
            )
            
            # 1. 비디오 수집
            logger.info("비디오 데이터 수집 중...")
            videos = await self.analyzer.collect_all_videos()
            
            if not videos:
                logger.warning("수집된 비디오가 없습니다.")
                return None
            
            logger.info(f"총 {len(videos)}개 비디오 수집 완료")
            
            # 2. 정량적 분석 수행
            logger.info("정량적 분석 수행 중...")
            analysis = self.analyzer.perform_quantitative_analysis()
            
            # 3. 결과 저장
            logger.info("분석 결과 저장 중...")
            saved_file = self.analyzer.save_quantitative_results(analysis)
            
            # 4. 분석 결과에 파일 정보 추가
            analysis['saved_file'] = saved_file
            analysis['analysis_timestamp'] = datetime.now().isoformat()
            
            logger.info("일일 분석 완료")
            return analysis
            
        except Exception as e:
            logger.error(f"일일 분석 중 오류 발생: {e}")
            logger.error(traceback.format_exc())
            return None
    
    def send_success_notification(self, analysis_data: Dict[str, Any]) -> bool:
        """성공 알림 전송"""
        try:
            basic_stats = analysis_data.get('basic_statistics', {})
            
            # 간단한 텍스트 메시지
            message = (
                f"✅ 포커 트렌드 일일 분석 완료!\n"
                f"📊 {basic_stats.get('total_videos', 0)}개 비디오 분석\n"
                f"👀 총 {basic_stats.get('total_views', 0):,} 조회수\n"
                f"상세 결과는 아래를 확인하세요 👇"
            )
            
            # 상세 블록 생성
            blocks = self.slack_notifier.create_analysis_blocks(analysis_data.get('quantitative_analysis', {}))
            
            return self.slack_notifier.send_message(message, blocks)
            
        except Exception as e:
            logger.error(f"성공 알림 전송 실패: {e}")
            return False
    
    def send_error_notification(self, error_message: str) -> bool:
        """오류 알림 전송"""
        try:
            message = (
                f"❌ 포커 트렌드 일일 분석 실패\n"
                f"시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"오류: {error_message[:200]}..."
            )
            
            blocks = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*❌ 일일 분석 실패*\n{error_message}"
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"실패 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        }
                    ]
                }
            ]
            
            return self.slack_notifier.send_message(message, blocks)
            
        except Exception as e:
            logger.error(f"오류 알림 전송 실패: {e}")
            return False
    
    def send_quota_exceeded_notification(self) -> bool:
        """할당량 초과 알림 전송"""
        try:
            message = (
                f"⚠️ YouTube API 할당량 초과\n"
                f"시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"내일 새벽 2시 이후 재시도 예정"
            )
            
            blocks = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*⚠️ YouTube API 할당량 초과*\n"
                                "일일 10,000 유닛 한도 도달\n"
                                "내일 새벽 2시(한국시간) 할당량 리셋 후 재시도"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*💡 대안책*\n"
                                "• 새 Google Cloud 프로젝트 생성\n"
                                "• 추가 API 키 발급\n"
                                "• 기존 분석 데이터 활용"
                    }
                }
            ]
            
            return self.slack_notifier.send_message(message, blocks)
            
        except Exception as e:
            logger.error(f"할당량 초과 알림 전송 실패: {e}")
            return False
    
    async def execute_daily_job(self):
        """일일 작업 실행"""
        logger.info("일일 작업 시작")
        
        try:
            # 분석 실행
            analysis_result = await self.run_daily_analysis()
            
            if analysis_result:
                # 성공 알림 전송
                success = self.send_success_notification(analysis_result)
                if success:
                    logger.info("슬랙 알림 전송 성공")
                else:
                    logger.warning("슬랙 알림 전송 실패")
            else:
                # 실패 알림 전송
                self.send_error_notification("분석 결과가 없습니다. 로그를 확인하세요.")
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"일일 작업 실행 중 오류: {error_msg}")
            
            # 할당량 초과 특별 처리
            if "quotaExceeded" in error_msg:
                self.send_quota_exceeded_notification()
            else:
                self.send_error_notification(error_msg)
    
    def start_scheduler(self):
        """스케줄러 시작"""
        logger.info("포커 트렌드 분석 스케줄러 시작")
        
        # 매일 오전 9시에 실행 (한국시간)
        schedule.every().day.at("09:00").do(
            lambda: asyncio.run(self.execute_daily_job())
        )
        
        # 테스트용: 즉시 실행 (주석 해제하면 바로 실행)
        # schedule.every().minute.do(
        #     lambda: asyncio.run(self.execute_daily_job())
        # )
        
        logger.info("스케줄 등록 완료: 매일 오전 9시 실행")
        
        # 시작 알림
        start_message = (
            f"🚀 포커 트렌드 분석 스케줄러 시작\n"
            f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"실행 주기: 매일 오전 9시"
        )
        
        self.slack_notifier.send_message(start_message)
        
        # 스케줄러 실행
        while True:
            schedule.run_pending()
            time.sleep(60)  # 1분마다 스케줄 확인

def test_slack_notification():
    """슬랙 알림 테스트"""
    slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
    
    if not slack_webhook:
        print("SLACK_WEBHOOK_URL 환경 변수가 설정되지 않았습니다.")
        return
    
    notifier = SlackNotifier(slack_webhook)
    
    # 테스트 메시지 전송
    test_message = f"🧪 포커 트렌드 분석기 테스트 메시지\n시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    success = notifier.send_message(test_message)
    
    if success:
        print("✅ 슬랙 테스트 메시지 전송 성공")
    else:
        print("❌ 슬랙 테스트 메시지 전송 실패")

def run_immediate_test():
    """즉시 테스트 실행"""
    print("포커 트렌드 분석 즉시 테스트 실행 중...")
    
    try:
        scheduler = DailyAnalysisScheduler()
        asyncio.run(scheduler.execute_daily_job())
        print("✅ 즉시 테스트 완료")
    except Exception as e:
        print(f"❌ 즉시 테스트 실패: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # 테스트 모드
        if len(sys.argv) > 2 and sys.argv[2] == "slack":
            test_slack_notification()
        else:
            run_immediate_test()
    else:
        # 스케줄러 모드
        try:
            scheduler = DailyAnalysisScheduler()
            scheduler.start_scheduler()
        except KeyboardInterrupt:
            logger.info("스케줄러가 사용자에 의해 중단되었습니다.")
        except Exception as e:
            logger.error(f"스케줄러 실행 중 오류: {e}")
            logger.error(traceback.format_exc())