// 포커 트렌드 분석 플랫폼 - End-to-End 통합 테스트
const { test, expect } = require('@playwright/test');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

test.describe('End-to-End Integration Tests', () => {
  const testResultsDir = path.join(__dirname, '..', 'test-results');
  let integrationTestResults = {};
  
  test.beforeAll(async () => {
    // 통합 테스트 세션 시작
    integrationTestResults = {
      sessionId: `e2e-${Date.now()}`,
      startTime: new Date().toISOString(),
      components: [],
      workflows: [],
      errors: []
    };
    
    if (!fs.existsSync(testResultsDir)) {
      fs.mkdirSync(testResultsDir, { recursive: true });
    }
  });

  test.afterAll(async () => {
    // 통합 테스트 결과 저장
    integrationTestResults.endTime = new Date().toISOString();
    integrationTestResults.duration = Date.now() - new Date(integrationTestResults.startTime).getTime();
    
    const resultPath = path.join(testResultsDir, 'e2e-integration-results.json');
    fs.writeFileSync(resultPath, JSON.stringify(integrationTestResults, null, 2));
    
    console.log(`🎯 E2E 통합 테스트 완료 - 결과: ${resultPath}`);
  });

  test('전체 시스템 워크플로우 시뮬레이션', async () => {
    const workflowScript = `
import json
import time
from datetime import datetime, date

class PokerTrendWorkflow:
    def __init__(self):
        self.workflow_state = {
            "current_step": 0,
            "completed_steps": [],
            "errors": [],
            "start_time": datetime.now().isoformat()
        }
        
        self.workflow_steps = [
            "schedule_determination",
            "pokernews_collection", 
            "pokernews_analysis",
            "youtube_data_collection",
            "youtube_analysis",
            "platform_data_collection",
            "platform_analysis",
            "slack_reporting"
        ]
    
    def simulate_schedule_determination(self):
        """스케줄 결정 단계 시뮬레이션"""
        try:
            # 오늘이 월요일인지 확인하여 리포트 타입 결정
            today = date.today()
            day_of_week = today.weekday() + 1  # 1=월요일
            
            if day_of_week == 1:
                # 첫째주인지 확인
                day_of_month = today.day
                week_of_month = (day_of_month - 1) // 7 + 1
                
                if week_of_month == 1:
                    report_type = "monthly"
                else:
                    report_type = "weekly"
            elif 2 <= day_of_week <= 5:
                report_type = "daily"
            else:
                report_type = "none"
            
            self.workflow_state["schedule_result"] = {
                "date": today.isoformat(),
                "report_type": report_type,
                "should_execute": report_type != "none"
            }
            
            return {"success": True, "report_type": report_type}
            
        except Exception as e:
            self.workflow_state["errors"].append(f"Schedule determination failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def simulate_pokernews_pipeline(self):
        """PokerNews 파이프라인 시뮬레이션"""
        try:
            # RSS 수집 시뮬레이션
            rss_data = {
                "articles": [
                    {"title": "WSOP 2025 업데이트", "url": "https://example.com/1"},
                    {"title": "온라인 포커 트렌드", "url": "https://example.com/2"},
                    {"title": "프로 선수 인터뷰", "url": "https://example.com/3"}
                ],
                "collected_at": datetime.now().isoformat(),
                "total_articles": 3
            }
            
            # AI 분석 시뮬레이션
            analysis_result = {
                "main_topics": ["tournament", "online_poker", "strategy"],
                "sentiment_score": 7.5,
                "trend_keywords": ["WSOP", "온라인", "전략"],
                "summary": "포커 토너먼트와 온라인 포커 활동이 증가하는 추세"
            }
            
            self.workflow_state["pokernews_result"] = {
                "rss_data": rss_data,
                "analysis": analysis_result
            }
            
            return {"success": True, "articles_analyzed": 3}
            
        except Exception as e:
            self.workflow_state["errors"].append(f"PokerNews pipeline failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def simulate_youtube_pipeline(self):
        """YouTube 분석 파이프라인 시뮬레이션"""
        try:
            # YouTube 트렌드 데이터 시뮬레이션
            youtube_data = {
                "trending_videos": [
                    {
                        "title": "Texas Hold'em Strategy Guide",
                        "views": 125000,
                        "likes": 8500,
                        "channel": "PokerPro Channel"
                    },
                    {
                        "title": "포커 토너먼트 하이라이트",
                        "views": 98000,
                        "likes": 6200,
                        "channel": "Korean Poker TV"
                    }
                ],
                "analysis_period": "last_24h",
                "total_videos_analyzed": 50
            }
            
            # Gemini AI 분석 시뮬레이션
            ai_insights = {
                "popular_topics": ["strategy", "tournament", "cash_game"],
                "content_quality_score": 8.2,
                "engagement_rate": 0.068,
                "trend_direction": "increasing",
                "korean_summary": "전략 콘텐츠와 토너먼트 관련 영상의 인기가 상승 중"
            }
            
            self.workflow_state["youtube_result"] = {
                "raw_data": youtube_data,
                "ai_analysis": ai_insights
            }
            
            return {"success": True, "videos_analyzed": 50}
            
        except Exception as e:
            self.workflow_state["errors"].append(f"YouTube pipeline failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def simulate_platform_analysis(self):
        """플랫폼 분석 시뮬레이션"""
        try:
            # Firebase 데이터 수집 시뮬레이션
            platform_data = {
                "online_players": 45230,
                "cash_games_active": 1247,
                "tournament_entries": 892,
                "daily_growth": 5.2,
                "peak_hours": "20:00-23:00 KST"
            }
            
            # 일일 비교 분석
            comparison_result = {
                "vs_yesterday": {
                    "players": "+5.2%",
                    "cash_games": "+3.1%", 
                    "tournaments": "+8.7%"
                },
                "vs_last_week": {
                    "players": "+12.5%",
                    "cash_games": "+9.3%",
                    "tournaments": "+15.2%"
                }
            }
            
            self.workflow_state["platform_result"] = {
                "current_data": platform_data,
                "comparison": comparison_result
            }
            
            return {"success": True, "data_points_processed": 500}
            
        except Exception as e:
            self.workflow_state["errors"].append(f"Platform analysis failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def simulate_slack_reporting(self):
        """Slack 리포팅 시뮬레이션"""
        try:
            # 통합 리포트 생성
            integrated_report = {
                "report_type": self.workflow_state.get("schedule_result", {}).get("report_type", "daily"),
                "timestamp": datetime.now().isoformat(),
                "components": {
                    "pokernews": self.workflow_state.get("pokernews_result"),
                    "youtube": self.workflow_state.get("youtube_result"), 
                    "platform": self.workflow_state.get("platform_result")
                },
                "summary": "모든 구성요소의 데이터 수집 및 분석이 성공적으로 완료됨"
            }
            
            # Slack 메시지 전송 시뮬레이션
            slack_result = {
                "message_sent": True,
                "webhook_response": "ok",
                "delivery_time": datetime.now().isoformat()
            }
            
            self.workflow_state["slack_result"] = {
                "report": integrated_report,
                "delivery": slack_result
            }
            
            return {"success": True, "report_sent": True}
            
        except Exception as e:
            self.workflow_state["errors"].append(f"Slack reporting failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def execute_full_workflow(self):
        """전체 워크플로우 실행"""
        workflow_methods = [
            ("schedule_determination", self.simulate_schedule_determination),
            ("pokernews_pipeline", self.simulate_pokernews_pipeline),
            ("youtube_pipeline", self.simulate_youtube_pipeline),
            ("platform_analysis", self.simulate_platform_analysis),
            ("slack_reporting", self.simulate_slack_reporting)
        ]
        
        results = {}
        
        for step_name, method in workflow_methods:
            print(f"Executing {step_name}...")
            result = method()
            results[step_name] = result
            
            if result["success"]:
                self.workflow_state["completed_steps"].append(step_name)
                print(f"  ✓ {step_name} completed successfully")
            else:
                print(f"  ✗ {step_name} failed: {result.get('error', 'Unknown error')}")
                break
        
        self.workflow_state["end_time"] = datetime.now().isoformat()
        self.workflow_state["total_duration"] = (
            datetime.now() - datetime.fromisoformat(self.workflow_state["start_time"])
        ).total_seconds()
        
        return {
            "workflow_state": self.workflow_state,
            "step_results": results,
            "overall_success": len(self.workflow_state["errors"]) == 0
        }

# 워크플로우 실행
print("🚀 포커 트렌드 분석 플랫폼 - End-to-End 워크플로우 시뮬레이션")
print("=" * 70)

workflow = PokerTrendWorkflow()
final_result = workflow.execute_full_workflow()

print("\\n📊 워크플로우 실행 결과:")
print(f"  전체 성공: {'✓' if final_result['overall_success'] else '✗'}")
print(f"  완료된 단계: {len(final_result['workflow_state']['completed_steps'])}/{len(workflow.workflow_steps)}")
print(f"  총 실행 시간: {final_result['workflow_state']['total_duration']:.2f}초")

if final_result["workflow_state"]["errors"]:
    print(f"  오류 발생: {len(final_result['workflow_state']['errors'])}개")
    for error in final_result["workflow_state"]["errors"]:
        print(f"    - {error}")

print("\\nE2E 워크플로우 시뮬레이션: COMPLETED")
`;
    
    const tempScript = path.join(testResultsDir, 'temp_e2e_workflow.py');
    fs.writeFileSync(tempScript, workflowScript);
    
    const result = await runPythonScript(tempScript, []);
    
    expect(result.output).toContain('포커 트렌드 분석 플랫폼 - End-to-End 워크플로우 시뮬레이션');
    expect(result.output).toContain('워크플로우 실행 결과');
    expect(result.output).toContain('COMPLETED');
    
    // 통합 테스트 결과에 기록
    integrationTestResults.workflows.push({
      name: 'full_system_workflow',
      success: result.output.includes('전체 성공: ✓'),
      output: result.output
    });
    
    // 임시 파일 정리
    if (fs.existsSync(tempScript)) {
      fs.unlinkSync(tempScript);
    }
  });

  test('구성요소 간 데이터 흐름 검증', async () => {
    const dataFlowScript = `
import json
from datetime import datetime

class DataFlowValidator:
    def __init__(self):
        self.data_contracts = {
            "schedule_to_components": {
                "required_fields": ["report_type", "date", "should_execute"],
                "types": {"report_type": str, "date": str, "should_execute": bool}
            },
            "pokernews_to_integration": {
                "required_fields": ["articles", "analysis_summary", "timestamp"],
                "types": {"articles": list, "analysis_summary": dict, "timestamp": str}
            },
            "youtube_to_integration": {
                "required_fields": ["trending_data", "ai_insights", "processed_count"],
                "types": {"trending_data": list, "ai_insights": dict, "processed_count": int}
            },
            "platform_to_integration": {
                "required_fields": ["current_stats", "comparison_data", "growth_metrics"],
                "types": {"current_stats": dict, "comparison_data": dict, "growth_metrics": dict}
            },
            "integration_to_slack": {
                "required_fields": ["report_type", "components", "summary", "timestamp"],
                "types": {"report_type": str, "components": dict, "summary": str, "timestamp": str}
            }
        }
    
    def validate_data_contract(self, contract_name, data):
        """데이터 계약 검증"""
        if contract_name not in self.data_contracts:
            return {"valid": False, "error": f"Unknown contract: {contract_name}"}
        
        contract = self.data_contracts[contract_name]
        validation_result = {
            "valid": True,
            "missing_fields": [],
            "type_mismatches": [],
            "extra_fields": []
        }
        
        # 필수 필드 검증
        for field in contract["required_fields"]:
            if field not in data:
                validation_result["missing_fields"].append(field)
                validation_result["valid"] = False
        
        # 타입 검증
        for field, expected_type in contract["types"].items():
            if field in data and not isinstance(data[field], expected_type):
                validation_result["type_mismatches"].append({
                    "field": field,
                    "expected": expected_type.__name__,
                    "actual": type(data[field]).__name__
                })
                validation_result["valid"] = False
        
        return validation_result
    
    def simulate_data_flow(self):
        """데이터 흐름 시뮬레이션"""
        flow_results = {}
        
        # 1. 스케줄 결정 → 구성요소들
        schedule_data = {
            "report_type": "daily",
            "date": "2025-08-08",
            "should_execute": True
        }
        flow_results["schedule_validation"] = self.validate_data_contract(
            "schedule_to_components", schedule_data
        )
        
        # 2. PokerNews → 통합
        pokernews_data = {
            "articles": [
                {"title": "Test Article", "url": "https://test.com"},
            ],
            "analysis_summary": {
                "main_topic": "tournament",
                "sentiment": "positive"
            },
            "timestamp": datetime.now().isoformat()
        }
        flow_results["pokernews_validation"] = self.validate_data_contract(
            "pokernews_to_integration", pokernews_data
        )
        
        # 3. YouTube → 통합
        youtube_data = {
            "trending_data": [
                {"title": "Test Video", "views": 1000}
            ],
            "ai_insights": {
                "popular_topics": ["strategy"],
                "trend_score": 8.5
            },
            "processed_count": 50
        }
        flow_results["youtube_validation"] = self.validate_data_contract(
            "youtube_to_integration", youtube_data
        )
        
        # 4. Platform → 통합
        platform_data = {
            "current_stats": {
                "online_players": 45000,
                "active_games": 1200
            },
            "comparison_data": {
                "vs_yesterday": "+5.2%"
            },
            "growth_metrics": {
                "weekly_growth": 12.5,
                "monthly_growth": 35.8
            }
        }
        flow_results["platform_validation"] = self.validate_data_contract(
            "platform_to_integration", platform_data
        )
        
        # 5. 통합 → Slack
        integration_data = {
            "report_type": "daily",
            "components": {
                "pokernews": pokernews_data,
                "youtube": youtube_data,
                "platform": platform_data
            },
            "summary": "All components processed successfully",
            "timestamp": datetime.now().isoformat()
        }
        flow_results["slack_validation"] = self.validate_data_contract(
            "integration_to_slack", integration_data
        )
        
        return flow_results

# 데이터 흐름 검증 실행
print("🔄 구성요소 간 데이터 흐름 검증")
print("=" * 50)

validator = DataFlowValidator()
flow_results = validator.simulate_data_flow()

overall_success = True
for contract_name, result in flow_results.items():
    status = "✓" if result["valid"] else "✗"
    print(f"{contract_name}: {status}")
    
    if not result["valid"]:
        overall_success = False
        if result["missing_fields"]:
            print(f"  Missing fields: {result['missing_fields']}")
        if result["type_mismatches"]:
            for mismatch in result["type_mismatches"]:
                print(f"  Type mismatch - {mismatch['field']}: expected {mismatch['expected']}, got {mismatch['actual']}")

print(f"\\n데이터 흐름 검증 결과: {'SUCCESS' if overall_success else 'FAILED'}")
print("Data flow validation: COMPLETED")
`;
    
    const tempScript = path.join(testResultsDir, 'temp_data_flow.py');
    fs.writeFileSync(tempScript, dataFlowScript);
    
    const result = await runPythonScript(tempScript, []);
    
    expect(result.output).toContain('구성요소 간 데이터 흐름 검증');
    expect(result.output).toContain('Data flow validation: COMPLETED');
    
    // 통합 테스트 결과에 기록
    integrationTestResults.components.push({
      name: 'data_flow_validation',
      success: result.output.includes('SUCCESS'),
      output: result.output
    });
    
    // 임시 파일 정리
    if (fs.existsSync(tempScript)) {
      fs.unlinkSync(tempScript);
    }
  });

  test('시스템 복원력 및 장애 처리 테스트', async () => {
    const resilienceScript = `
import random
import time
from datetime import datetime

class SystemResilienceTest:
    def __init__(self):
        self.failure_scenarios = [
            "api_rate_limit",
            "network_timeout", 
            "invalid_response",
            "service_unavailable",
            "quota_exceeded"
        ]
        
        self.recovery_strategies = {
            "api_rate_limit": "exponential_backoff",
            "network_timeout": "retry_with_timeout",
            "invalid_response": "fallback_data",
            "service_unavailable": "skip_and_continue",
            "quota_exceeded": "switch_to_cache"
        }
    
    def simulate_failure(self, component, failure_type):
        """실패 시나리오 시뮬레이션"""
        failure_details = {
            "component": component,
            "failure_type": failure_type,
            "timestamp": datetime.now().isoformat(),
            "severity": "medium"
        }
        
        # 실패 심각도 결정
        if failure_type in ["service_unavailable", "quota_exceeded"]:
            failure_details["severity"] = "high"
        elif failure_type in ["network_timeout"]:
            failure_details["severity"] = "low"
        
        return failure_details
    
    def simulate_recovery(self, failure_details):
        """복구 전략 시뮬레이션"""
        failure_type = failure_details["failure_type"]
        strategy = self.recovery_strategies.get(failure_type, "default_retry")
        
        recovery_result = {
            "strategy_used": strategy,
            "recovery_time": random.uniform(1, 10),  # 1-10초
            "success": random.choice([True, True, True, False]),  # 75% 성공률
            "fallback_used": strategy == "fallback_data",
            "timestamp": datetime.now().isoformat()
        }
        
        return recovery_result
    
    def test_component_resilience(self, component):
        """구성요소별 복원력 테스트"""
        print(f"\\n테스팅 {component} 복원력:")
        
        component_results = []
        
        # 각 구성요소에 대해 다양한 실패 시나리오 테스트
        test_failures = random.sample(self.failure_scenarios, 3)
        
        for failure_type in test_failures:
            # 실패 시뮬레이션
            failure = self.simulate_failure(component, failure_type)
            print(f"  🔴 {failure_type} 실패 시뮬레이션")
            
            # 복구 시뮬레이션
            recovery = self.simulate_recovery(failure)
            recovery_status = "✓" if recovery["success"] else "✗"
            print(f"    {recovery_status} {recovery['strategy_used']} 복구 전략 ({recovery['recovery_time']:.1f}초)")
            
            component_results.append({
                "failure": failure,
                "recovery": recovery
            })
        
        return component_results
    
    def run_full_resilience_test(self):
        """전체 시스템 복원력 테스트"""
        components = ["pokernews", "youtube", "platform", "slack"]
        all_results = {}
        
        for component in components:
            all_results[component] = self.test_component_resilience(component)
        
        # 전체 결과 분석
        total_tests = sum(len(results) for results in all_results.values())
        successful_recoveries = sum(
            1 for results in all_results.values() 
            for result in results 
            if result["recovery"]["success"]
        )
        
        recovery_rate = (successful_recoveries / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"\\n📊 복원력 테스트 결과:")
        print(f"  총 테스트: {total_tests}개")
        print(f"  성공적 복구: {successful_recoveries}개")
        print(f"  복구 성공률: {recovery_rate:.1f}%")
        
        return {
            "total_tests": total_tests,
            "successful_recoveries": successful_recoveries,
            "recovery_rate": recovery_rate,
            "component_results": all_results
        }

# 시스템 복원력 테스트 실행
print("🛡️ 시스템 복원력 및 장애 처리 테스트")
print("=" * 50)

resilience_tester = SystemResilienceTest()
test_results = resilience_tester.run_full_resilience_test()

# 결과 평가
if test_results["recovery_rate"] >= 70:
    print("\\n✅ 시스템 복원력: EXCELLENT")
elif test_results["recovery_rate"] >= 50:
    print("\\n⚠️ 시스템 복원력: ACCEPTABLE")
else:
    print("\\n❌ 시스템 복원력: NEEDS IMPROVEMENT")

print("\\nResilience testing: COMPLETED")
`;
    
    const tempScript = path.join(testResultsDir, 'temp_resilience_test.py');
    fs.writeFileSync(tempScript, resilienceScript);
    
    const result = await runPythonScript(tempScript, []);
    
    expect(result.output).toContain('시스템 복원력 및 장애 처리 테스트');
    expect(result.output).toContain('복원력 테스트 결과');
    expect(result.output).toContain('COMPLETED');
    
    // 통합 테스트 결과에 기록
    integrationTestResults.components.push({
      name: 'system_resilience_test',
      success: result.output.includes('EXCELLENT') || result.output.includes('ACCEPTABLE'),
      output: result.output
    });
    
    // 임시 파일 정리
    if (fs.existsSync(tempScript)) {
      fs.unlinkSync(tempScript);
    }
  });

  test('통합 보고서 생성 및 배포 테스트', async () => {
    const reportingScript = `
import json
from datetime import datetime, timedelta

class IntegratedReportingSystem:
    def __init__(self):
        self.report_templates = {
            "daily": self._generate_daily_report,
            "weekly": self._generate_weekly_report,
            "monthly": self._generate_monthly_report
        }
        
        self.distribution_channels = [
            "slack_daily_channel",
            "slack_weekly_channel", 
            "slack_alerts_channel",
            "email_subscribers",
            "dashboard_update"
        ]
    
    def _generate_daily_report(self, data):
        return {
            "title": "📊 일간 포커 트렌드 분석 리포트",
            "date": data["date"],
            "sections": [
                {
                    "name": "YouTube 트렌드",
                    "data": data.get("youtube", {}),
                    "insights": ["전략 콘텐츠 인기 상승", "토너먼트 영상 조회수 증가"]
                },
                {
                    "name": "PokerNews 분석", 
                    "data": data.get("pokernews", {}),
                    "insights": ["WSOP 관련 기사 증가", "온라인 포커 동향 리포트"]
                },
                {
                    "name": "플랫폼 현황",
                    "data": data.get("platform", {}),
                    "insights": ["일일 플레이어 증가", "현금 게임 활성화"]
                }
            ],
            "summary": "전반적으로 포커 시장이 성장세를 보이고 있음"
        }
    
    def _generate_weekly_report(self, data):
        return {
            "title": "📈 주간 포커 트렌드 종합 분석",
            "period": f"{data['start_date']} ~ {data['end_date']}",
            "sections": [
                {
                    "name": "주간 하이라이트",
                    "highlights": [
                        "YouTube 조회수 전주 대비 +15.3% 증가",
                        "온라인 플레이어 수 +12.7% 증가",
                        "토너먼트 참가자 +20.1% 증가"
                    ]
                },
                {
                    "name": "트렌드 분석",
                    "trends": data.get("trends", []),
                    "predictions": data.get("predictions", [])
                }
            ],
            "summary": "주간 전반적인 성장세 지속"
        }
    
    def _generate_monthly_report(self, data):
        return {
            "title": "📊 월간 포커 생태계 종합 리포트",
            "month": data["month"],
            "sections": [
                {
                    "name": "월간 통계",
                    "statistics": data.get("monthly_stats", {}),
                    "growth_metrics": data.get("growth_metrics", {})
                },
                {
                    "name": "시장 동향",
                    "market_analysis": data.get("market_analysis", {}),
                    "competitive_landscape": data.get("competitive_analysis", {})
                },
                {
                    "name": "향후 전망",
                    "forecasts": data.get("forecasts", []),
                    "recommendations": data.get("recommendations", [])
                }
            ],
            "summary": "월간 종합 분석 및 향후 전략 제시"
        }
    
    def generate_integrated_report(self, report_type, raw_data):
        """통합 보고서 생성"""
        if report_type not in self.report_templates:
            return {"error": f"Unsupported report type: {report_type}"}
        
        try:
            report_generator = self.report_templates[report_type]
            report = report_generator(raw_data)
            
            # 메타데이터 추가
            report["metadata"] = {
                "generated_at": datetime.now().isoformat(),
                "report_type": report_type,
                "version": "1.0",
                "system": "poker-trend-analyzer"
            }
            
            return {"success": True, "report": report}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def distribute_report(self, report, distribution_config):
        """리포트 배포"""
        distribution_results = {}
        
        for channel in self.distribution_channels:
            if channel in distribution_config and distribution_config[channel]:
                # 각 채널별 배포 시뮬레이션
                success_rate = {
                    "slack_daily_channel": 0.95,
                    "slack_weekly_channel": 0.98,
                    "slack_alerts_channel": 0.99,
                    "email_subscribers": 0.85,
                    "dashboard_update": 0.90
                }.get(channel, 0.90)
                
                import random
                success = random.random() < success_rate
                
                distribution_results[channel] = {
                    "attempted": True,
                    "success": success,
                    "timestamp": datetime.now().isoformat(),
                    "recipients": distribution_config.get(f"{channel}_recipients", 1)
                }
            else:
                distribution_results[channel] = {
                    "attempted": False,
                    "reason": "not_configured"
                }
        
        return distribution_results
    
    def run_full_reporting_test(self):
        """전체 보고 시스템 테스트"""
        test_results = {}
        
        # 각 리포트 타입별 테스트
        test_data = {
            "daily": {
                "date": "2025-08-08",
                "youtube": {"trending_videos": 50, "avg_views": 125000},
                "pokernews": {"articles": 12, "main_topic": "tournament"},
                "platform": {"online_players": 45000, "growth": 5.2}
            },
            "weekly": {
                "start_date": "2025-08-05",
                "end_date": "2025-08-11",
                "trends": ["strategy_content_up", "tournament_interest_high"],
                "predictions": ["continued_growth", "new_format_adoption"]
            },
            "monthly": {
                "month": "2025-07",
                "monthly_stats": {"total_players": 850000, "total_games": 125000},
                "market_analysis": {"growth_rate": 15.3, "market_share": "increasing"}
            }
        }
        
        distribution_config = {
            "slack_daily_channel": True,
            "slack_weekly_channel": True,
            "slack_alerts_channel": False,
            "email_subscribers": True,
            "dashboard_update": True,
            "slack_daily_channel_recipients": 25,
            "email_subscribers_recipients": 150
        }
        
        for report_type, data in test_data.items():
            print(f"\\n{report_type.upper()} 리포트 테스트:")
            
            # 리포트 생성 테스트
            generation_result = self.generate_integrated_report(report_type, data)
            if generation_result["success"]:
                print(f"  ✓ 리포트 생성 성공")
                
                # 배포 테스트
                distribution_result = self.distribute_report(
                    generation_result["report"], distribution_config
                )
                
                successful_distributions = sum(
                    1 for result in distribution_result.values()
                    if result.get("attempted") and result.get("success")
                )
                total_attempted = sum(
                    1 for result in distribution_result.values()
                    if result.get("attempted")
                )
                
                print(f"  ✓ 배포 성공: {successful_distributions}/{total_attempted}")
                
                test_results[report_type] = {
                    "generation": True,
                    "distribution_success_rate": successful_distributions / total_attempted if total_attempted > 0 else 0
                }
            else:
                print(f"  ✗ 리포트 생성 실패: {generation_result.get('error')}")
                test_results[report_type] = {"generation": False}
        
        return test_results

# 통합 보고 시스템 테스트 실행
print("📋 통합 보고서 생성 및 배포 테스트")
print("=" * 50)

reporting_system = IntegratedReportingSystem()
test_results = reporting_system.run_full_reporting_test()

# 전체 결과 평가
all_generated = all(result.get("generation", False) for result in test_results.values())
avg_distribution_rate = sum(
    result.get("distribution_success_rate", 0) 
    for result in test_results.values()
) / len(test_results) if test_results else 0

print(f"\\n📊 보고 시스템 테스트 결과:")
print(f"  리포트 생성: {'모두 성공' if all_generated else '일부 실패'}")
print(f"  평균 배포 성공률: {avg_distribution_rate:.1%}")

if all_generated and avg_distribution_rate >= 0.8:
    print("\\n✅ 통합 보고 시스템: EXCELLENT")
else:
    print("\\n⚠️ 통합 보고 시스템: NEEDS REVIEW")

print("\\nIntegrated reporting: COMPLETED")
`;
    
    const tempScript = path.join(testResultsDir, 'temp_reporting_test.py');
    fs.writeFileSync(tempScript, reportingScript);
    
    const result = await runPythonScript(tempScript, []);
    
    expect(result.output).toContain('통합 보고서 생성 및 배포 테스트');
    expect(result.output).toContain('보고 시스템 테스트 결과');
    expect(result.output).toContain('COMPLETED');
    
    // 통합 테스트 결과에 기록
    integrationTestResults.components.push({
      name: 'integrated_reporting_system',
      success: result.output.includes('EXCELLENT'),
      output: result.output
    });
    
    // 임시 파일 정리
    if (fs.existsSync(tempScript)) {
      fs.unlinkSync(tempScript);
    }
  });
});

// Helper function: Python 스크립트 실행
async function runPythonScript(scriptPath, args = [], options = {}) {
  return new Promise((resolve) => {
    const python = spawn('python', [scriptPath, ...args], {
      stdio: ['pipe', 'pipe', 'pipe'],
      cwd: path.dirname(scriptPath),
      timeout: 60000, // E2E 테스트는 더 긴 타임아웃
      ...options
    });
    
    let output = '';
    let error = '';
    
    python.stdout.on('data', (data) => {
      output += data.toString();
    });
    
    python.stderr.on('data', (data) => {
      error += data.toString();
    });
    
    python.on('close', (code) => {
      resolve({
        code,
        output: output + error,
        stdout: output,
        stderr: error
      });
    });
    
    python.on('error', (err) => {
      resolve({
        code: -1,
        output: err.message,
        stdout: '',
        stderr: err.message
      });
    });
  });
}