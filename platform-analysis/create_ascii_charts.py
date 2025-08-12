#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ASCII 차트로 시각화된 플랫폼 분석 보고서
이미지 업로드 없이 텍스트만으로 트렌드 표현
"""

import requests
from datetime import datetime

class ASCIIChartReporter:
    def __init__(self):
        self.webhook_url = os.getenv('SLACK_WEBHOOK_URL', 'your-webhook-url-here')
    
    def create_bar_chart(self, data, max_width=20):
        """간단한 ASCII 막대 차트 생성"""
        max_val = max(data.values())
        chart_lines = []
        
        for name, value in data.items():
            bar_length = int((value / max_val) * max_width)
            bar = "█" * bar_length + "░" * (max_width - bar_length)
            chart_lines.append(f"{name:12} │{bar}│ {value:,}")
        
        return "\n".join(chart_lines)
    
    def create_trend_line(self, values, width=20):
        """간단한 ASCII 트렌드 라인"""
        if not values:
            return ""
        
        min_val, max_val = min(values), max(values)
        if max_val == min_val:
            return "━" * width
        
        normalized = [(v - min_val) / (max_val - min_val) for v in values]
        positions = [int(n * 3) for n in normalized]  # 0-3 높이
        
        trend_chars = ["▁", "▂", "▅", "▇"]
        return "".join(trend_chars[min(p, 3)] for p in positions)
    
    def send_daily_ascii_report(self):
        """ASCII 차트가 포함된 일간 보고서"""
        online_data = {
            "GGNetwork": 153008,
            "IDNPoker": 5528,
            "WPT Global": 5237,
            "Pokerdom": 2693,
            "Chico": 953
        }
        
        cash_data = {
            "GGNetwork": 10404,
            "WPT Global": 3019,
            "IDNPoker": 1400,
            "Pokerdom": 555,
            "Chico": 179
        }
        
        online_chart = self.create_bar_chart(online_data)
        cash_chart = self.create_bar_chart(cash_data)
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📊 [일간] 플랫폼 분석 (ASCII 차트)"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*기간:* 2025-08-10\n*보고시간:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"```[온라인 플레이어] 총 168,706명\n{online_chart}```"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"```[캐시 플레이어] 총 16,921명\n{cash_chart}```"
                }
            }
        ]
        
        return self._send_to_slack(blocks, "일간 ASCII")
    
    def send_weekly_ascii_report(self):
        """주간 트렌드 ASCII 차트"""
        # 주간 데이터 (8/4-8/10) - generate_stacked_area_reports.py 실제 데이터
        weekly_online_platforms = {
            'GGNetwork': [165234, 158472, 151683, 149295, 147516, 150842, 153008],
            'IDNPoker': [9837, 8956, 8423, 7891, 6987, 6234, 5528],
            'WPT Global': [7521, 7234, 6987, 6754, 6521, 6843, 5237],
            'Pokerdom': [3921, 3845, 3768, 3692, 3615, 3701, 2693],
            'Chico': [1567, 1432, 1298, 1165, 1032, 999, 953],
            'Others': [1341, 2164, 3733, 4437, 4205, 1615, 1287]
        }
        
        weekly_cash_platforms = {
            'GGNetwork': [11234, 10987, 10756, 10523, 10291, 10347, 10404],
            'WPT Global': [3521, 3445, 3378, 3301, 3234, 3287, 3019],
            'IDNPoker': [2156, 2089, 1987, 1876, 1654, 1523, 1400],
            'Pokerdom': [823, 798, 775, 751, 728, 739, 555],
            'Chico': [287, 265, 243, 221, 199, 187, 179],
            'Others': [213, 272, 95, 315, 437, 649, 1364]
        }
        
        # 일별 총합 계산
        weekly_online = [sum(weekly_online_platforms[p][i] for p in weekly_online_platforms) for i in range(7)]
        weekly_cash = [sum(weekly_cash_platforms[p][i] for p in weekly_cash_platforms) for i in range(7)]
        
        online_trend = self.create_trend_line(weekly_online, 14)
        cash_trend = self.create_trend_line(weekly_cash, 14)
        
        # 변화율 계산
        online_change = ((weekly_online[-1] - weekly_online[0]) / weekly_online[0]) * 100
        cash_change = ((weekly_cash[-1] - weekly_cash[0]) / weekly_cash[0]) * 100
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📈 [주간] 플랫폼 트렌드 (ASCII 차트)"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*기간:* 2025-08-04 ~ 2025-08-10\n*보고시간:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"```[온라인 플레이어 트렌드]\n8/4  8/5  8/6  8/7  8/8  8/9  8/10\n{online_trend}\n{weekly_online[0]:,} → {weekly_online[-1]:,} ({online_change:+.1f}%)```"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"```[캐시 플레이어 트렌드]\n8/4  8/5  8/6  8/7  8/8  8/9  8/10\n{cash_trend}\n{weekly_cash[0]:,} → {weekly_cash[-1]:,} ({cash_change:+.1f}%)```"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*주요 변화*\n• 온라인: GGNetwork 89.1% 독점 강화\n• 캐시: 전체적 하락세, GGNetwork 61.5%\n• IDNPoker, Pokerdom 큰 폭 감소"
                }
            }
        ]
        
        return self._send_to_slack(blocks, "주간 ASCII")
    
    def send_monthly_ascii_report(self):
        """월간 트렌드 ASCII 차트"""
        # 월간 데이터 (7/30-8/10) - generate_stacked_area_reports.py 실제 데이터
        monthly_online_platforms = {
            'GGNetwork': [198543, 195872, 188234, 182456, 167891, 165234, 158472, 151683, 149295, 147516, 150842, 153008],
            'IDNPoker': [15234, 14892, 13567, 12891, 11456, 9837, 8956, 8423, 7891, 6987, 6234, 5528],
            'WPT Global': [12456, 11823, 10987, 9876, 8456, 7521, 7234, 6987, 6754, 6521, 6843, 5237],
            'Pokerdom': [8234, 7891, 7234, 6543, 5432, 3921, 3845, 3768, 3692, 3615, 3701, 2693],
            'Chico': [3456, 3234, 2891, 2456, 1987, 1567, 1432, 1298, 1165, 1032, 999, 953],
            'Others': [68311, 45632, 32456, 21893, 11034, 1341, 2164, 3733, 4437, 4205, 1615, 1287]
        }
        
        monthly_cash_platforms = {
            'GGNetwork': [16543, 15891, 14234, 13456, 12567, 11234, 10987, 10756, 10523, 10291, 10347, 10404],
            'WPT Global': [5432, 5123, 4678, 4234, 3891, 3521, 3445, 3378, 3301, 3234, 3287, 3019],
            'IDNPoker': [4567, 4234, 3891, 3456, 2987, 2156, 2089, 1987, 1876, 1654, 1523, 1400],
            'Pokerdom': [1234, 1187, 1098, 987, 876, 823, 798, 775, 751, 728, 739, 555],
            'Chico': [567, 523, 456, 398, 345, 287, 265, 243, 221, 199, 187, 179],
            'Others': [113, 189, 287, 415, 556, 213, 272, 95, 315, 437, 649, 1364]
        }
        
        # 일별 총합 계산
        monthly_online = [sum(monthly_online_platforms[p][i] for p in monthly_online_platforms) for i in range(12)]
        monthly_cash = [sum(monthly_cash_platforms[p][i] for p in monthly_cash_platforms) for i in range(12)]
        
        online_trend = self.create_trend_line(monthly_online, 24)
        cash_trend = self.create_trend_line(monthly_cash, 24)
        
        # 변화율 계산
        online_change = ((monthly_online[-1] - monthly_online[0]) / monthly_online[0]) * 100
        cash_change = ((monthly_cash[-1] - monthly_cash[0]) / monthly_cash[0]) * 100
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📊 [월간] 플랫폼 트렌드 (ASCII 차트)"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*기간:* 2025-07-30 ~ 2025-08-10 (12일)\n*보고시간:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"```[온라인 플레이어 월간 트렌드]\n7/30    8/1     8/3     8/5     8/7     8/9    8/10\n{online_trend}\n{monthly_online[0]:,} → {monthly_online[-1]:,} ({online_change:+.1f}%)```"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"```[캐시 플레이어 월간 트렌드]\n7/30    8/1     8/3     8/5     8/7     8/9    8/10\n{cash_trend}\n{monthly_cash[0]:,} → {monthly_cash[-1]:,} ({cash_change:+.1f}%)```"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*핵심 분석*\n• 전체 시장 45% 급격 축소\n• GGNetwork 시장 지배력 65% → 89%\n• 8/3 이후 Others 플랫폼 대규모 이탈\n• 소규모 플랫폼들 지속적 감소 추세"
                }
            }
        ]
        
        return self._send_to_slack(blocks, "월간 ASCII")
    
    def _send_to_slack(self, blocks, report_type):
        """Slack 전송"""
        payload = {"blocks": blocks}
        
        try:
            response = requests.post(self.webhook_url, json=payload)
            if response.status_code == 200:
                print(f"[OK] {report_type} 보고서 전송 완료")
                return True
            else:
                print(f"[ERROR] {report_type} 전송 실패: {response.status_code}")
                return False
        except Exception as e:
            print(f"[ERROR] {report_type} 전송 오류: {e}")
            return False

def main():
    """메인 실행"""
    print("=" * 60)
    print("ASCII 차트 플랫폼 분석 보고서 전송")
    print("=" * 60)
    
    reporter = ASCIIChartReporter()
    
    print("\n1. 일간 ASCII 보고서 전송...")
    reporter.send_daily_ascii_report()
    
    print("\n2. 주간 ASCII 보고서 전송...")
    reporter.send_weekly_ascii_report()
    
    print("\n3. 월간 ASCII 보고서 전송...")
    reporter.send_monthly_ascii_report()
    
    print("\n" + "=" * 60)
    print("ASCII 차트 보고서 전송 완료")
    print("=" * 60)

if __name__ == "__main__":
    main()