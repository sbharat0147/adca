import http.server
import socketserver
import json
import random
import datetime

# Dummy data for testing
dummy_data = [
    {"id": 1, "name": "John"},
    {"id": 2, "name": "Alice"},
    {"id": 3, "name": "Bob"},
    {"id": 4, "name": "Eve"},
]

# Define a function to generate random data
def generate_random_data():
    return random.choice(dummy_data)

# Define a function to generate a fake timestamp
def get_fake_timestamp():
    now = datetime.datetime.now()
    return now.strftime("%d-%m-%Y %H:%M:%S")

class FakeAPIRequestHandler(http.server.BaseHTTPRequestHandler):
    def _send_response(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        request_data = json.loads(post_data)

        # Generate fake response data
        response_data = {
            "table_name": request_data.get("table_name"),
            "response_time": get_fake_timestamp(),
            "data": [generate_random_data() for _ in range(request_data.get("page_size", 10))],
            "total": len(dummy_data),
            "page_size": request_data.get("page_size"),
            "page_number": request_data.get("page_number")
        }

        self._send_response(200, response_data)

    def do_GET(self):
        self.send_response(404)
        self.end_headers()

def run_fake_api():
    with socketserver.TCPServer(('localhost', 1006), FakeAPIRequestHandler) as httpd:
        print("Fake API server is running on port 1006")
        httpd.serve_forever()

# if __name__ == '__main__':
#     run_fake_api()
