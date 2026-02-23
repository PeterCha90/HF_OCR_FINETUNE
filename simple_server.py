import http.server
import json
import os
import sys
from urllib.parse import urlparse

PORT = 8000
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'dataset', 'jsonl', 'results_with_QA.jsonl')

class OCRHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/api/data':
            if not os.path.exists(DATA_FILE):
                self._send_response(404, {"error": "File not found"})
                return

            data = []
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        data.append(json.loads(line))
            self._send_response(200, data)
        elif self.path == '/':
            self.path = '/templates/index.html'
            return super().do_GET()
        else:
            return super().do_GET()

    def do_POST(self):
        if self.path == '/api/save':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            req = json.loads(post_data)
            
            index = req.get('index')
            updated_entry = req.get('data')
            
            if index is None or updated_entry is None:
                self._send_response(400, {"success": False, "message": "Invalid data"})
                return

            all_data = []
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        all_data.append(json.loads(line))
            
            if 0 <= index < len(all_data):
                all_data[index] = updated_entry
                with open(DATA_FILE, 'w', encoding='utf-8') as f:
                    for entry in all_data:
                        f.write(json.dumps(entry, ensure_ascii=False) + '\n')
                self._send_response(200, {"success": True})
            else:
                self._send_response(404, {"success": False, "message": "Index out of range"})

    def _send_response(self, code, data):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

if __name__ == '__main__':
    print(f"Starting server at http://localhost:{PORT}")
    print(f"Reading from: {DATA_FILE}")
    http.server.HTTPServer(('', PORT), OCRHandler).serve_forever()
