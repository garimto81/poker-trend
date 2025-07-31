#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
바이럴 점수 및 참여율 계산 방법 상세 설명
"""

import math
import sys

# UTF-8 인코딩 설정
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def explain_viral_score():
    """바이럴 점수 계산 과정 설명"""
    
    # 실제 데이터: "I Won A WSOP Bracelet!!!" 비디오
    video_data = {
        'title': 'I Won A WSOP Bracelet!!!',
        'view_count': 30118,
        'like_count': 2085,
        'comment_count': 284,
        'keyword': 'WSOP'
    }
    
    print("=" * 80)
    print("바이럴 점수(Viral Score) 계산 방법 상세 설명")
    print("=" * 80)
    print(f"\n분석 대상 비디오: {video_data['title']}")
    print(f"키워드: {video_data['keyword']}")
    print("\n[원본 데이터]")
    print(f"조회수: {video_data['view_count']:,}")
    print(f"좋아요: {video_data['like_count']:,}")
    print(f"댓글: {video_data['comment_count']:,}")
    
    # 1. 참여율 계산
    engagement_rate = (video_data['like_count'] + video_data['comment_count']) / video_data['view_count']
    
    print("\n" + "=" * 80)
    print("1. 참여율(Engagement Rate) 계산")
    print("=" * 80)
    print("\n공식: 참여율 = (좋아요 + 댓글) / 조회수")
    print(f"\n계산 과정:")
    print(f"= ({video_data['like_count']} + {video_data['comment_count']}) / {video_data['view_count']}")
    print(f"= {video_data['like_count'] + video_data['comment_count']} / {video_data['view_count']}")
    print(f"= {engagement_rate:.6f}")
    print(f"= {engagement_rate * 100:.2f}%")
    
    # 평균 참여율과 비교
    avg_engagement = 0.0476  # 상위 10개 평균
    print(f"\n[비교 분석]")
    print(f"이 비디오 참여율: {engagement_rate * 100:.2f}%")
    print(f"상위 10개 평균 참여율: {avg_engagement * 100:.2f}%")
    print(f"평균 대비: {engagement_rate / avg_engagement:.2f}배")
    
    # 2. 바이럴 점수 계산
    print("\n" + "=" * 80)
    print("2. 바이럴 점수(Viral Score) 계산")
    print("=" * 80)
    print("\n공식: 바이럴 점수 = log₁₀(조회수) × 0.4 + 참여율×1000 × 0.3 + log₁₀(좋아요) × 0.2 + log₁₀(댓글) × 0.1")
    
    # 각 구성 요소 계산
    view_component = math.log10(video_data['view_count']) * 0.4
    engagement_component = engagement_rate * 1000 * 0.3
    like_component = math.log10(video_data['like_count']) * 0.2
    comment_component = math.log10(video_data['comment_count']) * 0.1
    
    print(f"\n[각 구성 요소 계산]")
    print(f"\n1) 조회수 구성 요소 (40% 가중치)")
    print(f"   = log₁₀({video_data['view_count']}) × 0.4")
    print(f"   = {math.log10(video_data['view_count']):.4f} × 0.4")
    print(f"   = {view_component:.4f}")
    
    print(f"\n2) 참여율 구성 요소 (30% 가중치)")
    print(f"   = {engagement_rate:.6f} × 1000 × 0.3")
    print(f"   = {engagement_rate * 1000:.4f} × 0.3")
    print(f"   = {engagement_component:.4f}")
    
    print(f"\n3) 좋아요 구성 요소 (20% 가중치)")
    print(f"   = log₁₀({video_data['like_count']}) × 0.2")
    print(f"   = {math.log10(video_data['like_count']):.4f} × 0.2")
    print(f"   = {like_component:.4f}")
    
    print(f"\n4) 댓글 구성 요소 (10% 가중치)")
    print(f"   = log₁₀({video_data['comment_count']}) × 0.1")
    print(f"   = {math.log10(video_data['comment_count']):.4f} × 0.1")
    print(f"   = {comment_component:.4f}")
    
    # 최종 바이럴 점수
    viral_score = view_component + engagement_component + like_component + comment_component
    
    print(f"\n[최종 바이럴 점수 계산]")
    print(f"= {view_component:.4f} + {engagement_component:.4f} + {like_component:.4f} + {comment_component:.4f}")
    print(f"= {viral_score:.2f}")
    
    # 3. 가중치 설명
    print("\n" + "=" * 80)
    print("3. 가중치 설명")
    print("=" * 80)
    print("\n각 요소별 가중치 의미:")
    print("- 조회수 (40%): 콘텐츠의 도달 범위와 인기도")
    print("- 참여율 (30%): 시청자의 적극적 반응과 콘텐츠 품질")
    print("- 좋아요 (20%): 긍정적 반응의 절대적 규모")
    print("- 댓글 (10%): 깊은 참여와 커뮤니티 상호작용")
    
    print("\n[로그 변환을 사용하는 이유]")
    print("- 큰 수치의 영향력을 적절히 조절")
    print("- 예: 100만 조회수와 1000 조회수의 차이를 합리적으로 반영")
    print("- log₁₀(1,000,000) = 6.0")
    print("- log₁₀(1,000) = 3.0")
    print("- 1000배 차이 → 2배 차이로 조정")
    
    # 4. 다른 비디오와 비교
    print("\n" + "=" * 80)
    print("4. 다른 비디오와 비교")
    print("=" * 80)
    
    comparison_videos = [
        {'title': 'GTO Strategy Video', 'viral_score': 18.68, 'views': 1554, 'engagement': 0.0566},
        {'title': 'Ultimate Texas Holdem', 'viral_score': 18.46, 'views': 7740, 'engagement': 0.0541},
        {'title': 'High Stakes Cash Game', 'viral_score': 12.63, 'views': 166426, 'engagement': 0.0318}
    ]
    
    print(f"\n현재 비디오: {video_data['title']}")
    print(f"바이럴 점수: {viral_score:.2f} | 조회수: {video_data['view_count']:,} | 참여율: {engagement_rate*100:.2f}%")
    
    print("\n비교 비디오:")
    for video in comparison_videos:
        print(f"- {video['title']}")
        print(f"  바이럴 점수: {video['viral_score']:.2f} | 조회수: {video['views']:,} | 참여율: {video['engagement']*100:.2f}%")
    
    print("\n[분석 인사이트]")
    print("- WSOP 비디오가 최고 바이럴 점수를 기록한 이유:")
    print("  1) 높은 참여율 (7.87%) - 평균의 1.65배")
    print("  2) 적절한 조회수 규모 (30,118)")
    print("  3) 많은 댓글 수 (284개) - 깊은 참여도")
    print("  4) 개인적 성취 스토리의 감정적 어필")

if __name__ == "__main__":
    explain_viral_score()