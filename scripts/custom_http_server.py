import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path


class CustomHTTPRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        try:
            # Try to serve the requested file
            return SimpleHTTPRequestHandler.do_GET(self)
        except:
            # If file not found, serve our custom 404 page
            self.path = "/404.html"
            return SimpleHTTPRequestHandler.do_GET(self)

    def end_headers(self):
        # Add security headers
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        self.send_header("X-XSS-Protection", "1; mode=block")
        SimpleHTTPRequestHandler.end_headers(self)


def run_server(port=8080):
    # Set the working directory to docs
    os.chdir("docs")

    # Create server
    server_address = ("", port)
    httpd = HTTPServer(server_address, CustomHTTPRequestHandler)

    print(f"Starting server on port {port}...")
    print(f"Access the site at http://localhost:{port}")
    print("Press Ctrl+C to stop the server")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.server_close()


if __name__ == "__main__":
    run_server()
