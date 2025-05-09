import os
import threading
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler

import requests


class TestHTTPRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/test-404":
            self.send_error(404)
        else:
            return SimpleHTTPRequestHandler.do_GET(self)


def start_server(port=8090):
    try:
        os.chdir("docs")
        server_address = ("", port)
        httpd = HTTPServer(server_address, TestHTTPRequestHandler)
        print(f"Starting server on port {port}...")
        return httpd
    except Exception as e:
        print(f"Error starting server: {e}")
        return None


def test_404():
    # Start server
    server = start_server()
    if not server:
        print("Failed to start server")
        return

    try:
        # Test 404 page
        response = requests.get(f"http://localhost:{server.server_port}/test-404")
        if response.status_code == 404:
            print("✅ 404 status code test passed")
        else:
            print(f"❌ 404 status code test failed. Got status: {response.status_code}")

        # Test if 404 page content is correct
        response = requests.get(f"http://localhost:{server.server_port}/404.html")
        if response.status_code == 200:
            print("✅ 404 page content test passed")
        else:
            print(f"❌ 404 page content test failed. Got status: {response.status_code}")

    finally:
        # Clean up
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    test_404()
