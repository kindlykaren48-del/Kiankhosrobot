#!/usr/bin/env python3
"""Read and manage studio orders saved in this Arena workspace.

Examples:
  python3 studio_inbox.py list
  python3 studio_inbox.py latest
  python3 studio_inbox.py show ST-7K2P4
  python3 studio_inbox.py status ST-7K2P4 building
  python3 studio_inbox.py status ST-7K2P4 done
"""
import argparse
import json
import os
import sys
from datetime import datetime

import studio_server as studio


def fa_status(status):
    return {
        "pending": "در انتظار ساخت",
        "accepted": "برداشته‌شده",
        "building": "در حال ساخت",
        "done": "ساخته‌شده",
        "cancelled": "لغوشده",
    }.get(status, status)


def topic_of(data):
    if data.get("fromList"):
        return "عنوان بعدی از لیست"
    return data.get("title") or data.get("topic") or "—"


def print_summary(data):
    print(f"{data.get('pickup_code') or '—'}\t{fa_status(data.get('status', 'pending'))}\t"
          f"{data.get('received_at', '')}\t{topic_of(data)[:80]}")


def get_or_exit(code):
    path, data = studio.find_order(code)
    if data is None:
        print(f"سفارشی با کد {code} در صف این محیط کاری پیدا نشد.", file=sys.stderr)
        raise SystemExit(2)
    return path, data


def cmd_list(args):
    rows = studio.load_orders()
    shown = 0
    for _, data in rows:
        if not args.all and data.get("status", "pending") in {"done", "cancelled"}:
            continue
        print_summary(data)
        shown += 1
    if not shown:
        print("صف سفارش‌های باز خالی است.")


def cmd_latest(args):
    rows = [row for row in studio.load_orders()
            if row[1].get("status", "pending") not in {"done", "cancelled"}]
    if not rows:
        print("سفارش بازی در صف نیست.")
        return
    _, data = rows[-1] if args.newest else rows[0]
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print_summary(data)
        if data.get("text"):
            print("\n" + data["text"])


def cmd_show(args):
    path, data = get_or_exit(args.code)
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return
    print_summary(data)
    print(f"کد کامل: {data.get('order')}")
    print(f"فایل: {path}")
    if data.get("text"):
        print("\n" + data["text"])
    else:
        print("\n" + json.dumps(data, ensure_ascii=False, indent=2))


def cmd_status(args):
    if args.status not in studio.VALID_STATUSES:
        print("وضعیت مجاز: pending, accepted, building, done, cancelled", file=sys.stderr)
        raise SystemExit(2)
    path, data = get_or_exit(args.code)
    data["status"] = args.status
    data["status_updated_at"] = datetime.now().isoformat(timespec="seconds")
    temp_path = path + ".tmp"
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(temp_path, path)
    print_summary(data)


def main():
    parser = argparse.ArgumentParser(description="صف سفارش‌های استودیو در همین محیط کاری")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("list", help="فهرست سفارش‌های باز")
    p.add_argument("--all", action="store_true", help="نمایش سفارش‌های تمام‌شده هم")
    p.set_defaults(fn=cmd_list)

    p = sub.add_parser("latest", help="قدیمی‌ترین سفارش باز؛ با --newest تازه‌ترین")
    p.add_argument("--newest", action="store_true")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_latest)

    p = sub.add_parser("show", help="نمایش کامل یک سفارش با کد کوتاه")
    p.add_argument("code")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_show)

    p = sub.add_parser("status", help="تغییر وضعیت سفارش")
    p.add_argument("code")
    p.add_argument("status", choices=sorted(studio.VALID_STATUSES))
    p.set_defaults(fn=cmd_status)

    args = parser.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
