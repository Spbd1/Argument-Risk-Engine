def run(app_path: str, host: str = '127.0.0.1', port: int = 8000, reload: bool = False):
    import http.server
    import json
    import socketserver

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/health':
                self.send_response(200); self.send_header('Content-Type','application/json'); self.end_headers(); self.wfile.write(json.dumps({'status':'ok'}).encode())
            else:
                self.send_response(200); self.send_header('Content-Type','application/json'); self.end_headers(); self.wfile.write(json.dumps({'message':'Argument-Risk-Engine API MVP'}).encode())
        def log_message(self, *args):
            return

    with socketserver.TCPServer((host, port), Handler) as httpd:
        print(f'Backend: http://{host}:{port}')
        httpd.serve_forever()
