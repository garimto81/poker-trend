#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
순차적 워크플로우 설정 검증 스크립트
GitHub Actions 워크플로우가 제대로 설정되어 있는지 검증
"""

import os
import json
import yaml
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class WorkflowValidator:
    """워크플로우 설정 검증기"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.workflow_file = self.project_root / '.github' / 'workflows' / 'integrated-daily-poker-report.yml'
        self.health_check_file = self.project_root / '.github' / 'workflows' / 'workflow-health-check.yml'
        self.errors = []
        self.warnings = []
        self.success_items = []
        
    def validate_workflow_file_exists(self) -> bool:
        """워크플로우 파일 존재 확인"""
        if self.workflow_file.exists():
            self.success_items.append(f"[OK] 메인 워크플로우 파일 존재: {self.workflow_file}")
            return True
        else:
            self.errors.append(f"[ERROR] 메인 워크플로우 파일 없음: {self.workflow_file}")
            return False
    
    def validate_health_check_file_exists(self) -> bool:
        """헬스체크 파일 존재 확인"""
        if self.health_check_file.exists():
            self.success_items.append(f"[OK] 헬스체크 파일 존재: {self.health_check_file}")
            return True
        else:
            self.warnings.append(f"[WARNING] 헬스체크 파일 없음: {self.health_check_file}")
            return False
    
    def validate_yaml_syntax(self) -> bool:
        """YAML 문법 검증"""
        try:
            with open(self.workflow_file, 'r', encoding='utf-8') as f:
                yaml.safe_load(f)
            self.success_items.append("[OK] 메인 워크플로우 YAML 문법 정상")
            
            if self.health_check_file.exists():
                with open(self.health_check_file, 'r', encoding='utf-8') as f:
                    yaml.safe_load(f)
                self.success_items.append("[OK] 헬스체크 워크플로우 YAML 문법 정상")
            
            return True
        except yaml.YAMLError as e:
            self.errors.append(f"[ERROR] YAML 문법 오류: {e}")
            return False
        except FileNotFoundError as e:
            self.errors.append(f"[ERROR] 파일을 찾을 수 없음: {e}")
            return False
    
    def validate_workflow_structure(self) -> bool:
        """워크플로우 구조 검증"""
        try:
            with open(self.workflow_file, 'r', encoding='utf-8') as f:
                workflow = yaml.safe_load(f)
            
            # 필수 필드 검증 (on은 True로 파싱될 수 있음)
            required_fields = ['name', 'jobs']
            for field in required_fields:
                if field not in workflow:
                    self.errors.append(f"[ERROR] 필수 필드 누락: {field}")
                    return False
            
            # 'on' 필드는 True 또는 dict로 존재해야 함
            if 'on' not in workflow and True not in workflow:
                self.errors.append("[ERROR] 필수 필드 누락: on (트리거 설정)")
                return False
            
            # 스케줄 설정 확인 (True로 파싱된 경우 처리)
            trigger_config = workflow.get('on', workflow.get(True, {}))
            if isinstance(trigger_config, dict) and 'schedule' in trigger_config:
                cron = trigger_config['schedule'][0]['cron']
                if cron == '0 1 * * *':  # 매일 01:00 UTC (10:00 KST)
                    self.success_items.append("[OK] 스케줄 설정 정상: 매일 오전 10시 KST")
                else:
                    self.warnings.append(f"[WARNING] 예상과 다른 스케줄: {cron}")
            else:
                self.warnings.append("[WARNING] 스케줄 설정이 없습니다")
            
            # Jobs 순서 확인
            jobs = workflow['jobs']
            expected_jobs = [
                'poker-news-analysis',
                'youtube-trend-analysis', 
                'platform-trend-analysis',
                'workflow-completion-report'
            ]
            
            for job in expected_jobs:
                if job in jobs:
                    self.success_items.append(f"[OK] Job 존재: {job}")
                else:
                    self.errors.append(f"[ERROR] Job 누락: {job}")
            
            # 의존성 확인
            youtube_job = jobs.get('youtube-trend-analysis', {})
            if 'needs' in youtube_job and 'poker-news-analysis' in youtube_job['needs']:
                self.success_items.append("[OK] YouTube 분석이 PokerNews 분석 이후 실행되도록 설정")
            else:
                self.errors.append("[ERROR] YouTube 분석의 의존성 설정 오류")
            
            platform_job = jobs.get('platform-trend-analysis', {})
            if 'needs' in platform_job and 'youtube-trend-analysis' in platform_job['needs']:
                self.success_items.append("[OK] Platform 분석이 YouTube 분석 이후 실행되도록 설정")
            else:
                self.errors.append("[ERROR] Platform 분석의 의존성 설정 오류")
            
            return len(self.errors) == 0
            
        except Exception as e:
            self.errors.append(f"[ERROR] 워크플로우 구조 검증 실패: {e}")
            return False
    
    def validate_script_paths(self) -> bool:
        """스크립트 파일 경로 검증"""
        script_paths = [
            "poker-trend-analysis/backend/news-analyzer/pokernews_slack_reporter.py",
            "backend/data-collector/scripts/validated_analyzer_with_translation.py",
            "backend/platform-analyzer/scripts/final_slack_reporter.py"
        ]
        
        all_exist = True
        for script_path in script_paths:
            full_path = self.project_root / script_path
            if full_path.exists():
                self.success_items.append(f"[OK] 스크립트 존재: {script_path}")
            else:
                self.errors.append(f"[ERROR] 스크립트 누락: {script_path}")
                all_exist = False
        
        return all_exist
    
    def validate_requirements_files(self) -> bool:
        """Requirements 파일 존재 확인"""
        req_paths = [
            "poker-trend-analysis/backend/news-analyzer/requirements.txt",
            "backend/data-collector/requirements.txt", 
            "backend/platform-analyzer/requirements.txt"
        ]
        
        all_exist = True
        for req_path in req_paths:
            full_path = self.project_root / req_path
            if full_path.exists():
                self.success_items.append(f"[OK] Requirements 파일 존재: {req_path}")
            else:
                self.warnings.append(f"[WARNING] Requirements 파일 누락: {req_path}")
                all_exist = False
        
        return all_exist
    
    def validate_env_variables(self) -> bool:
        """환경 변수 문서 확인"""
        required_vars = [
            'SLACK_WEBHOOK_URL',
            'YOUTUBE_API_KEY', 
            'GEMINI_API_KEY'
        ]
        
        self.success_items.append("[OK] 필요한 GitHub Secrets:")
        for var in required_vars:
            self.success_items.append(f"   - {var}")
        
        return True
    
    def check_cron_schedule(self) -> str:
        """크론 스케줄 해석"""
        # 0 1 * * * = 매일 01:00 UTC
        # UTC+9 = KST이므로, 01:00 UTC = 10:00 KST
        return "매일 오전 10시 (KST) / 오전 1시 (UTC)"
    
    def generate_setup_checklist(self) -> List[str]:
        """설정 체크리스트 생성"""
        checklist = [
            "□ GitHub Repository Settings에서 Secrets 설정:",
            "  □ SLACK_WEBHOOK_URL (Slack Incoming Webhook URL)",
            "  □ YOUTUBE_API_KEY (YouTube Data API v3 키)",
            "  □ GEMINI_API_KEY (Google Gemini API 키)",
            "",
            "□ Actions 탭에서 워크플로우 확인:",
            "  □ 'Daily Poker Report - Sequential Workflow' 워크플로우 활성화",
            "  □ 'Workflow Health Check' 워크플로우로 연결 테스트",
            "",
            "□ 스케줄 확인:",
            f"  □ 실행 시간: {self.check_cron_schedule()}",
            "  □ Manual trigger 가능 (workflow_dispatch)",
            "",
            "□ 모니터링 설정:",
            "  □ Slack 채널에서 리포트 수신 확인",
            "  □ GitHub Actions 탭에서 실행 로그 모니터링",
            "  □ 실패 시 알림 설정"
        ]
        return checklist
    
    def run_validation(self) -> Dict:
        """전체 검증 실행"""
        print("순차적 워크플로우 설정 검증 시작...")
        print("=" * 60)
        
        # 1. 파일 존재 확인
        self.validate_workflow_file_exists()
        self.validate_health_check_file_exists()
        
        # 2. YAML 문법 검증
        self.validate_yaml_syntax()
        
        # 3. 워크플로우 구조 검증
        self.validate_workflow_structure()
        
        # 4. 스크립트 파일 확인
        self.validate_script_paths()
        
        # 5. Requirements 파일 확인
        self.validate_requirements_files()
        
        # 6. 환경 변수 확인
        self.validate_env_variables()
        
        # 결과 정리
        result = {
            'timestamp': datetime.now().isoformat(),
            'total_success': len(self.success_items),
            'total_warnings': len(self.warnings),
            'total_errors': len(self.errors),
            'success_items': self.success_items,
            'warnings': self.warnings,
            'errors': self.errors,
            'overall_status': 'PASS' if len(self.errors) == 0 else 'FAIL',
            'setup_checklist': self.generate_setup_checklist()
        }
        
        return result
    
    def print_report(self, result: Dict):
        """검증 결과 출력"""
        print("\n" + "=" * 60)
        print("워크플로우 검증 결과")
        print("=" * 60)
        
        # 성공 항목
        if result['success_items']:
            print(f"\n[SUCCESS] 성공 ({result['total_success']}개):")
            for item in result['success_items']:
                print(f"  {item}")
        
        # 경고 항목
        if result['warnings']:
            print(f"\n[WARNING] 경고 ({result['total_warnings']}개):")
            for warning in result['warnings']:
                print(f"  {warning}")
        
        # 에러 항목
        if result['errors']:
            print(f"\n[ERROR] 오류 ({result['total_errors']}개):")
            for error in result['errors']:
                print(f"  {error}")
        
        # 전체 상태
        print(f"\n[RESULT] 전체 상태: {result['overall_status']}")
        
        if result['overall_status'] == 'PASS':
            print("[SUCCESS] 워크플로우 설정이 정상적으로 완료되었습니다!")
        else:
            print("[ERROR] 워크플로우 설정에 문제가 있습니다. 위의 오류를 수정해주세요.")
        
        # 설정 체크리스트
        print("\n[CHECKLIST] 설정 완료 체크리스트:")
        print("-" * 40)
        for item in result['setup_checklist']:
            print(item)
        
        print(f"\n[TIME] 검증 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

def main():
    """메인 실행 함수"""
    validator = WorkflowValidator()
    result = validator.run_validation()
    validator.print_report(result)
    
    # 결과를 JSON 파일로 저장
    output_file = Path(__file__).parent / f"workflow-validation-{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n[FILE] 상세 결과 저장: {output_file}")
    
    # 에러가 있으면 비정상 종료
    if result['total_errors'] > 0:
        exit(1)

if __name__ == "__main__":
    main()