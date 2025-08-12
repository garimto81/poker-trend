#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
개선된 텍스트 기반 플랫폼 분석 보고서
- 주간: 날짜별 사이트 변화 추이
- 월간: 첫날/마지막날 + 최대 3개 주요 변화점
"""

from datetime import datetime

class ImprovedTextReporter:
    def __init__(self):
        # 실제 Firebase 데이터 구조 시뮬레이션
        self.daily_snapshot = {
            'date': '2025-08-10',
            'collection_time': '14:30 KST',
            'online_players': {
                'GGNetwork': 153008,
                'IDNPoker': 5528,
                'WPT Global': 5237,
                'Pokerdom': 2693,
                'Chico': 953,
                'Others': 1287
            },
            'cash_players': {
                'GGNetwork': 10404,
                'WPT Global': 3019,
                'IDNPoker': 1400,
                'Pokerdom': 555,
                'Chico': 179,
                'Others': 1364
            }
        }
        
        # 주간 데이터 (날짜별 변화 추이)
        self.weekly_data = {
            'period': '2025-08-04 ~ 2025-08-10',
            'daily_trends': {
                '8/4': {
                    'online': {'GGNetwork': 165234, 'IDNPoker': 9837, 'WPT Global': 7521, 'Pokerdom': 3921, 'Chico': 1567},
                    'cash': {'GGNetwork': 11234, 'WPT Global': 3521, 'IDNPoker': 2156, 'Pokerdom': 823, 'Chico': 287}
                },
                '8/5': {
                    'online': {'GGNetwork': 158472, 'IDNPoker': 8956, 'WPT Global': 7234, 'Pokerdom': 3845, 'Chico': 1432},
                    'cash': {'GGNetwork': 10987, 'WPT Global': 3445, 'IDNPoker': 2089, 'Pokerdom': 798, 'Chico': 265}
                },
                '8/6': {
                    'online': {'GGNetwork': 151683, 'IDNPoker': 8423, 'WPT Global': 6987, 'Pokerdom': 3768, 'Chico': 1298},
                    'cash': {'GGNetwork': 10756, 'WPT Global': 3378, 'IDNPoker': 1987, 'Pokerdom': 775, 'Chico': 243}
                },
                '8/7': {
                    'online': {'GGNetwork': 149295, 'IDNPoker': 7891, 'WPT Global': 6754, 'Pokerdom': 3692, 'Chico': 1165},
                    'cash': {'GGNetwork': 10523, 'WPT Global': 3301, 'IDNPoker': 1876, 'Pokerdom': 751, 'Chico': 221}
                },
                '8/8': {
                    'online': {'GGNetwork': 147516, 'IDNPoker': 6987, 'WPT Global': 6521, 'Pokerdom': 3615, 'Chico': 1032},
                    'cash': {'GGNetwork': 10291, 'WPT Global': 3234, 'IDNPoker': 1654, 'Pokerdom': 728, 'Chico': 199}
                },
                '8/9': {
                    'online': {'GGNetwork': 150842, 'IDNPoker': 6234, 'WPT Global': 6843, 'Pokerdom': 3701, 'Chico': 999},
                    'cash': {'GGNetwork': 10347, 'WPT Global': 3287, 'IDNPoker': 1523, 'Pokerdom': 739, 'Chico': 187}
                },
                '8/10': {
                    'online': {'GGNetwork': 153008, 'IDNPoker': 5528, 'WPT Global': 5237, 'Pokerdom': 2693, 'Chico': 953},
                    'cash': {'GGNetwork': 10404, 'WPT Global': 3019, 'IDNPoker': 1400, 'Pokerdom': 555, 'Chico': 179}
                }
            }
        }
        
        # 월간 데이터 (첫날/마지막날 + 주요 변화점)
        self.monthly_data = {
            'period': '2025-07-30 ~ 2025-08-10 (12일)',
            'start_date': '7/30',
            'end_date': '8/10',
            'start_snapshot': {
                'online': {'GGNetwork': 198543, 'IDNPoker': 15234, 'WPT Global': 12456, 'Pokerdom': 8234, 'Chico': 3456, 'Others': 68311},
                'cash': {'GGNetwork': 16543, 'WPT Global': 5432, 'IDNPoker': 4567, 'Pokerdom': 1234, 'Chico': 567, 'Others': 113}
            },
            'end_snapshot': {
                'online': {'GGNetwork': 153008, 'IDNPoker': 5528, 'WPT Global': 5237, 'Pokerdom': 2693, 'Chico': 953, 'Others': 1287},
                'cash': {'GGNetwork': 10404, 'WPT Global': 3019, 'IDNPoker': 1400, 'Pokerdom': 555, 'Chico': 179, 'Others': 1364}
            },
            'major_changes': [
                {
                    'date': '8/3',
                    'event': 'Others 카테고리 대규모 감소',
                    'online_change': {'Others': -49123},  # 68311 → 19188
                    'impact': '전체 시장 15% 축소'
                },
                {
                    'date': '8/5',
                    'event': 'IDNPoker 급격한 하락',
                    'online_change': {'IDNPoker': -6278},  # 15234 → 8956
                    'impact': '아시아 시장 재편'
                },
                {
                    'date': '8/8',
                    'event': '전체 시장 최저점 도달',
                    'online_change': {'Total': -137545},  # 전날 대비
                    'impact': '시장 전반 침체'
                }
            ]
        }
    
    def generate_daily_report(self):
        """일간 보고서 생성"""
        data = self.daily_snapshot
        
        report = f"""
📊 [일간] 플랫폼 분석 보고서

📅 기준일: {data['date']}
🕐 수집시간: {data['collection_time']}
📝 보고시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎮 온라인 플레이어
총 접속자: {sum(data['online_players'].values()):,}명

1. GGNetwork    : {data['online_players']['GGNetwork']:,}명 ({data['online_players']['GGNetwork']/sum(data['online_players'].values())*100:.1f}%)
2. IDNPoker     : {data['online_players']['IDNPoker']:,}명 ({data['online_players']['IDNPoker']/sum(data['online_players'].values())*100:.1f}%)
3. WPT Global   : {data['online_players']['WPT Global']:,}명 ({data['online_players']['WPT Global']/sum(data['online_players'].values())*100:.1f}%)
4. Pokerdom     : {data['online_players']['Pokerdom']:,}명 ({data['online_players']['Pokerdom']/sum(data['online_players'].values())*100:.1f}%)
5. Chico        : {data['online_players']['Chico']:,}명 ({data['online_players']['Chico']/sum(data['online_players'].values())*100:.1f}%)

💰 캐시 플레이어  
총 참여자: {sum(data['cash_players'].values()):,}명

1. GGNetwork    : {data['cash_players']['GGNetwork']:,}명 ({data['cash_players']['GGNetwork']/sum(data['cash_players'].values())*100:.1f}%)
2. WPT Global   : {data['cash_players']['WPT Global']:,}명 ({data['cash_players']['WPT Global']/sum(data['cash_players'].values())*100:.1f}%)
3. IDNPoker     : {data['cash_players']['IDNPoker']:,}명 ({data['cash_players']['IDNPoker']/sum(data['cash_players'].values())*100:.1f}%)
4. Pokerdom     : {data['cash_players']['Pokerdom']:,}명 ({data['cash_players']['Pokerdom']/sum(data['cash_players'].values())*100:.1f}%)
5. Chico        : {data['cash_players']['Chico']:,}명 ({data['cash_players']['Chico']/sum(data['cash_players'].values())*100:.1f}%)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 주요 지표: GGNetwork 압도적 우위 (온라인 {data['online_players']['GGNetwork']/sum(data['online_players'].values())*100:.1f}%, 캐시 {data['cash_players']['GGNetwork']/sum(data['cash_players'].values())*100:.1f}%)
"""
        return report.strip()
    
    def generate_weekly_report(self):
        """주간 보고서 - 날짜별 변화 추이"""
        data = self.weekly_data
        
        # 날짜별 총합 계산
        daily_totals = {}
        for date, platforms in data['daily_trends'].items():
            daily_totals[date] = {
                'online_total': sum(platforms['online'].values()),
                'cash_total': sum(platforms['cash'].values())
            }
        
        # 주요 플랫폼별 주간 변화 계산
        platforms = ['GGNetwork', 'IDNPoker', 'WPT Global', 'Pokerdom', 'Chico']
        platform_changes = {}
        
        for platform in platforms:
            start_online = data['daily_trends']['8/4']['online'][platform]
            end_online = data['daily_trends']['8/10']['online'][platform]
            start_cash = data['daily_trends']['8/4']['cash'][platform]
            end_cash = data['daily_trends']['8/10']['cash'][platform]
            
            platform_changes[platform] = {
                'online_change': ((end_online - start_online) / start_online) * 100,
                'cash_change': ((end_cash - start_cash) / start_cash) * 100
            }
        
        report = f"""
📈 [주간] 플랫폼 트렌드 분석

📅 분석기간: {data['period']}
📝 보고시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎮 온라인 플레이어 날짜별 추이

날짜    │  GGNetwork │  IDNPoker │ WPT Global│  Pokerdom │    Chico  │   총합
────────┼────────────┼───────────┼───────────┼───────────┼───────────┼─────────"""

        dates = ['8/4', '8/5', '8/6', '8/7', '8/8', '8/9', '8/10']
        for date in dates:
            daily = data['daily_trends'][date]['online']
            total = sum(daily.values())
            report += f"""
{date:7} │ {daily['GGNetwork']:,>9} │ {daily['IDNPoker']:,>8} │ {daily['WPT Global']:,>8} │ {daily['Pokerdom']:,>8} │ {daily['Chico']:,>8} │ {total:,>8}"""

        report += f"""

💰 캐시 플레이어 날짜별 추이

날짜    │  GGNetwork │ WPT Global│  IDNPoker │  Pokerdom │    Chico  │   총합
────────┼────────────┼───────────┼───────────┼───────────┼───────────┼─────────"""

        for date in dates:
            daily = data['daily_trends'][date]['cash']
            total = sum(daily.values())
            report += f"""
{date:7} │ {daily['GGNetwork']:,>9} │ {daily['WPT Global']:,>8} │ {daily['IDNPoker']:,>8} │ {daily['Pokerdom']:,>8} │ {daily['Chico']:,>8} │ {total:,>8}"""

        report += f"""

📊 주간 변화율 요약 (8/4 → 8/10)

플랫폼        │ 온라인 변화 │ 캐시 변화
─────────────┼─────────────┼──────────"""

        for platform in platforms:
            online_change = platform_changes[platform]['online_change']
            cash_change = platform_changes[platform]['cash_change']
            report += f"""
{platform:12} │ {online_change:+8.1f}% │ {cash_change:+7.1f}%"""

        # 전체 변화
        total_online_start = daily_totals['8/4']['online_total']
        total_online_end = daily_totals['8/10']['online_total']
        total_cash_start = daily_totals['8/4']['cash_total']
        total_cash_end = daily_totals['8/10']['cash_total']
        
        online_total_change = ((total_online_end - total_online_start) / total_online_start) * 100
        cash_total_change = ((total_cash_end - total_cash_start) / total_cash_start) * 100

        report += f"""
─────────────┼─────────────┼──────────
전체 시장    │ {online_total_change:+8.1f}% │ {cash_total_change:+7.1f}%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 주간 트렌드: 전반적 하락세, GGNetwork 독점 심화
"""
        return report.strip()
    
    def generate_monthly_report(self):
        """월간 보고서 - 첫날/마지막날 + 최대 3개 주요 변화점"""
        data = self.monthly_data
        
        # 첫날/마지막날 총합 계산
        start_online_total = sum(data['start_snapshot']['online'].values())
        end_online_total = sum(data['end_snapshot']['online'].values())
        start_cash_total = sum(data['start_snapshot']['cash'].values())
        end_cash_total = sum(data['end_snapshot']['cash'].values())
        
        # 전체 변화율
        online_total_change = ((end_online_total - start_online_total) / start_online_total) * 100
        cash_total_change = ((end_cash_total - start_cash_total) / start_cash_total) * 100
        
        report = f"""
📋 [월간] 플랫폼 전략 분석

📅 분석기간: {data['period']}
📝 보고시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏁 기간 시작 ({data['start_date']}) vs 종료 ({data['end_date']}) 비교

🎮 온라인 플레이어
                │   시작     │   종료     │   변화    │ 변화율
────────────────┼────────────┼────────────┼───────────┼────────"""

        platforms = ['GGNetwork', 'IDNPoker', 'WPT Global', 'Pokerdom', 'Chico', 'Others']
        for platform in platforms:
            start_val = data['start_snapshot']['online'][platform]
            end_val = data['end_snapshot']['online'][platform]
            change = end_val - start_val
            change_pct = (change / start_val) * 100 if start_val > 0 else 0
            report += f"""
{platform:15} │ {start_val:,>9} │ {end_val:,>9} │ {change:+,>8} │ {change_pct:+6.1f}%"""

        report += f"""
────────────────┼────────────┼────────────┼───────────┼────────
전체            │ {start_online_total:,>9} │ {end_online_total:,>9} │ {end_online_total-start_online_total:+,>8} │ {online_total_change:+6.1f}%

💰 캐시 플레이어
                │   시작     │   종료     │   변화    │ 변화율
────────────────┼────────────┼────────────┼───────────┼────────"""

        for platform in platforms:
            start_val = data['start_snapshot']['cash'][platform]
            end_val = data['end_snapshot']['cash'][platform]
            change = end_val - start_val
            change_pct = (change / start_val) * 100 if start_val > 0 else 0
            report += f"""
{platform:15} │ {start_val:,>9} │ {end_val:,>9} │ {change:+,>8} │ {change_pct:+6.1f}%"""

        report += f"""
────────────────┼────────────┼────────────┼───────────┼────────
전체            │ {start_cash_total:,>9} │ {end_cash_total:,>9} │ {end_cash_total-start_cash_total:+,>8} │ {cash_total_change:+6.1f}%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚡ 주요 변화 이벤트 (최대 3개)"""

        # 주요 변화 이벤트 표시
        if data['major_changes']:
            for i, event in enumerate(data['major_changes'], 1):
                report += f"""

{i}. {event['date']} - {event['event']}
   영향: {event['impact']}"""
                
                if 'online_change' in event:
                    for platform, change in event['online_change'].items():
                        if platform == 'Total':
                            report += f"""
   └ 전체 시장: {change:+,}명"""
                        else:
                            report += f"""
   └ {platform}: {change:+,}명"""
        else:
            report += """

   (이번 기간 중 특별한 변화 없음)"""

        report += f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 월간 요약: 전체 시장 {abs(online_total_change):.1f}% 축소, GGNetwork 독점 구조 심화
"""
        return report.strip()
    
    def generate_all_reports(self):
        """모든 보고서 생성"""
        print("=" * 60)
        print("개선된 텍스트 보고서 미리보기")
        print("=" * 60)
        
        print("\n" + "="*20 + " 일간 보고서 " + "="*20)
        print(self.generate_daily_report())
        
        print("\n\n" + "="*20 + " 주간 보고서 " + "="*20)
        print(self.generate_weekly_report())
        
        print("\n\n" + "="*20 + " 월간 보고서 " + "="*20)
        print(self.generate_monthly_report())
        
        print("\n\n" + "="*60)
        print("보고서 미리보기 완료")
        print("확인 후 Slack 전송 진행 가능")
        print("="*60)

def main():
    """메인 실행"""
    reporter = ImprovedTextReporter()
    reporter.generate_all_reports()

if __name__ == "__main__":
    main()