# -*- coding: utf-8 -*-
"""
YouTube 트렌드 분석 API 라우트
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from ..collectors.youtube_trend_collector import YouTubeTrendCollector
from ..analyzers.trend_analyzer import PokerTrendAnalyzer
from ..config.settings import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/youtube", tags=["youtube"])

# Pydantic 모델 정의
class CollectRequest(BaseModel):
    hours_back: int = 24
    max_results: int = 200
    
class AnalyzeRequest(BaseModel):
    videos: List[Dict[str, Any]]
    
class TrendResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    timestamp: datetime
    

# 전역 인스턴스
settings = get_settings()
collector = YouTubeTrendCollector(settings.youtube_api_key)
analyzer = PokerTrendAnalyzer()


@router.post("/collect", response_model=TrendResponse)
async def collect_youtube_trends(request: CollectRequest):
    """
    YouTube 포커 트렌드 데이터 수집
    """
    try:
        logger.info(f"Collecting YouTube trends - hours_back: {request.hours_back}")
        
        # 데이터 수집
        videos = collector.collect_trending_videos(hours_back=request.hours_back)
        
        # 최대 결과 수 제한
        if len(videos) > request.max_results:
            videos = videos[:request.max_results]
        
        logger.info(f"Collected {len(videos)} videos")
        
        return TrendResponse(
            success=True,
            data={"videos": videos, "count": len(videos)},
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Collection error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze", response_model=TrendResponse)
async def analyze_trends(request: AnalyzeRequest):
    """
    수집된 비디오 데이터 트렌드 분석
    """
    try:
        logger.info(f"Analyzing {len(request.videos)} videos")
        
        # 트렌드 분석 수행
        analysis_result = analyzer.analyze_trends(request.videos)
        
        return TrendResponse(
            success=True,
            data=analysis_result,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trending/realtime")
async def get_realtime_trending():
    """
    실시간 급상승 영상 조회
    """
    try:
        # 최근 4시간 데이터 수집
        videos = collector.collect_trending_videos(hours_back=4)
        
        # 트렌드 분석
        analysis = analyzer.analyze_trends(videos)
        
        # 트렌드 스코어 0.9 이상인 영상만 필터링
        hot_videos = [
            v for v in analysis['trending_videos'] 
            if v['trend_score'] >= 0.9
        ]
        
        return TrendResponse(
            success=True,
            data={
                "hot_videos": hot_videos,
                "count": len(hot_videos)
            },
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Realtime trending error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/report/latest")
async def get_latest_report():
    """
    최신 일일 리포트 조회
    """
    try:
        # TODO: 데이터베이스에서 최신 리포트 조회
        # 임시로 빈 응답 반환
        return TrendResponse(
            success=True,
            data={"message": "Latest report endpoint - to be implemented"},
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Report retrieval error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/collect-and-analyze")
async def collect_and_analyze(
    background_tasks: BackgroundTasks,
    hours_back: int = 24
):
    """
    데이터 수집과 분석을 한 번에 수행
    """
    try:
        # 백그라운드에서 수집 및 분석 수행
        background_tasks.add_task(
            perform_full_analysis,
            hours_back=hours_back
        )
        
        return {
            "success": True,
            "message": "Analysis started in background",
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Full analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def perform_full_analysis(hours_back: int):
    """
    전체 분석 프로세스 수행 (백그라운드 태스크)
    """
    try:
        # 1. 데이터 수집
        videos = collector.collect_trending_videos(hours_back=hours_back)
        logger.info(f"Background: Collected {len(videos)} videos")
        
        # 2. 트렌드 분석
        analysis = analyzer.analyze_trends(videos)
        logger.info("Background: Analysis completed")
        
        # 3. 결과 저장 (TODO: 데이터베이스 저장 구현)
        # await save_to_database(analysis)
        
        # 4. Slack 알림 (TODO: Node.js 서버로 웹훅 호출)
        # await notify_slack(analysis)
        
    except Exception as e:
        logger.error(f"Background analysis error: {str(e)}")


@router.get("/health")
async def health_check():
    """
    서비스 상태 확인
    """
    try:
        # YouTube API 연결 테스트
        test_search = collector.youtube.search().list(
            q="test",
            part="snippet",
            maxResults=1
        ).execute()
        
        return {
            "status": "healthy",
            "service": "YouTube Trend Collector",
            "youtube_api": "connected",
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "YouTube Trend Collector",
            "error": str(e),
            "timestamp": datetime.now()
        }