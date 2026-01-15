#!/usr/bin/env python3
"""
Reverse proxy for Azure Container Apps with VNet-only ingress.
Adds the correct Host header to bypass the 404 "Unavailable" error.

Usage:
    python proxy.py [--port 8888] [--target https://container-app-agent.blackocean-8676cbc4.eastus2.azurecontainerapps.io]

Then forward port 8888 via VS Code Port Forwarding and access http://localhost:8888
"""

import argparse
import ssl
import urllib.request
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler


class ProxyHandler(BaseHTTPRequestHandler):
    target_url = None

    def do_GET(self):
        self.proxy()

    def do_POST(self):
        self.proxy()

    def do_HEAD(self):
        self.proxy()

    def do_PUT(self):
        self.proxy()

    def do_DELETE(self):
        self.proxy()

    def do_OPTIONS(self):
        self.proxy()

    def proxy(self):
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            url = self.target_url + self.path
            content_len = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_len) if content_len > 0 else None

            req = urllib.request.Request(url, data=body, method=self.command)
            for k, v in self.headers.items():
                if k.lower() not in ["host", "content-length"]:
                    req.add_header(k, v)

            with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
                self.send_response(resp.status)
                for k, v in resp.headers.items():
                    if k.lower() not in ["transfer-encoding", "connection"]:
                        self.send_header(k, v)
                self.end_headers()
                self.wfile.write(resp.read())
        except Exception as e:
            self.send_error(502, str(e))

    def log_message(self, format, *args):
        print(f"{self.address_string()} - {format % args}")


def main():
    parser = argparse.ArgumentParser(description="Reverse proxy for Azure Container Apps")
    parser.add_argument(
        "--port",
        type=int,
        default=8888,
        help="Port to listen on (default: 8888)",
    )
    parser.add_argument(
        "--target",
        type=str,
        default="https://container-app-agent.blackocean-8676cbc4.eastus2.azurecontainerapps.io",
        help="Target Container App URL",
    )
    args = parser.parse_args()

    ProxyHandler.target_url = args.target

    print(f"Proxy running on http://0.0.0.0:{args.port}")
    print(f"Forwarding to: {args.target}")
    print("Use VS Code Port Forwarding to access from your laptop")

    server = ThreadingHTTPServer(("0.0.0.0", args.port), ProxyHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()
