"""
Static file server for test_websites/.
Serves the entire workspace root at http://localhost:5500
so that http://localhost:5500/test_websites/site1_contact/index.html works.

No WebSocket / LiveReload injection — pure static files, zero auto-refresh.

Usage:
    python scripts/serve.py          # default port 5500
    python scripts/serve.py 8080     # custom port
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

# ── Configuration ──────────────────────────────────────────────────────────────
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 5500
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent   # project root

# ── Custom handler ─────────────────────────────────────────────────────────────
class _Handler(http.server.SimpleHTTPRequestHandler):
    """Serve files from WORKSPACE_ROOT; log only errors."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WORKSPACE_ROOT), **kwargs)

    def log_message(self, fmt, *args):          # suppress access log spam
        code = args[1] if len(args) > 1 else ""
        if str(code).startswith(("4", "5")):    # only log errors
            super().log_message(fmt, *args)

    def end_headers(self):
        # Disable caching so browsers always load the latest file
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Pragma", "no-cache")
        super().end_headers()

# ── Server ─────────────────────────────────────────────────────────────────────
class _ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


def main():
    os.chdir(WORKSPACE_ROOT)
    with _ReusableTCPServer(("", PORT), _Handler) as httpd:
        print(f"[serve.py] Serving {WORKSPACE_ROOT}")
        print(f"[serve.py] Listening at http://localhost:{PORT}")
        print(f"[serve.py] Test sites:")
        for i in range(1, 6):
            names = ["site1_contact", "site2_booking", "site3_register",
                     "site4_search", "site5_feedback"]
            print(f"           http://localhost:{PORT}/test_websites/{names[i-1]}/index.html")
        print("[serve.py] Press Ctrl+C to stop.\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[serve.py] Server stopped.")


if __name__ == "__main__":
    main()
