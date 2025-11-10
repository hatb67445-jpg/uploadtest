import os
import cgi
import json
from http.server import BaseHTTPRequestHandler

# Vercel allows writing only to /tmp, so we store uploads there
UPLOAD_DIR = "/tmp/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_type, pdict = cgi.parse_header(self.headers.get('Content-Type'))
        if content_type == 'multipart/form-data':
            pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
            pdict['CONTENT-LENGTH'] = int(self.headers['Content-Length'])
            form = cgi.parse_multipart(self.rfile, pdict)

            if 'file' not in form:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"error": "No file uploaded"}')
                return

            # Extract file data
            file_data = form['file'][0]
            filename = form.get('filename', ['uploaded_file'])[0]
            filepath = os.path.join(UPLOAD_DIR, filename)

            # Save file temporarily
            with open(filepath, 'wb') as f:
                f.write(file_data)

            # Send response
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {
                "message": f"File '{filename}' uploaded successfully!",
                "path": filepath
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error": "Invalid content type"}')
