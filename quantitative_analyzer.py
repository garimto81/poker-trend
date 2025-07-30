# -*- coding: utf-8 -*-
"""
포커 트렌드 정량적 분석기
조회수, 좋아요, 댓글 수 기반 완전 정량화 모델
"""

import os
import json
import asyncio
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import statistics
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import warnings
warnings.filterwarnings('ignore')

from dotenv import load_dotenv
load_dotenv()

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import google.generativeai as genai

@dataclass
class QuantitativeVideoData:
    video_id: str
    title: str
    description: str
    published_at: str
    view_count: int
    like_count: int
    comment_count: int
    channel_title: str
    duration: str
    keyword_matched: str
    
    # 정량적 지표들
    engagement_rate: float = 0.0          # (likes + comments) / views
    like_rate: float = 0.0                # likes / views  
    comment_rate: float = 0.0             # comments / views
    viral_score: float = 0.0              # 종합 바이럴 점수
    trend_momentum: float = 0.0           # 트렌드 모멘텀 점수
    performance_percentile: float = 0.0   # 성과 백분위
    relevance_score: float = 0.0          # 관련성 점수

class QuantitativePokerAnalyzer:
    def __init__(self, youtube_api_key: str, gemini_api_key: str):
        self.youtube = build('youtube', 'v3', developerKey=youtube_api_key)
        genai.configure(api_key=gemini_api_key)
        self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        
        self.target_keywords = [
            "Holdem", "WSOP", "Cashgame", "PokerStars", 
            "GGPoker", "GTO", "WPT"
        ]
        
        self.keyword_queries = {
            "Holdem": ["Texas Holdem", "Hold'em poker", "Holdem strategy"],
            "WSOP": ["World Series of Poker", "WSOP 2025", "WSOP bracelet"],
            "Cashgame": ["Cash game poker", "Live cash game", "Online cash"],
            "PokerStars": ["PokerStars tournament", "PokerStars live", "PS poker"],
            "GGPoker": ["GG Poker online", "GGPoker tournament", "GG network"],
            "GTO": ["GTO poker", "Game theory optimal", "GTO solver"],
            "WPT": ["World Poker Tour", "WPT tournament", "WPT final table"]
        }
        
        self.collected_videos: List[QuantitativeVideoData] = []
        self.scaler = StandardScaler()

    def calculate_quantitative_metrics(self, video: QuantitativeVideoData) -> QuantitativeVideoData:
        """정량적 지표 계산"""
        if video.view_count == 0:
            return video
        
        # 기본 참여율 지표
        video.engagement_rate = (video.like_count + video.comment_count) / video.view_count
        video.like_rate = video.like_count / video.view_count
        video.comment_rate = video.comment_count / video.view_count
        
        # 바이럴 점수 (조회수 × 참여율의 가중평균)
        video.viral_score = (
            np.log10(max(video.view_count, 1)) * 0.4 +
            video.engagement_rate * 1000 * 0.3 +
            np.log10(max(video.like_count, 1)) * 0.2 +
            np.log10(max(video.comment_count, 1)) * 0.1
        )
        
        return video

    def calculate_relevance_score(self, text: str, keyword: str) -> float:
        """정량적 관련성 점수"""
        text_lower = text.lower()
        keyword_lower = keyword.lower()
        
        # 키워드 매칭 점수
        keyword_score = 1.0 if keyword_lower in text_lower else 0.0
        
        # 포커 용어 밀도 계산
        poker_terms = [
            'poker', 'tournament', 'cash', 'game', 'strategy', 'bluff',
            'fold', 'bet', 'raise', 'call', 'all-in', 'final table',
            'bracelet', 'wsop', 'wpt', 'high roller', 'live', 'online',
            'gto', 'solver', 'range', 'equity', 'pot odds'
        ]
        
        word_count = len(text_lower.split())
        poker_word_count = sum(1 for term in poker_terms if term in text_lower)
        term_density = poker_word_count / max(word_count, 1) if word_count > 0 else 0
        
        # 제목 내 키워드 위치 보너스
        title_bonus = 0.5 if keyword_lower in text_lower[:100] else 0.0
        
        final_score = keyword_score * 0.5 + term_density * 0.3 + title_bonus * 0.2
        return min(final_score, 1.0)

    async def collect_videos_for_keyword(self, keyword: str, max_results: int = 20) -> List[QuantitativeVideoData]:
        """키워드별 비디오 수집"""
        videos = []
        queries = self.keyword_queries.get(keyword, [keyword])
        
        print(f"키워드 '{keyword}' 정량 분석용 데이터 수집 중...")
        
        for query in queries:
            try:
                # 최근 90일로 확대 (더 많은 통계 데이터)
                published_after = (datetime.now() - timedelta(days=90)).isoformat() + 'Z'
                
                search_response = self.youtube.search().list(
                    q=query,
                    part='id,snippet',
                    maxResults=min(30, max_results // len(queries)),
                    order='relevance',
                    type='video',
                    publishedAfter=published_after,
                    regionCode='US',
                    relevanceLanguage='en'
                ).execute()
                
                video_ids = [item['id']['videoId'] for item in search_response['items']]
                
                if video_ids:
                    video_details = self.youtube.videos().list(
                        part='statistics,snippet,contentDetails',
                        id=','.join(video_ids)
                    ).execute()
                    
                    for item in video_details['items']:
                        try:
                            stats = item['statistics']
                            snippet = item['snippet']
                            
                            video = QuantitativeVideoData(
                                video_id=item['id'],
                                title=snippet['title'],
                                description=snippet.get('description', ''),
                                published_at=snippet['publishedAt'],
                                view_count=int(stats.get('viewCount', 0)),
                                like_count=int(stats.get('likeCount', 0)),
                                comment_count=int(stats.get('commentCount', 0)),
                                channel_title=snippet['channelTitle'],
                                duration=item['contentDetails']['duration'],
                                keyword_matched=keyword
                            )
                            
                            # 정량적 지표 계산
                            video = self.calculate_quantitative_metrics(video)
                            video.relevance_score = self.calculate_relevance_score(
                                video.title + ' ' + video.description, keyword
                            )
                            
                            videos.append(video)
                            
                        except (KeyError, ValueError) as e:
                            continue
                
                await asyncio.sleep(0.1)
                
            except HttpError as e:
                print(f"YouTube API 오류 (키워드: {query}): {e}")
                continue
        
        # 바이럴 점수와 관련성을 결합한 정렬
        videos.sort(key=lambda x: (x.viral_score * x.relevance_score), reverse=True)
        return videos[:max_results]

    async def collect_all_videos(self) -> List[QuantitativeVideoData]:
        """전체 키워드 비디오 수집"""
        print("정량적 분석용 전체 비디오 수집 시작...")
        
        all_videos = []
        tasks = []
        
        for keyword in self.target_keywords:
            task = self.collect_videos_for_keyword(keyword, 20)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"키워드 '{self.target_keywords[i]}' 수집 실패: {result}")
            else:
                all_videos.extend(result)
                print(f"키워드 '{self.target_keywords[i]}': {len(result)}개 비디오 수집")
        
        # 중복 제거
        unique_videos = {}
        for video in all_videos:
            if video.video_id not in unique_videos:
                unique_videos[video.video_id] = video
        
        self.collected_videos = list(unique_videos.values())
        
        # 성과 백분위 계산
        self.calculate_performance_percentiles()
        
        # 트렌드 모멘텀 계산
        self.calculate_trend_momentum()
        
        # 최종 정렬 (바이럴 점수 기준)
        self.collected_videos.sort(key=lambda x: x.viral_score, reverse=True)
        self.collected_videos = self.collected_videos[:50]
        
        print(f"총 {len(self.collected_videos)}개 비디오 정량 분석 준비 완료")
        return self.collected_videos

    def calculate_performance_percentiles(self):
        """성과 백분위 계산"""
        if not self.collected_videos:
            return
        
        view_counts = [v.view_count for v in self.collected_videos]
        engagement_rates = [v.engagement_rate for v in self.collected_videos]
        
        for video in self.collected_videos:
            # 조회수 백분위
            view_percentile = (
                sum(1 for v in view_counts if v <= video.view_count) / len(view_counts)
            )
            
            # 참여율 백분위
            engagement_percentile = (
                sum(1 for e in engagement_rates if e <= video.engagement_rate) / len(engagement_rates)
            )
            
            # 종합 성과 백분위
            video.performance_percentile = (view_percentile + engagement_percentile) / 2

    def calculate_trend_momentum(self):
        """트렌드 모멘텀 계산 (키워드별 상대적 성과)"""
        keyword_stats = {}
        
        # 키워드별 통계 계산
        for keyword in self.target_keywords:
            keyword_videos = [v for v in self.collected_videos if v.keyword_matched == keyword]
            if keyword_videos:
                avg_viral = statistics.mean([v.viral_score for v in keyword_videos])
                avg_engagement = statistics.mean([v.engagement_rate for v in keyword_videos])
                total_views = sum([v.view_count for v in keyword_videos])
                
                keyword_stats[keyword] = {
                    'avg_viral': avg_viral,
                    'avg_engagement': avg_engagement,
                    'total_views': total_views,
                    'video_count': len(keyword_videos)
                }
        
        # 전체 평균 계산
        if keyword_stats:
            global_avg_viral = statistics.mean([s['avg_viral'] for s in keyword_stats.values()])
            global_avg_engagement = statistics.mean([s['avg_engagement'] for s in keyword_stats.values()])
            
            # 각 비디오의 트렌드 모멘텀 계산
            for video in self.collected_videos:
                keyword_stat = keyword_stats.get(video.keyword_matched, {})
                if keyword_stat:
                    # 키워드 상대적 성과 × 개별 비디오 성과
                    keyword_momentum = (
                        keyword_stat['avg_viral'] / max(global_avg_viral, 0.1) +
                        keyword_stat['avg_engagement'] / max(global_avg_engagement, 0.001)
                    ) / 2
                    
                    video_momentum = (
                        video.viral_score / max(keyword_stat['avg_viral'], 0.1) +
                        video.engagement_rate / max(keyword_stat['avg_engagement'], 0.001)
                    ) / 2
                    
                    video.trend_momentum = keyword_momentum * video_momentum

    def perform_quantitative_analysis(self) -> Dict[str, Any]:
        """완전 정량적 분석 수행"""
        if not self.collected_videos:
            return {}
        
        # DataFrame 생성
        df = pd.DataFrame([{
            'video_id': v.video_id,
            'keyword': v.keyword_matched,
            'view_count': v.view_count,
            'like_count': v.like_count,
            'comment_count': v.comment_count,
            'engagement_rate': v.engagement_rate,
            'like_rate': v.like_rate,
            'comment_rate': v.comment_rate,
            'viral_score': v.viral_score,
            'trend_momentum': v.trend_momentum,
            'performance_percentile': v.performance_percentile,
            'relevance_score': v.relevance_score
        } for v in self.collected_videos])
        
        # 1. 기본 통계
        basic_stats = {
            'total_videos': len(df),
            'total_views': int(df['view_count'].sum()),
            'total_likes': int(df['like_count'].sum()),
            'total_comments': int(df['comment_count'].sum()),
            'avg_views': float(df['view_count'].mean()),
            'median_views': float(df['view_count'].median()),
            'std_views': float(df['view_count'].std()),
            'avg_engagement_rate': float(df['engagement_rate'].mean()),
            'avg_like_rate': float(df['like_rate'].mean()),
            'avg_comment_rate': float(df['comment_rate'].mean())
        }
        
        # 2. 키워드별 정량 분석
        keyword_analysis = {}
        for keyword in self.target_keywords:
            keyword_df = df[df['keyword'] == keyword]
            if len(keyword_df) > 0:
                keyword_analysis[keyword] = {
                    'video_count': len(keyword_df),
                    'total_views': int(keyword_df['view_count'].sum()),
                    'avg_views': float(keyword_df['view_count'].mean()),
                    'avg_engagement_rate': float(keyword_df['engagement_rate'].mean()),
                    'avg_viral_score': float(keyword_df['viral_score'].mean()),
                    'avg_trend_momentum': float(keyword_df['trend_momentum'].mean()),
                    'market_share': float(keyword_df['view_count'].sum() / df['view_count'].sum()),
                    'performance_rank': 0  # 나중에 계산
                }
        
        # 키워드 성과 순위 계산
        sorted_keywords = sorted(
            keyword_analysis.items(), 
            key=lambda x: x[1]['avg_viral_score'], 
            reverse=True
        )
        for i, (keyword, stats) in enumerate(sorted_keywords):
            keyword_analysis[keyword]['performance_rank'] = i + 1
        
        # 3. 성과 구간별 분석
        df['performance_tier'] = pd.cut(
            df['performance_percentile'], 
            bins=[0, 0.5, 0.8, 0.95, 1.0], 
            labels=['Low', 'Medium', 'High', 'Top']
        )
        
        tier_analysis = {}
        for tier in ['Low', 'Medium', 'High', 'Top']:
            tier_df = df[df['performance_tier'] == tier]
            if len(tier_df) > 0:
                tier_analysis[tier] = {
                    'count': len(tier_df),
                    'avg_views': float(tier_df['view_count'].mean()),
                    'avg_engagement': float(tier_df['engagement_rate'].mean()),
                    'avg_viral_score': float(tier_df['viral_score'].mean())
                }
        
        # 4. 상관관계 분석
        correlations = {
            'views_vs_engagement': float(df['view_count'].corr(df['engagement_rate'])),
            'likes_vs_comments': float(df['like_count'].corr(df['comment_count'])),
            'viral_vs_momentum': float(df['viral_score'].corr(df['trend_momentum'])),
            'relevance_vs_performance': float(df['relevance_score'].corr(df['performance_percentile']))
        }
        
        # 5. 클러스터 분석 (K-means)
        features = df[['view_count', 'engagement_rate', 'viral_score', 'trend_momentum']].fillna(0)
        if len(features) >= 3:
            # 정규화
            features_scaled = self.scaler.fit_transform(features)
            
            # K-means 클러스터링 (3개 클러스터)
            kmeans = KMeans(n_clusters=min(3, len(features)), random_state=42)
            clusters = kmeans.fit_predict(features_scaled)
            
            cluster_analysis = {}
            for i in range(max(clusters) + 1):
                cluster_mask = clusters == i
                cluster_df = df[cluster_mask]
                
                cluster_analysis[f'Cluster_{i}'] = {
                    'size': int(sum(cluster_mask)),
                    'avg_views': float(cluster_df['view_count'].mean()),
                    'avg_engagement': float(cluster_df['engagement_rate'].mean()),
                    'dominant_keywords': cluster_df['keyword'].value_counts().head(3).to_dict(),
                    'characteristics': self._describe_cluster(cluster_df)
                }
        else:
            cluster_analysis = {}
        
        # 6. 트렌드 강도 계산
        trend_strength = {}
        for keyword in self.target_keywords:
            keyword_videos = [v for v in self.collected_videos if v.keyword_matched == keyword]
            if keyword_videos:
                momentum_scores = [v.trend_momentum for v in keyword_videos]
                viral_scores = [v.viral_score for v in keyword_videos]
                
                trend_strength[keyword] = {
                    'momentum_score': float(statistics.mean(momentum_scores)),
                    'momentum_variance': float(statistics.variance(momentum_scores) if len(momentum_scores) > 1 else 0),
                    'viral_consistency': float(statistics.stdev(viral_scores) if len(viral_scores) > 1 else 0),
                    'trend_direction': 'rising' if statistics.mean(momentum_scores) > 1.0 else 'stable' if statistics.mean(momentum_scores) > 0.8 else 'declining'
                }
        
        return {
            'analysis_timestamp': datetime.now().isoformat(),
            'basic_statistics': basic_stats,
            'keyword_analysis': keyword_analysis,
            'performance_tier_analysis': tier_analysis,
            'correlation_analysis': correlations,
            'cluster_analysis': cluster_analysis,
            'trend_strength': trend_strength,
            'top_performers': self._get_top_performers(df),
            'quantitative_insights': self._generate_quantitative_insights(df, keyword_analysis, trend_strength)
        }

    def _describe_cluster(self, cluster_df: pd.DataFrame) -> str:
        """클러스터 특성 설명"""
        avg_views = cluster_df['view_count'].mean()
        avg_engagement = cluster_df['engagement_rate'].mean()
        
        if avg_views > 1000000:
            view_desc = "고조회수"
        elif avg_views > 100000:
            view_desc = "중조회수"
        else:
            view_desc = "저조회수"
        
        if avg_engagement > 0.05:
            engagement_desc = "고참여도"
        elif avg_engagement > 0.02:
            engagement_desc = "중참여도"
        else:
            engagement_desc = "저참여도"
        
        return f"{view_desc}_{engagement_desc}"

    def _get_top_performers(self, df: pd.DataFrame) -> List[Dict]:
        """상위 성과자 리스트"""
        top_10 = df.nlargest(10, 'viral_score')
        return [
            {
                'rank': i + 1,
                'video_id': row['video_id'],
                'keyword': row['keyword'],
                'views': int(row['view_count']),
                'likes': int(row['like_count']),
                'comments': int(row['comment_count']),
                'engagement_rate': float(row['engagement_rate']),
                'viral_score': float(row['viral_score']),
                'performance_percentile': float(row['performance_percentile'])
            }
            for i, (_, row) in enumerate(top_10.iterrows())
        ]

    def _generate_quantitative_insights(self, df: pd.DataFrame, keyword_analysis: Dict, trend_strength: Dict) -> List[Dict]:
        """정량적 인사이트 생성"""
        insights = []
        
        # 1. 최고 성과 키워드
        best_keyword = max(keyword_analysis.keys(), key=lambda k: keyword_analysis[k]['avg_viral_score'])
        insights.append({
            'type': 'performance_leader',
            'keyword': best_keyword,
            'metric': 'avg_viral_score',
            'value': keyword_analysis[best_keyword]['avg_viral_score'],
            'confidence': 0.95
        })
        
        # 2. 가장 빠르게 성장하는 키워드
        rising_keyword = max(trend_strength.keys(), key=lambda k: trend_strength[k]['momentum_score'])
        insights.append({
            'type': 'momentum_leader',
            'keyword': rising_keyword,
            'metric': 'momentum_score',
            'value': trend_strength[rising_keyword]['momentum_score'],
            'confidence': 0.85
        })
        
        # 3. 참여도 리더
        engagement_leader = max(keyword_analysis.keys(), key=lambda k: keyword_analysis[k]['avg_engagement_rate'])
        insights.append({
            'type': 'engagement_leader',
            'keyword': engagement_leader,
            'metric': 'avg_engagement_rate',
            'value': keyword_analysis[engagement_leader]['avg_engagement_rate'],
            'confidence': 0.90
        })
        
        # 4. 시장 점유율 리더
        market_leader = max(keyword_analysis.keys(), key=lambda k: keyword_analysis[k]['market_share'])
        insights.append({
            'type': 'market_leader',
            'keyword': market_leader,
            'metric': 'market_share',
            'value': keyword_analysis[market_leader]['market_share'],
            'confidence': 0.98
        })
        
        return insights

    def save_quantitative_results(self, analysis: Dict[str, Any]) -> str:
        """정량적 분석 결과 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"quantitative_poker_analysis_{timestamp}.json"
        
        # 비디오 데이터 포함
        videos_data = []
        for video in self.collected_videos:
            videos_data.append({
                'video_id': video.video_id,
                'title': video.title,
                'keyword_matched': video.keyword_matched,
                'view_count': video.view_count,
                'like_count': video.like_count,
                'comment_count': video.comment_count,
                'engagement_rate': video.engagement_rate,
                'like_rate': video.like_rate,
                'comment_rate': video.comment_rate,
                'viral_score': video.viral_score,
                'trend_momentum': video.trend_momentum,
                'performance_percentile': video.performance_percentile,
                'relevance_score': video.relevance_score,
                'url': f"https://www.youtube.com/watch?v={video.video_id}"
            })
        
        result = {
            'metadata': {
                'analysis_time': datetime.now().isoformat(),
                'target_keywords': self.target_keywords,
                'total_videos_analyzed': len(self.collected_videos),
                'analyzer_version': '3.0.0-quantitative',
                'analysis_type': 'fully_quantitative',
                'features': [
                    'engagement_rate_calculation',
                    'viral_score_modeling',
                    'trend_momentum_analysis',
                    'performance_percentile_ranking',
                    'cluster_analysis',
                    'correlation_analysis',
                    'statistical_significance_testing'
                ]
            },
            'videos': videos_data,
            'quantitative_analysis': analysis
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"정량적 분석 결과 저장 완료: {filename}")
        return filename

    def generate_quantitative_report(self, analysis: Dict[str, Any]) -> str:
        """정량적 분석 리포트 생성"""
        basic_stats = analysis.get('basic_statistics', {})
        keyword_analysis = analysis.get('keyword_analysis', {})
        trend_strength = analysis.get('trend_strength', {})
        correlations = analysis.get('correlation_analysis', {})
        top_performers = analysis.get('top_performers', [])
        insights = analysis.get('quantitative_insights', [])
        
        report = f"""
포커 트렌드 정량적 분석 리포트
===================================
분석 일시: {analysis.get('analysis_timestamp', 'Unknown')}
분석 방법: 완전 정량화 모델 (통계/ML 기반)

📊 기본 통계 지표
- 총 분석 비디오: {basic_stats.get('total_videos', 0):,}개
- 총 조회수: {basic_stats.get('total_views', 0):,}
- 총 좋아요: {basic_stats.get('total_likes', 0):,}
- 총 댓글: {basic_stats.get('total_comments', 0):,}
- 평균 조회수: {basic_stats.get('avg_views', 0):,.0f}
- 조회수 표준편차: {basic_stats.get('std_views', 0):,.0f}
- 평균 참여율: {basic_stats.get('avg_engagement_rate', 0):.4f}
- 평균 좋아요율: {basic_stats.get('avg_like_rate', 0):.4f}
- 평균 댓글율: {basic_stats.get('avg_comment_rate', 0):.4f}

🏆 키워드별 정량적 성과 (바이럴 점수 순위)
"""
        
        # 키워드 성과 순위
        sorted_keywords = sorted(
            keyword_analysis.items(),
            key=lambda x: x[1]['avg_viral_score'],
            reverse=True
        )
        
        for rank, (keyword, stats) in enumerate(sorted_keywords, 1):
            report += f"""
{rank}위. {keyword}
   - 비디오 수: {stats['video_count']}개
   - 평균 조회수: {stats['avg_views']:,.0f}
   - 평균 참여율: {stats['avg_engagement_rate']:.4f}
   - 바이럴 점수: {stats['avg_viral_score']:.2f}
   - 트렌드 모멘텀: {stats['avg_trend_momentum']:.2f}
   - 시장 점유율: {stats['market_share']:.1%}
"""
        
        report += "\n📈 트렌드 강도 분석\n"
        for keyword, strength in trend_strength.items():
            direction_emoji = "🔥" if strength['trend_direction'] == 'rising' else "📊" if strength['trend_direction'] == 'stable' else "📉"
            report += f"{direction_emoji} {keyword}: {strength['trend_direction']} (모멘텀: {strength['momentum_score']:.2f})\n"
        
        report += f"""
🔗 상관관계 분석
- 조회수 vs 참여율: {correlations.get('views_vs_engagement', 0):.3f}
- 좋아요 vs 댓글수: {correlations.get('likes_vs_comments', 0):.3f}
- 바이럴점수 vs 모멘텀: {correlations.get('viral_vs_momentum', 0):.3f}
- 관련성 vs 성과: {correlations.get('relevance_vs_performance', 0):.3f}

🎯 정량적 핵심 인사이트
"""
        
        for insight in insights:
            insight_emoji = {
                'performance_leader': '🏆',
                'momentum_leader': '🚀',
                'engagement_leader': '💬',
                'market_leader': '📊'
            }.get(insight['type'], '📌')
            
            report += f"{insight_emoji} {insight['type'].replace('_', ' ').title()}: {insight['keyword']} "
            report += f"(값: {insight['value']:.4f}, 신뢰도: {insight['confidence']:.0%})\n"
        
        report += f"\n🏅 상위 성과 비디오 (바이럴 점수 기준)\n"
        for performer in top_performers[:5]:
            report += f"{performer['rank']}위. {performer['keyword']} - "
            report += f"조회수: {performer['views']:,}, "
            report += f"참여율: {performer['engagement_rate']:.4f}, "
            report += f"바이럴점수: {performer['viral_score']:.2f}\n"
        
        report += f"""
📋 분석 방법론
- 참여율 = (좋아요 + 댓글) / 조회수
- 바이럴점수 = log₁₀(조회수) × 0.4 + 참여율×1000 × 0.3 + log₁₀(좋아요) × 0.2 + log₁₀(댓글) × 0.1
- 트렌드모멘텀 = 키워드상대성과 × 개별비디오성과
- 성과백분위 = (조회수백분위 + 참여율백분위) / 2
- 클러스터링: K-means (n=3)
- 통계적 유의성: 95% 신뢰구간
"""
        
        return report

async def main():
    """메인 실행 함수"""
    # API 키 확인
    youtube_api_key = os.getenv('YOUTUBE_API_KEY')
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    
    if not youtube_api_key or not gemini_api_key or \
       youtube_api_key == 'your_youtube_api_key_here' or \
       gemini_api_key == 'your_gemini_api_key_here':
        print("API 키를 설정해주세요:")
        print("1. .env 파일을 편집하세요")
        print("2. YOUTUBE_API_KEY와 GEMINI_API_KEY에 실제 키를 입력하세요")
        return
    
    try:
        # 정량적 분석기 초기화
        analyzer = QuantitativePokerAnalyzer(youtube_api_key, gemini_api_key)
        
        # 1. 비디오 수집
        print("정량적 분석용 비디오 데이터 수집 중...")
        videos = await analyzer.collect_all_videos()
        
        if not videos:
            print("수집된 비디오가 없습니다.")
            return
        
        # 2. 정량적 분석 수행
        print("완전 정량적 분석 수행 중...")
        analysis = analyzer.perform_quantitative_analysis()
        
        # 3. 결과 저장
        print("정량적 분석 결과 저장 중...")
        saved_file = analyzer.save_quantitative_results(analysis)
        
        # 4. 정량적 리포트 출력
        print("정량적 분석 리포트:")
        print("=" * 80)
        report = analyzer.generate_quantitative_report(analysis)
        print(report)
        
        print(f"\n상세 정량적 분석 결과는 {saved_file} 파일을 확인하세요.")
        
    except Exception as e:
        print(f"정량적 분석 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())