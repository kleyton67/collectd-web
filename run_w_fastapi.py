#!/usr/bin/env python3

import http.server
import argparse
from dotenv import load_dotenv
import os
import base64
import binascii

load_dotenv()

DEFAULT_HOST = os.getenv("HOST", "0.0.0.0")
DEFAULT_PORT = int(os.getenv("PORT", 8888))


class Handler(http.server.CGIHTTPRequestHandler):
    cgi_directories = ["/cgi-bin"]

    def check_auth(self):
        auth_header = self.headers.get('Authorization')
        if not auth_header:
            return False
        
        # Parse Authorization header
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'basic':
            return False

        # Decode base64 credentials
        try:
            decoded = base64.b64decode(parts[1]).decode('utf-8')
        except (binascii.Error, UnicodeDecodeError):
            return False

        # Split into username/password
        try:
            username, password = decoded.split(':', 1)
        except ValueError:
            return False

        # Get expected credentials
        expected_user = os.getenv("AUTH_USER")
        expected_pass = os.getenv("AUTH_PASSWORD")
        
        if not expected_user or not expected_pass:
            self.log_error("Server error: Missing authentication credentials")
            return False
            
        return username == expected_user and password == expected_pass

    def send_auth_required(self):
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm="Login Required"')
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'<h1>401 Unauthorized</h1>')

    def do_GET(self):
        if not self.check_auth():
            self.send_auth_required()
            return
        super().do_GET()

    def do_HEAD(self):
        if not self.check_auth():
            self.send_auth_required()
            return
        super().do_HEAD()

    def do_POST(self):
        if not self.check_auth():
            self.send_auth_required()
            return
        super().do_POST()

def main():
    parser = argparse.ArgumentParser(
        description="Start a CGI-capable web server with authentication."
    )
    parser.add_argument(
        "host",
        nargs="?",
        default=DEFAULT_HOST,
        help="Hostname or IP address to bind to (default: %(default)s)"
    )
    parser.add_argument(
        "port",
        nargs="?",
        type=int,
        default=DEFAULT_PORT,
        help="Port number to listen on (default: %(default)s)"
    )
    args = parser.parse_args()

    # Validate credentials
    if not os.getenv("AUTH_USER") or not os.getenv("AUTH_PASSWORD"):
        print("Error: AUTH_USER and AUTH_PASSWORD must be set in environment")
        return

    with http.server.HTTPServer((args.host, args.port), Handler) as httpd:
        print(f"Protected server running at http://{args.host}:{args.port}/")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")
            httpd.server_close()


if __name__ == "__main__":
    main()