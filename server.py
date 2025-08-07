import http.server
import socketserver
import json
import pathlib
import os
import signal
import sys
import time

PORT = 8500
BASE_DIR = pathlib.Path(__file__).resolve().parent

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/data':
            file_path = BASE_DIR / 'test_results.json'
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

    def do_POST(self):
        if self.path == '/data':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data)
                print(f"Received data: {data}")

                # Save the data to test_results.json
                file_path = BASE_DIR / 'test_results.json'
                if file_path.exists():
                    with file_path.open('r') as f:
                        results = json.load(f)
                else:
                    results = []

                results.append(data)

                with file_path.open('w') as f:
                    json.dump(results, f, indent=2)

                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"Data saved successfully")
            except Exception as e:
                print(f"Error processing POST request: {e}")
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b"Internal Server Error")

def find_and_kill_existing_process(port):
    #Find and kill any process using the specified port.
    try:
        result = os.popen(f"sudo netstat -tuln | grep :{port}").read()
        if result:
            pid = int(result.split()[-1].split('/')[0])
            print(f"Port {port} is in use by PID {pid}. Killing it...")
            os.kill(pid, signal.SIGKILL)
            print(f"Process {pid} killed successfully.")
    except Exception as e:
        print(f"Failed to kill process on port {port}: {e}")

def signal_handler(sig, frame):
    #Handle graceful shutdown on SIGINT or SIGTERM
    print("\nShutting down server gracefully...")
    sys.exit(0)

def start_server():
    #Start the server with retries if the port is still in use.
    retries = 3
    for attempt in range(retries):
        try:
            with socketserver.TCPServer(('', PORT), Handler) as httpd:
                print(f"Serving on port {PORT}")
                try:
                    httpd.serve_forever()
                except KeyboardInterrupt:
                    print("\nServer interrupted by user.")
                finally:
                    print("Server shutting down...")
                    httpd.server_close()
                break
        except OSError as e:
            if "Address already in use" in str(e):
                print(f"Port {PORT} is still in use. Retrying... ({attempt + 1}/{retries})")
                find_and_kill_existing_process(PORT)
                time.sleep(1) #wait to retry again
            else:
                raise
    else:
        print(f"Failed to start the server after {retries} attempts. Exiting.")
        sys.exit(1)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # If the port is already in use then kill
    find_and_kill_existing_process(PORT)

    os.chdir(BASE_DIR)
    start_server()
