#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
검증된 포커 트렌드 분석기 - 한글 번역 포함
- 영상 유효성 검증 (존재 여부, 재생 가능 여부)
- 차순위 데이터 자동 추출
- 언어/국가 감지 및 한글 번역
- 간결한 쇼츠 아이디어 1개
- 일괄 Slack 업로드
"""

import os
import json
import logging
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
from googleapiclient.discovery import build
import re
import sys
sys.path.append(str(Path(__file__).parent.parent / 'src'))
from validators.poker_content_validator import PokerContentValidator

# 환경 변수 로드
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ValidatedAnalyzerWithTranslation:
    def __init__(self):
        self.youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        self.slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
        
        # 포커 콘텐츠 검증기 초기화
        cache_path = Path(__file__).parent / 'validation_cache.json'
        self.poker_validator = PokerContentValidator(str(cache_path))
        
        self.keywords = [
            'poker', 'holdem', 'wsop', 'wpt', 'ept', 
            'pokerstars', 'ggpoker', 'triton poker'
        ]
    
    def validate_video_availability(self, video_id):
        """영상 유효성 검증"""
        try:
            # YouTube API로 영상 세부 정보 확인
            response = self.youtube.videos().list(
                part='status,statistics,contentDetails',
                id=video_id
            ).execute()
            
            if not response.get('items'):
                logger.warning(f"Video not found: {video_id}")
                return False, "Video not found"
            
            video_data = response['items'][0]
            status = video_data.get('status', {})
            stats = video_data.get('statistics', {})
            
            # 영상 상태 확인
            if not status.get('uploadStatus') == 'processed':
                logger.warning(f"Video not processed: {video_id}")
                return False, "Video not processed"
            
            if status.get('privacyStatus') not in ['public', 'unlisted']:
                logger.warning(f"Video not public: {video_id} - {status.get('privacyStatus')}")
                return False, f"Video privacy: {status.get('privacyStatus')}"
            
            if status.get('embeddable') == False:
                logger.warning(f"Video not embeddable: {video_id}")
                return False, "Video not embeddable"
            
            # 조회수 확인 (0이면 문제가 있을 가능성)
            view_count = int(stats.get('viewCount', 0))
            if view_count == 0:
                logger.warning(f"Video has zero views: {video_id}")
                return False, "Zero views"
            
            logger.info(f"Video validated successfully: {video_id} ({view_count:,} views)")
            return True, "Valid"
            
        except Exception as e:
            logger.error(f"Video validation failed for {video_id}: {e}")
            return False, f"Validation error: {str(e)}"
    
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
                # 명확한 단일 번역만 요청하는 개선된 프롬프트
                translate_prompt = f"""Translate to Korean: {title}
                
                Rules:
                - Give me ONLY ONE Korean translation
                - No options, no alternatives, no explanations
                - Just the Korean text itself
                
                Korean:"""
                
                response = self.gemini_model.generate_content(translate_prompt)
                korean_title = response.text.strip()
                
                # 여러 옵션이 포함된 경우 첫 번째 줄만 추출
                if '\n' in korean_title:
                    korean_title = korean_title.split('\n')[0]
                
                # 불필요한 문자 및 패턴 제거
                korean_title = korean_title.replace('"', '').replace("'", '').strip()
                korean_title = korean_title.replace('옵션', '').replace('선택', '')
                
                # "Several options" 또는 "Here are" 등의 패턴 감지 및 처리
                if any(phrase in korean_title.lower() for phrase in ['several options', 'here are', 'options:', 'choices:']):
                    # 문제가 있는 경우 원본 제목 반환
                    logger.warning(f"Translation issue detected, using original: {title}")
                    translations[title] = title
                    continue
                
                # "1." 또는 "*" 같은 번호/불릿 제거
                korean_title = re.sub(r'^[0-9\.\*\-\s]+', '', korean_title)
                korean_title = korean_title.strip()
                
                translations[title] = korean_title
                logger.info(f"Translated: {title[:30]}... -> {korean_title[:30]}...")
                
            except Exception as e:
                logger.warning(f"Translation failed for {title[:30]}...: {e}")
                translations[title] = title  # 원본 반환
        
        return translations
    
    def collect_validated_video_data(self, max_results=10, target_count=5):
        """검증된 영상 데이터 수집 (더 많이 수집 후 유효한 것만 선별)"""
        logger.info(f"Starting validated video collection (collecting {max_results}, targeting {target_count})...")
        all_valid_videos = []
        validation_stats = {
            'total_checked': 0,
            'valid': 0,
            'invalid': 0,
            'invalid_reasons': {}
        }
        
        for keyword in self.keywords:
            try:
                # 더 많은 결과를 요청하여 유효하지 않은 영상 대비
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
                
                logger.info(f"Found {len(videos)} videos for keyword: {keyword}")
                
                for video in videos:
                    video_id = video['id']['videoId']
                    snippet = video['snippet']
                    
                    validation_stats['total_checked'] += 1
                    
                    # 영상 유효성 검증
                    is_valid, reason = self.validate_video_availability(video_id)
                    
                    if not is_valid:
                        validation_stats['invalid'] += 1
                        validation_stats['invalid_reasons'][reason] = validation_stats['invalid_reasons'].get(reason, 0) + 1
                        logger.info(f"Skipping invalid video: {video_id} - {reason}")
                        continue
                    
                    validation_stats['valid'] += 1
                    
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
                        'country': detected_country,
                        'validation_status': 'valid'
                    }
                    
                    # 상세 정보 가져오기 (이미 validation에서 확인했지만 다시 가져오기)
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
                    
                    all_valid_videos.append(video_data)
                
                logger.info(f"Valid videos collected for {keyword}: {validation_stats['valid'] - (validation_stats['total_checked'] - len(videos))}")
                
            except Exception as e:
                logger.error(f"Error collecting data for {keyword}: {e}")
        
        # 중복 제거
        unique_videos = []
        seen_ids = set()
        for video in all_valid_videos:
            if video['video_id'] not in seen_ids:
                unique_videos.append(video)
                seen_ids.add(video['video_id'])
        
        # 포커 콘텐츠 검증 필터링
        logger.info(f"🔍 포커 콘텐츠 검증 시작: {len(unique_videos)}개 영상")
        
        # 비디오 데이터를 포커 검증기에 맞는 형식으로 변환
        videos_for_validation = []
        for video in unique_videos:
            validation_data = {
                'videoId': video['video_id'],
                'title': video['original_title'],
                'description': video.get('description', ''),
                'tags': [],  # 기본값
                'channelTitle': video.get('channel_title', ''),
                'channelId': '',  # 필요하면 추후 추가
                'categoryId': '20',  # Gaming 카테고리 기본값
                'viewCount': str(video.get('view_count', 0)),
                'likeCount': str(video.get('like_count', 0)),
                'commentCount': str(video.get('comment_count', 0)),
                'duration': video.get('duration', ''),
                'publishedAt': video.get('published_at', '')
            }
            videos_for_validation.append(validation_data)
        
        # 포커 콘텐츠 검증 실행
        if videos_for_validation:
            poker_validated_videos = self.poker_validator.batch_validate(videos_for_validation)
            
            # 검증된 비디오 ID 추출
            validated_video_ids = {v.get('videoId') for v in poker_validated_videos}
            
            # 원본 비디오 데이터에서 검증된 것들만 필터링
            poker_filtered_videos = [
                video for video in unique_videos 
                if video['video_id'] in validated_video_ids
            ]
        else:
            logger.warning("검증할 비디오가 없습니다.")
            poker_filtered_videos = []
            poker_validated_videos = []
        
        # 포커 검증 결과를 원본 데이터에 추가
        for video in poker_filtered_videos:
            for validated in poker_validated_videos:
                if validated.get('videoId') == video['video_id']:
                    video['poker_validation'] = validated.get('validation', {})
                    break
        
        logger.info(f"✅ 포커 콘텐츠 검증 완료: {len(poker_filtered_videos)}/{len(unique_videos)}개 영상이 포커 콘텐츠로 확인")
        
        # 검증 통계 로깅
        logger.info("=== VALIDATION STATISTICS ===")
        logger.info(f"Total videos checked: {validation_stats['total_checked']}")
        logger.info(f"Poker content validated: {len(poker_filtered_videos)}/{len(unique_videos)}")
        logger.info(f"Valid videos: {validation_stats['valid']}")
        logger.info(f"Invalid videos: {validation_stats['invalid']}")
        logger.info("Invalid reasons:")
        for reason, count in validation_stats['invalid_reasons'].items():
            logger.info(f"  - {reason}: {count}")
        
        # TOP 5 선별 후 번역 (포커 검증된 영상에서)
        top_videos = sorted(poker_filtered_videos, key=lambda x: x.get('view_count', 0), reverse=True)[:target_count]
        
        if len(top_videos) < target_count:
            logger.warning(f"Only {len(top_videos)} poker validated videos found, requested {target_count}")
        
        # 번역할 제목들 준비
        titles_for_translation = [(video['title'], video['language']) for video in top_videos]
        
        # 배치 번역 실행
        logger.info(f"Starting Korean translation for TOP {len(top_videos)} videos...")
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
        
        logger.info(f"Total poker content validated videos: {len(poker_filtered_videos)}")
        logger.info(f"Korean translations completed for TOP {len(top_videos)}")
        
        return poker_filtered_videos, validation_stats
    
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
포커 트렌드 분석 전문가로서 다음 검증된 TOP {len(top_videos)} 영상(한글 번역 포함)을 분석하여 핵심 인사이트와 최고의 쇼츠 아이디어를 제안하세요.

=== 검증된 TOP {len(top_videos)} 영상 데이터 (원제 + 한글 번역) ===
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
    
    def create_slack_report_with_validation(self, videos, ai_insights, validation_stats):
        """검증 통계 포함 Slack 리포트"""
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
                    "text": "🎰 Validated Poker Analysis (Korean Translation)"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}\n📊 Total: {len(videos)} validated videos | {total_views:,} views\n🌍 Languages: {lang_summary}\n✅ Validation: {validation_stats['valid']}/{validation_stats['total_checked']} valid"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*🏆 TOP {len(top_videos)} VALIDATED VIDEOS WITH KOREAN TRANSLATION*"
                }
            }
        ]
        
        # TOP 5 영상 (원제 + 한글 번역)
        for i, video in enumerate(top_videos, 1):
            original_title = video.get('title', '')[:50] + "..." if len(video.get('title', '')) > 50 else video.get('title', '')
            korean_title = video.get('korean_title', '')[:50] + "..." if len(video.get('korean_title', '')) > 50 else video.get('korean_title', '')
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
    
    def run_validated_analysis(self):
        """검증된 분석 실행 (번역 포함)"""
        logger.info("=" * 70)
        logger.info("VALIDATED POKER TREND ANALYSIS WITH KOREAN TRANSLATION")
        logger.info("=" * 70)
        
        # 1. 검증된 데이터 수집 (번역 포함)
        videos, validation_stats = self.collect_validated_video_data(max_results=15, target_count=5)
        
        # 2. AI 인사이트 생성 (번역 포함)
        ai_insights = self.generate_insights_with_translation(videos)
        
        # 3. TOP 5 추출
        top_videos = sorted(videos, key=lambda x: x.get('view_count', 0), reverse=True)[:5]
        
        # 4. 리포트 생성
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "analysis_type": "validated_with_korean_translation",
            "total_videos": len(videos),
            "validation_stats": validation_stats,
            "data_fields": [
                "title", "korean_title", "language", "country", 
                "view_count", "like_count", "comment_count", "channel_title", "keyword"
            ],
            "ai_insights": ai_insights,
            "top_videos": top_videos,
            "all_videos": videos
        }
        
        # 5. 파일 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        reports_dir = Path(__file__).parent / 'reports'
        reports_dir.mkdir(exist_ok=True)
        
        report_path = reports_dir / f'validated_analysis_translated_{timestamp}.json'
        insights_path = reports_dir / f'validated_insights_translated_{timestamp}.txt'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        with open(insights_path, 'w', encoding='utf-8') as f:
            f.write("VALIDATED POKER TREND ANALYSIS WITH KOREAN TRANSLATION\n")
            f.write("=" * 60 + "\n\n")
            
            f.write("VALIDATION STATISTICS:\n")
            f.write("-" * 30 + "\n")
            f.write(f"Total videos checked: {validation_stats['total_checked']}\n")
            f.write(f"Valid videos: {validation_stats['valid']}\n")
            f.write(f"Invalid videos: {validation_stats['invalid']}\n")
            f.write("Invalid reasons:\n")
            for reason, count in validation_stats['invalid_reasons'].items():
                f.write(f"  - {reason}: {count}\n")
            f.write("\n")
            
            f.write(f"TOP {len(top_videos)} VALIDATED VIDEOS WITH KOREAN TRANSLATION:\n")
            f.write("-" * 50 + "\n")
            for i, video in enumerate(top_videos, 1):
                f.write(f"{i}. 원제: {video.get('title', '')}\n")
                f.write(f"   한글: {video.get('korean_title', '')}\n")
                f.write(f"   언어: {video.get('language', '')} ({video.get('country', '')})\n")
                f.write(f"   성과: {video.get('view_count', 0):,} views | 키워드: {video.get('keyword', '')}\n")
                f.write(f"   채널: {video.get('channel_title', '')}\n")
                f.write(f"   상태: {video.get('validation_status', 'unknown')}\n\n")
            
            f.write("\nAI INSIGHTS WITH TRANSLATION:\n")
            f.write("=" * 40 + "\n")
            f.write(ai_insights)
        
        logger.info(f"Complete report saved: {report_path}")
        logger.info(f"Insights saved: {insights_path}")
        
        # 6. 모든 데이터 완료 후 일괄 Slack 전송
        logger.info("Sending complete Slack report with validation stats...")
        slack_message = self.create_slack_report_with_validation(videos, ai_insights, validation_stats)
        slack_success = self.send_slack_notification(slack_message)
        
        # 7. 결과 요약
        logger.info("=" * 70)
        logger.info("VALIDATED ANALYSIS WITH TRANSLATION COMPLETED")
        logger.info("=" * 70)
        logger.info(f"✅ Videos validated and analyzed: {len(videos)}")
        logger.info(f"✅ Validation success rate: {validation_stats['valid']}/{validation_stats['total_checked']} ({round(validation_stats['valid']/validation_stats['total_checked']*100, 1)}%)")
        logger.info(f"✅ Korean translations: {len([v for v in top_videos if v.get('korean_title')])}") 
        logger.info(f"✅ Languages detected: {len(set(v.get('language', '') for v in top_videos))}")
        logger.info(f"✅ AI insights: {'Generated' if ai_insights else 'Failed'}")
        logger.info(f"✅ Slack report: {'Sent' if slack_success else 'Failed'}")
        
        # TOP 5 번역 결과 요약
        logger.info(f"\n🏆 TOP {len(top_videos)} VALIDATED WITH TRANSLATION:")
        for i, video in enumerate(top_videos, 1):
            logger.info(f"{i}. {video.get('view_count', 0):,} views - {video.get('language', '')}")
            logger.info(f"   Original: {video.get('title', '')[:50]}...")
            logger.info(f"   Korean: {video.get('korean_title', '')[:50]}...")
        
        return report_data

if __name__ == "__main__":
    analyzer = ValidatedAnalyzerWithTranslation()
    analyzer.run_validated_analysis()