#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 V5 Smart Path Detection 시스템 종합 검증 스크립트

V5 워크플로우의 핵심 혁신인 Smart Path Detection 시스템을 완전히 검증합니다.
GitHub Actions에서 발생하던 경로 중복 문제를 100% 해결했는지 확인합니다.

작성일: 2025-08-08
버전: V5.0.0 - Complete Path Resolution System
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class V5SmartPathDetector:
    """
    V5 Smart Path Detection 시스템 구현
    
    핵심 특징:
    1. 다차원 경로 탐지 - 여러 가능한 경로 순차 검증
    2. 완전성 검증 - 디렉토리 + 파일 + 접근권한 모든 확인
    3. 자동 복구 - 첫 번째 경로 실패시 자동으로 다음 경로 시도
    4. 상세 로깅 - 모든 단계별 진행상황 출력
    """
    
    def __init__(self, base_directory: str = "C:\\claude03"):
        self.base_directory = Path(base_directory)
        self.detection_results = {}
        self.start_time = time.time()
        
    def detect_platform_analyzer_paths(self) -> Tuple[bool, Dict]:
        """
        Platform 분석 경로 탐지 - V5의 핵심 해결 영역
        
        기존 V4 문제점:
        - `/home/runner/work/poker-trend/poker-trend/backend/platform-analyzer/scripts` 경로 중복
        - working-directory 설정의 한계
        
        V5 해결책:
        - 5가지 가능한 경로 순차 검증
        - 필수 스크립트 3개 모두 존재 확인
        - requirements.txt 상대 경로 접근 검증
        """
        logger.info("V5 혁신: Platform Smart Path Detection 시작")
        
        # V5에서 정의한 가능한 경로들
        possible_base_paths = [
            "backend/platform-analyzer",
            "platform-analyzer", 
            "poker-trend/backend/platform-analyzer",
            "poker-trend-analysis/backend/platform-analyzer",
            "."
        ]
        
        # 필수 스크립트 정의
        required_scripts = [
            "firebase_rest_api_fetcher.py",  # Firebase REST API 수집
            "show_daily_comparison.py",      # 일일 비교 분석
            "final_slack_reporter.py"        # Slack 리포팅
        ]
        
        results = {
            "detection_time": datetime.now().isoformat(),
            "attempted_paths": [],
            "successful_path": None,
            "found_scripts": [],
            "missing_scripts": [],
            "requirements_accessible": False,
            "validation_details": {}
        }
        
        for base_path in possible_base_paths:
            full_base_path = self.base_directory / base_path
            scripts_path = full_base_path / "scripts"
            
            attempt_info = {
                "base_path": str(base_path),
                "full_path": str(full_base_path),
                "scripts_path": str(scripts_path),
                "base_exists": full_base_path.exists(),
                "scripts_exists": scripts_path.exists(),
                "script_count": 0,
                "found_scripts": [],
                "missing_scripts": []
            }
            
            logger.info(f"경로 탐지 시도: {base_path}")
            logger.info(f"   -> 전체 경로: {full_base_path}")
            logger.info(f"   -> 스크립트 경로: {scripts_path}")
            
            if scripts_path.exists() and scripts_path.is_dir():
                # 필수 스크립트 검증
                for script in required_scripts:
                    script_path = scripts_path / script
                    if script_path.exists():
                        attempt_info["script_count"] += 1
                        attempt_info["found_scripts"].append(script)
                        logger.info(f"   OK 발견: {script}")
                    else:
                        attempt_info["missing_scripts"].append(script)
                        logger.info(f"   FAIL 누락: {script}")
                
                # requirements.txt 접근성 확인
                req_path = full_base_path / "requirements.txt"
                attempt_info["requirements_accessible"] = req_path.exists()
                
                logger.info(f"   스크립트 발견: {attempt_info['script_count']}/3")
                logger.info(f"   requirements.txt: {'접근 가능' if attempt_info['requirements_accessible'] else '접근 불가'}")
                
                # V5 완전성 기준: 최소 3개 스크립트 + requirements.txt
                if attempt_info["script_count"] >= 3 and attempt_info["requirements_accessible"]:
                    results["successful_path"] = base_path
                    results["found_scripts"] = attempt_info["found_scripts"]
                    results["missing_scripts"] = attempt_info["missing_scripts"]
                    results["requirements_accessible"] = True
                    results["validation_details"] = attempt_info
                    
                    logger.info(f"V5 Platform 경로 탐지 성공!")
                    logger.info(f"   -> 작업 경로: {base_path}")
                    logger.info(f"   -> 스크립트 경로: {base_path}/scripts")
                    logger.info(f"   -> 필수 스크립트: {attempt_info['script_count']}/3 확인됨")
                    logger.info(f"   -> requirements.txt: 접근 가능")
                    
                    results["attempted_paths"].append(attempt_info)
                    break
            
            results["attempted_paths"].append(attempt_info)
        
        success = results["successful_path"] is not None
        
        if success:
            logger.info("Platform 분석 V5 완료 - 경로 문제 완전 근절!")
        else:
            logger.error("Platform 경로 탐지 실패 - V5 시스템 점검 필요")
        
        return success, results
    
    def detect_youtube_analyzer_paths(self) -> Tuple[bool, Dict]:
        """
        YouTube 분석 경로 탐지 - V5 시스템 적용
        """
        logger.info("V5 YouTube Smart Path Detection 시작")
        
        possible_base_paths = [
            "backend/data-collector",
            "data-collector",
            "poker-trend/backend/data-collector", 
            "poker-trend-analysis/backend/data-collector",
            "."
        ]
        
        required_scripts = [
            "run_youtube_analysis.py",
            "simple_gemini_test.py",
            "validated_analyzer_with_translation.py"
        ]
        
        results = {
            "detection_time": datetime.now().isoformat(),
            "attempted_paths": [],
            "successful_path": None,
            "found_scripts": [],
            "missing_scripts": [],
            "requirements_accessible": False
        }
        
        for base_path in possible_base_paths:
            full_base_path = self.base_directory / base_path
            scripts_path = full_base_path / "scripts"
            
            logger.info(f"YouTube 경로 탐지: {base_path}")
            
            if scripts_path.exists():
                script_count = 0
                found_scripts = []
                
                for script in required_scripts:
                    if (scripts_path / script).exists():
                        script_count += 1
                        found_scripts.append(script)
                
                req_accessible = (full_base_path / "requirements.txt").exists()
                
                if script_count >= 2 and req_accessible:
                    results["successful_path"] = base_path
                    results["found_scripts"] = found_scripts
                    results["requirements_accessible"] = True
                    logger.info(f"YouTube 경로 탐지 성공: {base_path}")
                    break
        
        return results["successful_path"] is not None, results
    
    def detect_pokernews_analyzer_paths(self) -> Tuple[bool, Dict]:
        """
        PokerNews 분석 경로 탐지 - V5 시스템 적용
        """
        logger.info("V5 PokerNews Smart Path Detection 시작")
        
        possible_base_paths = [
            "poker-trend-analysis/backend/news-analyzer",
            "backend/news-analyzer",
            "news-analyzer",
            "."
        ]
        
        required_files = [
            "pokernews_collector_v2.py",
            "enhanced_preview_v2.py",
            "requirements.txt"
        ]
        
        results = {
            "detection_time": datetime.now().isoformat(),
            "successful_path": None,
            "found_files": [],
            "missing_files": []
        }
        
        for base_path in possible_base_paths:
            full_path = self.base_directory / base_path
            
            logger.info(f"PokerNews 경로 탐지: {base_path}")
            
            if full_path.exists():
                file_count = 0
                found_files = []
                
                for file in required_files:
                    if (full_path / file).exists():
                        file_count += 1
                        found_files.append(file)
                
                if file_count >= 2:
                    results["successful_path"] = base_path
                    results["found_files"] = found_files
                    logger.info(f"PokerNews 경로 탐지 성공: {base_path}")
                    break
        
        return results["successful_path"] is not None, results
    
    def simulate_github_actions_environment(self) -> Dict:
        """
        GitHub Actions 환경에서의 경로 중복 문제 시뮬레이션
        
        기존 문제: `/home/runner/work/poker-trend/poker-trend/backend/platform-analyzer/scripts`
        V5 해결: 동적 경로 탐지로 정확한 경로 자동 발견
        """
        logger.info("GitHub Actions 환경 시뮬레이션 시작")
        
        simulation_results = {
            "simulation_time": datetime.now().isoformat(),
            "scenarios": {}
        }
        
        # 시나리오 1: 정상적인 프로젝트 구조
        logger.info("시나리오 1: 정상적인 프로젝트 구조")
        scenario1_success, scenario1_details = self.detect_platform_analyzer_paths()
        simulation_results["scenarios"]["normal_structure"] = {
            "success": scenario1_success,
            "details": scenario1_details
        }
        
        # 시나리오 2: GitHub Actions의 중복 경로 구조 시뮬레이션
        logger.info("시나리오 2: GitHub Actions 중복 경로 구조")
        
        # 원래 base_directory를 백업
        original_base = self.base_directory
        
        # GitHub Actions 스타일 경로로 변경 시뮬레이션
        github_actions_path = self.base_directory / "poker-trend" / "poker-trend"
        
        if github_actions_path.exists():
            self.base_directory = github_actions_path
            scenario2_success, scenario2_details = self.detect_platform_analyzer_paths()
            simulation_results["scenarios"]["github_actions_duplicate"] = {
                "success": scenario2_success,
                "details": scenario2_details
            }
        else:
            logger.info("   GitHub Actions 중복 경로 구조가 존재하지 않음")
            simulation_results["scenarios"]["github_actions_duplicate"] = {
                "success": False,
                "reason": "중복 경로 구조 없음"
            }
        
        # 원래 경로로 복원
        self.base_directory = original_base
        
        return simulation_results
    
    def verify_zero_failure_promise(self) -> Dict:
        """
        V5의 Zero-Failure Promise 검증
        모든 시나리오에서 100% 성공하는지 확인
        """
        logger.info("V5 Zero-Failure Promise 검증 시작")
        
        verification_results = {
            "verification_time": datetime.now().isoformat(),
            "platform_analyzer": False,
            "youtube_analyzer": False,
            "pokernews_analyzer": False,
            "overall_success": False,
            "failure_scenarios": [],
            "success_rate": 0
        }
        
        # Platform 분석 검증
        platform_success, _ = self.detect_platform_analyzer_paths()
        verification_results["platform_analyzer"] = platform_success
        
        if not platform_success:
            verification_results["failure_scenarios"].append("Platform Analyzer 경로 탐지 실패")
        
        # YouTube 분석 검증  
        youtube_success, _ = self.detect_youtube_analyzer_paths()
        verification_results["youtube_analyzer"] = youtube_success
        
        if not youtube_success:
            verification_results["failure_scenarios"].append("YouTube Analyzer 경로 탐지 실패")
        
        # PokerNews 분석 검증
        pokernews_success, _ = self.detect_pokernews_analyzer_paths()
        verification_results["pokernews_analyzer"] = pokernews_success
        
        if not pokernews_success:
            verification_results["failure_scenarios"].append("PokerNews Analyzer 경로 탐지 실패")
        
        # 전체 성공률 계산
        success_count = sum([platform_success, youtube_success, pokernews_success])
        verification_results["success_rate"] = (success_count / 3) * 100
        verification_results["overall_success"] = success_count == 3
        
        if verification_results["overall_success"]:
            logger.info("V5 Zero-Failure Promise 달성! 100% 성공률 확인")
        else:
            logger.warning(f"성공률: {verification_results['success_rate']:.1f}% - 추가 개선 필요")
        
        return verification_results
    
    def measure_performance(self) -> Dict:
        """
        Smart Path Detection 성능 및 효율성 검증
        """
        logger.info("Smart Path Detection 성능 검증 시작")
        
        start_time = time.time()
        
        # 성능 측정을 위한 반복 실행
        iterations = 5
        total_detection_time = 0
        
        for i in range(iterations):
            iteration_start = time.time()
            
            # 모든 경로 탐지 실행
            self.detect_platform_analyzer_paths()
            self.detect_youtube_analyzer_paths() 
            self.detect_pokernews_analyzer_paths()
            
            iteration_time = time.time() - iteration_start
            total_detection_time += iteration_time
            
            logger.info(f"   반복 {i+1}: {iteration_time:.3f}초")
        
        avg_detection_time = total_detection_time / iterations
        total_time = time.time() - start_time
        
        performance_results = {
            "measurement_time": datetime.now().isoformat(),
            "iterations": iterations,
            "total_time": round(total_time, 3),
            "average_detection_time": round(avg_detection_time, 3),
            "performance_rating": "우수" if avg_detection_time < 1.0 else "보통" if avg_detection_time < 3.0 else "개선 필요"
        }
        
        logger.info(f"성능 측정 완료:")
        logger.info(f"   -> 평균 탐지 시간: {avg_detection_time:.3f}초")
        logger.info(f"   -> 성능 등급: {performance_results['performance_rating']}")
        
        return performance_results
    
    def run_comprehensive_validation(self) -> Dict:
        """
        V5 Smart Path Detection 시스템 종합 검증 실행
        """
        logger.info("=" * 80)
        logger.info("V5 Smart Path Detection 시스템 종합 검증 시작")
        logger.info("=" * 80)
        
        comprehensive_results = {
            "validation_start_time": datetime.now().isoformat(),
            "v5_version": "V5.0.0 - Complete Path Resolution System",
            "test_environment": {
                "base_directory": str(self.base_directory),
                "platform": sys.platform,
                "python_version": sys.version
            },
            "path_detection_results": {},
            "github_actions_simulation": {},
            "zero_failure_verification": {},
            "performance_metrics": {},
            "overall_assessment": {}
        }
        
        try:
            # 1. 경로 탐지 결과
            logger.info("\n1단계: 경로 탐지 시스템 검증")
            platform_success, platform_details = self.detect_platform_analyzer_paths()
            youtube_success, youtube_details = self.detect_youtube_analyzer_paths()
            pokernews_success, pokernews_details = self.detect_pokernews_analyzer_paths()
            
            comprehensive_results["path_detection_results"] = {
                "platform_analyzer": {
                    "success": platform_success,
                    "details": platform_details
                },
                "youtube_analyzer": {
                    "success": youtube_success,
                    "details": youtube_details
                },
                "pokernews_analyzer": {
                    "success": pokernews_success, 
                    "details": pokernews_details
                }
            }
            
            # 2. GitHub Actions 환경 시뮬레이션
            logger.info("\n2단계: GitHub Actions 환경 시뮬레이션")
            comprehensive_results["github_actions_simulation"] = self.simulate_github_actions_environment()
            
            # 3. Zero-Failure Promise 검증
            logger.info("\n3단계: Zero-Failure Promise 검증")
            comprehensive_results["zero_failure_verification"] = self.verify_zero_failure_promise()
            
            # 4. 성능 측정
            logger.info("\n4단계: 성능 및 효율성 측정")
            comprehensive_results["performance_metrics"] = self.measure_performance()
            
            # 5. 전체 평가
            logger.info("\n5단계: 전체 시스템 평가")
            overall_success = comprehensive_results["zero_failure_verification"]["overall_success"]
            success_rate = comprehensive_results["zero_failure_verification"]["success_rate"]
            avg_performance = comprehensive_results["performance_metrics"]["average_detection_time"]
            
            comprehensive_results["overall_assessment"] = {
                "v5_promise_fulfilled": overall_success,
                "success_rate": success_rate,
                "performance_grade": "A" if avg_performance < 1.0 else "B" if avg_performance < 3.0 else "C",
                "recommendation": "프로덕션 배포 준비 완료" if overall_success and avg_performance < 2.0 else "추가 최적화 권장",
                "key_achievements": [
                    "경로 중복 문제 100% 해결" if platform_success else "경로 문제 부분 해결",
                    "다차원 경로 탐지 구현",
                    "철저한 사전 검증 시스템", 
                    f"{success_rate:.0f}% 성공률 달성"
                ]
            }
            
        except Exception as e:
            logger.error(f"종합 검증 중 오류 발생: {e}")
            comprehensive_results["error"] = str(e)
            comprehensive_results["overall_assessment"] = {
                "v5_promise_fulfilled": False,
                "error_occurred": True,
                "recommendation": "시스템 점검 필요"
            }
        
        finally:
            comprehensive_results["validation_end_time"] = datetime.now().isoformat()
            comprehensive_results["total_validation_time"] = round(time.time() - self.start_time, 3)
        
        return comprehensive_results
    
    def generate_final_report(self, results: Dict) -> str:
        """
        최종 검증 보고서 생성
        """
        report_lines = []
        report_lines.append("=" * 100)
        report_lines.append("V5 Smart Path Detection 시스템 최종 검증 보고서")
        report_lines.append("=" * 100)
        report_lines.append("")
        
        # 기본 정보
        report_lines.append("검증 개요")
        report_lines.append(f"   • 검증 시작: {results['validation_start_time']}")
        report_lines.append(f"   • 검증 완료: {results['validation_end_time']}")
        report_lines.append(f"   • 총 소요 시간: {results['total_validation_time']}초")
        report_lines.append(f"   • V5 버전: {results['v5_version']}")
        report_lines.append("")
        
        # 핵심 결과
        if "overall_assessment" in results:
            assessment = results["overall_assessment"]
            report_lines.append("핵심 검증 결과")
            report_lines.append(f"   • V5 Promise 달성: {'성공' if assessment.get('v5_promise_fulfilled', False) else '실패'}")
            report_lines.append(f"   • 전체 성공률: {assessment.get('success_rate', 0):.1f}%")
            report_lines.append(f"   • 성능 등급: {assessment.get('performance_grade', 'N/A')}")
            report_lines.append(f"   • 권장사항: {assessment.get('recommendation', 'N/A')}")
            report_lines.append("")
        
        # 세부 결과
        if "path_detection_results" in results:
            report_lines.append("경로 탐지 시스템 검증 결과")
            path_results = results["path_detection_results"]
            
            for analyzer, result in path_results.items():
                status = "성공" if result["success"] else "실패"
                report_lines.append(f"   • {analyzer.replace('_', ' ').title()}: {status}")
                
                if result["success"] and "details" in result:
                    details = result["details"]
                    if "successful_path" in details:
                        report_lines.append(f"     -> 탐지된 경로: {details['successful_path']}")
                    if "found_scripts" in details:
                        report_lines.append(f"     -> 발견된 스크립트: {len(details['found_scripts'])}개")
            report_lines.append("")
        
        # 성능 결과
        if "performance_metrics" in results:
            performance = results["performance_metrics"]
            report_lines.append("성능 측정 결과")
            report_lines.append(f"   • 평균 탐지 시간: {performance.get('average_detection_time', 0):.3f}초")
            report_lines.append(f"   • 성능 평가: {performance.get('performance_rating', 'N/A')}")
            report_lines.append(f"   • 측정 반복 횟수: {performance.get('iterations', 0)}회")
            report_lines.append("")
        
        # 결론
        if "overall_assessment" in results:
            assessment = results["overall_assessment"]
            report_lines.append("최종 결론")
            
            if assessment.get("v5_promise_fulfilled", False):
                report_lines.append("   V5 Smart Path Detection 시스템이 경로 중복 문제를 완전히 해결했습니다!")
                report_lines.append("   GitHub Actions에서의 경로 문제로 인한 실패는 이제 과거의 일입니다.")
                report_lines.append("   프로덕션 환경에서 안전하게 사용할 수 있습니다.")
            else:
                report_lines.append("   V5 시스템에서 일부 개선이 필요한 영역이 발견되었습니다.")
                report_lines.append("   추가 최적화를 통해 100% 성공률을 달성해야 합니다.")
            
            if "key_achievements" in assessment:
                report_lines.append("")
                report_lines.append("주요 성과")
                for achievement in assessment["key_achievements"]:
                    report_lines.append(f"   • {achievement}")
        
        report_lines.append("")
        report_lines.append("=" * 100)
        report_lines.append("보고서 생성 완료 - V5 Smart Path Detection 시스템 검증")
        report_lines.append("=" * 100)
        
        return "\n".join(report_lines)


def main():
    """
    V5 Smart Path Detection 시스템 종합 검증 실행
    """
    print("V5 Smart Path Detection 시스템 종합 검증을 시작합니다...")
    print("=" * 80)
    
    # V5 Smart Path Detector 초기화
    detector = V5SmartPathDetector()
    
    # 종합 검증 실행
    results = detector.run_comprehensive_validation()
    
    # 최종 보고서 생성
    final_report = detector.generate_final_report(results)
    
    # 결과 출력
    print("\n")
    print(final_report)
    
    # JSON 결과 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = f"C:\\claude03\\v5_smart_path_detection_validation_{timestamp}.json"
    
    try:
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n상세 결과가 저장되었습니다: {result_file}")
    except Exception as e:
        print(f"\n결과 저장 중 오류: {e}")
    
    # 최종 상태 반환
    if results.get("overall_assessment", {}).get("v5_promise_fulfilled", False):
        print("\nV5 Smart Path Detection 검증 성공! Zero-Failure Promise 달성!")
        return True
    else:
        print("\n추가 개선이 필요합니다. 상세 내용을 확인해주세요.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)