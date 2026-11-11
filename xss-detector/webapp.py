"""XSS EMBER · 反射型 XSS 检测控制台（Web 后端）。

标准库实现（零额外依赖）：静态页面 + JSON 接口 + SSE 流式进度。
只绑定回环地址。

    .\\venv\\Scripts\\python.exe .\\xss_injection_tool\\webapp.py
    .\\venv\\Scripts\\python.exe .\\xss_injection_tool\\webapp.py --port 8849 --open
"""

from __future__ import annotations

import argparse
import json
import os
import queue
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR / "web"
OUT_DIR = BASE_DIR / "out"

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import engine  # noqa: E402
import payloads  # noqa: E402
import xsscan  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # pragma: no cover
    pass

BUSY_LOCK = threading.Lock()
CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon",
    ".json": "application/json; charset=utf-8",
    ".md": "text/markdown; charset=utf-8",
}


def load_env_file() -> None:
    env_path = BASE_DIR / ".env"
    if not env_path.exists():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip().lstrip("\ufeff")
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def as_float(value: str | None, default: float, low: float, high: float) -> float:
    try:
        return max(low, min(high, float(value if value is not None else default)))
    except (TypeError, ValueError):
        return default


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "XssEmber/1.0"

    def log_message(self, fmt: str, *args) -> None:
        if args and str(args[1]).startswith(("4", "5")):
            sys.stderr.write("[web] %s %s\n" % (self.address_string(), fmt % args))

    # ── 基础响应 ──
    def send_bytes(self, body: bytes, status: int = 200, content_type: str = "text/plain; charset=utf-8") -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def send_json(self, payload: dict, status: int = 200) -> None:
        self.send_bytes(
            json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            status,
            "application/json; charset=utf-8",
        )

    def send_file(self, path: Path) -> None:
        if not path.is_file():
            self.send_json({"error": f"文件不存在：{path.name}"}, 404)
            return
        ctype = CONTENT_TYPES.get(path.suffix.lower(), "application/octet-stream")
        self.send_bytes(path.read_bytes(), 200, ctype)

    # ── SSE ──
    def start_sse(self, worker) -> None:
        events: queue.Queue = queue.Queue()

        def emit(event: dict) -> None:
            events.put(event)

        def runner() -> None:
            try:
                worker(emit)
            except Exception as exc:  # noqa: BLE001
                emit({"type": "error", "message": f"{type(exc).__name__}: {exc}"})
            finally:
                events.put({"type": "__end__"})

        threading.Thread(target=runner, daemon=True).start()

        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache, no-transform")
        self.send_header("Connection", "keep-alive")
        self.send_header("X-Accel-Buffering", "no")
        self.send_header("Transfer-Encoding", "chunked")
        self.end_headers()

        def write_chunk(text: str) -> None:
            data = text.encode("utf-8")
            self.wfile.write(f"{len(data):X}\r\n".encode("ascii") + data + b"\r\n")
            self.wfile.flush()

        try:
            write_chunk(": connected\n\n")
            while True:
                event = events.get()
                if event.get("type") == "__end__":
                    write_chunk('data: {"type": "end"}\n\n')
                    break
                write_chunk("data: " + json.dumps(event, ensure_ascii=False) + "\n\n")
            self.wfile.write(b"0\r\n\r\n")
            self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception as exc:  # pragma: no cover
            sys.stderr.write(f"[web] SSE 中断：{exc}\n")
        finally:
            self.close_connection = True

    # ── 路由 ──
    def do_GET(self) -> None:  # noqa: N802
        parts = urlsplit(self.path)
        route = unquote(parts.path)
        query = parse_qs(parts.query)

        if route in ("/", "/index.html"):
            self.send_file(WEB_DIR / "index.html")
            return

        if route.startswith("/assets/"):
            candidate = (WEB_DIR / route[len("/assets/") :]).resolve()
            if WEB_DIR.resolve() not in candidate.parents:
                self.send_json({"error": "非法路径"}, 400)
                return
            self.send_file(candidate)
            return

        if route.startswith("/report/"):
            candidate = (OUT_DIR / route[len("/report/") :]).resolve()
            if OUT_DIR.resolve() not in candidate.parents:
                self.send_json({"error": "非法路径"}, 400)
                return
            self.send_file(candidate)
            return

        if route == "/api/defaults":
            self.send_json(
                {
                    "url": os.getenv("XSS_TARGET", ""),
                    "cookie": os.getenv("XSS_COOKIE", ""),
                    "cookiePresent": bool(os.getenv("XSS_COOKIE", "")),
                    "timeout": 10,
                    "stages": [{"key": k, "label": v} for k, v in xsscan.STAGES],
                    "matrixCount": len(payloads.BYPASS_MATRIX),
                }
            )
            return

        if route == "/api/health":
            self.send_json({"ok": True, "busy": BUSY_LOCK.locked()})
            return

        if route == "/api/scan":
            self.handle_scan(query)
            return

        self.send_json({"error": "not found"}, 404)

    def handle_scan(self, query: dict[str, list[str]]) -> None:
        def one(key: str, default: str = "") -> str:
            values = query.get(key)
            return values[0] if values else default

        url = engine.strip_fragment(one("url") or os.getenv("XSS_TARGET", ""))
        cookie = one("cookie", None) if "cookie" in query else os.getenv("XSS_COOKIE", "")
        timeout = as_float(one("timeout") or None, 10.0, 1.0, 60.0)
        force_bypass = one("full") in ("1", "true", "yes")
        skip_bypass = one("nobypass") in ("1", "true", "yes")
        only = [p.strip() for p in one("param").split(",") if p.strip()]

        if not url:
            self.send_json({"error": "缺少目标 URL"}, 400)
            return

        params = engine.parse_params(url)
        if not params:
            self.send_json({"error": "目标 URL 没有 GET 参数"}, 400)
            return
        if only:
            params = [(n, v) for n, v in params if n in only] or params

        if not BUSY_LOCK.acquire(blocking=False):
            self.send_json({"error": "已有任务在运行，请等当前任务结束"}, 429)
            return

        def worker(emit) -> None:
            try:
                xsscan.run_scan(
                    url=url,
                    params=params,
                    cookie=cookie,
                    timeout=timeout,
                    force_bypass=force_bypass,
                    skip_bypass=skip_bypass,
                    out_dir=OUT_DIR,
                    emit=emit,
                )
            finally:
                BUSY_LOCK.release()

        self.start_sse(worker)


def main() -> int:
    parser = argparse.ArgumentParser(description="XSS EMBER 控制台")
    parser.add_argument("--host", default="127.0.0.1", help="监听地址（默认仅回环）")
    parser.add_argument("--port", type=int, default=8849, help="监听端口（默认 8849）")
    parser.add_argument("--open", action="store_true", help="启动后自动打开浏览器")
    args = parser.parse_args()

    load_env_file()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    url = f"http://{args.host}:{args.port}/"
    print("=" * 62)
    print("  XSS EMBER · 反射型 XSS 检测控制台")
    print(f"  界面：{url}")
    print(f"  目标：{os.getenv('XSS_TARGET', '(未配置)')}")
    print(f"  Cookie：{'已载入 .env' if os.getenv('XSS_COOKIE') else '(空)'}")
    print("  只使用 alert(1) 做判定；Ctrl+C 退出")
    print("=" * 62)

    if args.open:
        threading.Timer(0.7, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[web] 已停止")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
