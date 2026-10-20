#!/usr/bin/env python3
"""ساخت ریل‌های بانک: python3 reels/build.py [slug ...]"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reel_engine as E          # noqa: E402
from topics_5 import TOPICS, with_audio   # noqa: E402

wanted = sys.argv[1:]
for t in TOPICS:
    if wanted and t["slug"] not in wanted:
        continue
    cfg = with_audio(t)
    missing = [a for a in cfg["audio"] if not os.path.isfile(a)]
    if missing:
        print(f"[×] {cfg['slug']}: نریشن ناقص -> {[os.path.basename(m) for m in missing]}")
        continue
    E.render(cfg)
