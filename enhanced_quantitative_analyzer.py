#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
향상된 정량적 포커 트렌드 분석기
- 제목과 함께 모든 정량 데이터 표시
- 직관적이고 명확한 데이터 시각화
"""

import json
import os
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai
import sys

# UTF-8 인코딩 설정
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class EnhancedQuantitativeAnalyzer:
    def __init__(self):
        load_dotenv()
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def load_latest_data(self):
        """최신 분석 데이터 로드"""
        with open('quantitative_poker_analysis_20250730_190913.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def display_quantitative_overview(self, data):
        """정량적 개요 표시"""
        print("=" * 120)
        print("📊 포커 트렌드 정량적 분석 대시보드")
        print("=" * 120)
        print(f"분석 일시: {data['metadata']['analysis_time']}")
        print(f"총 분석 비디오: {len(data['videos'])}개")
        print()
        
        # 전체 통계
        stats = data['aggregate_stats']
        print("【 전체 성과 지표 】")
        print(f"├─ 총 조회수: {stats['total_views']:,} ({stats['total_views']/1000000:.1f}M)")
        print(f"├─ 총 좋아요: {stats['total_likes']:,} ({stats['total_likes']/1000:.1f}K)")
        print(f"├─ 총 댓글: {stats['total_comments']:,}")
        print(f"├─ 평균 참여율: {stats['avg_engagement_rate']*100:.2f}%")
        print(f"└─ 평균 바이럴 점수: {data['keyword_analysis']['overall_avg_viral_score']:.2f}")
        print()
    
    def display_top_videos_with_metrics(self, data, top_n=15):
        """상위 비디오를 정량 데이터와 함께 표시"""
        print("=" * 120)
        print(f"🏆 TOP {top_n} 비디오 (바이럴 점수 기준)")
        print("=" * 120)
        print(f"{'순위':<4} {'제목':<50} {'조회수':>10} {'좋아요':>8} {'댓글':>6} {'참여율':>8} {'바이럴':>8} {'키워드':<12}")
        print("-" * 120)
        
        # 바이럴 점수 기준 정렬
        sorted_videos = sorted(data['videos'], key=lambda x: x['viral_score'], reverse=True)[:top_n]
        
        for i, video in enumerate(sorted_videos, 1):
            title = video['title'][:47] + "..." if len(video['title']) > 50 else video['title']
            print(f"{i:<4} {title:<50} {video['view_count']:>10,} {video['like_count']:>8,} "
                  f"{video.get('comment_count', 0):>6,} {video['engagement_rate']*100:>7.2f}% "
                  f"{video['viral_score']:>8.2f} {video['keyword_matched']:<12}")
    
    def display_keyword_performance(self, data):
        """키워드별 성과 분석"""
        print("\n" + "=" * 120)
        print("📈 키워드별 정량적 성과 분석")
        print("=" * 120)
        
        keyword_data = data['keyword_analysis']['keywords']
        
        # 헤더
        print(f"{'키워드':<12} {'비디오수':>8} {'총조회수':>12} {'평균조회수':>12} {'평균참여율':>10} {'바이럴점수':>10} {'트렌드':>10}")
        print("-" * 120)
        
        # 바이럴 점수 기준 정렬
        sorted_keywords = sorted(keyword_data.items(), 
                               key=lambda x: x[1]['avg_viral_score'], 
                               reverse=True)
        
        for keyword, stats in sorted_keywords:
            total_views = stats['total_views']
            avg_views = stats['avg_views']
            trend = self._get_trend_indicator(stats['momentum'])
            
            print(f"{keyword:<12} {stats['count']:>8} {total_views:>12,} {avg_views:>12,} "
                  f"{stats['avg_engagement']*100:>9.2f}% {stats['avg_viral_score']:>10.2f} {trend:>10}")
    
    def display_engagement_analysis(self, data):
        """참여율 중심 분석"""
        print("\n" + "=" * 120)
        print("💬 참여율 TOP 10 비디오 (진짜 인기 콘텐츠)")
        print("=" * 120)
        
        # 참여율 기준 정렬
        sorted_by_engagement = sorted(data['videos'], 
                                    key=lambda x: x['engagement_rate'], 
                                    reverse=True)[:10]
        
        print(f"{'순위':<4} {'제목':<45} {'조회수':>10} {'좋아요':>8} {'댓글':>6} {'참여율':>8} {'좋아요율':>8}")
        print("-" * 120)
        
        for i, video in enumerate(sorted_by_engagement, 1):
            title = video['title'][:42] + "..." if len(video['title']) > 45 else video['title']
            like_rate = (video['like_count'] / video['view_count'] * 100) if video['view_count'] > 0 else 0
            
            print(f"{i:<4} {title:<45} {video['view_count']:>10,} {video['like_count']:>8,} "
                  f"{video.get('comment_count', 0):>6,} {video['engagement_rate']*100:>7.2f}% "
                  f"{like_rate:>7.2f}%")
    
    def display_view_giants(self, data):
        """조회수 TOP 10 (대중성 분석)"""
        print("\n" + "=" * 120)
        print("👀 조회수 TOP 10 비디오 (대중적 인기)")
        print("=" * 120)
        
        sorted_by_views = sorted(data['videos'], 
                               key=lambda x: x['view_count'], 
                               reverse=True)[:10]
        
        print(f"{'순위':<4} {'제목':<45} {'조회수':>12} {'좋아요':>8} {'댓글':>6} {'참여율':>8} {'키워드':<10}")
        print("-" * 120)
        
        for i, video in enumerate(sorted_by_views, 1):
            title = video['title'][:42] + "..." if len(video['title']) > 45 else video['title']
            
            print(f"{i:<4} {title:<45} {video['view_count']:>12,} {video['like_count']:>8,} "
                  f"{video.get('comment_count', 0):>6,} {video['engagement_rate']*100:>7.2f}% "
                  f"{video['keyword_matched']:<10}")
    
    def generate_actionable_insights(self, data):
        """실행 가능한 인사이트 생성"""
        print("\n" + "=" * 120)
        print("💡 정량 데이터 기반 핵심 인사이트")
        print("=" * 120)
        
        # 1. 최적 참여율 구간 찾기
        high_engagement_videos = [v for v in data['videos'] if v['engagement_rate'] > 0.04]
        if high_engagement_videos:
            avg_views_high_engagement = sum(v['view_count'] for v in high_engagement_videos) / len(high_engagement_videos)
            print(f"\n1. 【고참여율 콘텐츠 특성】")
            print(f"   - 4% 이상 참여율 비디오: {len(high_engagement_videos)}개")
            print(f"   - 평균 조회수: {avg_views_high_engagement:,.0f} (스위트 스팟)")
        
        # 2. 키워드별 효율성
        keyword_data = data['keyword_analysis']['keywords']
        print(f"\n2. 【키워드 효율성 순위】")
        efficiency_data = []
        for keyword, stats in keyword_data.items():
            if stats['count'] > 0:
                efficiency = stats['avg_engagement'] * stats['avg_viral_score']
                efficiency_data.append((keyword, efficiency, stats['avg_engagement'], stats['avg_viral_score']))
        
        efficiency_data.sort(key=lambda x: x[1], reverse=True)
        for i, (keyword, efficiency, engagement, viral) in enumerate(efficiency_data[:5], 1):
            print(f"   {i}. {keyword}: 효율성 지수 {efficiency:.2f} (참여율 {engagement*100:.2f}% × 바이럴 {viral:.1f})")
        
        # 3. 콘텐츠 형식 분석
        print(f"\n3. 【성공 콘텐츠 패턴】")
        
        # 제목 길이 분석
        title_lengths = [(len(v['title']), v['engagement_rate']) for v in data['videos']]
        short_titles = [e for l, e in title_lengths if l < 30]
        long_titles = [e for l, e in title_lengths if l >= 30]
        
        if short_titles and long_titles:
            print(f"   - 짧은 제목 (<30자) 평균 참여율: {sum(short_titles)/len(short_titles)*100:.2f}%")
            print(f"   - 긴 제목 (≥30자) 평균 참여율: {sum(long_titles)/len(long_titles)*100:.2f}%")
        
        # 4. 시간대별 최적 전략
        print(f"\n4. 【데이터 기반 콘텐츠 전략】")
        print(f"   - 고조회수 전략: {list(keyword_data.keys())[0]} 키워드 + 유명 플레이어")
        print(f"   - 고참여율 전략: GTO/전략 콘텐츠 + 교육적 요소")
        print(f"   - 균형 전략: WSOP/토너먼트 + 개인 스토리")
    
    def _get_trend_indicator(self, momentum):
        """트렌드 지표 반환"""
        if momentum > 1.5:
            return "🔥 급상승"
        elif momentum > 1.1:
            return "📈 상승"
        elif momentum > 0.9:
            return "➡️ 유지"
        else:
            return "📉 하락"
    
    def create_slack_report(self, data):
        """Slack용 간결한 리포트 생성"""
        print("\n" + "=" * 120)
        print("📱 Slack 전송용 일일 리포트")
        print("=" * 120)
        
        report = f"""
🎯 포커 트렌드 일일 분석 리포트 - {datetime.now().strftime('%Y-%m-%d')}

📊 전체 성과
• 총 분석: {data['metadata']['total_videos']}개 비디오
• 총 조회수: {data['aggregate_stats']['total_views']:,} ({data['aggregate_stats']['total_views']/1000000:.1f}M)
• 평균 참여율: {data['aggregate_stats']['avg_engagement_rate']*100:.2f}%

🏆 오늘의 TOP 3 (바이럴 점수)
"""
        
        sorted_videos = sorted(data['videos'], key=lambda x: x['viral_score'], reverse=True)[:3]
        for i, video in enumerate(sorted_videos, 1):
            report += f"{i}. {video['title'][:40]}...\n"
            report += f"   조회수: {video['view_count']:,} | 참여율: {video['engagement_rate']*100:.1f}% | 바이럴: {video['viral_score']:.1f}\n\n"
        
        print(report)
        return report

def main():
    analyzer = EnhancedQuantitativeAnalyzer()
    data = analyzer.load_latest_data()
    
    # 1. 정량적 개요
    analyzer.display_quantitative_overview(data)
    
    # 2. TOP 15 비디오 (정량 데이터 포함)
    analyzer.display_top_videos_with_metrics(data, top_n=15)
    
    # 3. 키워드별 성과
    analyzer.display_keyword_performance(data)
    
    # 4. 참여율 분석
    analyzer.display_engagement_analysis(data)
    
    # 5. 조회수 거물들
    analyzer.display_view_giants(data)
    
    # 6. 실행 가능한 인사이트
    analyzer.generate_actionable_insights(data)
    
    # 7. Slack 리포트
    analyzer.create_slack_report(data)

if __name__ == "__main__":
    main()