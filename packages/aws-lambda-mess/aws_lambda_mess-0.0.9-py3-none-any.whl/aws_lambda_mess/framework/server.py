import http.server
import socketserver


def run(port, routes):
    from aws_lambda_mess.framework.lambda_dispatcher import get_handler
    lambda_handler = get_handler(routes)

    class Handler(http.server.BaseHTTPRequestHandler):
        def build_event(self):
            content_len = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_len).decode()
            method = self.command
            path = self.path

            return {
                "body": body.strip() if len(body.strip())>0 else "{}",
                "path": path,
                "httpMethod": method,
                "isBase64Encoded": False
            }

        def do_ANY(self):
            event = self.build_event()

            response = lambda_handler(event, None)

            self.send_response(response.get("statusCode", 500))
            for header, header_value in response.get("headers", {}).items():
                self.send_header(header, header_value)
            self.end_headers()
            self.wfile.write(response.get("body", "").encode(encoding='utf_8'))
            return

        def do_GET(self):
            return self.do_ANY()

        def do_POST(self):
            return self.do_ANY()

        def do_PUT(self):
            return self.do_ANY()

        def do_DELETE(self):
            return self.do_ANY()

    with socketserver.TCPServer(("", port), Handler) as httpd:
        print("Http Server Serving at port", port)
        httpd.serve_forever()

