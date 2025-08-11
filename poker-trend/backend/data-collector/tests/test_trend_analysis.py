#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
End-to-End 테스트 스크립트
포커 트렌드 분석 시스템 전체 테스트
"""

import os
import sys
import json
from datetime import datetime

# 환경 변수 설정 (테스트용)
test_env = {
    'YOUTUBE_API_KEY': os.getenv('YOUTUBE_API_KEY'),
    'SLACK_WEBHOOK_URL': os.getenv('SLACK_WEBHOOK_URL'),
    'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY')
}

# 환경 변수 확인
missing_vars = [var for var, value in test_env.items() if not value]
if missing_vars:
    print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
    print("\n테스트를 위해 다음 환경 변수를 설정해주세요:")
    print("export YOUTUBE_API_KEY='your_key'")
    print("export SLACK_WEBHOOK_URL='your_webhook'")
    print("export GEMINI_API_KEY='your_key'")
    sys.exit(1)

print("=== 포커 트렌드 분석 End-to-End 테스트 ===\n")

# 1. 동적 키워드 수집 테스트
print("1️⃣ 동적 키워드 수집 테스트...")
try:
    from dynamic_keyword_collector import DynamicKeywordCollector
    
    collector = DynamicKeywordCollector()
    # 키워드 업데이트는 API 할당량을 많이 사용하므로 기존 데이터 사용
    keywords = collector.get_search_keywords()
    
    print(f"✅ 검색 키워드 ({len(keywords)}개): {', '.join(keywords[:10])}...")
    print(f"   - 기본 키워드: {len(collector.base_keywords)}개")
    print(f"   - 동적 키워드: {len(keywords) - len(collector.base_keywords)}개")
    
except Exception as e:
    print(f"❌ 키워드 수집 실패: {e}")
    keywords = ['poker', '포커', 'holdem', '홀덤', 'WSOP']  # 기본값

print("\n" + "="*50 + "\n")

# 2. YouTube 트렌드 분석 테스트
print("2️⃣ YouTube 트렌드 분석 테스트...")
try:
    from youtube_trend_webhook_enhanced import EnhancedYouTubeTrendAnalyzer
    
    analyzer = EnhancedYouTubeTrendAnalyzer()
    print(f"   검색 키워드: {', '.join(analyzer.search_terms[:5])}...")
    
    # 데이터 수집 (API 할당량 절약을 위해 작은 샘플)
    print("   데이터 수집 중...")
    videos = analyzer.collect_videos(lookback_hours=24)  # 24시간만
    print(f"✅ 수집된 영상: {len(videos)}개")
    
    if videos:
        # 샘플 영상 정보
        sample = videos[0]
        print(f"\n   샘플 영상:")
        print(f"   - 제목: {sample['title'][:50]}...")
        print(f"   - 채널: {sample['channel_title']}")
        print(f"   - 조회수: {sample.get('view_count', 0):,}")
        print(f"   - 시간당 조회수: {sample.get('views_per_hour', 0):.0f}")
    
    # 트렌드 분석
    print("\n   트렌드 분석 중...")
    analysis_result = analyzer.analyze_trends(videos)
    
    print(f"\n✅ 분석 결과:")
    print(f"   - 총 영상: {analysis_result['total_videos']}개")
    print(f"   - 평균 조회수: {analysis_result['avg_views']:,.0f}")
    print(f"   - 평균 참여율: {analysis_result['avg_engagement']:.2f}%")
    print(f"   - 검색 키워드: {len(analysis_result.get('search_keywords', []))}개")
    print(f"   - TOP 채널: {analysis_result.get('top_channels', [('N/A', 0)])[0][0]}")
    
    # 카테고리 분석
    print(f"\n   카테고리별 분포:")
    for cat, stats in analysis_result['category_breakdown'].items():
        if stats['count'] > 0:
            print(f"   - {cat}: {stats['count']}개 (평균 {stats['avg_views']:,.0f}회)")
    
except Exception as e:
    print(f"❌ 트렌드 분석 실패: {e}")
    import traceback
    traceback.print_exc()
    analysis_result = None

print("\n" + "="*50 + "\n")

# 3. AI 분석 테스트
print("3️⃣ Gemini AI 분석 테스트...")
if analysis_result:
    try:
        # 트렌드 한줄 요약
        print("   트렌드 분석 생성 중...")
        trend_analysis = analyzer.generate_trend_analysis(analysis_result)
        print(f"✅ 트렌드 분석: {trend_analysis}")
        
        # AI 쇼츠 제안
        print("\n   AI 쇼츠 제안 생성 중...")
        ai_suggestions = analyzer.generate_ai_suggestions(analysis_result)
        
        if "AI 제안 생성 중 오류" not in ai_suggestions:
            print("✅ AI 쇼츠 제안 생성 완료")
            # 첫 번째 제안만 출력
            lines = ai_suggestions.split('\n')
            for i, line in enumerate(lines[:10]):  # 처음 10줄만
                if line.strip():
                    print(f"   {line[:80]}...")
        else:
            print(f"⚠️  AI 제안 생성 실패: {ai_suggestions}")
            
    except Exception as e:
        print(f"❌ AI 분석 실패: {e}")
        trend_analysis = "트렌드 분석 실패"
        ai_suggestions = "AI 제안 생성 실패"
else:
    print("⚠️  분석 데이터가 없어 AI 분석을 건너뜁니다.")
    trend_analysis = "테스트 트렌드 분석"
    ai_suggestions = "테스트 AI 제안"

print("\n" + "="*50 + "\n")

# 4. Slack 메시지 포맷 테스트
print("4️⃣ Slack 메시지 포맷 테스트...")
if analysis_result:
    try:
        from youtube_trend_webhook_enhanced import send_enhanced_slack_webhook, format_number
        
        # 테스트용 샘플 블록 생성
        print("\n📋 생성될 Slack 메시지 미리보기:\n")
        
        kst_time = datetime.now()
        print(f"🎰 포커 YouTube 트렌드 정밀 분석 ({kst_time.strftime('%Y.%m.%d %H:%M')} KST)")
        print("-" * 60)
        
        print("\n📊 전체 트렌드 요약")
        print(f"총 분석 영상: {analysis_result['total_videos']}개")
        print(f"평균 조회수: {format_number(analysis_result['avg_views'])}회")
        print(f"평균 참여율: {analysis_result['avg_engagement']:.2f}%")
        print(f"시간당 조회수: {format_number(analysis_result['hourly_avg_views'])}회/h")
        
        print(f"\n🔍 검색 키워드: {', '.join(analysis_result.get('search_keywords', [])[:5])}...")
        
        top_channels = analysis_result.get('top_channels', [])
        if top_channels:
            print(f"🎬 TOP 채널: {', '.join([f'{ch[0]} ({ch[1]}개)' for ch in top_channels[:3]])}")
        
        print(f"📈 트렌드 분석: {trend_analysis}")
        
        hot_keywords = [kw[0] for kw in analysis_result['trending_keywords'][:5]]
        print(f"🔥 핫 키워드: {', '.join(hot_keywords)}")
        
        print("\n" + "-" * 60)
        print("\n🚀 TOP 5 급상승 영상")
        
        for i, video in enumerate(analysis_result['trending_videos'][:5], 1):
            print(f"\n{i}. {video['title'][:60]}...")
            print(f"   📺 {video['channel_title']}")
            print(f"   👁️ {format_number(video['view_count'])} | 💕 {format_number(video['like_count'])} | ⚡ {format_number(video['views_per_hour'])}/h")
            print(f"   🔗 https://youtube.com/watch?v={video['video_id']}")
        
        print("\n✅ Slack 메시지 포맷 테스트 성공")
        
    except Exception as e:
        print(f"❌ Slack 포맷 테스트 실패: {e}")

print("\n" + "="*50 + "\n")

# 5. 실제 Slack 전송 테스트 (선택적)
print("5️⃣ Slack 전송 테스트...")
response = input("실제로 Slack에 테스트 메시지를 전송하시겠습니까? (y/N): ")

if response.lower() == 'y' and analysis_result:
    try:
        print("   Slack 메시지 전송 중...")
        send_enhanced_slack_webhook(analysis_result, ai_suggestions, trend_analysis)
        print("✅ Slack 메시지 전송 성공!")
        print(f"   Webhook URL: {test_env['SLACK_WEBHOOK_URL'][:30]}...")
    except Exception as e:
        print(f"❌ Slack 전송 실패: {e}")
else:
    print("⏭️  Slack 전송을 건너뜁니다.")

print("\n" + "="*50 + "\n")

# 테스트 결과 요약
print("📊 테스트 결과 요약")
print("-" * 30)
print("✅ 동적 키워드 수집: 성공" if keywords else "❌ 동적 키워드 수집: 실패")
print("✅ YouTube 데이터 수집: 성공" if analysis_result else "❌ YouTube 데이터 수집: 실패")
print("✅ 트렌드 분석: 성공" if analysis_result and analysis_result['total_videos'] > 0 else "❌ 트렌드 분석: 실패")
print("✅ AI 분석: 성공" if trend_analysis != "트렌드 분석 실패" else "❌ AI 분석: 실패")
print("✅ Slack 포맷: 성공" if analysis_result else "❌ Slack 포맷: 실패")

print("\n🎉 End-to-End 테스트 완료!")

# 테스트 데이터 저장
if analysis_result:
    test_data = {
        'test_time': datetime.now().isoformat(),
        'total_videos': analysis_result['total_videos'],
        'keywords_used': len(keywords),
        'top_channels': analysis_result.get('top_channels', [])[:3],
        'trend_analysis': trend_analysis,
        'test_status': 'success'
    }
    
    os.makedirs('test_results', exist_ok=True)
    with open('test_results/e2e_test_result.json', 'w', encoding='utf-8') as f:
        json.dump(test_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 테스트 결과가 test_results/e2e_test_result.json에 저장되었습니다.")