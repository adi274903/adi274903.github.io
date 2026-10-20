#!/usr/bin/env python3
"""Preview server: serves dist/ and POST /api/ask -> the SmolLM2-135M record harness.
Run with the chatbot venv:  ../smollm_chatbot/.venv/bin/python serve.py [port]"""
import json, pathlib, sys, threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "smollm_chatbot"))
import harness  # noqa: E402

H = harness.Harness()
LOCK = threading.Lock()          # one generation at a time on the CPU model


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(HERE / "dist"), **k)

    def do_POST(self):
        if self.path != "/api/ask":
            return self.send_error(404)
        try:
            n = min(int(self.headers.get("Content-Length", 0)), 2000)
            q = json.loads(self.rfile.read(n) or b"{}").get("q", "").strip()[:300]
            if not q:
                raise ValueError("empty")
            with LOCK:
                a, t = H.ask(q)
            body = json.dumps({"answer": a, "route": t["route"], "source": t.get("source"), "guard": t["guard"], "links": t.get("links")})
            code = 200
        except Exception as ex:
            body, code = json.dumps({"error": str(ex)}), 400
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body.encode())))
        self.end_headers()
        self.wfile.write(body.encode())

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8770
    print(f"serving dist/ + /api/ask on http://127.0.0.1:{port}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
