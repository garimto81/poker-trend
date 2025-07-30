"""
YouTube 포커 트렌드 분석 엔진
수집된 데이터를 분석하여 트렌드를 파악하고 인사이트를 도출합니다.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
import re
from collections import Counter
import logging

logger = logging.getLogger(__name__)


class PokerTrendAnalyzer:
    """포커 트렌드 분석기"""
    
    def __init__(self):
        self.category_keywords = {
            'tournament': ['WSOP', 'WPT', 'EPT', 'tournament', '토너먼트', 'final table', '파이널'],
            'online': ['PokerStars', 'GGPoker', 'online', '온라인', 'app', '앱'],
            'education': ['strategy', '전략', 'tutorial', '강의', 'tips', '팁', 'how to', '방법'],
            'entertainment': ['funny', '재미', 'crazy', 'amazing', '대박', 'highlight', '하이라이트'],
            'pro_player': ['Negreanu', 'Ivey', 'Hellmuth', 'pro', '프로', 'player', '선수']
        }
        
        self.trend_threshold = 0.8
        
    def analyze_trends(self, videos_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """전체 트렌드 분석 실행"""
        if not videos_data:
            return self._empty_analysis()
            
        df = pd.DataFrame(videos_data)
        
        # 데이터 전처리
        df = self._preprocess_data(df)
        
        # 트렌드 스코어 계산
        df['trend_score'] = df.apply(self._calculate_trend_score, axis=1)
        
        # 카테고리 분류
        df['category'] = df.apply(self._categorize_video, axis=1)
        
        # 분석 결과 생성
        analysis = {
            'summary': self._generate_summary(df),
            'trending_videos': self._get_trending_videos(df),
            'category_breakdown': self._analyze_by_category(df),
            'top_channels': self._get_top_channels(df),
            'keyword_analysis': self._analyze_keywords(df),
            'time_analysis': self._analyze_upload_times(df),
            'engagement_metrics': self._calculate_engagement_metrics(df)
        }
        
        return analysis
    
    def _preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """데이터 전처리"""
        # 날짜 변환
        df['published_at'] = pd.to_datetime(df['published_at'])
        df['hours_since_upload'] = (datetime.now() - df['published_at']).dt.total_seconds() / 3600
        
        # 결측값 처리
        df['view_count'] = df['view_count'].fillna(0)
        df['like_count'] = df['like_count'].fillna(0)
        df['comment_count'] = df['comment_count'].fillna(0)
        
        # 파생 변수 생성
        df['engagement_rate'] = ((df['like_count'] + df['comment_count']) / 
                                 df['view_count'].replace(0, 1))
        df['views_per_hour'] = df['view_count'] / df['hours_since_upload'].replace(0, 1)
        
        return df
    
    def _calculate_trend_score(self, row: pd.Series) -> float:
        """트렌드 스코어 계산 (0-1)"""
        # 시간당 조회수 점수 (로그 스케일)
        views_per_hour = row['views_per_hour']
        vph_score = np.log1p(views_per_hour) / np.log1p(10000)  # 10K/hour = 1.0
        
        # 참여율 점수
        engagement_score = min(row['engagement_rate'] * 10, 1.0)  # 10% = 1.0
        
        # 절대 조회수 점수
        view_score = np.log1p(row['view_count']) / np.log1p(1000000)  # 1M = 1.0
        
        # 신선도 점수 (24시간 이내 = 1.0)
        freshness_score = max(0, 1 - (row['hours_since_upload'] / 24))
        
        # 가중 평균
        trend_score = (
            vph_score * 0.35 +
            engagement_score * 0.25 +
            view_score * 0.25 +
            freshness_score * 0.15
        )
        
        return min(trend_score, 1.0)
    
    def _categorize_video(self, row: pd.Series) -> str:
        """비디오 카테고리 분류"""
        title_desc = (row['title'] + ' ' + row['description']).lower()
        
        category_scores = {}
        for category, keywords in self.category_keywords.items():
            score = sum(1 for keyword in keywords if keyword.lower() in title_desc)
            category_scores[category] = score
        
        if max(category_scores.values()) > 0:
            return max(category_scores, key=category_scores.get)
        return 'general'
    
    def _generate_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """전체 요약 통계 생성"""
        return {
            'total_videos': len(df),
            'total_views': int(df['view_count'].sum()),
            'avg_views': int(df['view_count'].mean()),
            'avg_engagement_rate': float(df['engagement_rate'].mean()),
            'trending_count': len(df[df['trend_score'] >= self.trend_threshold]),
            'new_videos_24h': len(df[df['hours_since_upload'] <= 24])
        }
    
    def _get_trending_videos(self, df: pd.DataFrame, limit: int = 10) -> List[Dict]:
        """급상승 비디오 추출"""
        trending = df[df['trend_score'] >= self.trend_threshold].nlargest(limit, 'trend_score')
        
        return [
            {
                'video_id': row['video_id'],
                'title': row['title'],
                'channel_name': row['channel_name'],
                'view_count': int(row['view_count']),
                'like_count': int(row['like_count']),
                'comment_count': int(row['comment_count']),
                'trend_score': float(row['trend_score']),
                'category': row['category'],
                'published_at': row['published_at'].isoformat(),
                'views_per_hour': int(row['views_per_hour']),
                'engagement_rate': float(row['engagement_rate']),
                'video_url': row['video_url'],
                'thumbnail_url': row['thumbnail_url']
            }
            for _, row in trending.iterrows()
        ]
    
    def _analyze_by_category(self, df: pd.DataFrame) -> Dict[str, Dict]:
        """카테고리별 분석"""
        category_stats = {}
        
        for category in df['category'].unique():
            cat_df = df[df['category'] == category]
            category_stats[category] = {
                'count': len(cat_df),
                'total_views': int(cat_df['view_count'].sum()),
                'avg_views': int(cat_df['view_count'].mean()),
                'avg_engagement': float(cat_df['engagement_rate'].mean()),
                'top_video': {
                    'title': cat_df.nlargest(1, 'view_count').iloc[0]['title'],
                    'views': int(cat_df.nlargest(1, 'view_count').iloc[0]['view_count'])
                } if len(cat_df) > 0 else None
            }
        
        return category_stats
    
    def _get_top_channels(self, df: pd.DataFrame, limit: int = 5) -> List[Dict]:
        """상위 채널 분석"""
        channel_stats = df.groupby(['channel_id', 'channel_name']).agg({
            'video_id': 'count',
            'view_count': ['sum', 'mean'],
            'engagement_rate': 'mean'
        }).reset_index()
        
        channel_stats.columns = ['channel_id', 'channel_name', 'video_count', 
                                'total_views', 'avg_views', 'avg_engagement']
        
        top_channels = channel_stats.nlargest(limit, 'total_views')
        
        return [
            {
                'channel_id': row['channel_id'],
                'channel_name': row['channel_name'],
                'video_count': int(row['video_count']),
                'total_views': int(row['total_views']),
                'avg_views': int(row['avg_views']),
                'avg_engagement': float(row['avg_engagement'])
            }
            for _, row in top_channels.iterrows()
        ]
    
    def _analyze_keywords(self, df: pd.DataFrame) -> Dict[str, int]:
        """키워드 빈도 분석"""
        # 제목과 설명에서 키워드 추출
        all_text = ' '.join(df['title'] + ' ' + df['description'])
        
        # 포커 관련 주요 키워드 추출
        poker_keywords = re.findall(
            r'\b(poker|포커|holdem|홀덤|wsop|wpt|ept|bluff|블러프|all.?in|올인|' +
            r'tournament|토너먼트|cash.?game|캐시게임|final.?table|파이널)\b',
            all_text.lower()
        )
        
        keyword_counts = Counter(poker_keywords)
        return dict(keyword_counts.most_common(20))
    
    def _analyze_upload_times(self, df: pd.DataFrame) -> Dict[str, Any]:
        """업로드 시간 패턴 분석"""
        df['upload_hour'] = df['published_at'].dt.hour
        df['upload_day'] = df['published_at'].dt.day_name()
        
        return {
            'peak_hours': df['upload_hour'].value_counts().head(3).to_dict(),
            'peak_days': df['upload_day'].value_counts().head(3).to_dict()
        }
    
    def _calculate_engagement_metrics(self, df: pd.DataFrame) -> Dict[str, float]:
        """참여도 지표 계산"""
        return {
            'avg_like_ratio': float((df['like_count'] / df['view_count'].replace(0, 1)).mean()),
            'avg_comment_ratio': float((df['comment_count'] / df['view_count'].replace(0, 1)).mean()),
            'high_engagement_videos': len(df[df['engagement_rate'] > 0.1]),
            'viral_potential': len(df[(df['views_per_hour'] > 1000) & (df['engagement_rate'] > 0.05)])
        }
    
    def _empty_analysis(self) -> Dict[str, Any]:
        """빈 분석 결과 반환"""
        return {
            'summary': {
                'total_videos': 0,
                'total_views': 0,
                'avg_views': 0,
                'avg_engagement_rate': 0,
                'trending_count': 0,
                'new_videos_24h': 0
            },
            'trending_videos': [],
            'category_breakdown': {},
            'top_channels': [],
            'keyword_analysis': {},
            'time_analysis': {},
            'engagement_metrics': {}
        }


if __name__ == "__main__":
    # 테스트 데이터로 분석 실행
    analyzer = PokerTrendAnalyzer()
    
    # 샘플 데이터
    sample_videos = [
        {
            'video_id': 'test1',
            'title': 'WSOP Main Event Final Table',
            'description': 'Amazing poker tournament action',
            'channel_id': 'ch1',
            'channel_name': 'PokerTV',
            'published_at': datetime.now() - timedelta(hours=5),
            'view_count': 50000,
            'like_count': 2000,
            'comment_count': 500,
            'video_url': 'https://youtube.com/watch?v=test1',
            'thumbnail_url': 'https://i.ytimg.com/vi/test1/hqdefault.jpg'
        }
    ]
    
    results = analyzer.analyze_trends(sample_videos)
    print(f"Analysis complete: {results['summary']}")