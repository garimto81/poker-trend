#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run backfill for testing
"""

import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from daily_scheduler import DailyScheduler

def main():
    print("📅 백필 데이터 수집 시작...")
    scheduler = DailyScheduler()
    
    # Backfill last 5 days for testing
    scheduler.backfill_data(5)
    
    print("\n📊 백필 완료 후 상태:")
    scheduler.show_status()

if __name__ == "__main__":
    main()