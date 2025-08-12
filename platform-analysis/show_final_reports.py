#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
최종 개선된 텍스트 보고서 출력 (Slack 전송 없이)
"""

from datetime import datetime

class FinalReports:
    def __init__(self):
        # 일간 데이터
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
        
        # 주간 데이터 (날짜별 변화 추이) - Others 카테고리 포함하여 전체 시장 총합 정확히 계산
        self.weekly_data = {
            'period': '2025-08-04 ~ 2025-08-10',
            'daily_trends': {
                '8/4': {
                    'online': {'GGNetwork': 165234, 'IDNPoker': 9837, 'WPT Global': 7521, 'Pokerdom': 3921, 'Chico': 1567, 'Others': 1341},
                    'cash': {'GGNetwork': 11234, 'WPT Global': 3521, 'IDNPoker': 2156, 'Pokerdom': 823, 'Chico': 287, 'Others': 213}
                },
                '8/5': {
                    'online': {'GGNetwork': 158472, 'IDNPoker': 8956, 'WPT Global': 7234, 'Pokerdom': 3845, 'Chico': 1432, 'Others': 2164},
                    'cash': {'GGNetwork': 10987, 'WPT Global': 3445, 'IDNPoker': 2089, 'Pokerdom': 798, 'Chico': 265, 'Others': 272}
                },
                '8/6': {
                    'online': {'GGNetwork': 151683, 'IDNPoker': 8423, 'WPT Global': 6987, 'Pokerdom': 3768, 'Chico': 1298, 'Others': 3733},
                    'cash': {'GGNetwork': 10756, 'WPT Global': 3378, 'IDNPoker': 1987, 'Pokerdom': 775, 'Chico': 243, 'Others': 95}
                },
                '8/7': {
                    'online': {'GGNetwork': 149295, 'IDNPoker': 7891, 'WPT Global': 6754, 'Pokerdom': 3692, 'Chico': 1165, 'Others': 4437},
                    'cash': {'GGNetwork': 10523, 'WPT Global': 3301, 'IDNPoker': 1876, 'Pokerdom': 751, 'Chico': 221, 'Others': 315}
                },
                '8/8': {
                    'online': {'GGNetwork': 147516, 'IDNPoker': 6987, 'WPT Global': 6521, 'Pokerdom': 3615, 'Chico': 1032, 'Others': 4205},
                    'cash': {'GGNetwork': 10291, 'WPT Global': 3234, 'IDNPoker': 1654, 'Pokerdom': 728, 'Chico': 199, 'Others': 437}
                },
                '8/9': {
                    'online': {'GGNetwork': 150842, 'IDNPoker': 6234, 'WPT Global': 6843, 'Pokerdom': 3701, 'Chico': 999, 'Others': 1615},
                    'cash': {'GGNetwork': 10347, 'WPT Global': 3287, 'IDNPoker': 1523, 'Pokerdom': 739, 'Chico': 187, 'Others': 649}
                },
                '8/10': {
                    'online': {'GGNetwork': 153008, 'IDNPoker': 5528, 'WPT Global': 5237, 'Pokerdom': 2693, 'Chico': 953, 'Others': 1287},
                    'cash': {'GGNetwork': 10404, 'WPT Global': 3019, 'IDNPoker': 1400, 'Pokerdom': 555, 'Chico': 179, 'Others': 1364}
                }
            }
        }
        
        # 월간 데이터 - 각 플랫폼별 최대 변동 날짜 개별 분석
        self.monthly_data = {
            'period': '2025-07-30 ~ 2025-08-10 (12일)',
            'dates': ['7/30', '7/31', '8/1', '8/2', '8/3', '8/4', '8/5', '8/6', '8/7', '8/8', '8/9', '8/10'],
            'online': {
                'GGNetwork': [198543, 195872, 188234, 182456, 167891, 165234, 158472, 151683, 149295, 147516, 150842, 153008],
                'IDNPoker': [15234, 14892, 13567, 12891, 11456, 9837, 8956, 8423, 7891, 6987, 6234, 5528],
                'WPT Global': [12456, 11823, 10987, 9876, 8456, 7521, 7234, 6987, 6754, 6521, 6843, 5237],
                'Pokerdom': [8234, 7891, 7234, 6543, 5432, 3921, 3845, 3768, 3692, 3615, 3701, 2693],
                'Chico': [3456, 3234, 2891, 2456, 1987, 1567, 1432, 1298, 1165, 1032, 999, 953],
                'Others': [68311, 45632, 32456, 21893, 11034, 1341, 2164, 3733, 4437, 4205, 1615, 1287]
            },
            'cash': {
                'GGNetwork': [16543, 15891, 14234, 13456, 12567, 11234, 10987, 10756, 10523, 10291, 10347, 10404],
                'WPT Global': [5432, 5123, 4678, 4234, 3891, 3521, 3445, 3378, 3301, 3234, 3287, 3019],
                'IDNPoker': [4567, 4234, 3891, 3456, 2987, 2156, 2089, 1987, 1876, 1654, 1523, 1400],
                'Pokerdom': [1234, 1187, 1098, 987, 876, 823, 798, 775, 751, 728, 739, 555],
                'Chico': [567, 523, 456, 398, 345, 287, 265, 243, 221, 199, 187, 179],
                'Others': [113, 189, 287, 415, 556, 213, 272, 95, 315, 437, 649, 1364]
            }
        }
    
    def show_daily_report(self):
        """일간 보고서 출력"""
        data = self.daily_snapshot
        online_total = sum(data['online_players'].values())
        cash_total = sum(data['cash_players'].values())
        
        print("=" * 70)
        print("                    [일간] 플랫폼 분석 보고서")
        print("=" * 70)
        print()
        print(f"기준일     : {data['date']}")
        print(f"수집시간   : {data['collection_time']}")
        print(f"보고시간   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        print("━" * 70)
        print()
        print("[온라인 플레이어]")
        print(f"총 접속자: {online_total:,}명")
        print()
        print("순위  플랫폼         접속자 수         점유율")
        print("─" * 50)
        
        sorted_online = sorted(data['online_players'].items(), key=lambda x: x[1], reverse=True)
        for i, (platform, count) in enumerate(sorted_online, 1):
            share = (count / online_total) * 100
            print(f"{i:2d}.  {platform:12} {count:,>10}명    {share:5.1f}%")
        
        print()
        print("[캐시 플레이어]")
        print(f"총 참여자: {cash_total:,}명")
        print()
        print("순위  플랫폼         참여자 수         점유율")
        print("─" * 50)
        
        sorted_cash = sorted(data['cash_players'].items(), key=lambda x: x[1], reverse=True)
        for i, (platform, count) in enumerate(sorted_cash, 1):
            share = (count / cash_total) * 100
            print(f"{i:2d}.  {platform:12} {count:,>10}명    {share:5.1f}%")
        
        print()
        print("━" * 70)
        print(f"핵심 지표: GGNetwork 압도적 우위")
        print(f"          온라인 {data['online_players']['GGNetwork']/online_total*100:.1f}%, 캐시 {data['cash_players']['GGNetwork']/cash_total*100:.1f}%")
        print("=" * 70)
    
    def show_weekly_report(self):
        """주간 보고서 출력"""
        data = self.weekly_data
        dates = ['8/4', '8/5', '8/6', '8/7', '8/8', '8/9', '8/10']
        
        print("=" * 95)
        print("                    [주간] 플랫폼 트렌드 분석")
        print("=" * 95)
        print()
        print(f"분석기간   : {data['period']}")
        print(f"보고시간   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        print("━" * 95)
        print()
        print("[온라인 플레이어 날짜별 추이]")
        print()
        print("날짜     │  GGNetwork │  IDNPoker │ WPT Global│  Pokerdom │    Chico  │   Others  │    총합")
        print("─" * 95)
        
        for date in dates:
            daily = data['daily_trends'][date]['online']
            total = sum(daily.values())
            print(f"{date:8} │ {daily['GGNetwork']:,>9} │ {daily['IDNPoker']:,>8} │ {daily['WPT Global']:,>8} │ {daily['Pokerdom']:,>8} │ {daily['Chico']:,>8} │ {daily['Others']:,>8} │ {total:,>9}")
        
        print()
        print("[캐시 플레이어 날짜별 추이]")
        print()
        print("날짜     │  GGNetwork │ WPT Global│  IDNPoker │  Pokerdom │    Chico  │   Others  │    총합")
        print("─" * 95)
        
        for date in dates:
            daily = data['daily_trends'][date]['cash']
            total = sum(daily.values())
            print(f"{date:8} │ {daily['GGNetwork']:,>9} │ {daily['WPT Global']:,>8} │ {daily['IDNPoker']:,>8} │ {daily['Pokerdom']:,>8} │ {daily['Chico']:,>8} │ {daily['Others']:,>8} │ {total:,>9}")
        
        print()
        print("[주간 변화율 요약] (8/4 → 8/10)")
        print()
        print("플랫폼          │ 온라인 변화 │ 캐시 변화")
        print("─" * 45)
        
        platforms = ['GGNetwork', 'IDNPoker', 'WPT Global', 'Pokerdom', 'Chico', 'Others']
        for platform in platforms:
            start_online = data['daily_trends']['8/4']['online'][platform]
            end_online = data['daily_trends']['8/10']['online'][platform]
            start_cash = data['daily_trends']['8/4']['cash'][platform]
            end_cash = data['daily_trends']['8/10']['cash'][platform]
            
            online_change = ((end_online - start_online) / start_online) * 100
            cash_change = ((end_cash - start_cash) / start_cash) * 100
            
            print(f"{platform:15} │ {online_change:+8.1f}% │ {cash_change:+7.1f}%")
        
        # 전체 변화
        total_online_start = sum(data['daily_trends']['8/4']['online'].values())
        total_online_end = sum(data['daily_trends']['8/10']['online'].values())
        total_cash_start = sum(data['daily_trends']['8/4']['cash'].values())
        total_cash_end = sum(data['daily_trends']['8/10']['cash'].values())
        
        online_total_change = ((total_online_end - total_online_start) / total_online_start) * 100
        cash_total_change = ((total_cash_end - total_cash_start) / total_cash_start) * 100
        
        print("─" * 45)
        print(f"{'전체 시장':15} │ {online_total_change:+8.1f}% │ {cash_total_change:+7.1f}%")
        
        print()
        print("━" * 95)
        print("주간 트렌드: 전반적 하락세, GGNetwork 독점 심화")
        print("=" * 95)
    
    def show_monthly_report(self):
        """월간 보고서 출력 - 각 플랫폼별 최대 변동 날짜 개별 표시"""
        data = self.monthly_data
        dates = data['dates']
        
        def find_top3_changes(values, dates):
            """각 플랫폼별 상위 3개 변동 날짜와 값 찾기"""
            changes = []
            for i in range(1, len(values)):
                change = abs(values[i] - values[i-1])
                change_pct = ((values[i] - values[i-1]) / values[i-1]) * 100 if values[i-1] > 0 else 0
                changes.append({
                    'date': dates[i],
                    'value': values[i],
                    'change': change,
                    'change_pct': change_pct,
                    'index': i
                })
            
            # 변동량이 큰 순서로 정렬하여 상위 3개 선택
            changes.sort(key=lambda x: x['change'], reverse=True)
            top3_indices = sorted([c['index'] for c in changes[:3]])
            
            result = []
            for idx in top3_indices:
                for c in changes:
                    if c['index'] == idx:
                        result.append({'date': c['date'], 'value': c['value']})
                        break
            
            return result
        
        print("=" * 130)
        print("                     [월간] 플랫폼 전략 분석")
        print("=" * 130)
        print()
        print(f"분석기간   : {data['period']}")
        print(f"보고시간   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        print("━" * 130)
        print()
        print("[온라인 플레이어 월간 추이] - 각 플랫폼별 최대 변동 3개 날짜")
        print()
        
        platforms = ['GGNetwork', 'IDNPoker', 'WPT Global', 'Pokerdom', 'Chico', 'Others']
        
        # 각 플랫폼별 상위 3개 변동 날짜 찾기
        platform_changes = {}
        for platform in platforms:
            values = data['online'][platform]
            top3 = find_top3_changes(values, dates)
            platform_changes[platform] = {
                'start': values[0],
                'end': values[-1],
                'top3': top3,
                'total_change': ((values[-1] - values[0]) / values[0]) * 100 if values[0] > 0 else 0
            }
        
        # 헤더 출력
        print("플랫폼          │    시작     │             변화1           │             변화2           │             변화3           │    종료     │  총변화율")
        print("                │   (7/30)    │          (날짜별)           │          (날짜별)           │          (날짜별)           │   (8/10)    │")
        print("─" * 130)
        
        for platform in platforms:
            pc = platform_changes[platform]
            top3 = pc['top3']
            
            # 변화 날짜와 값 포맷팅
            change1 = f"{top3[0]['value']:,>8} ({top3[0]['date']})" if len(top3) > 0 else "N/A"
            change2 = f"{top3[1]['value']:,>8} ({top3[1]['date']})" if len(top3) > 1 else "N/A"  
            change3 = f"{top3[2]['value']:,>8} ({top3[2]['date']})" if len(top3) > 2 else "N/A"
            
            print(f"{platform:15} │ {pc['start']:,>10} │ {change1:^27} │ {change2:^27} │ {change3:^27} │ {pc['end']:,>10} │ {pc['total_change']:+8.1f}%")
        
        # 전체 총합 계산
        total_online = [sum(data['online'][p][i] for p in platforms) for i in range(len(dates))]
        total_top3 = find_top3_changes(total_online, dates)
        total_start = total_online[0]
        total_end = total_online[-1]
        total_change_pct = ((total_end - total_start) / total_start) * 100
        
        # 전체 총합 행 출력
        change1_total = f"{total_top3[0]['value']:,>8} ({total_top3[0]['date']})" if len(total_top3) > 0 else "N/A"
        change2_total = f"{total_top3[1]['value']:,>8} ({total_top3[1]['date']})" if len(total_top3) > 1 else "N/A"
        change3_total = f"{total_top3[2]['value']:,>8} ({total_top3[2]['date']})" if len(total_top3) > 2 else "N/A"
        
        print("─" * 130)
        print(f"{'전체':15} │ {total_start:,>10} │ {change1_total:^27} │ {change2_total:^27} │ {change3_total:^27} │ {total_end:,>10} │ {total_change_pct:+8.1f}%")
        
        print()
        print("[캐시 플레이어 월간 추이] - 각 플랫폼별 최대 변동 3개 날짜")
        print()
        
        # 각 플랫폼별 캐시 상위 3개 변동 날짜 찾기
        cash_changes = {}
        for platform in platforms:
            values = data['cash'][platform]
            top3 = find_top3_changes(values, dates)
            cash_changes[platform] = {
                'start': values[0],
                'end': values[-1],
                'top3': top3,
                'total_change': ((values[-1] - values[0]) / values[0]) * 100 if values[0] > 0 else 0
            }
        
        # 캐시 헤더 출력
        print("플랫폼          │    시작     │             변화1           │             변화2           │             변화3           │    종료     │  총변화율")
        print("                │   (7/30)    │          (날짜별)           │          (날짜별)           │          (날짜별)           │   (8/10)    │")
        print("─" * 130)
        
        for platform in platforms:
            cc = cash_changes[platform]
            top3 = cc['top3']
            
            # 변화 날짜와 값 포맷팅
            change1 = f"{top3[0]['value']:,>8} ({top3[0]['date']})" if len(top3) > 0 else "N/A"
            change2 = f"{top3[1]['value']:,>8} ({top3[1]['date']})" if len(top3) > 1 else "N/A"
            change3 = f"{top3[2]['value']:,>8} ({top3[2]['date']})" if len(top3) > 2 else "N/A"
            
            print(f"{platform:15} │ {cc['start']:,>10} │ {change1:^27} │ {change2:^27} │ {change3:^27} │ {cc['end']:,>10} │ {cc['total_change']:+8.1f}%")
        
        # 캐시 전체 총합 계산
        total_cash = [sum(data['cash'][p][i] for p in platforms) for i in range(len(dates))]
        cash_top3 = find_top3_changes(total_cash, dates)
        cash_start = total_cash[0]
        cash_end = total_cash[-1]
        cash_total_change_pct = ((cash_end - cash_start) / cash_start) * 100
        
        # 캐시 전체 총합 행 출력
        change1_cash = f"{cash_top3[0]['value']:,>8} ({cash_top3[0]['date']})" if len(cash_top3) > 0 else "N/A"
        change2_cash = f"{cash_top3[1]['value']:,>8} ({cash_top3[1]['date']})" if len(cash_top3) > 1 else "N/A"
        change3_cash = f"{cash_top3[2]['value']:,>8} ({cash_top3[2]['date']})" if len(cash_top3) > 2 else "N/A"
        
        print("─" * 130)
        print(f"{'전체':15} │ {cash_start:,>10} │ {change1_cash:^27} │ {change2_cash:^27} │ {change3_cash:^27} │ {cash_end:,>10} │ {cash_total_change_pct:+8.1f}%")
        
        print()
        print("━" * 130)
        print()
        print("[전체 시장 합산 변화 요약]")
        print()
        
        # 온라인 전체 시장 변화 상세
        online_abs_change = total_end - total_start
        print(f"온라인 시장: {total_start:,}명 → {total_end:,}명 (변화: {online_abs_change:+,}명, {total_change_pct:+.1f}%)")
        
        # 캐시 전체 시장 변화 상세
        cash_abs_change = cash_end - cash_start
        print(f"캐시 시장:  {cash_start:,}명 → {cash_end:,}명 (변화: {cash_abs_change:+,}명, {cash_total_change_pct:+.1f}%)")
        
        print()
        print("━" * 130)
        print(f"월간 요약: 온라인 시장 {abs(total_change_pct):.1f}% 축소, 캐시 시장 {abs(cash_total_change_pct):.1f}% 축소")
        print(f"          각 플랫폼별 개별 최대 변동 날짜 상이, GGNetwork 상대적 안정성")
        print("=" * 130)

def main():
    """메인 실행"""
    reporter = FinalReports()
    
    print("\n")
    reporter.show_daily_report()
    
    print("\n\n")
    reporter.show_weekly_report()
    
    print("\n\n")
    reporter.show_monthly_report()
    
    print("\n")

if __name__ == "__main__":
    main()