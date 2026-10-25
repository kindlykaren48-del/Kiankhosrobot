#!/usr/bin/env python3
"""Arena-workspace backend for the content studio page.

Run: python3 studio_server.py [port]  (default 8123, bound to 0.0.0.0)

GET  /api/health                 Connection check used by the page
POST /api/generate               Save an order in studio_orders/ in this repo
GET  /api/orders                 List order summaries in the local queue
GET  /api/orders/<code>          Read one order by pickup code or full order id
POST /api/orders/<code>/status   Update pending/accepted/building/done/cancelled

When the page is opened from this Arena workspace (Live Preview), Generate
writes the complete settings directly into studio_orders/ and returns a short
pickup code such as ST-7K2P4. The agent reads that same queue with
studio_inbox.py; the public GitHub Pages copy has no backend and therefore
keeps its external form only as a backup path.
"""
import json
import os
import secrets
import sys
import threading
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlparse

ROOT = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(ROOT, "docs")
ORDERS = os.path.join(ROOT, "studio_orders")
MAX_BODY = 5_000_000
WRITE_LOCK = threading.Lock()
VALID_STATUSES = {"pending", "accepted", "building", "done", "cancelled"}
CODE_ALPHABET = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"


def normalize_code(code):
    value = str(code or "").strip().upper()
    value = value.translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789"))
    return value[3:] if value.startswith("ST-") else value


def load_orders():
    """Return [(path, data), ...] sorted by receive time / filename."""
    rows = []
    if not os.path.isdir(ORDERS):
        return rows
    for name in sorted(os.listdir(ORDERS)):
        if not name.endswith(".json") or name.startswith("."):
            continue
        path = os.path.join(ORDERS, name)
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            continue
        if isinstance(data, dict):
            rows.append((path, data))
    rows.sort(key=lambda row: (row[1].get("received_at", ""), row[1].get("order", "")))
    return rows


def order_summary(data):
    return {
        "order": data.get("order"),
        "pickup_code": data.get("pickup_code"),
        "status": data.get("status", "pending"),
        "topic": data.get("topic", ""),
        "title": data.get("title", ""),
        "fromList": bool(data.get("fromList")),
        "received_at": data.get("received_at"),
    }


def find_order(code):
    wanted = normalize_code(code)
    for path, data in load_orders():
        candidates = {
            normalize_code(data.get("pickup_code")),
            normalize_code(data.get("order")),
            str(data.get("order", "")).upper(),
        }
        if wanted and (wanted in candidates or str(code).strip().upper() in candidates):
            return path, data
    return None, None


def new_pickup_code(existing_rows):
    used = {normalize_code(data.get("pickup_code")) for _, data in existing_rows}
    while True:
        suffix = "".join(secrets.choice(CODE_ALPHABET) for _ in range(6))
        if suffix not in used:
            return f"ST-{suffix}"


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

    def _read_json(self):
        size = int(self.headers.get("Content-Length", 0))
        if size <= 0 or size > MAX_BODY:
            raise ValueError("bad length")
        raw = self.rfile.read(size)
        if len(raw) != size:
            raise ValueError("short body")
        data = json.loads(raw.decode("utf-8"))
        if not isinstance(data, dict):
            raise ValueError("bad payload")
        return data

    def do_GET(self):
        if self.path_only == "/api/health":
            return self._json(200, {
                "ok": True,
                "service": "studio",
                "mode": "arena-workspace",
                "queue": "studio_orders",
                "time": datetime.now().isoformat(timespec="seconds"),
            })
        if self.path_only == "/api/orders":
            return self._json(200, {
                "ok": True,
                "orders": [order_summary(data) for _, data in load_orders()],
            })
        if self.path_only.startswith("/api/orders/"):
            code = unquote(self.path_only.rsplit("/", 1)[-1])
            _, data = find_order(code)
            if data is None:
                return self._json(404, {"ok": False, "error": "order not found"})
            return self._json(200, {"ok": True, "order_data": data})
        return super().do_GET()

    def _find_client_order(self, client_id):
        if not client_id:
            return None
        for _, data in load_orders():
            if data.get("client_id") == client_id:
                return data
        return None

    def _update_status(self, code):
        try:
            payload = self._read_json()
            status = str(payload.get("status", "")).strip().lower()
            if status not in VALID_STATUSES:
                raise ValueError("bad status")
        except Exception:
            return self._json(400, {"ok": False, "error": "invalid status"})

        with WRITE_LOCK:
            path, data = find_order(code)
            if data is None:
                return self._json(404, {"ok": False, "error": "order not found"})
            data["status"] = status
            data["status_updated_at"] = datetime.now().isoformat(timespec="seconds")
            temp_path = path + ".tmp"
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(temp_path, path)
        return self._json(200, {"ok": True, "order": order_summary(data)})

    def do_POST(self):
        if self.path_only.startswith("/api/orders/") and self.path_only.endswith("/status"):
            code = unquote(self.path_only.split("/")[-2])
            return self._update_status(code)
        if self.path_only != "/api/generate":
            return self._json(404, {"ok": False, "error": "not found"})

        try:
            data = self._read_json()
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
                    "order": existing.get("order"),
                    "pickup_code": existing.get("pickup_code"),
                    "status": existing.get("status", "pending"),
                    "duplicate": True,
                })

            os.makedirs(ORDERS, exist_ok=True)
            existing_rows = load_orders()
            pickup_code = new_pickup_code(existing_rows)
            stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            code = f"ORD-{stamp}"
            path = os.path.join(ORDERS, code + ".json")
            suffix = 1
            while os.path.exists(path):
                suffix += 1
                code = f"ORD-{stamp}-{suffix}"
                path = os.path.join(ORDERS, code + ".json")

            data["order"] = code
            data["pickup_code"] = pickup_code
            data["status"] = "pending"
            data["source"] = "arena-studio"
            data["schema"] = 2
            data["received_at"] = datetime.now().isoformat(timespec="seconds")
            temp_path = path + ".tmp"
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(temp_path, path)

        print(
            f"[studio order] {pickup_code} ({code}): {str(data.get('topic', ''))[:60]}",
            flush=True,
        )
        return self._json(200, {
            "ok": True,
            "order": code,
            "pickup_code": pickup_code,
            "status": "pending",
        })


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8123
    print(f"Studio: http://0.0.0.0:{port} | workspace queue: {ORDERS}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
