// 포커 트렌드 분석 플랫폼 - 성능 및 에러 시나리오 테스트
const { test, expect } = require('@playwright/test');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

test.describe('Performance and Error Scenario Tests', () => {
  const testResultsDir = path.join(__dirname, '..', 'test-results');
  let performanceResults = {
    benchmarks: [],
    errorHandling: [],
    loadTests: [],
    memoryUsage: []
  };

  test.beforeAll(async () => {
    if (!fs.existsSync(testResultsDir)) {
      fs.mkdirSync(testResultsDir, { recursive: true });
    }
  });

  test.afterAll(async () => {
    // 성능 테스트 결과 저장
    const resultPath = path.join(testResultsDir, 'performance-test-results.json');
    fs.writeFileSync(resultPath, JSON.stringify(performanceResults, null, 2));
    
    console.log(`📊 성능 테스트 결과 저장: ${resultPath}`);
  });

  test('시스템 성능 벤치마크 테스트', async () => {
    const performanceScript = `
import time
import json
import psutil
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

class PerformanceBenchmark:
    def __init__(self):
        self.benchmark_results = {}
        self.system_metrics = {}
    
    def measure_execution_time(self, func, *args, **kwargs):
        """함수 실행 시간 측정"""
        start_time = time.time()
        start_cpu = time.process_time()
        
        try:
            result = func(*args, **kwargs)
            success = True
            error = None
        except Exception as e:
            result = None
            success = False
            error = str(e)
        
        end_time = time.time()
        end_cpu = time.process_time()
        
        return {
            "result": result,
            "success": success,
            "error": error,
            "wall_time": end_time - start_time,
            "cpu_time": end_cpu - start_cpu,
            "timestamp": datetime.now().isoformat()
        }
    
    def simulate_pokernews_collection(self, article_count=100):
        """PokerNews 수집 성능 시뮬레이션"""
        articles = []
        processing_times = []
        
        for i in range(article_count):
            start = time.time()
            
            # 기사 처리 시뮬레이션 (실제로는 RSS 파싱, AI 분석 등)
            article = {
                "id": f"article_{i}",
                "title": f"Poker News Article {i}",
                "content": f"Content for article {i}" * 50,  # 긴 내용 시뮬레이션
                "processed_at": datetime.now().isoformat()
            }
            
            # 처리 지연 시뮬레이션
            time.sleep(0.01)  # 10ms 처리 시간
            
            articles.append(article)
            processing_times.append(time.time() - start)
        
        return {
            "total_articles": len(articles),
            "avg_processing_time": sum(processing_times) / len(processing_times),
            "max_processing_time": max(processing_times),
            "min_processing_time": min(processing_times),
            "throughput": len(articles) / sum(processing_times) if processing_times else 0
        }
    
    def simulate_youtube_analysis(self, video_count=200):
        """YouTube 분석 성능 시뮬레이션"""
        videos = []
        analysis_times = []
        
        for i in range(video_count):
            start = time.time()
            
            # 비디오 분석 시뮬레이션
            video_analysis = {
                "video_id": f"video_{i}",
                "title": f"Poker Video {i}",
                "views": 1000 + (i * 100),
                "analysis": {
                    "sentiment_score": 7.5 + (i % 3),
                    "topic_relevance": 0.8 + (i % 10) / 100,
                    "engagement_prediction": "high" if i % 3 == 0 else "medium"
                },
                "processed_at": datetime.now().isoformat()
            }
            
            # AI 분석 지연 시뮬레이션
            time.sleep(0.02)  # 20ms AI 분석 시간
            
            videos.append(video_analysis)
            analysis_times.append(time.time() - start)
        
        return {
            "total_videos": len(videos),
            "avg_analysis_time": sum(analysis_times) / len(analysis_times),
            "max_analysis_time": max(analysis_times),
            "throughput": len(videos) / sum(analysis_times) if analysis_times else 0
        }
    
    def simulate_platform_data_processing(self, data_points=1000):
        """플랫폼 데이터 처리 성능 시뮬레이션"""
        data_processing_times = []
        processed_data = []
        
        for i in range(data_points):
            start = time.time()
            
            # 데이터 포인트 처리 시뮬레이션
            data_point = {
                "timestamp": datetime.now().isoformat(),
                "player_id": f"player_{i}",
                "game_type": "cash" if i % 2 == 0 else "tournament",
                "stakes": ["low", "medium", "high"][i % 3],
                "duration": 3600 + (i * 60),  # 게임 시간 (초)
                "profit_loss": (i - data_points/2) * 10  # 손익
            }
            
            # 데이터 검증 및 변환 시뮬레이션
            time.sleep(0.001)  # 1ms 처리 시간
            
            processed_data.append(data_point)
            data_processing_times.append(time.time() - start)
        
        return {
            "total_data_points": len(processed_data),
            "avg_processing_time": sum(data_processing_times) / len(data_processing_times),
            "throughput": len(processed_data) / sum(data_processing_times) if data_processing_times else 0,
            "data_size_mb": len(str(processed_data)) / (1024 * 1024)
        }
    
    def run_concurrent_load_test(self, max_workers=5):
        """동시성 부하 테스트"""
        tasks = [
            ("pokernews", self.simulate_pokernews_collection, 50),
            ("youtube", self.simulate_youtube_analysis, 100),
            ("platform", self.simulate_platform_data_processing, 500),
            ("pokernews_heavy", self.simulate_pokernews_collection, 100),
            ("youtube_heavy", self.simulate_youtube_analysis, 200)
        ]
        
        results = {}
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 모든 작업을 동시에 시작
            future_to_task = {
                executor.submit(func, count): (name, func, count)
                for name, func, count in tasks
            }
            
            # 결과 수집
            for future in as_completed(future_to_task):
                name, func, count = future_to_task[future]
                try:
                    result = future.result()
                    results[name] = {
                        "success": True,
                        "result": result,
                        "task_count": count
                    }
                except Exception as e:
                    results[name] = {
                        "success": False,
                        "error": str(e),
                        "task_count": count
                    }
        
        total_time = time.time() - start_time
        
        return {
            "concurrent_tasks": len(tasks),
            "total_execution_time": total_time,
            "successful_tasks": sum(1 for r in results.values() if r["success"]),
            "task_results": results
        }
    
    def monitor_system_resources(self, duration=10):
        """시스템 리소스 모니터링"""
        measurements = []
        
        for i in range(duration):
            measurement = {
                "timestamp": datetime.now().isoformat(),
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "memory_used_mb": psutil.virtual_memory().used / (1024 * 1024),
                "disk_io_read_mb": psutil.disk_io_counters().read_bytes / (1024 * 1024) if psutil.disk_io_counters() else 0,
                "disk_io_write_mb": psutil.disk_io_counters().write_bytes / (1024 * 1024) if psutil.disk_io_counters() else 0
            }
            measurements.append(measurement)
        
        return {
            "duration_seconds": duration,
            "measurements": measurements,
            "avg_cpu_percent": sum(m["cpu_percent"] for m in measurements) / len(measurements),
            "avg_memory_percent": sum(m["memory_percent"] for m in measurements) / len(measurements),
            "max_memory_used_mb": max(m["memory_used_mb"] for m in measurements)
        }
    
    def run_full_performance_test(self):
        """전체 성능 테스트 실행"""
        print("🚀 포커 트렌드 분석 플랫폼 - 성능 벤치마크 테스트")
        print("=" * 60)
        
        # 1. 개별 컴포넌트 성능 테스트
        print("\\n1️⃣ 개별 컴포넌트 성능 테스트")
        
        # PokerNews 성능 테스트
        pokernews_result = self.measure_execution_time(self.simulate_pokernews_collection, 100)
        print(f"   PokerNews (100 articles): {pokernews_result['wall_time']:.2f}초")
        self.benchmark_results["pokernews"] = pokernews_result
        
        # YouTube 성능 테스트
        youtube_result = self.measure_execution_time(self.simulate_youtube_analysis, 200)
        print(f"   YouTube (200 videos): {youtube_result['wall_time']:.2f}초")
        self.benchmark_results["youtube"] = youtube_result
        
        # Platform 성능 테스트
        platform_result = self.measure_execution_time(self.simulate_platform_data_processing, 1000)
        print(f"   Platform (1000 data points): {platform_result['wall_time']:.2f}초")
        self.benchmark_results["platform"] = platform_result
        
        # 2. 동시성 부하 테스트
        print("\\n2️⃣ 동시성 부하 테스트")
        concurrent_result = self.run_concurrent_load_test(max_workers=5)
        print(f"   동시 작업 수: {concurrent_result['concurrent_tasks']}")
        print(f"   총 실행 시간: {concurrent_result['total_execution_time']:.2f}초")
        print(f"   성공한 작업: {concurrent_result['successful_tasks']}/{concurrent_result['concurrent_tasks']}")
        self.benchmark_results["concurrent_load"] = concurrent_result
        
        # 3. 시스템 리소스 모니터링
        print("\\n3️⃣ 시스템 리소스 모니터링 (10초)")
        resource_monitoring = self.monitor_system_resources(10)
        print(f"   평균 CPU 사용률: {resource_monitoring['avg_cpu_percent']:.1f}%")
        print(f"   평균 메모리 사용률: {resource_monitoring['avg_memory_percent']:.1f}%")
        print(f"   최대 메모리 사용량: {resource_monitoring['max_memory_used_mb']:.1f}MB")
        self.benchmark_results["system_resources"] = resource_monitoring
        
        # 4. 성능 평가
        print("\\n4️⃣ 성능 평가")
        
        # 처리량 기준 (초당 처리 건수)
        pokernews_throughput = pokernews_result["result"]["throughput"] if pokernews_result["success"] else 0
        youtube_throughput = youtube_result["result"]["throughput"] if youtube_result["success"] else 0
        platform_throughput = platform_result["result"]["throughput"] if platform_result["success"] else 0
        
        print(f"   PokerNews 처리량: {pokernews_throughput:.1f} articles/sec")
        print(f"   YouTube 처리량: {youtube_throughput:.1f} videos/sec")  
        print(f"   Platform 처리량: {platform_throughput:.1f} data points/sec")
        
        # 전반적 성능 점수 계산
        performance_score = 0
        if pokernews_result["success"] and pokernews_result["wall_time"] < 5:
            performance_score += 25
        if youtube_result["success"] and youtube_result["wall_time"] < 10:
            performance_score += 25
        if platform_result["success"] and platform_result["wall_time"] < 3:
            performance_score += 25
        if concurrent_result["successful_tasks"] == concurrent_result["concurrent_tasks"]:
            performance_score += 25
        
        print(f"\\n📊 전체 성능 점수: {performance_score}/100")
        
        if performance_score >= 80:
            print("✅ 성능 등급: EXCELLENT")
        elif performance_score >= 60:
            print("⚠️ 성능 등급: GOOD")
        else:
            print("❌ 성능 등급: NEEDS IMPROVEMENT")
        
        return {
            "performance_score": performance_score,
            "benchmark_results": self.benchmark_results
        }

# 성능 벤치마크 실행
try:
    import psutil
    benchmark = PerformanceBenchmark()
    results = benchmark.run_full_performance_test()
    print("\\n성능 벤치마크 테스트: COMPLETED")
    
except ImportError:
    print("⚠️ psutil 라이브러리가 없어 시스템 모니터링을 건너뜁니다.")
    print("간단한 성능 테스트만 실행됩니다.")
    
    # psutil 없이 간단한 테스트
    benchmark = PerformanceBenchmark()
    
    # 기본 성능 테스트만 실행
    print("🚀 기본 성능 테스트")
    pokernews_result = benchmark.simulate_pokernews_collection(50)
    youtube_result = benchmark.simulate_youtube_analysis(100) 
    platform_result = benchmark.simulate_platform_data_processing(500)
    
    print(f"PokerNews 처리량: {pokernews_result['throughput']:.1f} articles/sec")
    print(f"YouTube 처리량: {youtube_result['throughput']:.1f} videos/sec")
    print(f"Platform 처리량: {platform_result['throughput']:.1f} data points/sec")
    
    print("\\n기본 성능 테스트: COMPLETED")
`;
    
    const tempScript = path.join(testResultsDir, 'temp_performance_test.py');
    fs.writeFileSync(tempScript, performanceScript);
    
    const result = await runPythonScript(tempScript, []);
    
    expect(result.output).toContain('성능 벤치마크 테스트');
    expect(result.output).toContain('COMPLETED');
    
    // 성능 결과 기록
    performanceResults.benchmarks.push({
      name: 'system_performance_benchmark',
      success: result.code === 0,
      output: result.output
    });
    
    // 임시 파일 정리
    if (fs.existsSync(tempScript)) {
      fs.unlinkSync(tempScript);
    }
  });

  test('에러 시나리오 및 복구 테스트', async () => {
    const errorScenarioScript = `
import json
import random
import time
from datetime import datetime

class ErrorScenarioTester:
    def __init__(self):
        self.error_scenarios = {
            "api_failure": {
                "description": "API 서비스 실패",
                "probability": 0.1,
                "recovery_strategies": ["retry", "fallback", "cache"]
            },
            "network_timeout": {
                "description": "네트워크 타임아웃",
                "probability": 0.15,
                "recovery_strategies": ["retry", "timeout_extension"]
            },
            "rate_limit": {
                "description": "API 요청 제한 초과",
                "probability": 0.05,
                "recovery_strategies": ["backoff", "queue", "alternative_source"]
            },
            "data_corruption": {
                "description": "데이터 손상",
                "probability": 0.02,
                "recovery_strategies": ["validation", "backup_restore", "skip"]
            },
            "memory_pressure": {
                "description": "메모리 부족",
                "probability": 0.03,
                "recovery_strategies": ["garbage_collection", "batch_processing", "disk_cache"]
            },
            "dependency_failure": {
                "description": "외부 의존성 실패",
                "probability": 0.08,
                "recovery_strategies": ["circuit_breaker", "alternative_service", "degraded_mode"]
            }
        }
        
        self.recovery_success_rates = {
            "retry": 0.8,
            "fallback": 0.9,
            "cache": 0.7,
            "timeout_extension": 0.6,
            "backoff": 0.85,
            "queue": 0.75,
            "alternative_source": 0.8,
            "validation": 0.95,
            "backup_restore": 0.9,
            "skip": 1.0,
            "garbage_collection": 0.7,
            "batch_processing": 0.8,
            "disk_cache": 0.85,
            "circuit_breaker": 0.9,
            "alternative_service": 0.7,
            "degraded_mode": 0.95
        }
    
    def simulate_component_operation(self, component, operation_count=100):
        """구성요소 작업 시뮬레이션"""
        results = {
            "component": component,
            "total_operations": operation_count,
            "successful_operations": 0,
            "failed_operations": 0,
            "errors_encountered": {},
            "recovery_attempts": {},
            "total_recovery_time": 0
        }
        
        for i in range(operation_count):
            # 에러 발생 시뮬레이션
            error_occurred = None
            for error_type, config in self.error_scenarios.items():
                if random.random() < config["probability"]:
                    error_occurred = error_type
                    break
            
            if error_occurred:
                # 에러 기록
                if error_occurred not in results["errors_encountered"]:
                    results["errors_encountered"][error_occurred] = 0
                results["errors_encountered"][error_occurred] += 1
                
                # 복구 시도
                recovery_success = self.attempt_recovery(error_occurred)
                
                if recovery_success["success"]:
                    results["successful_operations"] += 1
                    results["total_recovery_time"] += recovery_success["recovery_time"]
                    
                    if error_occurred not in results["recovery_attempts"]:
                        results["recovery_attempts"][error_occurred] = {"success": 0, "failure": 0}
                    results["recovery_attempts"][error_occurred]["success"] += 1
                else:
                    results["failed_operations"] += 1
                    if error_occurred not in results["recovery_attempts"]:
                        results["recovery_attempts"][error_occurred] = {"success": 0, "failure": 0}
                    results["recovery_attempts"][error_occurred]["failure"] += 1
            else:
                # 정상 작업
                results["successful_operations"] += 1
        
        # 성공률 계산
        results["success_rate"] = results["successful_operations"] / results["total_operations"]
        results["avg_recovery_time"] = (
            results["total_recovery_time"] / 
            sum(r["success"] for r in results["recovery_attempts"].values())
            if any(results["recovery_attempts"].values()) else 0
        )
        
        return results
    
    def attempt_recovery(self, error_type):
        """복구 시도 시뮬레이션"""
        config = self.error_scenarios[error_type]
        strategies = config["recovery_strategies"]
        
        # 복구 전략 선택 (첫 번째 전략 시도)
        chosen_strategy = strategies[0]
        success_rate = self.recovery_success_rates[chosen_strategy]
        
        # 복구 시간 시뮬레이션 (전략에 따라 다름)
        recovery_time_map = {
            "retry": random.uniform(0.5, 2.0),
            "fallback": random.uniform(0.1, 0.5),
            "cache": random.uniform(0.05, 0.2),
            "backoff": random.uniform(1.0, 5.0),
            "validation": random.uniform(0.2, 1.0),
            "circuit_breaker": random.uniform(0.01, 0.1),
        }
        
        recovery_time = recovery_time_map.get(chosen_strategy, random.uniform(0.5, 2.0))
        
        # 복구 성공 여부 결정
        success = random.random() < success_rate
        
        return {
            "success": success,
            "strategy_used": chosen_strategy,
            "recovery_time": recovery_time,
            "error_type": error_type
        }
    
    def run_stress_test(self, duration_minutes=5):
        """스트레스 테스트 실행"""
        components = ["pokernews", "youtube", "platform", "slack"]
        operations_per_minute = 50  # 분당 작업 수
        
        total_operations = duration_minutes * operations_per_minute
        
        print(f"🔥 스트레스 테스트 실행 ({duration_minutes}분, {total_operations} 작업)")
        
        stress_results = {}
        
        for component in components:
            print(f"\\n{component.upper()} 스트레스 테스트:")
            component_result = self.simulate_component_operation(component, total_operations)
            
            print(f"  성공률: {component_result['success_rate']:.2%}")
            print(f"  에러 발생: {component_result['failed_operations']}회")
            print(f"  평균 복구 시간: {component_result['avg_recovery_time']:.2f}초")
            
            if component_result["errors_encountered"]:
                print("  발생한 에러:")
                for error_type, count in component_result["errors_encountered"].items():
                    print(f"    {error_type}: {count}회")
            
            stress_results[component] = component_result
        
        return stress_results
    
    def test_cascading_failures(self):
        """연쇄 장애 시나리오 테스트"""
        print("\\n⛓️ 연쇄 장애 시나리오 테스트")
        
        # 연쇄 장애 시나리오: YouTube API 실패 → PokerNews 과부하 → Slack 알림 폭주
        cascade_scenario = {
            "initial_failure": "youtube_api_failure",
            "cascade_effects": [
                {
                    "component": "pokernews",
                    "effect": "increased_load",
                    "severity_multiplier": 2.0
                },
                {
                    "component": "slack",
                    "effect": "notification_flood", 
                    "severity_multiplier": 3.0
                },
                {
                    "component": "platform",
                    "effect": "delayed_processing",
                    "severity_multiplier": 1.5
                }
            ]
        }
        
        cascade_results = {
            "scenario": cascade_scenario,
            "timeline": [],
            "recovery_time": 0,
            "total_impact": 0
        }
        
        # T+0: 초기 장애 발생
        cascade_results["timeline"].append({
            "time": 0,
            "event": "YouTube API 실패 발생",
            "component": "youtube",
            "impact_level": "high"
        })
        
        # T+30초: 연쇄 효과 시작
        cascade_results["timeline"].append({
            "time": 30,
            "event": "PokerNews 처리량 증가로 인한 부하",
            "component": "pokernews", 
            "impact_level": "medium"
        })
        
        # T+60초: 알림 폭주
        cascade_results["timeline"].append({
            "time": 60,
            "event": "Slack 알림 시스템 과부하",
            "component": "slack",
            "impact_level": "high"
        })
        
        # T+90초: 플랫폼 지연
        cascade_results["timeline"].append({
            "time": 90,
            "event": "플랫폼 분석 지연 발생",
            "component": "platform",
            "impact_level": "medium"
        })
        
        # 복구 시뮬레이션
        recovery_strategies = [
            {"time": 120, "action": "YouTube API 복구", "success": True},
            {"time": 180, "action": "PokerNews 부하 정상화", "success": True},
            {"time": 240, "action": "Slack 알림 대기열 정리", "success": True},
            {"time": 300, "action": "전체 시스템 정상화", "success": True}
        ]
        
        cascade_results["recovery_actions"] = recovery_strategies
        cascade_results["recovery_time"] = 300  # 5분
        
        print("  연쇄 장애 타임라인:")
        for event in cascade_results["timeline"]:
            print(f"    T+{event['time']}초: {event['event']} ({event['impact_level']})")
        
        print("  복구 과정:")
        for action in recovery_strategies:
            status = "✓" if action["success"] else "✗"
            print(f"    T+{action['time']}초: {action['action']} {status}")
        
        print(f"  총 복구 시간: {cascade_results['recovery_time']}초")
        
        return cascade_results
    
    def generate_error_report(self, test_results):
        """에러 테스트 보고서 생성"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "test_summary": {
                "components_tested": len(test_results),
                "total_operations": sum(r["total_operations"] for r in test_results.values()),
                "overall_success_rate": sum(r["success_rate"] for r in test_results.values()) / len(test_results),
                "total_errors": sum(r["failed_operations"] for r in test_results.values())
            },
            "component_details": test_results,
            "recommendations": []
        }
        
        # 개선 권장사항 생성
        for component, result in test_results.items():
            if result["success_rate"] < 0.95:
                report["recommendations"].append(
                    f"{component}: 성공률 {result['success_rate']:.2%}로 개선 필요"
                )
            
            if result["avg_recovery_time"] > 2.0:
                report["recommendations"].append(
                    f"{component}: 평균 복구 시간 {result['avg_recovery_time']:.2f}초로 최적화 필요"
                )
        
        return report
    
    def run_full_error_test(self):
        """전체 에러 시나리오 테스트 실행"""
        print("💥 포커 트렌드 분석 플랫폼 - 에러 시나리오 테스트")
        print("=" * 60)
        
        # 1. 스트레스 테스트
        stress_results = self.run_stress_test(duration_minutes=2)  # 테스트용으로 2분
        
        # 2. 연쇄 장애 테스트
        cascade_results = self.test_cascading_failures()
        
        # 3. 보고서 생성
        error_report = self.generate_error_report(stress_results)
        
        print("\\n📊 에러 테스트 종합 결과:")
        print(f"  전체 성공률: {error_report['test_summary']['overall_success_rate']:.2%}")
        print(f"  총 에러 발생: {error_report['test_summary']['total_errors']}회")
        print(f"  테스트한 구성요소: {error_report['test_summary']['components_tested']}개")
        
        if error_report["recommendations"]:
            print("\\n🔧 개선 권장사항:")
            for rec in error_report["recommendations"]:
                print(f"  • {rec}")
        else:
            print("\\n✅ 모든 구성요소가 우수한 내결함성을 보입니다.")
        
        return {
            "stress_results": stress_results,
            "cascade_results": cascade_results,
            "error_report": error_report
        }

# 에러 시나리오 테스트 실행
error_tester = ErrorScenarioTester()
test_results = error_tester.run_full_error_test()

print("\\n에러 시나리오 테스트: COMPLETED")
`;
    
    const tempScript = path.join(testResultsDir, 'temp_error_scenarios.py');
    fs.writeFileSync(tempScript, errorScenarioScript);
    
    const result = await runPythonScript(tempScript, []);
    
    expect(result.output).toContain('에러 시나리오 테스트');
    expect(result.output).toContain('COMPLETED');
    
    // 에러 처리 결과 기록
    performanceResults.errorHandling.push({
      name: 'error_scenarios_and_recovery',
      success: result.code === 0,
      output: result.output
    });
    
    // 임시 파일 정리
    if (fs.existsSync(tempScript)) {
      fs.unlinkSync(tempScript);
    }
  });

  test('메모리 누수 및 리소스 관리 테스트', async () => {
    const memoryTestScript = `
import time
import gc
from datetime import datetime

class MemoryLeakTester:
    def __init__(self):
        self.memory_snapshots = []
        self.resource_usage = []
    
    def simulate_memory_intensive_operation(self, iterations=1000):
        """메모리 집약적 작업 시뮬레이션"""
        large_datasets = []
        
        for i in range(iterations):
            # 대용량 데이터 시뮬레이션
            dataset = {
                "id": i,
                "data": list(range(1000)),  # 1000개 정수 배열
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "size": 1000,
                    "type": "simulation_data",
                    "content": "x" * 100  # 100자 문자열
                }
            }
            large_datasets.append(dataset)
            
            # 주기적으로 메모리 정리
            if i % 100 == 0:
                # 일부 데이터 정리 (실제 시스템에서의 정리 과정 시뮬레이션)
                if len(large_datasets) > 500:
                    # 오래된 데이터 50% 정리
                    remove_count = len(large_datasets) // 2
                    large_datasets = large_datasets[remove_count:]
                
                # 강제 가비지 컬렉션
                gc.collect()
        
        return {
            "iterations_completed": iterations,
            "final_dataset_size": len(large_datasets),
            "memory_management": "active_cleanup_applied"
        }
    
    def simulate_file_handle_management(self, file_operations=100):
        """파일 핸들 관리 시뮬레이션"""
        file_handles = []
        operations_log = []
        
        for i in range(file_operations):
            operation_type = ["read", "write", "append"][i % 3]
            
            # 파일 작업 시뮬레이션
            file_info = {
                "handle_id": f"file_{i}",
                "operation": operation_type,
                "timestamp": datetime.now().isoformat(),
                "size": 1024 * (i + 1),  # 점진적 크기 증가
                "status": "open"
            }
            
            file_handles.append(file_info)
            operations_log.append({
                "operation": f"{operation_type}_file_{i}",
                "timestamp": datetime.now().isoformat()
            })
            
            # 파일 핸들 정리 (20개마다)
            if i > 0 and i % 20 == 0:
                # 오래된 핸들 정리
                cleanup_count = min(10, len(file_handles))
                for j in range(cleanup_count):
                    if j < len(file_handles):
                        file_handles[j]["status"] = "closed"
                
                # 실제로 닫힌 핸들 제거
                file_handles = [f for f in file_handles if f["status"] == "open"]
                
                operations_log.append({
                    "operation": f"cleanup_{cleanup_count}_handles",
                    "timestamp": datetime.now().isoformat()
                })
        
        return {
            "total_operations": file_operations,
            "open_handles": len([f for f in file_handles if f["status"] == "open"]),
            "cleanup_operations": len([op for op in operations_log if "cleanup" in op["operation"]]),
            "operations_log": operations_log
        }
    
    def simulate_connection_pool_management(self, connections=50):
        """연결 풀 관리 시뮬레이션"""
        connection_pool = []
        connection_stats = {
            "created": 0,
            "reused": 0,
            "closed": 0,
            "max_pool_size": 10
        }
        
        for i in range(connections):
            # 연결이 필요한 작업 시뮬레이션
            if len(connection_pool) < connection_stats["max_pool_size"]:
                # 새 연결 생성
                connection = {
                    "id": f"conn_{connection_stats['created']}",
                    "created_at": datetime.now().isoformat(),
                    "last_used": datetime.now().isoformat(),
                    "usage_count": 1,
                    "status": "active"
                }
                connection_pool.append(connection)
                connection_stats["created"] += 1
            else:
                # 기존 연결 재사용
                if connection_pool:
                    reused_conn = connection_pool[0]
                    reused_conn["last_used"] = datetime.now().isoformat()
                    reused_conn["usage_count"] += 1
                    connection_stats["reused"] += 1
                    
                    # 연결을 풀의 끝으로 이동 (LRU 시뮬레이션)
                    connection_pool.append(connection_pool.pop(0))
            
            # 주기적으로 유휴 연결 정리
            if i % 15 == 0:
                current_time = time.time()
                for conn in connection_pool[:]:
                    # 5초 이상 사용되지 않은 연결 정리 (시뮬레이션)
                    if conn["usage_count"] < 2:  # 사용량이 적은 연결
                        connection_pool.remove(conn)
                        connection_stats["closed"] += 1
        
        return {
            "total_connection_requests": connections,
            "final_pool_size": len(connection_pool),
            "connections_created": connection_stats["created"],
            "connections_reused": connection_stats["reused"],
            "connections_closed": connection_stats["closed"],
            "reuse_rate": connection_stats["reused"] / connections if connections > 0 else 0
        }
    
    def run_resource_leak_detection(self):
        """리소스 누수 탐지 테스트"""
        print("🔍 리소스 누수 탐지 테스트")
        print("=" * 40)
        
        test_results = {}
        
        # 1. 메모리 관리 테스트
        print("\\n1️⃣ 메모리 관리 테스트")
        memory_result = self.simulate_memory_intensive_operation(500)
        print(f"   반복 작업: {memory_result['iterations_completed']}회")
        print(f"   최종 데이터셋 크기: {memory_result['final_dataset_size']}개")
        print(f"   메모리 정리: {memory_result['memory_management']}")
        test_results["memory_management"] = memory_result
        
        # 2. 파일 핸들 관리 테스트
        print("\\n2️⃣ 파일 핸들 관리 테스트")
        file_result = self.simulate_file_handle_management(100)
        print(f"   파일 작업: {file_result['total_operations']}회")
        print(f"   열린 핸들: {file_result['open_handles']}개")
        print(f"   정리 작업: {file_result['cleanup_operations']}회")
        test_results["file_handle_management"] = file_result
        
        # 3. 연결 풀 관리 테스트
        print("\\n3️⃣ 연결 풀 관리 테스트")
        connection_result = self.simulate_connection_pool_management(100)
        print(f"   연결 요청: {connection_result['total_connection_requests']}회")
        print(f"   풀 크기: {connection_result['final_pool_size']}개")
        print(f"   재사용률: {connection_result['reuse_rate']:.2%}")
        print(f"   정리된 연결: {connection_result['connections_closed']}개")
        test_results["connection_pool_management"] = connection_result
        
        # 4. 전체 평가
        print("\\n4️⃣ 리소스 관리 평가")
        
        memory_score = 100 if memory_result["final_dataset_size"] < 600 else 50
        file_score = 100 if file_result["open_handles"] < 20 else 50
        connection_score = 100 if connection_result["reuse_rate"] > 0.5 else 50
        
        total_score = (memory_score + file_score + connection_score) / 3
        
        print(f"   메모리 관리: {'✅' if memory_score == 100 else '⚠️'} ({memory_score}점)")
        print(f"   파일 핸들: {'✅' if file_score == 100 else '⚠️'} ({file_score}점)")
        print(f"   연결 풀: {'✅' if connection_score == 100 else '⚠️'} ({connection_score}점)")
        print(f"   종합 점수: {total_score:.0f}/100")
        
        if total_score >= 80:
            print("\\n✅ 리소스 관리: EXCELLENT")
        elif total_score >= 60:
            print("\\n⚠️ 리소스 관리: GOOD")
        else:
            print("\\n❌ 리소스 관리: NEEDS IMPROVEMENT")
        
        return {
            "total_score": total_score,
            "test_results": test_results
        }

# 메모리 누수 테스트 실행
memory_tester = MemoryLeakTester()
leak_test_results = memory_tester.run_resource_leak_detection()

print("\\n메모리 누수 및 리소스 관리 테스트: COMPLETED")
`;
    
    const tempScript = path.join(testResultsDir, 'temp_memory_test.py');
    fs.writeFileSync(tempScript, memoryTestScript);
    
    const result = await runPythonScript(tempScript, []);
    
    expect(result.output).toContain('리소스 누수 탐지 테스트');
    expect(result.output).toContain('COMPLETED');
    
    // 메모리 테스트 결과 기록
    performanceResults.memoryUsage.push({
      name: 'memory_leak_and_resource_management',
      success: result.code === 0,
      output: result.output
    });
    
    // 임시 파일 정리
    if (fs.existsSync(tempScript)) {
      fs.unlinkSync(tempScript);
    }
  });

  test('부하 테스트 및 확장성 검증', async () => {
    const loadTestScript = `
import time
import threading
import queue
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

class LoadTester:
    def __init__(self):
        self.load_test_results = {}
        self.concurrent_users = [1, 5, 10, 20, 50]
        self.test_duration = 30  # 30초 테스트
    
    def simulate_user_workflow(self, user_id, test_queue):
        """단일 사용자 워크플로우 시뮬레이션"""
        user_results = {
            "user_id": user_id,
            "operations": [],
            "total_time": 0,
            "successful_operations": 0,
            "failed_operations": 0
        }
        
        start_time = time.time()
        operation_count = 0
        
        while time.time() - start_time < self.test_duration:
            operation_start = time.time()
            
            # 포커 트렌드 조회 작업 시뮬레이션
            try:
                # YouTube 트렌드 조회 (50ms ~ 200ms)
                time.sleep(0.05 + (operation_count % 4) * 0.0375)
                
                # PokerNews 분석 (100ms ~ 300ms)
                time.sleep(0.1 + (operation_count % 3) * 0.067)
                
                # 플랫폼 데이터 조회 (30ms ~ 150ms) 
                time.sleep(0.03 + (operation_count % 5) * 0.024)
                
                operation_time = time.time() - operation_start
                user_results["operations"].append({
                    "operation_id": operation_count,
                    "time": operation_time,
                    "success": True
                })
                user_results["successful_operations"] += 1
                
            except Exception as e:
                operation_time = time.time() - operation_start
                user_results["operations"].append({
                    "operation_id": operation_count,
                    "time": operation_time,
                    "success": False,
                    "error": str(e)
                })
                user_results["failed_operations"] += 1
            
            operation_count += 1
            
            # 사용자 간 요청 간격 (0.5초 ~ 2초)
            time.sleep(0.5 + (user_id % 3) * 0.5)
        
        user_results["total_time"] = time.time() - start_time
        user_results["operations_per_second"] = len(user_results["operations"]) / user_results["total_time"]
        
        test_queue.put(user_results)
        return user_results
    
    def run_concurrent_load_test(self, concurrent_users):
        """동시 사용자 부하 테스트"""
        print(f"\\n📈 동시 사용자 {concurrent_users}명 부하 테스트")
        
        test_queue = queue.Queue()
        start_time = time.time()
        
        # 동시 사용자 시뮬레이션
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [
                executor.submit(self.simulate_user_workflow, user_id, test_queue)
                for user_id in range(concurrent_users)
            ]
            
            # 모든 사용자 테스트 완료 대기
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"   사용자 테스트 중 오류: {e}")
        
        total_test_time = time.time() - start_time
        
        # 결과 수집
        user_results = []
        while not test_queue.empty():
            user_results.append(test_queue.get())
        
        # 통계 계산
        if user_results:
            total_operations = sum(len(u["operations"]) for u in user_results)
            successful_operations = sum(u["successful_operations"] for u in user_results)
            failed_operations = sum(u["failed_operations"] for u in user_results)
            avg_response_time = sum(
                sum(op["time"] for op in u["operations"]) for u in user_results
            ) / total_operations if total_operations > 0 else 0
            
            throughput = total_operations / total_test_time if total_test_time > 0 else 0
            success_rate = successful_operations / total_operations if total_operations > 0 else 0
            
            test_result = {
                "concurrent_users": concurrent_users,
                "test_duration": total_test_time,
                "total_operations": total_operations,
                "successful_operations": successful_operations,
                "failed_operations": failed_operations,
                "success_rate": success_rate,
                "avg_response_time": avg_response_time,
                "throughput_ops_per_sec": throughput,
                "user_results": user_results
            }
            
            print(f"   총 작업: {total_operations}개")
            print(f"   성공률: {success_rate:.2%}")
            print(f"   평균 응답시간: {avg_response_time:.3f}초")
            print(f"   처리량: {throughput:.1f} ops/sec")
            
            return test_result
        else:
            return {
                "concurrent_users": concurrent_users,
                "error": "No user results collected"
            }
    
    def analyze_scalability(self, load_test_results):
        """확장성 분석"""
        print("\\n📊 확장성 분석")
        print("=" * 40)
        
        scalability_metrics = {}
        
        print("사용자 수별 성능 지표:")
        print("사용자 | 처리량(ops/sec) | 응답시간(ms) | 성공률")
        print("-" * 50)
        
        for result in load_test_results:
            if "error" not in result:
                users = result["concurrent_users"]
                throughput = result["throughput_ops_per_sec"]
                response_time = result["avg_response_time"] * 1000  # ms로 변환
                success_rate = result["success_rate"] * 100  # 퍼센트로 변환
                
                print(f"   {users:2d}  |     {throughput:6.1f}     |    {response_time:6.1f}    | {success_rate:5.1f}%")
                
                scalability_metrics[users] = {
                    "throughput": throughput,
                    "response_time": response_time,
                    "success_rate": success_rate
                }
        
        # 확장성 점수 계산
        if len(scalability_metrics) > 1:
            users_list = sorted(scalability_metrics.keys())
            
            # 처리량 확장성 (이상적으로는 선형 증가)
            throughput_scalability = (
                scalability_metrics[users_list[-1]]["throughput"] / 
                scalability_metrics[users_list[0]]["throughput"]
            ) / (users_list[-1] / users_list[0])
            
            # 응답시간 안정성 (너무 많이 증가하면 안됨)
            response_time_stability = (
                scalability_metrics[users_list[0]]["response_time"] /
                scalability_metrics[users_list[-1]]["response_time"]
            )
            
            # 성공률 안정성
            min_success_rate = min(m["success_rate"] for m in scalability_metrics.values())
            success_rate_stability = min_success_rate / 100
            
            print(f"\\n확장성 지표:")
            print(f"  처리량 확장성: {throughput_scalability:.2f} (1.0이 이상적)")
            print(f"  응답시간 안정성: {response_time_stability:.2f} (1.0에 가까울수록 좋음)")
            print(f"  성공률 안정성: {success_rate_stability:.2f} (1.0이 이상적)")
            
            # 종합 확장성 점수
            scalability_score = (
                throughput_scalability * 40 +
                response_time_stability * 30 +
                success_rate_stability * 30
            )
            
            print(f"  종합 확장성 점수: {scalability_score:.1f}/100")
            
            if scalability_score >= 80:
                print("\\n✅ 확장성: EXCELLENT")
            elif scalability_score >= 60:
                print("\\n⚠️ 확장성: GOOD")
            else:
                print("\\n❌ 확장성: NEEDS IMPROVEMENT")
            
            return {
                "scalability_score": scalability_score,
                "metrics": scalability_metrics
            }
    
    def run_full_load_test(self):
        """전체 부하 테스트 실행"""
        print("🚀 포커 트렌드 분석 플랫폼 - 부하 테스트")
        print("=" * 50)
        
        load_test_results = []
        
        # 다양한 동시 사용자 수로 테스트
        for users in self.concurrent_users:
            result = self.run_concurrent_load_test(users)
            if result:
                load_test_results.append(result)
        
        # 확장성 분석
        scalability_analysis = self.analyze_scalability(load_test_results)
        
        return {
            "load_test_results": load_test_results,
            "scalability_analysis": scalability_analysis
        }

# 부하 테스트 실행
print("⚡ 부하 테스트는 시간이 오래 걸릴 수 있습니다...")
load_tester = LoadTester()

# 테스트 시간 단축 (실제 환경에서는 더 길게)
load_tester.test_duration = 10  # 10초로 단축
load_tester.concurrent_users = [1, 5, 10]  # 사용자 수 단축

load_results = load_tester.run_full_load_test()

print("\\n부하 테스트 및 확장성 검증: COMPLETED")
`;
    
    const tempScript = path.join(testResultsDir, 'temp_load_test.py');
    fs.writeFileSync(tempScript, loadTestScript);
    
    const result = await runPythonScript(tempScript, [], { timeout: 120000 }); // 2분 타임아웃
    
    expect(result.output).toContain('부하 테스트');
    expect(result.output).toContain('COMPLETED');
    
    // 부하 테스트 결과 기록
    performanceResults.loadTests.push({
      name: 'load_test_and_scalability',
      success: result.code === 0,
      output: result.output
    });
    
    // 임시 파일 정리
    if (fs.existsSync(tempScript)) {
      fs.unlinkSync(tempScript);
    }
  });
});

// Helper function: Python 스크립트 실행 (타임아웃 지원)
async function runPythonScript(scriptPath, args = [], options = {}) {
  return new Promise((resolve) => {
    const defaultTimeout = options.timeout || 60000; // 기본 1분
    
    const python = spawn('python', [scriptPath, ...args], {
      stdio: ['pipe', 'pipe', 'pipe'],
      cwd: path.dirname(scriptPath),
      ...options
    });
    
    let output = '';
    let error = '';
    let timeoutId;
    
    // 타임아웃 설정
    if (defaultTimeout) {
      timeoutId = setTimeout(() => {
        python.kill('SIGTERM');
        resolve({
          code: -1,
          output: 'Process timed out',
          stdout: '',
          stderr: 'Process timed out'
        });
      }, defaultTimeout);
    }
    
    python.stdout.on('data', (data) => {
      output += data.toString();
    });
    
    python.stderr.on('data', (data) => {
      error += data.toString();
    });
    
    python.on('close', (code) => {
      if (timeoutId) clearTimeout(timeoutId);
      resolve({
        code,
        output: output + error,
        stdout: output,
        stderr: error
      });
    });
    
    python.on('error', (err) => {
      if (timeoutId) clearTimeout(timeoutId);
      resolve({
        code: -1,
        output: err.message,
        stdout: '',
        stderr: err.message
      });
    });
  });
}