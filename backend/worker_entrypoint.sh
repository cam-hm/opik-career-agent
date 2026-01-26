#!/bin/bash
set -e

echo "=== LiveKit Agent Worker Starting ==="
echo "Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"

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

# ============================================
# WARMUP: Pre-load ML models before agent starts
# This prevents timeout during first job assignment
# ============================================
echo "=== Warming up ML models ==="
python -c "
import time
start = time.time()

print('Loading Silero VAD model...')
from livekit.plugins import silero
vad = silero.VAD.load()
print(f'Silero VAD loaded in {time.time() - start:.2f}s')

# Verify model is functional
print('VAD model ready!')
"
echo "=== Warmup complete ==="

# Run the LiveKit Agent (as module)
echo "=== Starting LiveKit Agent Server ==="
python -m app.agents.server start
