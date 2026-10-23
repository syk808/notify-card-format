"""Run from the repo root:  python examples/demo.py"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from notify_card import bj_time, card, money, parse, pct  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")   # Windows consoles

cards = [
    card("异动", "ABC", "15 分钟涨 " + pct(18.2),
         nums=["现价 0.1234", "成交额 " + money(2_530_000), "持仓量 " + money(41_000_000)],
         todo="不追，回踩 0.11 附近再看", link="https://example.com/abc"),
    card("日历", "XYZ", "代币解锁 %s" % bj_time(time.time() + 86400),
         nums=["解锁 " + money(12_500_000), "占流通 4.1%"], todo="解锁前 1 小时复查"),
    card("故障", "price-feed", "30 分钟没有新数据", todo="检查数据源"),
    card("机会", "DEF", "白名单开放", todo="10-25 前登记（风险：需要 KYC）", update=True),
]

for c in cards:
    print(c)
    print("-" * 30)

print("parsed:", parse(cards[-1]))
