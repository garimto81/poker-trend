#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
최종 포커 트렌드 분석기 - 한글 번역 포함
- 언어/국가 감지
- 제목 한글 번역 추가
- 간결한 쇼츠 아이디어 1개
- 일괄 Slack 업로드
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
from googleapiclient.discovery import build
import requests
import re

# 환경 변수 로드
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FinalAnalyzerWithTranslation:
    def __init__(self):
        self.youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        self.slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
        
        self.keywords = [
            'poker', 'holdem', 'wsop', 'wpt', 'ept', 
            'pokerstars', 'ggpoker', 'triton poker'
        ]
    
    def detect_language_and_country(self, title, description, channel_title):
        """언어 및 국가 감지"""
        text_sample = f"{title} {description[:100]} {channel_title}"
        
        if re.search(r'[\u0B80-\u0BFF]', text_sample):  # Tamil
            return "Tamil", "India"
        elif re.search(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', text_sample):  # Japanese
            return "Japanese", "Japan"
        elif re.search(r'[\uAC00-\uD7AF]', text_sample):  # Korean
            return "Korean", "South Korea"
        elif re.search(r'[\u4E00-\u9FFF]', text_sample):  # Chinese
            return "Chinese", "China"
        elif re.search(r'[\u0400-\u04FF]', text_sample):  # Russian
            return "Russian", "Russia"
        elif re.search(r'español|français|português', text_sample.lower()):
            return "Spanish/French/Portuguese", "Europe/Latin America"
        else:
            return "English", "Global"
    
    def translate_to_korean_batch(self, titles_and_languages):
        """배치로 한글 번역 (효율성 향상)"""
        translations = {}
        
        for title, language in titles_and_languages:
            if language == "Korean":
                translations[title] = title
                continue
            
            try:
                # 간단한 번역 프롬프트
                translate_prompt = f"Translate this {language} poker video title to Korean in 1 line: {title}"
                
                response = self.gemini_model.generate_content(translate_prompt)
                korean_title = response.text.strip()
                
                # 따옴표나 불필요한 문자 제거
                korean_title = korean_title.replace('"', '').replace("'", '').strip()
                
                translations[title] = korean_title
                logger.info(f"Translated: {title[:30]}... -> {korean_title[:30]}...")
                
            except Exception as e:
                logger.warning(f"Translation failed for {title[:30]}...: {e}")
                translations[title] = title  # 원본 반환
        
        return translations
    
    def collect_complete_video_data(self, max_results=5):
        """완전한 데이터 수집 (번역 포함)"""
        logger.info("Starting complete video data collection with translation...")
        all_videos = []
        
        for keyword in self.keywords:
            try:
                request = self.youtube.search().list(
                    part='snippet',
                    q=keyword,
                    type='video',
                    maxResults=max_results,
                    order='viewCount',
                    publishedAfter='2025-08-04T00:00:00Z'
                )
                
                response = request.execute()
                videos = response.get('items', [])
                
                for video in videos:
                    video_id = video['id']['videoId']
                    snippet = video['snippet']
                    
                    # 언어 및 국가 감지
                    title = snippet.get('title', '')
                    description = snippet.get('description', '')
                    channel_title = snippet.get('channelTitle', '')
                    
                    detected_language, detected_country = self.detect_language_and_country(
                        title, description, channel_title
                    )
                    
                    # 기본 정보
                    video_data = {
                        'video_id': video_id,
                        'title': title,
                        'description': description[:200],
                        'channel_title': channel_title,
                        'published_at': snippet.get('publishedAt', ''),
                        'upload_date': snippet.get('publishedAt', '')[:10],
                        'keyword': keyword,
                        'url': f"https://youtube.com/watch?v={video_id}",
                        'language': detected_language,
                        'country': detected_country
                    }
                    
                    # 상세 정보 가져오기
                    details = self.youtube.videos().list(
                        part='statistics,contentDetails',
                        id=video_id
                    ).execute()
                    
                    if details['items']:
                        stats = details['items'][0]['statistics']
                        content = details['items'][0]['contentDetails']
                        
                        video_data.update({
                            'view_count': int(stats.get('viewCount', 0)),
                            'like_count': int(stats.get('likeCount', 0)),
                            'comment_count': int(stats.get('commentCount', 0)),
                            'duration': content.get('duration', ''),
                        })
                    
                    all_videos.append(video_data)
                
                logger.info(f"Collected {len(videos)} videos for keyword: {keyword}")
                
            except Exception as e:
                logger.error(f"Error collecting data for {keyword}: {e}")
        
        # 중복 제거
        unique_videos = []
        seen_ids = set()
        for video in all_videos:
            if video['video_id'] not in seen_ids:
                unique_videos.append(video)
                seen_ids.add(video['video_id'])
        
        # TOP 5 선별 후 번역
        top_videos = sorted(unique_videos, key=lambda x: x.get('view_count', 0), reverse=True)[:5]
        
        # 번역할 제목들 준비
        titles_for_translation = [(video['title'], video['language']) for video in top_videos]
        
        # 배치 번역 실행
        logger.info("Starting Korean translation for TOP 5 videos...")
        translations = self.translate_to_korean_batch(titles_for_translation)
        
        # 번역 결과 추가
        for video in top_videos:
            video['korean_title'] = translations.get(video['title'], video['title'])
        
        # 전체 비디오에도 번역 결과 추가 (TOP 5만)
        for video in unique_videos:
            if video['video_id'] in [v['video_id'] for v in top_videos]:
                video['korean_title'] = translations.get(video['title'], video['title'])
            else:
                video['korean_title'] = video['title']  # TOP 5가 아니면 원본
        
        logger.info(f"Total unique videos collected: {len(unique_videos)}")
        logger.info(f"Korean translations completed for TOP 5")
        
        return unique_videos
    
    def create_analysis_prompt_with_translation(self, top_videos):
        """번역이 포함된 분석 프롬프트"""
        
        video_summary = []
        for i, video in enumerate(top_videos[:5], 1):
            engagement_rate = round((video.get('like_count', 0) / max(video.get('view_count', 1), 1) * 100), 2)
            video_summary.append(f"""
{i}위: "{video.get('title', '')}"
한글: "{video.get('korean_title', '')}"
언어: {video.get('language', '')} ({video.get('country', '')})
조회수: {video.get('view_count', 0):,} | 참여율: {engagement_rate}%
채널: {video.get('channel_title', '')} | 키워드: {video.get('keyword', '')}
""")
        
        videos_text = "\n".join(video_summary)
        
        prompt = f"""
포커 트렌드 분석 전문가로서 다음 TOP 5 영상(한글 번역 포함)을 분석하여 핵심 인사이트와 최고의 쇼츠 아이디어를 제안하세요.

=== TOP 5 영상 데이터 (원제 + 한글 번역) ===
{videos_text}

=== 간결한 분석 요청 ===

**1. 핵심 트렌드 (각 1줄)**
- 가장 주목할만한 패턴:
- 언어/지역별 특징:
- 고참여율 콘텐츠 특징:

**2. 포커 팬 관심사 TOP 3 (각 1줄)**
- 1위 관심사:
- 2위 관심사:
- 3위 관심사:

**3. 최고의 쇼츠 아이디어 1개**
제목: [매력적인 한글 제목]
컨셉: [30초 스토리 - 2줄]
타겟: [대상 시청자]
예상 성과: [조회수 예측 + 근거 1줄]
해시태그: [5개]

모든 답변은 간결하고 구체적으로 작성하세요.
"""
        return prompt
    
    def generate_insights_with_translation(self, videos):
        """번역 포함 AI 인사이트 생성"""
        logger.info("Generating AI insights with Korean translations...")
        
        try:
            top_videos = sorted(videos, key=lambda x: x.get('view_count', 0), reverse=True)[:5]
            prompt = self.create_analysis_prompt_with_translation(top_videos)
            
            response = self.gemini_model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"AI insight generation failed: {e}")
            return "AI 인사이트 생성에 실패했습니다."
    
    def create_slack_report_with_translation(self, videos, ai_insights):
        """번역 포함 Slack 리포트"""
        top_videos = sorted(videos, key=lambda x: x.get('view_count', 0), reverse=True)[:5]
        total_views = sum(v.get('view_count', 0) for v in videos)
        
        # 언어별 통계
        language_stats = {}
        for video in top_videos:
            lang = video.get('language', 'Unknown')
            language_stats[lang] = language_stats.get(lang, 0) + 1
        
        lang_summary = ", ".join([f"{lang}({count})" for lang, count in language_stats.items()])
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🎰 Complete Poker Analysis (Korean Translation)"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}\n📊 Total: {len(videos)} videos | {total_views:,} views\n🌍 Languages: {lang_summary}\n🔤 Korean translations for TOP 5 completed"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🏆 TOP 5 VIDEOS WITH KOREAN TRANSLATION*"
                }
            }
        ]
        
        # TOP 5 영상 (원제 + 한글 번역)
        for i, video in enumerate(top_videos, 1):
            original_title = video.get('title', '')[:40] + "..." if len(video.get('title', '')) > 40 else video.get('title', '')
            korean_title = video.get('korean_title', '')[:40] + "..." if len(video.get('korean_title', '')) > 40 else video.get('korean_title', '')
            channel = video.get('channel_title', '')
            views = video.get('view_count', 0)
            likes = video.get('like_count', 0)
            language = video.get('language', '')
            country = video.get('country', '')
            keyword = video.get('keyword', '')
            url = video.get('url', '')
            
            engagement = round((likes / max(views, 1) * 100), 2)
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{i}. <{url}|{original_title}>*\n🇰🇷 {korean_title}\n📺 {channel} | 🎯 {keyword}\n🌍 {language} ({country})\n📊 {views:,} views • 👍 {likes:,} • 📈 {engagement}%"
                }
            })
        
        # AI 인사이트 미리보기
        insights_preview = ai_insights[:400] + "..." if len(ai_insights) > 400 else ai_insights
        
        blocks.extend([
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🤖 AI INSIGHTS & BEST SHORTS IDEA*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"```{insights_preview}```"
                }
            }
        ])
        
        return {"blocks": blocks}
    
    def send_slack_notification(self, message):
        """Slack 알림 전송"""
        try:
            response = requests.post(self.slack_webhook, json=message, timeout=30)
            if response.status_code == 200:
                logger.info("Slack notification sent successfully")
                return True
            else:
                logger.error(f"Slack notification failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Slack notification error: {e}")
            return False
    
    def run_final_analysis(self):
        """최종 분석 실행 (번역 포함)"""
        logger.info("=" * 70)
        logger.info("FINAL POKER TREND ANALYSIS WITH KOREAN TRANSLATION")
        logger.info("=" * 70)
        
        # 1. 완전한 데이터 수집 (번역 포함)
        videos = self.collect_complete_video_data()
        
        # 2. AI 인사이트 생성 (번역 포함)
        ai_insights = self.generate_insights_with_translation(videos)
        
        # 3. TOP 5 추출
        top_5 = sorted(videos, key=lambda x: x.get('view_count', 0), reverse=True)[:5]
        
        # 4. 리포트 생성
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "analysis_type": "final_with_korean_translation",
            "total_videos": len(videos),
            "data_fields": [
                "title", "korean_title", "language", "country", 
                "view_count", "like_count", "comment_count", "channel_title", "keyword"
            ],
            "ai_insights": ai_insights,
            "top_5_videos": top_5,
            "all_videos": videos
        }
        
        # 5. 파일 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = Path(__file__).parent / 'reports' / f'final_analysis_translated_{timestamp}.json'
        insights_path = Path(__file__).parent / 'reports' / f'final_insights_translated_{timestamp}.txt'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        with open(insights_path, 'w', encoding='utf-8') as f:
            f.write("FINAL POKER TREND ANALYSIS WITH KOREAN TRANSLATION\n")
            f.write("=" * 60 + "\n\n")
            f.write("TOP 5 VIDEOS WITH KOREAN TRANSLATION:\n")
            f.write("-" * 50 + "\n")
            for i, video in enumerate(top_5, 1):
                f.write(f"{i}. 원제: {video.get('title', '')}\n")
                f.write(f"   한글: {video.get('korean_title', '')}\n")
                f.write(f"   언어: {video.get('language', '')} ({video.get('country', '')})\n")
                f.write(f"   성과: {video.get('view_count', 0):,} views | 키워드: {video.get('keyword', '')}\n")
                f.write(f"   채널: {video.get('channel_title', '')}\n\n")
            
            f.write("\nAI INSIGHTS WITH TRANSLATION:\n")
            f.write("=" * 40 + "\n")
            f.write(ai_insights)
        
        logger.info(f"Complete report saved: {report_path}")
        logger.info(f"Insights saved: {insights_path}")
        
        # 6. 모든 데이터 완료 후 일괄 Slack 전송
        logger.info("Sending complete Slack report with translations...")
        slack_message = self.create_slack_report_with_translation(videos, ai_insights)
        slack_success = self.send_slack_notification(slack_message)
        
        # 7. 결과 요약
        logger.info("=" * 70)
        logger.info("FINAL ANALYSIS WITH TRANSLATION COMPLETED")
        logger.info("=" * 70)
        logger.info(f"✅ Videos analyzed: {len(videos)}")
        logger.info(f"✅ Korean translations: {len([v for v in top_5 if v.get('korean_title')])}")
        logger.info(f"✅ Languages detected: {len(set(v.get('language', '') for v in top_5))}")
        logger.info(f"✅ AI insights: {'Generated' if ai_insights else 'Failed'}")
        logger.info(f"✅ Slack report: {'Sent' if slack_success else 'Failed'}")
        
        # TOP 5 번역 결과 요약
        logger.info("\n🏆 TOP 5 WITH TRANSLATION:")
        for i, video in enumerate(top_5, 1):
            logger.info(f"{i}. {video.get('view_count', 0):,} views - {video.get('language', '')}")
            logger.info(f"   Original: {video.get('title', '')[:50]}...")
            logger.info(f"   Korean: {video.get('korean_title', '')[:50]}...")
        
        return report_data

if __name__ == "__main__":
    analyzer = FinalAnalyzerWithTranslation()
    analyzer.run_final_analysis()