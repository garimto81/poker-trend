#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
포커 콘텐츠 검증 모듈 테스트 스크립트
"""

import sys
from pathlib import Path

# 모듈 경로 추가
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from validators.poker_content_validator import PokerContentValidator, validate_single_video, filter_poker_videos

def test_poker_validator():
    """포커 콘텐츠 검증기 테스트"""
    print("포커 콘텐츠 검증기 테스트 시작")
    print("=" * 50)
    
    # 테스트 비디오 데이터 (실제 포커 관련)
    test_videos = [
        {
            'videoId': 'test1',
            'title': 'WSOP 2024 Main Event Final Table Highlights',
            'description': 'Watch the best moments from the WSOP 2024 Main Event final table with incredible poker action, big bluffs, and amazing calls.',
            'tags': ['poker', 'wsop', 'tournament'],
            'channelTitle': 'PokerGO',
            'channelId': 'test_channel_1',
            'categoryId': '20',  # Gaming
            'viewCount': '250000',
            'likeCount': '15000',
            'commentCount': '850',
            'duration': 'PT45M30S',
            'publishedAt': '2025-08-01T10:00:00Z'
        },
        {
            'videoId': 'test2',
            'title': 'Phil Ivey Incredible Bluff at Triton Poker',
            'description': 'Phil Ivey makes an incredible bluff against tough opponents in this high stakes cash game session.',
            'tags': ['poker', 'cash game', 'bluff'],
            'channelTitle': 'Triton Poker',
            'channelId': 'test_channel_2',
            'categoryId': '20',
            'viewCount': '180000',
            'likeCount': '12000',
            'commentCount': '650',
            'duration': 'PT25M15S',
            'publishedAt': '2025-08-02T14:00:00Z'
        },
        {
            'videoId': 'test3',
            'title': 'How to Cook Pasta - Easy Recipe',
            'description': 'Learn how to cook perfect pasta every time with this simple recipe and cooking tips.',
            'tags': ['cooking', 'recipe', 'pasta'],
            'channelTitle': 'Cooking Channel',
            'channelId': 'test_channel_3',
            'categoryId': '26',  # Howto & Style
            'viewCount': '50000',
            'likeCount': '2500',
            'commentCount': '150',
            'duration': 'PT10M00S',
            'publishedAt': '2025-08-03T16:00:00Z'
        },
        {
            'videoId': 'test4',
            'title': 'Poker Face Lady Gaga Cover',
            'description': 'My cover of Lady Gaga\'s Poker Face song with guitar and vocals.',
            'tags': ['cover', 'music', 'lady gaga'],
            'channelTitle': 'Music Covers',
            'channelId': 'test_channel_4',
            'categoryId': '10',  # Music
            'viewCount': '30000',
            'likeCount': '1500',
            'commentCount': '100',
            'duration': 'PT3M45S',
            'publishedAt': '2025-08-04T18:00:00Z'
        }
    ]
    
    # 1. 단일 비디오 검증 테스트
    print("1. 단일 비디오 검증 테스트")
    print("-" * 30)
    
    for i, video in enumerate(test_videos, 1):
        result = validate_single_video(video)
        print(f"{i}. {video['title'][:40]}...")
        print(f"   포커 콘텐츠: {'YES' if result['is_poker_content'] else 'NO'}")
        print(f"   신뢰도: {result['confidence']:.1%}")
        print(f"   점수: {result['total_score']:.1f}/100")
        print()
    
    # 2. 배치 검증 테스트
    print("2. 배치 검증 테스트")
    print("-" * 30)
    
    poker_videos = filter_poker_videos(test_videos)
    print(f"검증된 포커 콘텐츠: {len(poker_videos)}/{len(test_videos)}개")
    print()
    
    for i, video in enumerate(poker_videos, 1):
        validation = video.get('validation', {})
        print(f"{i}. {video['title'][:40]}...")
        print(f"   신뢰도: {validation.get('confidence', 0):.1%}")
        print(f"   신뢰도 레벨: {validation.get('confidence_level', 'unknown')}")
        print()
    
    # 3. 검증기 통계 확인
    print("3. 검증기 통계")
    print("-" * 30)
    
    validator = PokerContentValidator()
    stats = validator.get_validation_stats()
    
    if stats:
        print(f"총 검증: {stats.get('total_validations', 0)}개")
        print(f"포커 콘텐츠 감지: {stats.get('poker_content_detected', 0)}개")
        print(f"비포커 콘텐츠: {stats.get('non_poker_content_detected', 0)}개")
        print(f"캐시 히트: {stats.get('cache_hits', 0)}개")
    else:
        print("통계 데이터 없음")
    
    print("\n테스트 완료!")

if __name__ == "__main__":
    test_poker_validator()