#!/usr/bin/env python3
"""
모의 데이터를 사용한 포커 트렌드 분석 시스템 테스트
실제 API 키 없이 시스템 구조를 테스트합니다.
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
import random

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 모의 데이터 생성 함수들
def generate_mock_videos(keyword, count=5):
    """모의 YouTube 영상 데이터 생성"""
    video_titles = [
        f"INSANE {keyword} Bluff at WSOP 2025!",
        f"${random.randint(100000, 1000000)} Pot - Biggest {keyword} Game",
        f"How to Play {keyword} Like a Pro",
        f"{keyword} Tournament Final Table Highlights",
        f"Epic {keyword} Comeback - Must Watch!"
    ]
    
    channels = ["PokerGO", "Hustler Casino Live", "Brad Owen", "Doug Polk", "Daniel Negreanu"]
    
    videos = []
    for i in range(min(count, len(video_titles))):
        videos.append({
            'video_id': f'mock_{keyword}_{i}',
            'title': video_titles[i],
            'channel_title': random.choice(channels),
            'channel_id': f'channel_{i}',
            'published_at': (datetime.utcnow() - timedelta(hours=random.randint(1, 48))).isoformat() + 'Z',
            'view_count': random.randint(10000, 500000),
            'like_count': random.randint(100, 10000),
            'comment_count': random.randint(50, 1000),
            'duration': f'PT{random.randint(5, 30)}M{random.randint(0, 59)}S',
            'url': f'https://youtube.com/watch?v=mock_{keyword}_{i}',
            'keyword': keyword,
            'category': random.choice(['tournament', 'cash_game', 'education', 'entertainment'])
        })
    
    return videos

def generate_mock_ai_insights(report_type):
    """모의 AI 인사이트 생성"""
    insights = {
        'daily': """오늘의 포커 트렌드는 WSOP 관련 콘텐츠가 주도하고 있습니다. 
특히 Phil Ivey의 블러프 플레이가 화제를 모으며 관련 영상들이 급상승하고 있습니다. 
내일은 온라인 포커 플랫폼의 새로운 토너먼트 발표로 인해 관련 콘텐츠 수요가 증가할 것으로 예상됩니다.""",
        
        'weekly': """이번 주는 고액 캐시게임 콘텐츠가 전주 대비 250% 성장하며 폭발적인 인기를 끌었습니다. 
Triton Poker Series의 시작과 함께 프리미엄 콘텐츠에 대한 수요가 급증했으며, 
교육 콘텐츠보다는 엔터테인먼트 중심의 하이라이트 영상이 더 높은 참여율을 보였습니다. 
다음 주에는 WSOP 예선이 시작되어 토너먼트 관련 콘텐츠가 주목받을 것으로 예측됩니다.""",
        
        'monthly': """2025년 1월은 포커 콘텐츠의 전환점이 되는 달이었습니다. 
월초 대비 전체 조회수가 180% 증가했으며, 특히 모바일 시청자가 65%를 차지하며 주요 시청층으로 부상했습니다. 
짧은 형식의 하이라이트 영상(5-10분)이 긴 영상보다 3배 높은 완주율을 보였고, 
썸네일에 칩 스택과 확률을 표시한 영상이 평균 2.5배 높은 클릭률을 기록했습니다. 
2월에는 WSOP 시즌 시작과 함께 토너먼트 콘텐츠가 주류를 이룰 것으로 전망됩니다."""
    }
    
    return insights.get(report_type, insights['daily'])

def test_system_structure():
    """시스템 구조 테스트"""
    logger.info("=" * 50)
    logger.info("포커 트렌드 분석 시스템 구조 테스트")
    logger.info("=" * 50)
    
    # 1. 디렉토리 구조 확인
    logger.info("\n📁 디렉토리 구조 확인...")
    required_dirs = [
        'scripts',
        '../reports',
        '../data'
    ]
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            logger.info(f"✅ {dir_path} 디렉토리 존재")
        else:
            os.makedirs(dir_path, exist_ok=True)
            logger.info(f"📂 {dir_path} 디렉토리 생성됨")
    
    # 2. 모의 데이터 수집 테스트
    logger.info("\n🔍 모의 데이터 수집 테스트...")
    keywords = ['poker', 'holdem', 'wsop', 'wpt', 'ept', 'pokerstars', 'ggpoker', 'triton poker']
    all_videos = []
    
    for keyword in keywords[:3]:  # 테스트용으로 3개만
        videos = generate_mock_videos(keyword, 3)
        all_videos.extend(videos)
        logger.info(f"✅ '{keyword}' 키워드로 {len(videos)}개 영상 수집 (모의)")
    
    logger.info(f"\n📊 총 {len(all_videos)}개 영상 수집 완료")
    
    # 3. 데이터 분석 테스트
    logger.info("\n📈 데이터 분석 테스트...")
    
    # 조회수 통계
    total_views = sum(v['view_count'] for v in all_videos)
    avg_views = total_views // len(all_videos) if all_videos else 0
    
    logger.info(f"✅ 총 조회수: {total_views:,}")
    logger.info(f"✅ 평균 조회수: {avg_views:,}")
    
    # 채널별 통계
    channel_stats = {}
    for video in all_videos:
        channel = video['channel_title']
        if channel not in channel_stats:
            channel_stats[channel] = {'count': 0, 'views': 0}
        channel_stats[channel]['count'] += 1
        channel_stats[channel]['views'] += video['view_count']
    
    logger.info("\n🎬 TOP 채널:")
    for channel, stats in sorted(channel_stats.items(), key=lambda x: x[1]['views'], reverse=True)[:3]:
        logger.info(f"  - {channel}: {stats['count']}개 영상, {stats['views']:,} 조회")
    
    # 4. AI 인사이트 생성 테스트
    logger.info("\n🤖 AI 인사이트 생성 테스트...")
    for report_type in ['daily', 'weekly', 'monthly']:
        insights = generate_mock_ai_insights(report_type)
        logger.info(f"\n[{report_type.upper()} 인사이트]")
        logger.info(insights[:100] + "...")
    
    # 5. 리포트 저장 테스트
    logger.info("\n💾 리포트 저장 테스트...")
    report_data = {
        'report_type': 'test',
        'generated_at': datetime.now().isoformat(),
        'total_videos': len(all_videos),
        'keywords_analyzed': keywords[:3],
        'top_video': all_videos[0] if all_videos else None,
        'ai_insights': generate_mock_ai_insights('daily')
    }
    
    os.makedirs('../reports', exist_ok=True)
    report_file = f'../reports/test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        logger.info(f"✅ 테스트 리포트 저장 완료: {report_file}")
    except Exception as e:
        logger.error(f"❌ 리포트 저장 실패: {e}")
    
    # 6. Slack 메시지 포맷 테스트
    logger.info("\n📬 Slack 메시지 포맷 테스트...")
    slack_message = format_slack_message(all_videos[:5], generate_mock_ai_insights('daily'))
    logger.info("✅ Slack 메시지 포맷 생성 완료")
    logger.info(f"   메시지 블록 수: {len(slack_message['blocks'])}")
    
    return True

def format_slack_message(videos, ai_insights):
    """Slack 메시지 포맷팅"""
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🎰 포커 트렌드 테스트 리포트"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"📅 {datetime.now().strftime('%Y년 %m월 %d일')}\n"
                       f"📊 분석 영상: {len(videos)}개\n"
                       f"🧪 테스트 모드"
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*🤖 AI 인사이트*\n{ai_insights[:200]}..."
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*📺 TOP 영상*"
            }
        }
    ]
    
    # TOP 영상 추가
    for i, video in enumerate(videos[:3], 1):
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{i}. <{video['url']}|{video['title'][:50]}...>\n"
                       f"   조회수: {video['view_count']:,} | {video['channel_title']}"
            }
        })
    
    return {"blocks": blocks}

def main():
    """메인 테스트 실행"""
    logger.info("🚀 포커 트렌드 분석 시스템 모의 테스트 시작")
    logger.info(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("\n⚠️  주의: 이것은 모의 데이터를 사용한 구조 테스트입니다.")
    logger.info("실제 API 연결은 테스트하지 않습니다.\n")
    
    try:
        # 시스템 구조 테스트 실행
        success = test_system_structure()
        
        if success:
            logger.info("\n" + "=" * 50)
            logger.info("✅ 모든 구조 테스트가 성공적으로 완료되었습니다!")
            logger.info("=" * 50)
            
            logger.info("\n📋 다음 단계:")
            logger.info("1. 실제 API 키를 설정하여 test_integrated_analyzer.py 실행")
            logger.info("2. GitHub Actions 워크플로우 테스트")
            logger.info("3. 프로덕션 환경에서 자동 실행 확인")
            
            logger.info("\n💡 팁:")
            logger.info("- reports/ 폴더에서 생성된 테스트 리포트를 확인하세요")
            logger.info("- 실제 운영 시에는 API 할당량에 주의하세요")
            logger.info("- Slack 채널은 테스트용을 별도로 만드는 것을 권장합니다")
            
    except Exception as e:
        logger.error(f"\n❌ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()