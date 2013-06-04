import os
import sublime, sublime_plugin

class LiveCodeaParameterCommand(sublime_plugin.WindowCommand):
	
	params_type = ["number", "integer", "color", "boolean", "text", "action"]
	args_tmpl = ("name min max", "name min max", "name r g b a", "name initial", "name initial", "name callback")

	def run(self):
		self.window.show_quick_panel(self.params_type, self.on__param_choosed)
	
	def on__param_choosed(self, picked):
		if picked > -1:
			view = self.window.active_view()
			s = view.sel()[0]
			if s.empty():
				s = view.word(s)
			# scope = view.substr(view.extract_scope(s.a))
			scope = view.substr(s)
			str_args = self.args_tmpl[picked]
			if len(scope) > 0:
				str_args = str_args.replace("name", scope)
			self.picked = self.params_type[picked]
			self.window.show_input_panel("Enter parameter argument(s) for %s" % self.picked, str_args, self.on_args_filled, None, None)

	def on_args_filled(self, text):
		if len(text):
			args_list = text.split(" ")
			args_list[0] = "'" + args_list[0] + "'"
			args = ",".join(args_list)
			chunk = "parameter.%s(%s)" % (self.picked, args)
			view = self.window.active_view()
			name, ext = os.path.splitext(view.file_name())
			path = name + ".luac"
			mode = "a" if os.path.exists(path) else "w"
			with open(path, mode) as file:
				file.write(chunk)
				file.close()


class LiveCodeaWatchCommand(sublime_plugin.TextCommand):

	def run(self, edit):
		view = self.view
		s = view.sel()[0]
		#print view.substr(view.extract_scope(s.a))
		
		#view.erase_regions('lua')
		#view.add_regions('lua', [view.word(s)], 'invalid', 'DOT', sublime.DRAW_OUTLINED)
		
		w = view.substr(view.word(s))
		if len(w) > 0:
			chunk = "parameter.watch(\"%s\")" % w
			name, ext = os.path.splitext(view.file_name())
			path = name + ".luac"
			mode = "a" if os.path.exists(path) else "w"
			with open(path, mode) as file:
				file.write(chunk)
				file.close()
		
		# if region.empty():
		# 	print r[0]
		# for s in view.sel():
		# 	if s.empty():

class LiveCodeaEvalCommand(sublime_plugin.TextCommand):

	def run(self, edit):
		view = self.view
		chunk = ""
		#for s in self.view.sel():
		for s in view.sel():
			if s.empty():
				s = view.line(s)
			chunk+= view.substr(s)
		# TODO: si les tab sont des espaces, marche pas, regexp ?
		# chunk = chunk.replace("\t","hop")
		if len(chunk) > 0:
			name, ext = os.path.splitext(view.file_name())
			path = name + ".luac"
			mode = "a" if os.path.exists(path) else "w"
			with open(path, mode) as file:
				file.write(chunk)
				file.close()
