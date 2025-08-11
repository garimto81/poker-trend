#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
일일 분석 프로세스 모니터링 및 알림 시스템
"""

import os
import sys
import json
import logging
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Any

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('daily_monitor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DailyProcessMonitor:
    def __init__(self):
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.processes = [
            {
                'name': 'Firebase 데이터 수집',
                'script': 'scripts/firebase_data_fetcher.py',
                'critical': True,
                'timeout': 300  # 5분
            },
            {
                'name': '일일 비교 분석',
                'script': 'scripts/show_daily_comparison.py', 
                'critical': True,
                'timeout': 180  # 3분
            },
            {
                'name': '경쟁 구도 분석',
                'script': 'scripts/competitive_analysis_reporter.py',
                'critical': False,
                'timeout': 240  # 4분
            },
            {
                'name': 'Slack 리포트 전송',
                'script': 'scripts/final_slack_reporter.py',
                'critical': True,
                'timeout': 120  # 2분
            }
        ]
    
    def run_daily_process(self) -> Dict[str, Any]:
        """일일 분석 프로세스 실행 및 모니터링"""
        logger.info(f"🚀 일일 분석 프로세스 시작: {self.today}")
        
        results = {
            'date': self.today,
            'start_time': datetime.now().isoformat(),
            'processes': [],
            'success_count': 0,
            'error_count': 0,
            'critical_errors': []
        }
        
        for process in self.processes:
            result = self._run_single_process(process)
            results['processes'].append(result)
            
            if result['success']:
                results['success_count'] += 1
                logger.info(f"✅ {process['name']} 완료")
            else:
                results['error_count'] += 1
                logger.error(f"❌ {process['name']} 실패: {result['error']}")
                
                if process['critical']:
                    results['critical_errors'].append(result)
        
        results['end_time'] = datetime.now().isoformat()
        results['duration'] = self._calculate_duration(results['start_time'], results['end_time'])
        
        # 결과 저장
        self._save_results(results)
        
        # 알림 전송
        self._send_notifications(results)
        
        return results
    
    def _run_single_process(self, process: Dict) -> Dict[str, Any]:
        """개별 프로세스 실행"""
        start_time = datetime.now()
        
        try:
            result = subprocess.run(
                [sys.executable, process['script']],
                timeout=process['timeout'],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            success = result.returncode == 0
            
            return {
                'name': process['name'],
                'script': process['script'],
                'success': success,
                'start_time': start_time.isoformat(),
                'end_time': datetime.now().isoformat(),
                'duration': (datetime.now() - start_time).total_seconds(),
                'stdout': result.stdout[-1000:] if result.stdout else '',  # 마지막 1000자만
                'stderr': result.stderr[-1000:] if result.stderr else '',
                'error': result.stderr if not success else None
            }
            
        except subprocess.TimeoutExpired:
            return {
                'name': process['name'],
                'script': process['script'],
                'success': False,
                'start_time': start_time.isoformat(),
                'end_time': datetime.now().isoformat(),
                'duration': process['timeout'],
                'error': f"타임아웃 ({process['timeout']}초 초과)"
            }
        
        except Exception as e:
            return {
                'name': process['name'],
                'script': process['script'],
                'success': False,
                'start_time': start_time.isoformat(),
                'end_time': datetime.now().isoformat(),
                'duration': (datetime.now() - start_time).total_seconds(),
                'error': str(e)
            }
    
    def _calculate_duration(self, start: str, end: str) -> float:
        """실행 시간 계산"""
        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)
        return (end_dt - start_dt).total_seconds()
    
    def _save_results(self, results: Dict[str, Any]):
        """결과를 파일에 저장"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"daily_monitor_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📄 모니터링 결과 저장: {filename}")
    
    def _send_notifications(self, results: Dict[str, Any]):
        """결과에 따른 알림 전송"""
        if results['critical_errors']:
            self._send_error_notification(results)
        elif results['error_count'] > 0:
            self._send_warning_notification(results)
        else:
            self._send_success_notification(results)
    
    def _send_error_notification(self, results: Dict[str, Any]):
        """중요 오류 알림"""
        message = f"""
🚨 일일 포커 분석 프로세스 중요 오류 발생
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 날짜: {results['date']}
⏱️ 실행 시간: {results['duration']:.1f}초

❌ 중요 오류:
"""
        for error in results['critical_errors']:
            message += f"• {error['name']}: {error['error']}\n"
        
        message += f"""
📊 전체 결과: {results['success_count']}개 성공 / {results['error_count']}개 실패
🔧 조치 필요: 즉시 확인 및 수정 필요
        """
        
        logger.error(message)
        # TODO: Slack 긴급 알림 전송
    
    def _send_warning_notification(self, results: Dict[str, Any]):
        """경고 알림"""
        logger.warning(f"⚠️ 일부 프로세스 실패: {results['error_count']}개")
    
    def _send_success_notification(self, results: Dict[str, Any]):
        """성공 알림"""
        logger.info(f"✅ 모든 프로세스 성공 완료 ({results['duration']:.1f}초)")

def main():
    """메인 실행 함수"""
    monitor = DailyProcessMonitor()
    results = monitor.run_daily_process()
    
    print("\n" + "="*60)
    print("📊 일일 분석 프로세스 모니터링 결과")
    print("="*60)
    print(f"날짜: {results['date']}")
    print(f"총 실행 시간: {results['duration']:.1f}초")
    print(f"성공: {results['success_count']}개")
    print(f"실패: {results['error_count']}개")
    
    if results['critical_errors']:
        print("\n🚨 중요 오류:")
        for error in results['critical_errors']:
            print(f"  - {error['name']}: {error['error']}")
    
    print("="*60)
    
    # 종료 코드 설정
    return 1 if results['critical_errors'] else 0

if __name__ == "__main__":
    sys.exit(main())