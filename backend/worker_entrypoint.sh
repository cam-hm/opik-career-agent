#!/bin/bash
set -e

# Start a simple health check server in background (port 8080)
python -c "
import http.server
import socketserver
import threading

class HealthHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'OK')
    def log_message(self, format, *args):
        pass  # Suppress logging

PORT = int(__import__('os').environ.get('PORT', 8080))
with socketserver.TCPServer(('', PORT), HealthHandler) as httpd:
    httpd.serve_forever()
" &

# Wait a moment for health server to start
sleep 2

# Run the LiveKit Agent (as module)
python -m app.agents.server start
