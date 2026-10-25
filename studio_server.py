#!/usr/bin/env python3
"""Local/direct backend for the content studio page.

Run: python3 studio_server.py [port]  (default 8123, bound to 0.0.0.0)
GET  /api/health    Direct-submission health check used by the page
POST /api/generate  Save an order JSON in studio_orders/ and return its code
GET  /api/orders    List saved order codes

The public GitHub Pages copy is static, so the page detects that this API is
absent and uses its no-message GitHub order form instead. When this server is
the page origin, Generate submits directly to the queue.
"""
import json
import os
import sys
import threading
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(ROOT, "docs")
ORDERS = os.path.join(ROOT, "studio_orders")
MAX_BODY = 5_000_000
WRITE_LOCK = threading.Lock()


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DOCS, **kwargs)

    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def end_headers(self):
        # The studio changes independently of browser cache; always revalidate.
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    @property
    def path_only(self):
        return urlparse(self.path).path.rstrip("/") or "/"

    def _json(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path_only == "/api/health":
            return self._json(200, {
                "ok": True,
                "service": "studio",
                "time": datetime.now().isoformat(timespec="seconds"),
            })
        if self.path_only == "/api/orders":
            names = []
            if os.path.isdir(ORDERS):
                names = sorted(
                    name[:-5]
                    for name in os.listdir(ORDERS)
                    if name.endswith(".json") and not name.startswith(".")
                )
            return self._json(200, {"ok": True, "orders": names})
        return super().do_GET()

    def _find_client_order(self, client_id):
        if not client_id or not os.path.isdir(ORDERS):
            return None
        for name in sorted(os.listdir(ORDERS)):
            if not name.endswith(".json") or name.startswith("."):
                continue
            try:
                with open(os.path.join(ORDERS, name), encoding="utf-8") as f:
                    existing = json.load(f)
            except Exception:
                continue
            if existing.get("client_id") == client_id:
                return existing.get("order") or name[:-5]
        return None

    def do_POST(self):
        if self.path_only != "/api/generate":
            return self._json(404, {"ok": False, "error": "not found"})

        try:
            size = int(self.headers.get("Content-Length", 0))
            if size <= 0 or size > MAX_BODY:
                raise ValueError("bad length")
            raw = self.rfile.read(size)
            if len(raw) != size:
                raise ValueError("short body")
            data = json.loads(raw.decode("utf-8"))
            if not isinstance(data, dict):
                raise ValueError("bad payload")
            client_id = data.get("client_id")
            if client_id is not None and (
                not isinstance(client_id, str) or len(client_id) > 120
            ):
                raise ValueError("bad client id")
        except Exception:
            return self._json(400, {"ok": False, "error": "invalid order"})

        with WRITE_LOCK:
            existing = self._find_client_order(data.get("client_id"))
            if existing:
                return self._json(200, {
                    "ok": True,
                    "order": existing,
                    "duplicate": True,
                })

            os.makedirs(ORDERS, exist_ok=True)
            stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            code = f"ORD-{stamp}"
            path = os.path.join(ORDERS, code + ".json")
            suffix = 1
            while os.path.exists(path):
                suffix += 1
                code = f"ORD-{stamp}-{suffix}"
                path = os.path.join(ORDERS, code + ".json")

            data["order"] = code
            data["received_at"] = datetime.now().isoformat(timespec="seconds")
            temp_path = path + ".tmp"
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(temp_path, path)

        print(
            f"[new order] {code}: {str(data.get('topic', ''))[:60]}",
            flush=True,
        )
        return self._json(200, {"ok": True, "order": code})


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8123
    print(f"Studio: http://0.0.0.0:{port} | orders: {ORDERS}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
