#!/usr/local/bin/python2.7
# encoding: utf-8

# import socket

# server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server_sock.bind(('', 5000))
# server_sock.listen(10)

# while True:
#     cli_sock, addr = server_sock.accept()
#     print 'We have opened a cli_sockection with', addr
#     print cli_sock.recv(100)

#     output = "<h1>Hello Client</h1>"
#     cli_sock.send("HTTP/1.1 200 OK\n")
#     cli_sock.send("Content length: "+str(len(output)))
#     cli_sock.send("Content-Type: text/html\n\n")
    
#     cli_sock.send(output)
#     cli_sock.close()




import sys
import threading, time
import BaseHTTPServer
import server_methods as methods


methods.file_buffer = dict()
methods.documents_root = "Documents"

class CodeaRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
	"""HTTP request handler intented to CodeaLive
	"""

	def do_POST(self):
		"""Serve a POST request."""
		reload(methods)
		methods.do_POST(self)
	
	def do_PUT(self):
		"""Serve a PUT request."""
		reload(methods)
		methods.do_PUT(self)

	def do_GET(self):
		"""Serve a GET request."""
		reload(methods)
		methods.do_GET(self)

	def do_HEAD(self):
		"""Serve a HEAD request."""
		reload(methods)
		methods.do_HEAD(self)
	
	def log_request(self, code='-', size='-'):
		"""Log an accepted request.

		This is called by send_response().

		"""
		try:
			(200,201,304).index(code)
		except ValueError:
			self.log_message('"%s" %s %s',
		                 self.requestline, str(code), str(size))

def startServer(server_address, requestHandler):
	httpd = BaseHTTPServer.HTTPServer(server_address, requestHandler)
	httpd.serve_forever()


if __name__ == '__main__':	
	file_buffer = dict()
	server_address = ('', 8000)
	startServer(server_address, CodeaRequestHandler)
