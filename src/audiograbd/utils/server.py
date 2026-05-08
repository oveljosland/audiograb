import os
import http.server
import socketserver
from pathlib import Path


def serve(dir, port):
	"""Start HTTP server for a directory.
	Runs in a background thread.
	"""
	dir = Path(dir)
	if not dir.exists():
		logger.warning(f"Directory does not exist: {dir}")
		return

	os.chdir(dir)
	handler = http.server.SimpleHTTPRequestHandler
	
	try:
		with socketserver.TCPServer(("", port), handler) as httpd:
			logger.info(f"Web server at http://localhost:{port}")
			logger.info(f"Serving files from: {dir}")
			httpd.serve_forever()
	except Exception as e:
		logger.error(f"Failed to start web server: {e}")


