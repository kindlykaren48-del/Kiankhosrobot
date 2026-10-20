#!/usr/bin/env python3
"""ساخت کاروسل‌ها: python3 reels/build_carousels.py [slug ...]"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import carousel_engine as C       # noqa: E402
from carousels import CAROUSELS   # noqa: E402

wanted = sys.argv[1:]
for c in CAROUSELS:
    if wanted and c["slug"] not in wanted:
        continue
    C.build(c)
