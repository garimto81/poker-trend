#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
정량적 포커 트렌드 분석 - 직관적 표시
모든 콘텐츠 정보에 정량 데이터 포함
"""

import json
import sys
from datetime import datetime

# UTF-8 인코딩 설정
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def load_data():
    """데이터 로드"""
    with open('quantitative_poker_analysis_20250730_190913.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def display_header(data):
    """헤더 정보 표시"""
    print("=" * 150)
    print("📊 포커 트렌드 정량적 분석 리포트")
    print("=" * 150)
    print(f"분석 시간: {data['metadata']['analysis_time']}")
    print(f"총 비디오: {data['metadata']['total_videos_analyzed']}개")
    print(f"분석 키워드: {', '.join(data['metadata']['target_keywords'])}")
    print()

def calculate_totals(videos):
    """전체 통계 계산"""
    total_views = sum(v['view_count'] for v in videos)
    total_likes = sum(v['like_count'] for v in videos)
    total_comments = sum(v.get('comment_count', 0) for v in videos)
    avg_engagement = sum(v['engagement_rate'] for v in videos) / len(videos)
    
    return {
        'total_views': total_views,
        'total_likes': total_likes,
        'total_comments': total_comments,
        'avg_engagement': avg_engagement
    }

def display_overview(videos):
    """전체 개요"""
    stats = calculate_totals(videos)
    
    print("【 전체 성과 지표 】")
    print(f"├─ 총 조회수: {stats['total_views']:,} ({stats['total_views']/1000000:.1f}M views)")
    print(f"├─ 총 좋아요: {stats['total_likes']:,} ({stats['total_likes']/1000:.1f}K likes)")
    print(f"├─ 총 댓글: {stats['total_comments']:,}")
    print(f"└─ 평균 참여율: {stats['avg_engagement']*100:.2f}%")
    print()

def display_top_videos(videos, n=20):
    """TOP N 비디오 표시 - 모든 정량 데이터 포함"""
    print("=" * 150)
    print(f"🏆 TOP {n} 비디오 분석 (바이럴 점수 순위)")
    print("=" * 150)
    
    # 헤더
    print(f"{'#':<3} {'제목':<60} {'조회수':>10} {'좋아요':>8} {'댓글':>6} {'참여율':>8} {'바이럴':>8} {'키워드':<10}")
    print("-" * 150)
    
    # 바이럴 점수로 정렬
    sorted_videos = sorted(videos, key=lambda x: x['viral_score'], reverse=True)[:n]
    
    for i, video in enumerate(sorted_videos, 1):
        # 제목 자르기
        title = video['title']
        if len(title) > 57:
            title = title[:57] + "..."
        
        # 데이터 표시
        print(f"{i:<3} {title:<60} {video['view_count']:>10,} {video['like_count']:>8,} "
              f"{video.get('comment_count', 0):>6,} {video['engagement_rate']*100:>7.1f}% "
              f"{video['viral_score']:>8.1f} {video['keyword_matched']:<10}")
        
        # 추가 인사이트 (매 5개마다)
        if i % 5 == 0 and i < n:
            print()

def display_keyword_analysis(videos):
    """키워드별 정량 분석"""
    print("\n" + "=" * 150)
    print("📈 키워드별 정량적 성과 비교")
    print("=" * 150)
    
    # 키워드별 데이터 집계
    keyword_stats = {}
    for video in videos:
        keyword = video['keyword_matched']
        if keyword not in keyword_stats:
            keyword_stats[keyword] = {
                'count': 0,
                'total_views': 0,
                'total_likes': 0,
                'total_comments': 0,
                'engagement_rates': [],
                'viral_scores': []
            }
        
        stats = keyword_stats[keyword]
        stats['count'] += 1
        stats['total_views'] += video['view_count']
        stats['total_likes'] += video['like_count']
        stats['total_comments'] += video.get('comment_count', 0)
        stats['engagement_rates'].append(video['engagement_rate'])
        stats['viral_scores'].append(video['viral_score'])
    
    # 평균 계산 및 표시
    print(f"{'키워드':<12} {'비디오':<6} {'총조회수':>12} {'평균조회수':>12} {'총좋아요':>10} {'평균참여율':>10} {'평균바이럴':>10}")
    print("-" * 150)
    
    # 평균 바이럴 점수로 정렬
    sorted_keywords = sorted(keyword_stats.items(), 
                           key=lambda x: sum(x[1]['viral_scores'])/len(x[1]['viral_scores']), 
                           reverse=True)
    
    for keyword, stats in sorted_keywords:
        avg_views = stats['total_views'] // stats['count']
        avg_engagement = sum(stats['engagement_rates']) / len(stats['engagement_rates'])
        avg_viral = sum(stats['viral_scores']) / len(stats['viral_scores'])
        
        print(f"{keyword:<12} {stats['count']:<6} {stats['total_views']:>12,} {avg_views:>12,} "
              f"{stats['total_likes']:>10,} {avg_engagement*100:>9.2f}% {avg_viral:>10.2f}")

def display_engagement_leaders(videos):
    """참여율 TOP 10 - 진짜 인기 콘텐츠"""
    print("\n" + "=" * 150)
    print("💎 참여율 TOP 10 (진정한 시청자 관심도)")
    print("=" * 150)
    
    sorted_by_engagement = sorted(videos, key=lambda x: x['engagement_rate'], reverse=True)[:10]
    
    print(f"{'#':<3} {'제목':<55} {'조회수':>10} {'좋아요':>8} {'댓글':>6} {'참여율':>8} {'좋아요율':>9}")
    print("-" * 150)
    
    for i, video in enumerate(sorted_by_engagement, 1):
        title = video['title'][:52] + "..." if len(video['title']) > 55 else video['title']
        like_rate = video['like_rate'] * 100
        
        print(f"{i:<3} {title:<55} {video['view_count']:>10,} {video['like_count']:>8,} "
              f"{video.get('comment_count', 0):>6,} {video['engagement_rate']*100:>7.1f}% "
              f"{like_rate:>8.1f}%")

def display_view_champions(videos):
    """조회수 TOP 10 - 대중적 인기"""
    print("\n" + "=" * 150)
    print("👀 조회수 TOP 10 (대중적 도달력)")
    print("=" * 150)
    
    sorted_by_views = sorted(videos, key=lambda x: x['view_count'], reverse=True)[:10]
    
    print(f"{'#':<3} {'제목':<55} {'조회수':>12} {'좋아요':>8} {'댓글':>6} {'참여율':>8} {'키워드':<10}")
    print("-" * 150)
    
    for i, video in enumerate(sorted_by_views, 1):
        title = video['title'][:52] + "..." if len(video['title']) > 55 else video['title']
        
        print(f"{i:<3} {title:<55} {video['view_count']:>12,} {video['like_count']:>8,} "
              f"{video.get('comment_count', 0):>6,} {video['engagement_rate']*100:>7.1f}% "
              f"{video['keyword_matched']:<10}")

def display_key_insights(videos):
    """핵심 인사이트"""
    print("\n" + "=" * 150)
    print("💡 정량 데이터 기반 핵심 인사이트")
    print("=" * 150)
    
    # 1. 스위트 스팟 찾기
    high_engagement = [v for v in videos if v['engagement_rate'] > 0.04]
    medium_views = [v for v in videos if 10000 <= v['view_count'] <= 100000]
    
    print("\n1. 【최적 콘텐츠 구간】")
    print(f"   - 고참여율(4%+) 비디오: {len(high_engagement)}개")
    if high_engagement:
        avg_views = sum(v['view_count'] for v in high_engagement) / len(high_engagement)
        print(f"   - 고참여율 비디오 평균 조회수: {avg_views:,.0f} (스위트 스팟)")
    
    print(f"   - 중간 조회수(1-10만) 비디오: {len(medium_views)}개")
    if medium_views:
        avg_engagement = sum(v['engagement_rate'] for v in medium_views) / len(medium_views)
        print(f"   - 중간 조회수 비디오 평균 참여율: {avg_engagement*100:.2f}%")
    
    # 2. 바이럴 공식
    print("\n2. 【바이럴 점수 공식】")
    print("   바이럴 = log(조회수)×0.4 + 참여율×1000×0.3 + log(좋아요)×0.2 + log(댓글)×0.1")
    print("   → 조회수만 높다고 바이럴이 아님, 참여율이 핵심!")
    
    # 3. 키워드 효율성
    print("\n3. 【키워드 효율성 순위】 (참여율 × 바이럴 점수)")
    keyword_efficiency = {}
    for video in videos:
        keyword = video['keyword_matched']
        if keyword not in keyword_efficiency:
            keyword_efficiency[keyword] = []
        keyword_efficiency[keyword].append(video['engagement_rate'] * video['viral_score'])
    
    efficiency_scores = []
    for keyword, scores in keyword_efficiency.items():
        avg_efficiency = sum(scores) / len(scores)
        efficiency_scores.append((keyword, avg_efficiency))
    
    efficiency_scores.sort(key=lambda x: x[1], reverse=True)
    for i, (keyword, score) in enumerate(efficiency_scores[:5], 1):
        print(f"   {i}. {keyword}: {score:.2f}")

def create_slack_summary(data):
    """Slack용 간결한 요약"""
    print("\n" + "=" * 150)
    print("📱 Slack 일일 리포트 (복사용)")
    print("=" * 150)
    
    videos = data['videos']
    stats = calculate_totals(videos)
    top3 = sorted(videos, key=lambda x: x['viral_score'], reverse=True)[:3]
    
    summary = f"""🎯 포커 트렌드 일일 분석 - {datetime.now().strftime('%Y-%m-%d')}

📊 전체 성과
• 분석 비디오: {len(videos)}개
• 총 조회수: {stats['total_views']:,} ({stats['total_views']/1000000:.1f}M)
• 평균 참여율: {stats['avg_engagement']*100:.2f}%

🏆 TOP 3 바이럴 비디오
"""
    
    for i, video in enumerate(top3, 1):
        summary += f"\n{i}. {video['title'][:50]}..."
        summary += f"\n   📊 조회수: {video['view_count']:,} | 👍 {video['like_count']:,} | 💬 {video.get('comment_count', 0):,}"
        summary += f"\n   📈 참여율: {video['engagement_rate']*100:.1f}% | 🔥 바이럴: {video['viral_score']:.1f}\n"
    
    print(summary)
    return summary

def main():
    # 데이터 로드
    data = load_data()
    videos = data['videos']
    
    # 1. 헤더
    display_header(data)
    
    # 2. 전체 개요
    display_overview(videos)
    
    # 3. TOP 20 비디오 (모든 정량 데이터 포함)
    display_top_videos(videos, n=20)
    
    # 4. 키워드별 분석
    display_keyword_analysis(videos)
    
    # 5. 참여율 리더
    display_engagement_leaders(videos)
    
    # 6. 조회수 챔피언
    display_view_champions(videos)
    
    # 7. 핵심 인사이트
    display_key_insights(videos)
    
    # 8. Slack 요약
    create_slack_summary(data)

if __name__ == "__main__":
    main()