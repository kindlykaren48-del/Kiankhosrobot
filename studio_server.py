#!/usr/bin/env python3
"""سرور استودیو تولید محتوا — سرو صفحه (docs/) + ثبت سفارش‌های دکمهٔ «جنریت».

اجرا:  python3 studio_server.py [port]     (پیش‌فرض ۸۱۲۳، روی 0.0.0.0)
GET  /              → صفحهٔ استودیو (docs/index.html)
POST /api/generate  → ذخیرهٔ سفارش JSON در studio_orders/ و برگرداندن کد سفارش
GET  /api/orders    → فهرست کد سفارش‌های ثبت‌شده (برای برداشتن از صف تولید)

سفارش‌های ثبت‌شده در صف تولید قرار می‌گیرند و طبق روش قفل‌شده ساخته
و در گوگل درایو دکتر تحویل داده می‌شوند (نگاه کنید به reels/INDEX.md).
"""
import json
import os
import sys
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(ROOT, "docs")
ORDERS = os.path.join(ROOT, "studio_orders")


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=DOCS, **kw)

    def log_message(self, fmt, *args):  # لاگ خلاصه
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _json(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.rstrip("/") == "/api/orders":
            names = []
            if os.path.isdir(ORDERS):
                names = sorted(f[:-5] for f in os.listdir(ORDERS)
                               if f.endswith(".json"))
            return self._json(200, {"ok": True, "orders": names})
        return super().do_GET()

    def do_POST(self):
        if self.path.rstrip("/") != "/api/generate":
            return self._json(404, {"ok": False, "error": "not found"})
        try:
            n = int(self.headers.get("Content-Length", 0))
            if n <= 0 or n > 200_000:
                raise ValueError("bad length")
            data = json.loads(self.rfile.read(n).decode("utf-8"))
            if not isinstance(data, dict):
                raise ValueError("bad payload")
        except Exception:
            return self._json(400, {"ok": False, "error": "invalid order"})
        os.makedirs(ORDERS, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        code = f"ORD-{stamp}"
        path = os.path.join(ORDERS, code + ".json")
        n_try = 1
        while os.path.exists(path):  # دو سفارش در یک ثانیه
            n_try += 1
            code = f"ORD-{stamp}-{n_try}"
            path = os.path.join(ORDERS, code + ".json")
        data["order"] = code
        data["received_at"] = datetime.now().isoformat(timespec="seconds")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[سفارش جدید] {code}: {str(data.get('topic', ''))[:60]}", flush=True)
        return self._json(200, {"ok": True, "order": code})


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8123
    print(f"استودیو روی http://0.0.0.0:{port} بالا آمد؛ سفارش‌ها در {ORDERS}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
