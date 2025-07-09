import http.server
import socketserver
import json
import pathlib
import os
import signal
import sys

PORT = 8500
BASE_DIR = pathlib.Path('/home/pi/heatmap')  # Base directory for the server

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/data':
            file_path = pathlib.Path('test_results.json')
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
            # Serve static files (e.g., index.html)
            if self.path == '/':
                self.path = '/index.html'
            self.path = str(BASE_DIR / self.path.lstrip('/'))
            return http.server.SimpleHTTPRequestHandler.do_GET(self)

def find_and_kill_existing_process(port):
    """Find and kill any process using the specified port."""
    try:
        # Find the process using the port
        result = os.popen(f"sudo netstat -tuln | grep :{port}").read()
        if result:
            pid = int(result.split()[-1].split('/')[0])  # Extract the PID
            print(f"Port {port} is in use by PID {pid}. Killing it...")
            os.kill(pid, signal.SIGKILL)
            print(f"Process {pid} killed successfully.")
    except Exception as e:
        print(f"Failed to kill process on port {port}: {e}")

def signal_handler(sig, frame):
    """Handle graceful shutdown on SIGINT or SIGTERM."""
    print("\nShutting down server gracefully...")
    sys.exit(0)

if __name__ == '__main__':
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Check if the port is already in use and kill the process if necessary
    find_and_kill_existing_process(PORT)

    # Start the server
    with socketserver.TCPServer(('', PORT), Handler) as httpd:
        print(f"Serving on port {PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer interrupted by user.")
        finally:
            print("Server shutting down...")
            httpd.server_close()
