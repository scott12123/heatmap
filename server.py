import http.server
import socketserver
import json
import pathlib

PORT = 8500

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/data':
            file_path = pathlib.Path('/home/pi/test_results.json')
            if file_path.exists():
                try:
                    with file_path.open() as f:
                        data = json.load(f)
                except Exception:
                    data = []
            else:
                data = []
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
        else:
            if self.path == '/':
                self.path = '/index.html'
            return http.server.SimpleHTTPRequestHandler.do_GET(self)

if __name__ == '__main__':
    with socketserver.TCPServer(('', PORT), Handler) as httpd:
        print(f'Serving on port {PORT}')
        httpd.serve_forever()
