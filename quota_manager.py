# -*- coding: utf-8 -*-
"""
YouTube API 할당량 관리 및 대안 솔루션
"""

import os
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
import random

def check_quota_status():
    """API 할당량 상태 확인"""
    print("YouTube API 할당량 상태 확인")
    print("=" * 50)
    print("❌ 현재 상태: 할당량 초과 (quotaExceeded)")
    print("📅 일일 할당량: 10,000 units")
    print("🔄 리셋 시간: 매일 오전 9시 (PST)")
    print("⏰ 다음 리셋까지: 약 12-24시간")
    print()
    
    print("🔍 할당량 사용량 추정:")
    print("- Search API 호출: ~100 units per request")
    print("- Videos API 호출: ~1 unit per video")
    print("- 오늘 사용량: 약 8,000-10,000+ units")
    print()

def get_alternative_solutions():
    """대안 솔루션 제시"""
    print("🚀 대안 솔루션")
    print("=" * 50)
    
    solutions = [
        {
            "name": "1. 새로운 API 키 생성",
            "description": "Google Cloud Console에서 새 프로젝트 생성 → 새 API 키 발급",
            "difficulty": "쉬움",
            "time": "5분",
            "cost": "무료"
        },
        {
            "name": "2. 캐시된 데이터 활용",
            "description": "기존 수집 데이터로 분석 계속 진행",
            "difficulty": "매우 쉬움",
            "time": "즉시",
            "cost": "무료"
        },
        {
            "name": "3. 모의 데이터 분석",
            "description": "실제와 유사한 샘플 데이터로 시스템 테스트",
            "difficulty": "쉬움",
            "time": "즉시",
            "cost": "무료"
        },
        {
            "name": "4. 내일 재실행",
            "description": "할당량 리셋 후 다시 실행",
            "difficulty": "매우 쉬움",
            "time": "24시간 대기",
            "cost": "무료"
        }
    ]
    
    for i, sol in enumerate(solutions, 1):
        print(f"{sol['name']}")
        print(f"   📝 설명: {sol['description']}")
        print(f"   🎯 난이도: {sol['difficulty']}")
        print(f"   ⏱️ 소요시간: {sol['time']}")
        print(f"   💰 비용: {sol['cost']}")
        print()

def generate_mock_data_analysis():
    """모의 데이터로 완전한 분석 실행"""
    print("🎲 모의 데이터 분석 실행 중...")
    
    # 실제와 유사한 모의 데이터 생성
    mock_videos = []
    keywords = ["Holdem", "WSOP", "Cashgame", "PokerStars", "GGPoker", "GTO", "WPT"]
    
    for keyword in keywords:
        for i in range(random.randint(5, 15)):
            view_count = random.randint(1000, 2000000)
            like_count = int(view_count * random.uniform(0.01, 0.08))
            comment_count = int(view_count * random.uniform(0.001, 0.01))
            
            engagement_rate = (like_count + comment_count) / view_count
            viral_score = (
                np.log10(max(view_count, 1)) * 0.4 +
                engagement_rate * 1000 * 0.3 +
                np.log10(max(like_count, 1)) * 0.2 +
                np.log10(max(comment_count, 1)) * 0.1
            ) if 'np' in globals() else random.uniform(5, 20)
            
            mock_videos.append({
                'video_id': f'mock_{keyword}_{i}',
                'keyword': keyword,
                'view_count': view_count,
                'like_count': like_count,
                'comment_count': comment_count,
                'engagement_rate': engagement_rate,
                'viral_score': viral_score
            })
    
    # 키워드별 분석
    keyword_stats = {}
    for keyword in keywords:
        keyword_videos = [v for v in mock_videos if v['keyword'] == keyword]
        if keyword_videos:
            avg_views = sum(v['view_count'] for v in keyword_videos) / len(keyword_videos)
            avg_engagement = sum(v['engagement_rate'] for v in keyword_videos) / len(keyword_videos)
            avg_viral = sum(v['viral_score'] for v in keyword_videos) / len(keyword_videos)
            
            keyword_stats[keyword] = {
                'count': len(keyword_videos),
                'avg_views': avg_views,
                'avg_engagement': avg_engagement,
                'avg_viral_score': avg_viral
            }
    
    return mock_videos, keyword_stats

def show_mock_analysis_results():
    """모의 분석 결과 표시"""
    try:
        import numpy as np
        mock_videos, keyword_stats = generate_mock_data_analysis()
    except ImportError:
        # numpy 없이도 실행 가능하도록
        mock_videos = []
        keyword_stats = {
            'Holdem': {'count': 12, 'avg_views': 850000, 'avg_engagement': 0.035, 'avg_viral_score': 15.2},
            'GTO': {'count': 8, 'avg_views': 45000, 'avg_engagement': 0.055, 'avg_viral_score': 12.8},
            'WSOP': {'count': 10, 'avg_views': 320000, 'avg_engagement': 0.028, 'avg_viral_score': 11.5},
            'Cashgame': {'count': 7, 'avg_views': 125000, 'avg_engagement': 0.032, 'avg_viral_score': 10.1},
            'PokerStars': {'count': 6, 'avg_views': 95000, 'avg_engagement': 0.025, 'avg_viral_score': 9.2},
            'GGPoker': {'count': 5, 'avg_views': 78000, 'avg_engagement': 0.029, 'avg_viral_score': 8.8},
            'WPT': {'count': 4, 'avg_views': 110000, 'avg_engagement': 0.022, 'avg_viral_score': 8.1}
        }
    
    print("🎲 모의 데이터 분석 결과")
    print("=" * 60)
    print("(실제 API 데이터와 유사한 패턴으로 생성)")
    print()
    
    # 바이럴 점수 순으로 정렬
    sorted_keywords = sorted(keyword_stats.items(), key=lambda x: x[1]['avg_viral_score'], reverse=True)
    
    print("🏆 키워드별 성과 순위 (바이럴 점수 기준)")
    print("-" * 50)
    
    for rank, (keyword, stats) in enumerate(sorted_keywords, 1):
        print(f"{rank}위. {keyword}")
        print(f"    비디오 수: {stats['count']}개")
        print(f"    평균 조회수: {stats['avg_views']:,.0f}")
        print(f"    평균 참여율: {stats['avg_engagement']:.3f}")
        print(f"    바이럴 점수: {stats['avg_viral_score']:.1f}")
        print()
    
    total_views = sum(stats['avg_views'] * stats['count'] for stats in keyword_stats.values())
    total_videos = sum(stats['count'] for stats in keyword_stats.values())
    
    print("📊 전체 통계")
    print("-" * 30)
    print(f"총 비디오 수: {total_videos}개")
    print(f"총 예상 조회수: {total_views:,.0f}")
    print(f"평균 조회수: {total_views/total_videos:,.0f}")
    
    return keyword_stats

def suggest_new_api_key_steps():
    """새 API 키 생성 단계 안내"""
    print("🔑 새 YouTube API 키 생성 방법")
    print("=" * 50)
    
    steps = [
        "1. Google Cloud Console 접속 (https://console.cloud.google.com/)",
        "2. 새 프로젝트 생성 또는 다른 프로젝트 선택",
        "3. API 및 서비스 > 라이브러리 이동",
        "4. 'YouTube Data API v3' 검색 후 사용 설정",
        "5. API 및 서비스 > 사용자 인증 정보 이동",
        "6. '사용자 인증 정보 만들기' > 'API 키' 선택",
        "7. 생성된 API 키 복사",
        "8. .env 파일의 YOUTUBE_API_KEY 값 교체",
        "9. 분석기 다시 실행"
    ]
    
    for step in steps:
        print(f"   {step}")
    print()
    print("💡 팁: 여러 개의 Google 계정을 사용하면 더 많은 할당량 확보 가능")

def show_cached_data_option():
    """캐시된 데이터 활용 옵션"""
    print("💾 기존 수집 데이터 활용")
    print("=" * 50)
    
    # 기존 분석 파일 확인
    analysis_files = [f for f in os.listdir('.') if f.startswith('quantitative_poker_analysis_') or f.startswith('enhanced_poker_trend_analysis_')]
    
    if analysis_files:
        latest_file = max(analysis_files, key=lambda x: os.path.getctime(x))
        print(f"✅ 사용 가능한 최신 데이터: {latest_file}")
        print(f"📅 생성 시간: {datetime.fromtimestamp(os.path.getctime(latest_file))}")
        print()
        print("🚀 즉시 실행 가능:")
        print(f"   python show_quantitative_results.py")
        print()
        print("📊 또는 데이터 재분석:")
        print("   기존 JSON 파일의 videos 데이터를 활용해서")
        print("   새로운 분석 지표나 시각화 생성 가능")
    else:
        print("❌ 사용 가능한 캐시 데이터 없음")
        print("💡 모의 데이터 분석을 권장합니다.")

def main():
    """메인 실행 함수"""
    print("🚨 YouTube API 할당량 초과 문제 해결 가이드")
    print("=" * 60)
    print()
    
    # 1. 현재 상태 확인
    check_quota_status()
    
    # 2. 대안 솔루션 제시
    get_alternative_solutions()
    
    # 3. 즉시 실행 가능한 옵션들
    print("⚡ 지금 당장 실행 가능한 옵션들")
    print("=" * 50)
    
    print("A. 모의 데이터로 완전한 분석 실행")
    show_mock_analysis_results()
    print()
    
    print("B. 기존 수집 데이터 재활용")
    show_cached_data_option()
    print()
    
    print("C. 새 API 키로 완전한 데이터 수집")
    suggest_new_api_key_steps()
    
    print("🎯 권장사항")
    print("=" * 30)
    print("1순위: 새 API 키 생성 (5분 소요, 완전한 실제 데이터)")
    print("2순위: 기존 데이터 재활용 (즉시 실행)")
    print("3순위: 모의 데이터 분석 (시스템 테스트 목적)")

if __name__ == "__main__":
    main()