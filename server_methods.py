#!/usr/local/bin/python2.7
# encoding: utf-8

import sys,os,time

def do_POST(self):
	path = self.path[1:].replace("%20", " ")
	project, tab = filter(None, self.path.split('/'))
	
	length = self.headers.getheader('content-length')
	try:
		nbytes = int(length)
	except (TypeError, ValueError):
		nbytes = 0
	
	if tab and tab.lower() == "log":
		if (nbytes > 0):
			data = self.rfile.read(nbytes)
			print project + " - " + data
	if tab and tab.lower() == "watch":
		if (nbytes > 0):
			data = self.rfile.read(nbytes)
			#print project + ": WATCH" + data
	

def do_PUT(self):
	length = self.headers.getheader('content-length')
	try:
		nbytes = int(length)
	except (TypeError, ValueError):
		nbytes = 0
	if (nbytes > 0):
		data = self.rfile.read(nbytes)
	else:
		data = ""

	path = self.path.replace("%20", " ")
	project, tab = filter(None, path.split('/'))
	project_path = "%s/%s" % (documents_root,project)

	if not os.path.isdir(project_path):
		os.mkdir(project_path)
	
	file_path = "%s/%s.lua" % (project_path, tab)
	tab_path = project + ":" + tab
	if not os.path.exists(file_path):
		file = open(file_path, "w")
		file.write(data)
		file_buffer[tab_path] = data
		file.close()
		response = 201
	else:
		# TODO notification existe autre version
		if tab == "LiveCodea":
			response = 201
		else:
			print "%s - File exists - overwrite %s -" % (project, file_path)
			file = open(file_path, "w")
			file.write(data)
			file_buffer[tab_path] = data
			file.close()
			response = 200

	# TEMPDEV
	file = open(documents_root + "/LiveCodea/LiveCodea.lua", "r")
	file_buffer["LiveCodea:LiveCodea"] = file.read()
	file.close()
	##########

	self.send_response(response)
	self.end_headers()

def do_GET(self):	
	path = self.path[1:].replace("%20", " ")
	project, tab = filter(None, path.split('/'))
	project_path = "%s/%s" % (documents_root, project)	
	changes = None
	add_header = None
	data = ""

	if tab and tab.lower() == "changes":
		# Check files changes
		for f in os.listdir(project_path):
			path = project_path + "/" + f
			tab, ext = os.path.splitext(f)
			path_tab = project + ":" + tab
			if ext == ".lua":
				with open(path) as file:
					data = file.read()
					file.close()
				data_buf = file_buffer.get(path_tab, "")
				if data != data_buf:
					file_buffer[path_tab] = data
					changes = (path_tab, data)
					eval = "eval" if path_tab != "LiveCodea:LiveCodea" else "no-eval"
					add_header = ("Content-Eval", eval, "Content-Update", "save")
					break
			elif ext == ".luac":
				with open(path,'r') as file:
					data = file.read()
					file.close()					
				if len(data) > 0:
					changes = (path_tab, data)
					add_header = ("Content-Eval", "eval", "Content-Update", "no-save")
					with open(path,'w') as file:
						file.write("")
						file.close()
					break
	
	# TEMPDEV
	if not changes:
		file = open(documents_root + "/LiveCodea/LiveCodea.lua")
		data = file.read()
		file.close()
		data_buf = file_buffer.get("LiveCodea:LiveCodea", "")
		if data != data_buf:
			file_buffer["LiveCodea:LiveCodea"] = data
			changes = ("LiveCodea:LiveCodea", data)
			add_header = ("Content-Eval", "no-eval", "Content-Update", "save")
	#########
	

	if changes:
		self.send_response(200)
		self.send_header("Content-Length", len(changes[1]))
		self.send_header("Content-Type", "application/octet-stream")
		self.send_header("Content-Tab", changes[0])
		if add_header:
			for i in xrange(0, len(add_header), 2):
				self.send_header(add_header[i], add_header[i+1])
		self.end_headers()
		self.wfile.write(data)
	else:
		# Check for new assets
		docsent = False
		exts = (".gif", ".png", ".jpg", ".pdf")
		ctype = ("image/gif", "image/png", "image/jpeg", "application/pdf")
		for f in os.listdir(documents_root):
			path = documents_root + "/" + f
			file_name, ext = os.path.splitext(f)
			if ext:
					try:
						ind = exts.index(ext.lower())
					except ValueError:
						ind = -1
					if ind > -1:
						file = open(path, "rb")
						data = file.read()
						file.close()
						self.send_response(200)
						self.send_header("Content-Length", len(data))
						self.send_header("Content-Eval", "no-eval")
						self.send_header("Content-Update", "doc-save")
						self.send_header('Content-type', ctype[ind])
						self.send_header('Content-Tab', "Documents:" + file_name)
						self.end_headers()
						self.wfile.write(data)
						os.remove(path)
						docsent = True
						break
		if not docsent:
			# TODO
			self.send_response(304)
			self.end_headers()

def do_HEAD(self):
	## TODO
	custype = self.headers.get("Custom-codea","").lower();
	if custype == "connect":
		self.send_response(200)
		self.end_headers()
		print "Connected"
	else:
		self.send_response(500)
		self.end_headers()


