# -*- coding: utf-8 -*-
"""
정량적 분석 결과 표시기
"""

import json
import os
from datetime import datetime

def load_latest_quantitative_analysis():
    """최신 정량적 분석 결과 로드"""
    files = [f for f in os.listdir('.') if f.startswith('quantitative_poker_analysis_')]
    if not files:
        return None
    
    latest_file = max(files, key=lambda x: os.path.getctime(x))
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        return json.load(f), latest_file

def display_quantitative_results():
    """정량적 분석 결과 표시"""
    data, filename = load_latest_quantitative_analysis()
    if not data:
        print("정량적 분석 결과를 찾을 수 없습니다.")
        return
    
    print("포커 트렌드 정량적 분석 결과")
    print("=" * 60)
    print(f"파일: {filename}")
    print(f"분석 시간: {data['metadata']['analysis_time']}")
    print(f"분석 비디오 수: {data['metadata']['total_videos_analyzed']}개")
    
    analysis = data.get('quantitative_analysis', {})
    basic_stats = analysis.get('basic_statistics', {})
    
    print("\n기본 통계 지표")
    print("-" * 30)
    print(f"총 조회수: {basic_stats.get('total_views', 0):,}")
    print(f"총 좋아요: {basic_stats.get('total_likes', 0):,}")
    print(f"총 댓글: {basic_stats.get('total_comments', 0):,}")
    print(f"평균 조회수: {basic_stats.get('avg_views', 0):,.0f}")
    print(f"평균 참여율: {basic_stats.get('avg_engagement_rate', 0):.4f}")
    print(f"평균 좋아요율: {basic_stats.get('avg_like_rate', 0):.4f}")
    print(f"평균 댓글율: {basic_stats.get('avg_comment_rate', 0):.4f}")
    
    keyword_analysis = analysis.get('keyword_analysis', {})
    
    print("\n키워드별 성과 순위 (바이럴 점수 기준)")
    print("-" * 50)
    
    # 키워드를 바이럴 점수로 정렬
    sorted_keywords = sorted(
        keyword_analysis.items(),
        key=lambda x: x[1]['avg_viral_score'],
        reverse=True
    )
    
    for rank, (keyword, stats) in enumerate(sorted_keywords, 1):
        print(f"{rank}위. {keyword}")
        print(f"    비디오 수: {stats['video_count']}개")
        print(f"    평균 조회수: {stats['avg_views']:,.0f}")
        print(f"    평균 참여율: {stats['avg_engagement_rate']:.4f}")
        print(f"    바이럴 점수: {stats['avg_viral_score']:.2f}")
        print(f"    시장 점유율: {stats['market_share']:.1%}")
        print()
    
    trend_strength = analysis.get('trend_strength', {})
    print("트렌드 강도 분석")
    print("-" * 30)
    
    for keyword, strength in trend_strength.items():
        direction = strength['trend_direction']
        emoji = "상승" if direction == 'rising' else "안정" if direction == 'stable' else "하락"
        print(f"{keyword}: {emoji} (모멘텀: {strength['momentum_score']:.2f})")
    
    correlations = analysis.get('correlation_analysis', {})
    print(f"\n상관관계 분석")
    print("-" * 30)
    print(f"조회수 vs 참여율: {correlations.get('views_vs_engagement', 0):.3f}")
    print(f"좋아요 vs 댓글수: {correlations.get('likes_vs_comments', 0):.3f}")
    print(f"바이럴점수 vs 모멘텀: {correlations.get('viral_vs_momentum', 0):.3f}")
    print(f"관련성 vs 성과: {correlations.get('relevance_vs_performance', 0):.3f}")
    
    top_performers = analysis.get('top_performers', [])
    print(f"\n상위 성과 비디오 (바이럴 점수 기준)")
    print("-" * 50)
    
    for performer in top_performers[:5]:
        print(f"{performer['rank']}위. {performer['keyword']}")
        print(f"    조회수: {performer['views']:,}")
        print(f"    좋아요: {performer['likes']:,}")
        print(f"    댓글: {performer['comments']:,}")
        print(f"    참여율: {performer['engagement_rate']:.4f}")
        print(f"    바이럴점수: {performer['viral_score']:.2f}")
        print()
    
    insights = analysis.get('quantitative_insights', [])
    print("정량적 핵심 인사이트")
    print("-" * 30)
    
    insight_names = {
        'performance_leader': '최고 성과 키워드',
        'momentum_leader': '최고 모멘텀 키워드', 
        'engagement_leader': '최고 참여도 키워드',
        'market_leader': '시장 점유율 1위'
    }
    
    for insight in insights:
        name = insight_names.get(insight['type'], insight['type'])
        print(f"{name}: {insight['keyword']} (값: {insight['value']:.4f})")
    
    print(f"\n분석 방법론")
    print("-" * 30)
    print("- 참여율 = (좋아요 + 댓글) / 조회수")
    print("- 바이럴점수 = log10(조회수)×0.4 + 참여율×1000×0.3 + log10(좋아요)×0.2 + log10(댓글)×0.1")
    print("- 트렌드모멘텀 = 키워드상대성과 × 개별비디오성과")
    print("- K-means 클러스터링 적용")
    print("- 95% 신뢰구간 기준 통계 분석")

if __name__ == "__main__":
    display_quantitative_results()