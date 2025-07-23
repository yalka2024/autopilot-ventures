
from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            "app": "AutoPilot Ventures Platform",
            "status": "operational",
            "deployed": "2025-07-23T02:38:43.629197",
            "endpoints": ["/health", "/status"]
        }
        
        self.wfile.write(json.dumps(response).encode())
        return
