# PyGaap is the Python port of JGAAP,
# Java Graphical Authorship Attribution Program by Patrick Juola
# For JGAAP see https://evllabs.github.io/JGAAP/
#
# See PyGAAP_developer_manual.md for a guide to the structure of the GUI
# and how to add new modules.
# @ author: Michael Fang
#
# Style note: if-print checks using the GUI_debug variable
# are condensed into one line where possible.

GUI_debug = 0
# GUI debug level:
#   0 = no debug info.
#   1 = basic status update.
#   3 = all function calls.
#   info printed to the terminal.

from copy import deepcopy
from multiprocessing import Process, Queue, Pipe
from datetime import datetime
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename
import util.MultiprocessLoading as MultiprocessLoading
from sys import modules as sys_modules
from sys import exc_info
from sys import platform

# open a loading window so the app doesn't appear frozen.
pipe_from, pipe_to = Pipe(duplex=True)
if platform != "win32":
	p = Process(target=MultiprocessLoading.splash, args=(pipe_to,))
	p.start()
pipe_from.send("Loading API")

# LOCAL IMPORTS
from backend.API import API
from backend.CSVIO import readDocument, readCorpusCSV, readExperimentCSV
from backend.Document import Document
from backend import CSVIO
import Constants
# Top-level window.
topwindow = Tk()

topwindow.title("PyGAAP (GUI)")

try:topwindow.tk.call(
		'wm',
		'iconphoto',
		topwindow._w,
		PhotoImage(file = './res/icon.png'))
except TclError:
	print("Error: icon.png not found.")

topwindow.rowconfigure(0, weight = 1)
topwindow.rowconfigure(1, weight = 0, minsize = 50)
topwindow.columnconfigure(0, weight = 1)

# DPI settings
dpi = topwindow.winfo_fpixels('1i')
dpi_setting = None

if dpi > 72:
	if GUI_debug >= 2: print("1x UI scale")
	dpi_setting = 1
	topwindow.geometry("1000x670")
else:
	if GUI_debug >= 2: print("2x UI scale")
	dpi_setting = 2
	topwindow.geometry("2000x1150")

if platform == "win32":
	dpi_setting = 1
	topwindow.geometry("1000x670")
	
if dpi_setting == None:
	raise ValueError("Unknown DPI setting %s."% (str(dpi_setting)))

if dpi_setting == 1:
	# standard scaling
	dpi_scrollbar_width = 16
	dpi_option_menu_width = 10
	dpi_language_dropdown_width = 18
	dpi_process_window_geometry = "200x100"
	dpi_progress_bar_length = 200
	dpi_about_page_geometry = "600x300"
	dpi_author_window_geometry = "550x340"
	dpi_treeview_entry_height = 1
	dpi_process_window_geometry_finished = "700x900"
	dpi_description_box_border = 3

	ttk_style = ttk.Style()
	ttk_style.configure('Treeview', rowheight = 20)

elif dpi_setting == 2:
	# double scaling
	dpi_scrollbar_width = 28
	dpi_option_menu_width = 10
	dpi_language_dropdown_width =18
	dpi_process_window_geometry = "500x200"
	dpi_progress_bar_length = 400
	dpi_about_page_geometry = "1200x600"
	dpi_author_window_geometry = "1170x590"
	dpi_treeview_entry_height = 2
	dpi_process_window_geometry_finished = "1400x1100"
	dpi_description_box_border = 5

	ttk_style = ttk.Style()
	ttk_style.configure('Treeview', rowheight = 35)
	
style_choice = "JGAAP_blue"
styles = dict()

styles["JGAAP_blue"] = {"accent_color_dark":"#7eedfc",
						"accent_color_mid":"#c9f6fc",
						"accent_color_light":"#e0f9fc",
						"text":"#000000"}
styles["PyGAAP_pink"] = {"accent_color_dark": "#e0b5e5",
						"accent_color_mid":"#f2e1f4",
						"accent_color_light":"#fae9fe",
						"text":"#000000"}

if GUI_debug >= 3:
	print(
		"Accent colors:",
		styles[style_choice]["accent_color_dark"],
		styles[style_choice]["accent_color_mid"],
		styles[style_choice]["accent_color_mid"]
		)
ttk_style.map(
		'Treeview',
		background = [('selected', styles[style_choice]["accent_color_mid"])],
		foreground = [('selected', "#000000")]
		)

multiprocessing_limit_docs = float("inf")
# See TODO 1.
# the number of docs before
# multi-processing is used.

multiprocessing_limit_analysis = float("inf")
# See TODO 1.
# the sum score of the
# "time-consumingness" of analysis methods
# before multi-processing is used.

###############################
#### BACKEND API ##############
backend_API = API("place-holder")
###############################
###############################

pipe_from.send("Loading functions")

# Functions called by user interaction with the GUI.
def todofunc():
	"""Place-holder function for not-yet implemented features."""
	print("To-do function")
	return None

statusbar = None
statusbar_label = None

def status_update(displayed_text="", ifsame=None):
	"""
	updates the text in the status bar.
	"""
	# ifsame: only update the text
	# if the currently displayed text is the same as this string.
	
	if GUI_debug >= 3:
		print("status_update('%s', condition = %s)"
				%(displayed_text, ifsame))
	global statusbar
	global statusbar_label
	if ifsame == None:
		# do not check if the status text is the same as "ifsame"
		if statusbar_label['text'] == displayed_text:
			statusbar_label.config(text = " ")
			statusbar_label.after(20,
								lambda t = displayed_text:status_update(t))
		else: statusbar_label.config(text = displayed_text)
	else: # only change label if the text is the same as "ifsame"
		if statusbar_label['text'] == ifsame:
			statusbar_label.config(text = displayed_text)
	return None

# all_parameters: deferred parameter building to the backend.

def select_modules(listbox_available: Listbox,
				   Listbox_operate: list,
				   function: str,
				 **options):
	"""Used by Event Drivers, Event culling etc to
	add/remove/clear selected modules.
	Needs to check if module is already added."""

	# listbox_available: listbox with available modules
	# Listbox_operate: a list of listboxes to modify.
	#   Includes the one in the corresponding tab and the
	#   listbox in the Review & Process tab.
	# function: "clear", "remove", or "add"

	if function == "clear":
		if GUI_debug > 1: print("select_modules: clear")
		for listbox_member in Listbox_operate:
			if type(listbox_member) == Listbox:
				listbox_member.delete(0, END)
			else:
				listbox_member.delete(*listbox_member.get_children())
		module_type = options.get("module_type")
		backend_API.modulesInUse[module_type].clear()
		if module_type == "AnalysisMethods":
			backend_API.modulesInUse["DistanceFunctions"].clear()
		return None

	elif function == "remove":
		if GUI_debug > 1: print("select_modules: remove")
		module_type = options.get("module_type")
		try:
			if type(Listbox_operate[0]) == Listbox:
				removed = Listbox_operate[0].curselection()
				assert len(removed) > 0
			else:
				removed = Listbox_operate[0].selection()
				removed_index = Listbox_operate[0].index(removed)
			status_update()
			for listbox_member in Listbox_operate:
				listbox_member.delete(removed)
		
		except (ValueError, AssertionError, TclError):
			if GUI_debug > 0: print("remove from list: nothing selected or empty list.")
			status_update("Nothing selected.")
			return None
		if type(Listbox_operate[0]) == Listbox:
				backend_API.modulesInUse[module_type].pop(removed[0])
		else:
			backend_API.modulesInUse[module_type].pop(removed_index)
			backend_API.modulesInUse["DistanceFunctions"].pop(removed_index)
		return None

	elif function == "add":
		if GUI_debug > 1: print("select_modules: add")
		module_type = options.get("module_type")
		try:
			if type(Listbox_operate[0]) == Listbox:
				# canonicizers, event drivers, event cullers.
				selected_module =\
					listbox_available[0].get(listbox_available[0].curselection())
				backend_API.modulesInUse[module_type].append(
					backend_API.moduleTypeDict[module_type].get(selected_module)()
				)
			elif len(listbox_available) > 1 \
					and listbox_available[1]['state'] == DISABLED:
				# analysis methods, no distance function
				selected_module =\
					(listbox_available[0].get(listbox_available[0].curselection()), "NA")
				backend_API.modulesInUse[module_type].append(
					backend_API.moduleTypeDict[module_type].get(selected_module[0])()
				)
				backend_API.modulesInUse["DistanceFunctions"].append("NA")
			else:
				# analysis methods with distance function
				selected_module = [
					listbox_available[0].get(listbox_available[0].curselection()),
					listbox_available[1].get(listbox_available[1].curselection())
				]
				backend_API.modulesInUse["AnalysisMethods"].append(
					backend_API.moduleTypeDict[module_type].get(selected_module[0])()
				)
				backend_API.modulesInUse["DistanceFunctions"].append(
					backend_API.moduleTypeDict["DistanceFunctions"].get(selected_module[1])()
				)
			status_update()

		except TclError:
			status_update("Nothing selected or missing selection.")
			if GUI_debug > 0: print("add to list: nothing selected")
			return None

		for listbox_member in Listbox_operate:
			if type(Listbox_operate[0]) == Listbox:
				listbox_member.insert(END, selected_module)
			else:
				listbox_member.insert(parent = "",
									  index = END,
									  text = "",
									  value = selected_module)

	else:
		status_update("Bug: all escaped: 'select_modules(function = %s).'"%(function))
		raise ValueError("Bug: all escaped: 'select_modules(function = %s).'"%(function))

	return None


def check_DF_listbox(lbAv, lbOp: Listbox):
	"""Enable or disable the 'Distance Functions' listbox ...
	depending on whether the item selected in
	'Analysis Methods' allows using DFs."""
	if GUI_debug >= 3: print("check_DF_listbox()")
	try:
		if backend_API.analysisMethods[lbAv.get(lbAv.curselection())]\
				.__dict__.get("_NoDistanceFunction_") == True:
			lbOp.config(state = DISABLED)
		else:
			lbOp.config(state = NORMAL)
	except TclError:
		return

def find_description(desc: Text,
					 listbox: Listbox or ttk.Treeview,
					 API_dict: dict):

	"""find description of a module."""

	# TODO 3 low priority:
	#   retrieve desc from individual instances instead of from the API dict.

	# desc: the tkinter Text object to display the description.
	# listbox: the Listbox or Treeview object to get the selection from
	# API_dict: the API dictionary that contains
	#   the listed method classes from the backend.
	#   example -- API_dict could be backend_API.canonicizers.

	if GUI_debug >= 3: print("find_description()")

	if type(listbox) == Listbox:
		try:
			name = listbox.get(listbox.curselection())
			description_string = name + ":\n" \
									  + API_dict[name].displayDescription()
		except (TypeError, TclError):
			description_string = "No description"

	elif type(listbox) == ttk.Treeview:
		if listbox.item(listbox.selection())["values"] == "":
			description_string = ""
		else:
			am_name = listbox.item(listbox.selection())["values"][0]
			df_name = listbox.item(listbox.selection())["values"][1]
			am_d, df_d = "No description", "No description"
			try: am_d = backend_API.analysisMethods[am_name].displayDescription()
			except (TypeError, KeyError): pass
			try: df_d = backend_API.analysisMethods[df_name].displayDescription()
			except (TypeError, KeyError): pass
			if df_name == "NA": df_d = "Not applicable"
			description_string = am_name + ":\n" + am_d + "\n\n" + df_name + ":\n" + df_d

	desc.config(state = NORMAL)
	desc.delete(1.0, END)
	desc.insert(END, description_string)
	desc.config(state = DISABLED)
	return None

def set_parameters(stringvar, module, variable_name):
	"""sets parameters whenever the widget is touched."""
	if GUI_debug >= 3:
		print("set_parameters(module = %s, variable_name = %s)"
		%(module, variable_name))

	value_to = stringvar.get()

	try:
		value_to = float(value_to)
		# if value is a number, try converting to a number.
		if abs(int(value_to) - value_to) < 0.0000001:
			value_to = int(value_to)
	except ValueError:
		pass
	setattr(module, variable_name, value_to)
	return None

def set_API_global_parameters(parameter, stringvar):
	"""Wrapper for backend_API's global parameter setter"""
	backend_API.set_global_parameters(parameter, stringvar.get())
	return

def find_parameters(param_frame: Frame,
					listbox: Listbox or ttk.Treeview,
					displayed_params: list,
					clear: bool = False,
				  **options):

	"""find parameters and description in some modules to display and set"""

	# param_frame: the tkinter frame that displays the parameters.
	# listbox: the tkinter listbox that has the selected parameters.
	# displayed_params: a list of currently displayed parameter options.
	# clear: True if function only used to clear displayed parameters.

	if GUI_debug >= 3:
		print("find_parameters(clear = %s), displayed_params list length: %s."
		%(len(displayed_params), clear))


	module_type = options.get("module_type")
	# get dict of modules in the selected UI page.
	# first get the parameters to display from list.
	if type(listbox) == Listbox and len(listbox.curselection()) > 0:
		# event drivers, event cullers
		module_index = listbox.curselection()[0]
		this_module = backend_API.modulesInUse[module_type][module_index]
		this_module_name = listbox.get(module_index)
	elif type(listbox) == ttk.Treeview and len(listbox.selection()) > 0:
		# analysis methods, distance functions
		module_index = listbox.index(listbox.selection())
		this_module = backend_API.modulesInUse[module_type][module_index]
		this_df_module = backend_API.modulesInUse["DistanceFunctions"][module_index]
		# if not string "NA", this gets the df object.
		this_module_name = listbox.item(listbox.selection())["values"][0]
		this_df_module_name = listbox.item(listbox.selection())["values"][1]
		# this is the way to retrieve treeview selection names
		
	else: return None
	
	for params in displayed_params:
		params.destroy()
	displayed_params.clear()
	if clear == True:
		return None
	
	
	# currently only support OptionMenu variables
	param_options = []
	# list of StringVars.
	if type(listbox) == Listbox:
		number_of_modules = len(this_module._variable_options)
	else:
		try:
			df_variables = this_df_module._variable_options
		except AttributeError:
			df_variables = []
		number_of_modules = len(this_module._variable_options) \
						  + len(df_variables)
		number_of_am = len(this_module._variable_options)
	if number_of_modules == 0:
		# if this module does not have parameters to be set, say so.
		displayed_params.append(Label(param_frame,
								text = "No parameters for this module."))
		displayed_params[-1].pack()
	else:
		# if this module has parameters, find and display parameters.
		rowshift = 0
		# this is the row shift for widgets below the second tkinter.Label.
		# It's non-zero for when there are two groups of parameters to display.
		# (Analysis + DF)
		displayed_params.append(Label(param_frame,
									  text = str(this_module_name) + ":",
									  font = ("Helvetica", 14)))
		displayed_params[-1].grid(row = 0, column = 0, columnspan = 2, sticky = W)
		for i in range(number_of_modules):
			if type(listbox) == Listbox:
				parameter_i = list(this_module._variable_options.keys())[i]
				param_options.append(StringVar(
					value = str(this_module.__dict__.get(parameter_i)))
				)
			elif type(listbox) == ttk.Treeview:
				if i < number_of_am:
					parameter_i = list(this_module._variable_options.keys())[i]
					param_options.append(StringVar(
					value = str(this_module.__dict__.get(parameter_i)))
				)
				else:
					rowshift = 1
					if this_df_module == "NA": break
					parameter_i = list(this_df_module._variable_options.keys())[i - number_of_am]
					param_options.append(StringVar(
					value = str(this_df_module._variable_options[parameter_i]["options"]\
						[this_df_module._variable_options[parameter_i]["default"]]))
				)
			displayed_params.append(Label(param_frame, text = parameter_i))
			displayed_params[-1].grid(row = i + 1 + rowshift, column = 0)

			if this_module._variable_options[parameter_i]["type"] == 'Entry':
				raise NotImplementedError
				# TODO 2 priority low:
				# implement text entry for parameters.
				displayed_params.append(Entry(param_frame))
				displayed_params[-1].insert(
					0, str(parameter_i['options'][parameter_i])
				)
				displayed_params[-1].grid(row = i + 1 + rowshift, column = 1, sticky = W)
			elif this_module._variable_options[parameter_i]["type"] == 'OptionMenu':
				displayed_params.append(
					OptionMenu(
						param_frame, 
						param_options[-1],
						*this_module._variable_options[parameter_i]['options']
					)
				)
				displayed_params[-1].config(width = dpi_option_menu_width)
				displayed_params[-1].grid(row = i + 1 + rowshift, column = 1, sticky = W)
				param_options[-1].trace_add(("write"),
					lambda v1, v2, v3, stringvar = param_options[-1],
					module = this_module, var = parameter_i:\
						set_parameters(stringvar, module, var))
		if rowshift == 1:
			# if the rows are shifted, there is an extra label for the DF parameters.
			displayed_params.append(Label(param_frame,
				text = str(this_df_module_name) + ":",
				font = ("Helvetica", 14)))
			displayed_params[-1].grid(
				row = number_of_am + 1,
				column = 0,
				columnspan = 2,
				sticky = W)


	param_frame.columnconfigure(0, weight = 1)
	param_frame.columnconfigure(1, weight = 3)
	return None

def run_pre_processing(backend_API, doc: Document, dump_queue = None):
	"""
	Run pre-processing on a single document:
	Canonicizers, event drivers, event cullers.
	"""
	# doc: the document passed in.
	# dump_queue: when multi-processing,
	# the shared queue to temporarily store the documents.

	for c in backend_API.modulesInUse["Canonicizers"]:
		c._global_parameters = backend_API.global_parameters
		doc.text = c.process(doc.text)
	
	for e in backend_API.modulesInUse["EventDrivers"]:
		e._global_parameters = backend_API.global_parameters
		doc.setEventSet(e.createEventSet(doc.text), append=True)
	
	if len(backend_API.modulesInUse["EventCulling"]) != 0:
		raise NotImplementedError
		#?._global_parameters = backend_API.global_parameters
	
	if dump_queue != None:
		dump_queue.put(doc)
	else:
		return doc

results_window = None
def run_experiment(params: dict,
			check_listboxes: list,
			check_labels: list,
			process_button: Button,
			click: bool = False):

	"""
	Process all input files with the parameters in all tabs.
	input: unknown authors, known authors, all listboxes.
	"""

	# check_listboxes:
	#   list of listboxes that shouldn't be empty.
	# check_labels:
	#   list of labels whose text colors need to be updated upon checking the listboxes.
	if GUI_debug >= 3: print("run_experiment(click = %s)\nparams = %s" %(click, params))
	all_set = True
	# first check if the listboxes in check_listboxes are empty. If empty
	process_button.config(state = NORMAL, text = "Process", )
	for lb_index in range(len(check_listboxes)):
		try: size = len(check_listboxes[lb_index].get_children())
		except AttributeError: size = check_listboxes[lb_index].size()
		if size == 0:
			check_labels[lb_index].config(
				fg = "#e24444",
				activeforeground = "#e24444")
			all_set = False
			process_button.config(
				fg = "#333333",
				state = DISABLED,
				text = "Process [missing parameters]",
				activebackground = "light grey", bg = "light grey")
			# if something is missing
		else: # if all is ready
			check_labels[lb_index].config(fg = "black", activeforeground = "black")
	process_button.config(fg = "black")
	if not all_set or click == False:
		return None


	unknownAuthors = params["UnknownAuthors"].get(0, END)

	# LOADING DOCUMENTS
	canonicizers_names = list(params["Canonicizers"].get(0, END))
	event_drivers_names = list(params["EventDrivers"].get(0, END))
	event_cullers_names = list(params["EventCulling"].get(0, END))
	am_df_names = [params["AnalysisMethods"].item(j)["values"]
					for j in list(params["AnalysisMethods"].get_children())]

	# gathering the known (corpus) documents
	docs = []
	docs_GUI_debug = []
	for author in params["known_authors"]:
		for authorDoc in author[1]:
			docs.append(Document(author[0],
				authorDoc.split("/")[-1],
				readDocument(authorDoc), authorDoc))
			docs_GUI_debug.append([author[0], authorDoc.split("/")[-1]])

	for d in unknownAuthors:
		docs.append(Document(None, d.split("/")[-1], readDocument(d), d))
		docs_GUI_debug.append([None, d.split("/")[-1]])

	if GUI_debug >= 3: print("Loading parameters")
	

	backend_API.documents = docs
	if GUI_debug >= 2: print(backend_API.modulesInUse)

	if len(backend_API.documents) < multiprocessing_limit_docs:
		# only use multi-processing when the number of docs is large.
		if GUI_debug >= 2: print("single-threading.")
		processed_docs = []
		for doc in backend_API.documents:
			processed_docs.append(run_pre_processing(backend_API, doc))
		backend_API.documents = processed_docs

	else:
		# TODO 1 priority high:
		# implement multi-processing for pre-processing.
		raise NotImplementedError
		if GUI_debug >= 2: print("multi-threading")
		process_list = []
		dump_queue = Queue()
		for doc in backend_API.documents:
			process_list.append(Process(target = run_pre_processing(backend_API, doc, dump_queue)))
			process_list[-1].start()
		for proc in process_list:
			proc.join()
		backend_API.documents = []
		while not dump_queue.empty():
			doc_get = dump_queue.get()
			backend_API.documents.append(doc_get)

	# RUN ANALYSIS ON UNKNOWN DOCS
	unknown_docs = [d for d in deepcopy(backend_API.documents) if (d.author == None or d.author == "")]
	known_docs = [d for d in deepcopy(backend_API.documents) if (d.author != None and d.author != "")]
	
	# TODO 1 priority high:
	# implement multi-processing for analysis methods.
	# if $score < multiprocessing_limit_analysis:
		
	results = []
	if GUI_debug >= 3: print("Running analysis methods")
	for am_df_index in range(len(backend_API.modulesInUse["AnalysisMethods"])):
		am_df_pair = (backend_API.modulesInUse["AnalysisMethods"][am_df_index],
					  backend_API.modulesInUse["DistanceFunctions"][am_df_index])
		am_df_pair[0]._global_parameters = backend_API.global_parameters
		if am_df_pair[1] != "NA":
			am_df_pair[1]._global_parameters = backend_API.global_parameters

		am_df_pair[0].setDistanceFunction(am_df_pair[1])
		
		# for each method: first train models on known docs
		am_df_pair[0].train(known_docs)
		# then for each unknown document, analyze and output results
		
		am_df = list(params["AnalysisMethods"].get_children())
		am_df = [params["AnalysisMethods"].item(j)["values"] for j in am_df]
		for d in unknown_docs:
			doc_result = am_df_pair[0].analyze(d)
			formatted_results = \
				backend_API.prettyFormatResults(canonicizers_names,
												event_drivers_names,
												am_df_names[am_df_index][0],
												am_df_names[am_df_index][1],
												d,
												doc_result)
			results.append(formatted_results)
	
	results_text = ""
	for r in results:
		results_text += str(r + "\n")
	
	# show process results
	global results_window
	
	results_window = Toplevel()
	results_window.title("Results")
	results_window.geometry(dpi_process_window_geometry)
	
	results_window.bind("<Destroy>", lambda event, b = "":status_update(b))


	# create space to display results, release focus of process window.
	results_display = Text(results_window)
	results_display.pack(fill = BOTH, expand = True, side = LEFT)
	results_display.insert(END, results_text)
	#results_display.config(state = DISABLED)

	results_scrollbar = Scrollbar(results_window,
								  width = dpi_scrollbar_width,
								  command = results_display.yview)
	results_display.config(yscrollcommand = results_scrollbar.set)
	results_scrollbar.pack(side = LEFT, fill = BOTH)
	results_window.geometry(dpi_process_window_geometry_finished)
	results_window.title(str(datetime.now()))

	change_style(results_window)

	return None

About_page = None
def displayAbout():
	global versiondate
	global About_page
	"""Displays the About Page"""
	if GUI_debug >= 3: print("displayAbout()")
	try:
		About_page.lift()
		return None
	except (NameError, AttributeError):
		pass
	About_page = Toplevel()
	About_page.title("About PyGAAP")
	About_page.geometry(dpi_about_page_geometry)
	About_page.resizable(False, False)
	about_page_logosource = PhotoImage(file = "./res/logo.png")
	about_page_logosource = about_page_logosource.subsample(2, 2)
	AboutPage_logo = Label(About_page, image = about_page_logosource)
	AboutPage_logo.pack(side = "top", fill = "both", expand = "yes")

	textinfo = "THIS IS AN EARLY VERSION OF PyGAAP GUI.\n\
	Version date: " + Constants.versiondate + "\n\
	PyGAAP is a Python port of JGAAP,\n\
	Java Graphical Authorship Attribution Program.\n\
	This is an open-source tool developed by the EVL Lab\n\
	(Evaluating Variation in Language Laboratory)."
	AboutPage_text = Label(About_page, text = textinfo)
	AboutPage_text.pack(side = 'bottom', fill = 'both', expand = 'yes')
	About_page.mainloop()

notes_content = ""
notepad_window = None

def notepad():
	"""Notes button window"""
	global notes_content
	global notepad_window
	# prevents spam-spawning. took me way too long to figure this out
	if GUI_debug >= 3: print("notepad()")
	try:
		notepad_window.lift()
	except (NameError, AttributeError):
		notepad_window = Toplevel()
		notepad_window.title("Notes")
		#notepad_window.geometry("600x500")
		notepad_window_textfield = Text(notepad_window)
		notepad_window_textfield.insert("1.0", str(notes_content))
		notepad_window_save_button = Button(notepad_window, text = "Save & Close",\
			command = lambda:notepad_Save(
				notepad_window_textfield.get("1.0", "end-1c"),
				notepad_window))
		notepad_window_textfield.pack(padx = 7, pady = 7, expand = True, fill = BOTH)
		notepad_window_save_button.pack(pady = (0, 12), padx = 100, fill = BOTH)
		change_style(notepad_window)
		notepad_window.mainloop()
	return None

def notepad_Save(text, window):
	"""
	saves the contents displayed in the notepad textfield
	when the button is pressed
	"""
	global notes_content
	notes_content = text
	window.destroy()
	if GUI_debug >= 3: print("notepad_Save()")
	return None

def switch_tabs(notebook, mode, tabID = 0):
	"""
	Switch tabs from the buttons "Previous", "Next",  and "Finish & Review"
	"""
	# contains hard-coded limits of tabIDs.
	if GUI_debug >= 3: print("switch_tabs(mode = %s)" %(mode))
	if mode == "next":
		notebook.select(min((notebook.index(notebook.select()) + 1), 5))
	elif mode == "previous":
		notebook.select(max((notebook.index(notebook.select()) - 1), 0))
	elif mode == "choose":
		if tabID >= 0 and tabID <= 5:
			notebook.select(tabID)
	return

def file_add_remove(window_title, listbox_operate: Listbox, allow_duplicates: bool, function: str, lift_window = None):
	"""Universal add file function to bring up the explorer window"""
	# window_title is the title of the window,
	# may change depending on what kind of files are added
	# listbox_operate is the listbox object to operate on
	# allow_duplicates is whether the listbox allows duplicates.
	# if listbox does not allow duplicates,
	# item won't be added to the listbox and this prints a message to the terminal.
	# lift_window is the window to go back to focus when the file browser closes
	if GUI_debug >= 1: print("file_add_remove")
	elif GUI_debug >= 3: print("file_add_remove(allow_duplicates = %s)", allow_duplicates)
	if function == "add":
		filename = askopenfilename(
			filetypes = (("Text File", "*.txt"), ("All Files", "*.*")),
			title = window_title, multiple = True
		)
		if lift_window != None:
			lift_window.lift(topwindow)
		if allow_duplicates and filename != "" and len(filename) > 0:
			listbox_operate.insert(END, filename)
		else:
			for fileinlist in listbox_operate.get(0, END):
				if fileinlist == filename:
					status_update("File already in list.")
					if GUI_debug > 0:
						print("Add document: file already in list")
					lift_window.lift()
					return None
			if filename != None and filename != "" and len(filename) > 0:
				for file in filename:
					listbox_operate.insert(END, file)

		if lift_window != None:
			lift_window.lift()
		return
	elif function == "remove":
		try:
			listbox_operate.delete(listbox_operate.curselection())
			status_update()
		except TclError:
			status_update("Nothing selected")
			return

known_authors = []
# known_authors list format:
#   [
#	   [author, [file-directory, file-directory]],
#	   [author, [file-directory, file directory]]
#   ]
known_authors_list = []
# this decides which in the 1-dimensionl listbox is the author...load_save
#   and therefore can be deleted when using delete author
# format: [0, -1, -1. -1, 1, -1, ..., 2, -1, ..., 3, -1, ...]
#   -1 = not author; 
#   >= 0: author index.

def authors_list_updater(listbox):
	"""This updates the ListBox from the known_authors python-list"""
	global known_authors
	global known_authors_list
	listbox.delete(0, END)
	if GUI_debug >= 3: print("authors_list_updater()")
	known_authors_list = []
	for author_list_index in range(len(known_authors)):
		listbox.insert(END, known_authors[author_list_index][0])
		listbox.itemconfig(END, 
			background = styles[style_choice]["accent_color_light"],
			selectbackground = styles[style_choice]["accent_color_mid"])
		known_authors_list += [author_list_index]
		for document in known_authors[author_list_index][1]:
			listbox.insert(END, document)#Author's documents
			listbox.itemconfig(END, background = "gray90", selectbackground = "gray77")
			known_authors_list += [-1]
	return None

def author_save(window, listbox, author, documents_list, mode):
	"""
	This saves author when adding/editing to the known_authors list.
	Then uses authors_list_updater to update the listbox
	"""

	#Listbox: the authors listbox.
	#author: 
	#	   "ADD MODE": the author's name entered in authorsList window
	#	   "EDIT MODE": [original author name, changed author name]
	#documents_list: list of documents entered in the listbox in the authorsList window
	#mode: add or edit

	global known_authors
	if GUI_debug >= 3: print("author_save(mode = %s)" %(mode))
	if mode == "add":
		if (author != None and author.strip() != "") \
				and (documents_list != None \
				and len(documents_list) != 0):  
			author_index = 0
			while author_index<len(known_authors):
				#check if author already exists
				if known_authors[author_index][0] == author:
					#when author is already in the list, merge.
					known_authors[author_index][1] = \
						known_authors[author_index][1] \
						+ list([doc for doc in documents_list
							if doc not in known_authors[author_index][1]])
					authors_list_updater(listbox)
					window.destroy()
					return None
				author_index += 1
			known_authors += [[author, list(\
								[file for file in documents_list if type(file) == str]
								)]]
								#no existing author found, add.
			authors_list_updater(listbox)
		window.destroy()
		return None
	elif mode == 'edit':
		if (author[1] != None \
				and author[1].strip() != "") \
				and (documents_list != None \
				and len(documents_list) != 0):
			author_index = 0
			while author_index<len(known_authors):
				if known_authors[author_index][0] == author[0]:
					known_authors[author_index] = [author[1], documents_list]
					authors_list_updater(listbox)
					window.destroy()
					return None
				author_index += 1
			print("Bug: editing author:"
				+ "list of authors and documents changed unexpectedly when saving")
			return None
	else:
		print("Bug: unknown parameter passed to 'author_save' function: ",
			str(mode))
	window.destroy()
	return None

author_window = None
def authorsList(authorList, mode):
	"""Add, edit or remove authors
	This updates the global known_authors list.
	This opens a window to add/edit authors; does not open a window to remove authors
	"""
	#authorList: the listbox that displays known authors in the topwindow.
	#authorList calls author_save (which calls authorListUpdater) when adding/editing author
	#
	global known_authors
	global known_authors_list
	if GUI_debug >= 3: print("authorsList(mode = %s)"%(mode))
	if mode == "add":
		title = "Add Author"
	elif mode == 'edit':
		try:
			authorList.get(authorList.curselection())
			title = "Edit Author"
			selected = int(authorList.curselection()[0])
			if known_authors_list[selected] == -1:
				status_update("Select the author instead of the document.")
				print("edit author: select the author instead of the document")
				return None
			else:
				author_index = known_authors_list[selected] #gets the index in the 2D list
				insert_author = known_authors[author_index][0] #original author name
				insert_docs = known_authors[author_index][1] #original list of documents
		except TclError:
			status_update("No author selected.")
			if GUI_debug > 0:
				print("edit author: no author selected")
			return None

	elif mode == "remove":#remove author does not open a window
		try:
			selected = int(authorList.curselection()[0])
			#this gets the listbox selection index
			if known_authors_list[selected] == -1:
				status_update("Select the author instead of the document.")
				print("remove author: select the author instead of the document")
				return None
			else:
				author_index = known_authors_list[selected]
				#This gets the index in known_authors nested list
				if author_index >= len(known_authors)-1:
					known_authors = known_authors[:author_index]
				else:
					known_authors = known_authors[:author_index] \
						+ known_authors[author_index + 1:]
				authors_list_updater(authorList)

		except TclError:
			status_update("No author selected.")
			if GUI_debug > 0:
				print("remove author: nothing selected")
			return None
		return None
	else:
		assert mode == "add" or mode == "remove" or mode == "edit", \
			"bug: Internal function 'authorsList' has an unknown mode parameter " \
			+ str(mode)
		
		return None

	global author_window
	try:
		author_window.lift()
		return None
	except (NameError, AttributeError, TclError):
		pass
	
	author_window = Toplevel()
	author_window.grab_set()#Disables main window when the add/edit author window appears
	author_window.title(title)
	author_window.geometry(dpi_author_window_geometry)
	
	author_window.rowconfigure(1, weight = 1)
	author_window.columnconfigure(1, weight = 1)

	Label(author_window, text = "Author",font = "bold", padx = 10)\
		.grid(row = 0, column = 0, pady = 7, sticky = "NW")
	Label(author_window, text = "Files", font = "bold", padx = 10)\
		.grid(row = 1, column = 0, pady = 7, sticky = "NW")

	author_name_entry = Entry(author_window, width = 40)
	if mode == "edit":
		author_name_entry.insert(END, insert_author)
	author_name_entry.grid(row = 0, column = 1, pady = 7, sticky = "swen", padx = (0, 10))

	author_listbox = Listbox(author_window, height = 12, width = 60)
	if mode == "edit":
		for j in insert_docs:
			author_listbox.insert(END, j)
	author_listbox.grid(row = 1, column = 1, sticky = "swen", padx = (0, 10))

	author_buttons_frame = Frame(author_window)
	
	author_add_doc_button = Button(author_buttons_frame, text = "Add Document",\
		command = lambda:file_add_remove("Add Document For Author", author_listbox, False, "add", author_window))
	author_add_doc_button.grid(row = 0, column = 0)
	author_remove_doc_button = Button(author_buttons_frame, text = "Remove Document",\
		command = lambda:select_modules(None, [author_listbox], 'remove'))
	author_remove_doc_button.grid(row = 0, column = 1)
	author_buttons_frame.grid(row = 2, column = 1, sticky = 'NW')

	author_bottom_buttons_frame = Frame(author_window)
	#OK button functions differently depending on "add" or "edit".
	author_ok_button = Button(author_bottom_buttons_frame, text = "OK",)
	if mode == "add":
		author_ok_button.configure(command
		   = lambda:author_save(author_window,
								 authorList,
								 author_name_entry.get(),
								 author_listbox.get(0, END),
								 mode))
	elif mode == "edit":
		author_ok_button.configure(command
		   = lambda:author_save(author_window,
								 authorList,
								 [insert_author, author_name_entry.get()],
								 author_listbox.get(0, END),
								 mode))

	author_ok_button.grid(row = 0, column = 0, sticky = "W")
	author_cancel_button = Button(author_bottom_buttons_frame, text = "Cancel",
		command = lambda:author_window.destroy())
	author_cancel_button.grid(row = 0, column = 1, sticky = "W")
	author_bottom_buttons_frame.grid(row = 3, column = 1, pady = 7, sticky = "NW")	
	change_style(author_window)

	author_window.mainloop()
	return None


def reload_modules_button(frame: Frame, button_shown: list, destroy=False):
	"""Hides or shows the reload modules button."""
	# function: "hide" or "show"
	if button_shown == []:
		show_button = \
			Button(frame,
					text = "Reload all modules",
					height = 2,
					command=reload_modules
			)
		show_button.pack(pady=100)
		button_shown.append(show_button)
		frame.after(4000, lambda
			f=frame, b=button_shown, d=True:reload_modules_button(f, b, d))
		return
	if destroy == True:
		button_shown[0].destroy()
		button_shown.clear()
	return

def load_save_docs(function: str,
						 unknown_docs_listbox: Listbox,
						 known_docs_listbox: Listbox):
	if "load" in function:
		filename = askopenfilename(
			filetypes = (("Comma-separated values", "*.csv"), ("All files", "*.*")),
			title = "Load corpus specifications",
			multiple = False
		)
		# TODO 4 priority high:
		# implement loading from/saving experiments to csvs.
		if len(filename) == 0:
			return
		files_list = readCorpusCSV(filename[0])
		if "clear" in function:
			backend_API.documents = []
		for file in files_list:
			if file[0] == "":
				# unknown author
				unknown_docs_listbox.insert(END, file[1])
			else:
				# known author
				...
	elif function == "save":
		raise NotImplementedError
		filename = asksaveasfilename(
			filetypes = (("Comma-separated values", "*.csv"), ("All files", "*.*")),
			title = "Save corpus specifications"
		)

def load_AAAC_problems(problem: str):
	# problem expects a letter string, ex: "A", "B", etc.
	...


pipe_from.send("Loading GUI")

menubar = Menu(topwindow)
menu_file = Menu(menubar, tearoff = 0)

Tab_Documents_UnknownAuthors_listbox = None
Tab_Documents_KnownAuthors_listbox = None

#tkinter menu building goes from bottom to top / leaves to root
menu_batch_documents = Menu(menu_file, tearoff = 0)#batch documents menu
menu_batch_documents.add_command(
	label = "Save Documents",
	command = lambda function = "save":
	load_save_docs(
		function,
		Tab_Documents_UnknownAuthors_listbox,
		Tab_Documents_KnownAuthors_listbox
	)
)
menu_batch_documents.add_command(
	label="Load Documents",
	command=lambda function = "load":
		load_save_docs(
			function,
			Tab_Documents_UnknownAuthors_listbox,
			Tab_Documents_KnownAuthors_listbox
		)
)
menu_batch_documents.add_command(
	label="Clear and load Documents",
	command=lambda function = "load_clear":
		load_save_docs(
			function,
			Tab_Documents_UnknownAuthors_listbox,
			Tab_Documents_KnownAuthors_listbox
		)
)
menu_file.add_cascade(
	label = "Batch Documents ***", menu = menu_batch_documents,
	underline = 0
)

menu_AAAC_problems = Menu(menu_file, tearoff = 0)
menu_AAAC_problems.add_command(label = "Problem 1", command = todofunc)
menu_file.add_cascade(
	label = "AAAC Problems ***", menu = menu_AAAC_problems,
	underline = 0
)

menu_file.add_separator()#file menu
menu_themes = Menu(menu_file, tearoff = 0)
menu_themes.add_command(
	label = "PyGaap Pink", command = lambda thm = "PyGAAP_pink":change_style_live(thm)
)
menu_themes.add_command(
	label = "JGAAP Blue", command = lambda thm = "JGAAP_blue":change_style_live(thm)
)
menu_file.add_cascade(label = "Themes", menu = menu_themes, underline = 0)

menu_file.add_separator()#file menu
menu_file.add_command(label = "Exit", command = topwindow.destroy)
menubar.add_cascade(label = "File", menu = menu_file)

menu_help = Menu(menubar, tearoff = 0)#help menu
menu_help.add_command(label = "About...", command = displayAbout)
menubar.add_cascade(label = "Help", menu = menu_help)

topwindow.config(menu = menubar)
#bottom of the main window is at the bottom of this file


#the middle workspace where the tabs are

workspace = Frame(topwindow, height = 800, width = 570)
workspace.grid(padx = 10, pady = 5, row = 0, sticky = "nswe")
workspace.columnconfigure(0, weight = 1)
workspace.rowconfigure(0, weight = 2)

tabs = ttk.Notebook(workspace)
tabs.pack(pady = 1, padx = 5, expand = True, fill = "both")

#size for all the main tabs.
tabheight = 570
tabwidth = 1000

Tabs_names = [
	"Tab_Documents",
	"Tab_Canonicizers",
	"Tab_EventDrivers",
	"Tab_EventCulling",
	"Tab_AnalysisMethods",
	"Tab_ReviewProcess"
]
Tabs_Frames = dict() # this stores the main Frame objects for all the tabs.

#below is the tabs framework
for t in Tabs_names:
	Tabs_Frames[t] = Frame(tabs, height = tabheight, width = tabwidth)
	Tabs_Frames[t].pack(fill = 'both', expand = True, anchor = NW)


tabs.add(Tabs_Frames["Tab_Documents"], text = "Documents")
tabs.add(Tabs_Frames["Tab_Canonicizers"], text = "Canonicizers")
tabs.add(Tabs_Frames["Tab_EventDrivers"], text = "Event Drivers")
tabs.add(Tabs_Frames["Tab_EventCulling"], text = "Event Culling")
tabs.add(Tabs_Frames["Tab_AnalysisMethods"], text = "Analysis Methods")
tabs.add(Tabs_Frames["Tab_ReviewProcess"], text = "Review & Process")
#above is the tabs framework


#BELOW ARE CONFIGS FOR EACH TAB

#Note: the review & process tab is set-up first instead of last.

#####REVIEW & PROCESS TAB
#basic frames structure
Tab_ReviewProcess_Canonicizers = Frame(Tabs_Frames["Tab_ReviewProcess"])
Tab_ReviewProcess_Canonicizers.grid(
	row = 0, column = 0, columnspan = 3, sticky = "wens", padx = 10, pady = 10
)

Tab_ReviewProcess_EventDrivers = Frame(Tabs_Frames["Tab_ReviewProcess"])
Tab_ReviewProcess_EventDrivers.grid(
	row = 1, column = 0, sticky = "wens", padx = 10, pady = 10
)

Tab_ReviewProcess_EventCulling = Frame(Tabs_Frames["Tab_ReviewProcess"])
Tab_ReviewProcess_EventCulling.grid(
	row = 1, column = 1, sticky = "wens", padx = 10, pady = 10
)

Tab_ReviewProcess_AnalysisMethods = Frame(Tabs_Frames["Tab_ReviewProcess"])
Tab_ReviewProcess_AnalysisMethods.grid(
	row = 1, column = 2, sticky = "wens", padx = 10, pady = 10
)

for n in range(3):
	Tabs_Frames["Tab_ReviewProcess"].columnconfigure(n, weight = 1)
for n in range(2):
	Tabs_Frames["Tab_ReviewProcess"].rowconfigure(n, weight = 1)

#RP = ReviewProcess
#note: the buttons below (that redirect to corresponding tabs) have hard-coded tab numbers
Tab_RP_Canonicizers_Button = Button(
	Tab_ReviewProcess_Canonicizers,  text = "Canonicizers", font = ("helvetica", 16), relief = FLAT,
	command = lambda:switch_tabs(tabs, "choose", 1), activeforeground = "#333333")
Tab_RP_Canonicizers_Button.pack(anchor = "n")
Tab_RP_Canonicizers_Button.excludestyle = True

Tab_RP_Canonicizers_Listbox = Listbox(Tab_ReviewProcess_Canonicizers)
Tab_RP_Canonicizers_Listbox.pack(side = LEFT, expand = True, fill = BOTH)
Tab_RP_Canonicizers_Listbox_scrollbar = Scrollbar(
	Tab_ReviewProcess_Canonicizers, width = dpi_scrollbar_width,
	command = Tab_RP_Canonicizers_Listbox.yview)
Tab_RP_Canonicizers_Listbox_scrollbar.pack(side = RIGHT, fill = BOTH)
Tab_RP_Canonicizers_Listbox.config(yscrollcommand = Tab_RP_Canonicizers_Listbox_scrollbar.set)

Tab_RP_EventDrivers_Button = Button(
	Tab_ReviewProcess_EventDrivers,  text = "Event Drivers",font = ("helvetica", 16), relief = FLAT,
	command = lambda:switch_tabs(tabs, "choose", 2))
Tab_RP_EventDrivers_Button.pack(anchor = "n")
Tab_RP_EventDrivers_Button.excludestyle = True

Tab_RP_EventDrivers_Listbox = Listbox(Tab_ReviewProcess_EventDrivers)
Tab_RP_EventDrivers_Listbox.pack(side = LEFT, expand = True, fill = BOTH)
Tab_RP_EventDrivers_Listbox_scrollbar = Scrollbar(
	Tab_ReviewProcess_EventDrivers,  width = dpi_scrollbar_width, 
	command = Tab_RP_EventDrivers_Listbox.yview)
Tab_RP_EventDrivers_Listbox_scrollbar.pack(side = RIGHT, fill = BOTH)
Tab_RP_EventDrivers_Listbox.config(yscrollcommand = Tab_RP_EventDrivers_Listbox_scrollbar.set)
Tab_RP_EventCulling_Button = Button(
	Tab_ReviewProcess_EventCulling, text = "Event Culling",font = ("helvetica", 16), relief = FLAT,
	command = lambda:switch_tabs(tabs, "choose", 3))
Tab_RP_EventCulling_Button.pack(anchor = "n")
Tab_RP_EventCulling_Button.excludestyle = True

Tab_RP_EventCulling_Listbox = Listbox(Tab_ReviewProcess_EventCulling)
Tab_RP_EventCulling_Listbox.pack(side = LEFT, expand = True, fill = BOTH)
Tab_RP_EventCulling_Listbox_scrollbar = Scrollbar(
	Tab_ReviewProcess_EventCulling, width = dpi_scrollbar_width,
	command = Tab_RP_EventCulling_Listbox.yview)
Tab_RP_EventCulling_Listbox_scrollbar.pack(side = RIGHT, fill = BOTH)
Tab_RP_EventCulling_Listbox.config(yscrollcommand = Tab_RP_EventCulling_Listbox_scrollbar.set)
Tab_RP_AnalysisMethods_Button = Button(
	Tab_ReviewProcess_AnalysisMethods, text = "Analysis Methods",font = ("helvetica", 16), relief = FLAT,
	command = lambda:switch_tabs(tabs, "choose", 4))
Tab_RP_AnalysisMethods_Button.pack(anchor = "n")
Tab_RP_AnalysisMethods_Button.excludestyle = True

Tab_RP_AnalysisMethods_Listbox = ttk.Treeview(Tab_ReviewProcess_AnalysisMethods, columns = ("AM", "DF"))
Tab_RP_AnalysisMethods_Listbox.column("#0", width = 0, stretch = NO)
Tab_RP_AnalysisMethods_Listbox.heading("AM", text = "Method", anchor = W)
Tab_RP_AnalysisMethods_Listbox.heading("DF", text = "Distance", anchor = W)

Tab_RP_AnalysisMethods_Listbox.pack(side = LEFT, expand = True, fill = BOTH)
Tab_RP_AnalysisMethods_Listbox_scrollbar = Scrollbar(
	Tab_ReviewProcess_AnalysisMethods,
	width = dpi_scrollbar_width,
	command = Tab_RP_AnalysisMethods_Listbox.yview)
Tab_RP_AnalysisMethods_Listbox_scrollbar.pack(side = RIGHT, fill = BOTH)
Tab_RP_AnalysisMethods_Listbox.config(yscrollcommand = Tab_RP_AnalysisMethods_Listbox_scrollbar.set)
Tab_RP_Process_Button = Button(Tabs_Frames["Tab_ReviewProcess"], text = "Process", width = 25)

# button command see after documents tab.

Tab_RP_Process_Button.grid(row = 2, column = 0, columnspan = 3, sticky = "se", pady = 5, padx = 20)

Tab_RP_Process_Button.bind("<Map>",
	lambda event, a = [], lb = [Tab_RP_EventDrivers_Listbox, Tab_RP_AnalysisMethods_Listbox],
	labels = [Tab_RP_EventDrivers_Button, Tab_RP_AnalysisMethods_Button],
	button = Tab_RP_Process_Button:run_experiment("", lb, labels, button))




############### DOCUMENTS TAB ####################

Tab_Documents_Language_label = Label(
	Tabs_Frames["Tab_Documents"],text = "Language", font = ("helvetica", 15), anchor = 'nw'
)
Tab_Documents_Language_label.grid(row = 1, column = 0, sticky = 'NW', pady = (10, 5))

for n in range(10):
	if n == 5 or n == 8:
		w = 1
		Tabs_Frames["Tab_Documents"].columnconfigure(0, weight = 1)

	else: w = 0
	Tabs_Frames["Tab_Documents"].rowconfigure(n, weight = w)


# !!! to allow for per-document language settings,
# also change the spacy (canonicizer) module's langauge module loading functions.
#documents-language selection
analysisLanguage = StringVar()
analysisLanguage.set("English")
#may need a lookup function for the options below
analysisLanguageOptions = ["Arabic (ISO-8859-6)", "Chinese (GB2123)", "English"]
Tab_Documents_language_dropdown = OptionMenu(
	Tabs_Frames["Tab_Documents"], analysisLanguage, *analysisLanguageOptions
)
Tab_Documents_language_dropdown.config(width = dpi_language_dropdown_width)
Tab_Documents_language_dropdown['anchor'] = 'nw'
Tab_Documents_language_dropdown.grid(row = 2, column = 0, sticky = 'NW')


analysisLanguage.trace_add("write",
					lambda v1, v2, v3, p = "language", stringvar = analysisLanguage:
					set_API_global_parameters(p, stringvar))


#documents-unknown authors
Tab_Documents_UnknownAuthors_label =\
	Label(Tabs_Frames["Tab_Documents"], text = "Unknown Authors", font = ("helvetica", 15), anchor = 'nw')
Tab_Documents_UnknownAuthors_label.grid(row = 4, column = 0, sticky = "W", pady = (10, 5))


Tab_Documents_UnknownAuthors_Frame =\
	Frame(Tabs_Frames["Tab_Documents"])
Tab_Documents_UnknownAuthors_Frame.grid(row = 5, column = 0, sticky = "wnse")


Tab_Documents_UnknownAuthors_listbox =\
	Listbox(Tab_Documents_UnknownAuthors_Frame, width = "100")
Tab_Documents_UnknownAuthors_listscrollbar =\
	Scrollbar(Tab_Documents_UnknownAuthors_Frame, width = dpi_scrollbar_width)
#loop below: to be removed

Tab_Documents_UnknownAuthors_listbox.config(
	yscrollcommand = Tab_Documents_UnknownAuthors_listscrollbar.set
)
Tab_Documents_UnknownAuthors_listscrollbar.config(
	command = Tab_Documents_UnknownAuthors_listbox.yview
)


Tab_Documents_UnknownAuthors_listbox.pack(side = LEFT, fill = BOTH, expand = True)
Tab_Documents_UnknownAuthors_listscrollbar.pack(side = RIGHT, fill = BOTH, padx = (0, 30))

Tab_Documents_doc_buttons = Frame(Tabs_Frames["Tab_Documents"])
Tab_Documents_doc_buttons.grid(row = 6, column = 0, sticky = "W")
Tab_Documents_UnknownAuthors_AddDoc_Button = Button(
	Tab_Documents_doc_buttons, text = "Add Document", width = "16",
	command = lambda:file_add_remove(
		"Add a document to Unknown Authors", Tab_Documents_UnknownAuthors_listbox, False, "add")
	)
Tab_Documents_UnknownAuthors_RmvDoc_Button = Button(
	Tab_Documents_doc_buttons, text = "Remove Document", width = "16",
	command = lambda:file_add_remove(
		None, Tab_Documents_UnknownAuthors_listbox, False, "remove")
	)

Tab_Documents_UnknownAuthors_AddDoc_Button.grid(row = 1, column = 1, sticky = "W")
Tab_Documents_UnknownAuthors_RmvDoc_Button.grid(row = 1, column = 2, sticky = "W")

#documents-known authors
Tab_Documents_KnownAuthors_label = Label(
	Tabs_Frames["Tab_Documents"], text = "Known Authors", font = ("helvetica", 15), anchor = 'nw'
)
Tab_Documents_KnownAuthors_label.grid(row = 7, column = 0, sticky = "W", pady = (10, 5))


Tab_Documents_KnownAuthors_Frame = Frame(Tabs_Frames["Tab_Documents"])
Tab_Documents_KnownAuthors_Frame.grid(row = 8, column = 0, sticky = "wnse")


Tab_Documents_KnownAuthors_listbox = Listbox(Tab_Documents_KnownAuthors_Frame, width = "100")
Tab_Documents_KnownAuthors_listscroller = Scrollbar(Tab_Documents_KnownAuthors_Frame, width = dpi_scrollbar_width)

Tab_Documents_KnownAuthors_listbox.config(
	yscrollcommand = Tab_Documents_KnownAuthors_listscroller.set
)
Tab_Documents_KnownAuthors_listscroller.config(command = Tab_Documents_KnownAuthors_listbox.yview)


Tab_Documents_KnownAuthors_listbox.pack(side = LEFT, fill = BOTH, expand = True)
Tab_Documents_KnownAuthors_listscroller.pack(side = RIGHT, fill = BOTH, padx = (0, 30))

#These are known authors
Tab_Documents_knownauth_buttons = Frame(Tabs_Frames["Tab_Documents"])
Tab_Documents_knownauth_buttons.grid(row = 9, column = 0, sticky = "W")
Tab_Documents_KnownAuthors_AddAuth_Button = Button(
	Tab_Documents_knownauth_buttons, text = "Add Author", width = "15",
	command = lambda:authorsList(Tab_Documents_KnownAuthors_listbox, 'add'))
Tab_Documents_KnownAuthors_EditAuth_Button = Button(
	Tab_Documents_knownauth_buttons, text = "Edit Author", width = "15",
	command = lambda:authorsList(Tab_Documents_KnownAuthors_listbox, 'edit'))
Tab_Documents_KnownAuthors_RmvAuth_Button = Button(
	Tab_Documents_knownauth_buttons, text = "Remove Author", width = "15",
	command = lambda:authorsList(Tab_Documents_KnownAuthors_listbox, "remove"))

Tab_Documents_KnownAuthors_AddAuth_Button.grid(row = 1, column = 1, sticky = "W")
Tab_Documents_KnownAuthors_EditAuth_Button.grid(row = 1, column = 2, sticky = "W")
Tab_Documents_KnownAuthors_RmvAuth_Button.grid(row = 1, column = 3, sticky = "W")



selected_parameters = {"known_authors": known_authors,
					"UnknownAuthors": Tab_Documents_UnknownAuthors_listbox,
					"Canonicizers": Tab_RP_Canonicizers_Listbox,
					"EventDrivers": Tab_RP_EventDrivers_Listbox,
					"EventCulling": Tab_RP_EventCulling_Listbox,
					"AnalysisMethods": Tab_RP_AnalysisMethods_Listbox}

Tab_RP_Process_Button.config(\
	command = lambda lb = [Tab_RP_EventDrivers_Listbox, Tab_RP_AnalysisMethods_Listbox],\
		labels = [Tab_RP_EventDrivers_Button, Tab_RP_AnalysisMethods_Button],\
			button = Tab_RP_Process_Button:run_experiment(selected_parameters, lb, labels, button, True))




# This function creates canonicizers, event drivers, event culling, and analysis methods tabs.
def create_module_tab(tab_frame: Frame, available_content: list, parameters_content = None, **extra):
	"""
	creates a tab of available-buttons-selected-description tab.
	See PyGAAP_developer_manual.md for list of major widgets/frames.
	tab_frame: the top-level frame in the notebook tab
	available_content: list of label texts for the available modules to go in.
	button_functions: list of buttons in the middle frame
	selected_content: list of names of listboxes for the selected modules to go in.
	parameters_content: governs how the parameters frame is displayed
	description_content: governs how the descriptions frame is displayed.
	"""
	assert len(set(available_content)) == len(available_content), \
		"Bug: create_modules_tab: available_content can't have repeated names."
	global dpi_scrollbar_width

	# Layer 0
	objects = dict() # objects in the frame
	tab_frame.columnconfigure(0, weight = 1)
	tab_frame.rowconfigure(0, weight = 1)

	topheight = 0.7
	bottomheight = 1-topheight
	
	objects["top_frame"] = Frame(tab_frame)
	objects["top_frame"].place(relx = 0, rely = 0, relwidth = 1, relheight = topheight)

	# Layer 1: main frames
	objects["available_frame"] = Frame(objects["top_frame"])
	objects["available_frame"].place(relx = 0, rely = 0, relwidth = 0.3, relheight = 1)

	objects["buttons_frame"] = Frame(objects["top_frame"])
	objects["buttons_frame"].place(relx = 0.3, rely = 0, relwidth = 0.1, relheight = 1)

	objects["selected_frame"] = Frame(objects["top_frame"])
	objects["selected_frame"].place(relx = 0.4, rely = 0, relwidth = 0.3, relheight = 1)

	objects["parameters_frame"] = Frame(objects["top_frame"])
	objects["parameters_frame"].place(relx = 0.7, rely = 0, relwidth = 0.3, relheight = 1)

	objects["description_frame"] = Frame(tab_frame)
	objects["description_frame"].place(relx = 0, rely = topheight, relheight = bottomheight, relwidth = 1)

	# Layer 2: objects in main frames
	counter = 0
	objects["available_listboxes"] = []
	# each entry in objects["available_listboxes"]:
	# [frame, label, listbox, scrollbar]
	objects["available_frame"].columnconfigure(0, weight = 1)

	listboxAvList = [] # list of "available" listboxes to pass into select_modules() later.
	for name in available_content:
		# "Available" listboxes
		objects["available_listboxes"].append(
			[Frame(objects["available_frame"])]
		)
		objects["available_listboxes"][-1][0].grid(row = counter, column = 0, sticky = "swen")

		objects["available_frame"].rowconfigure(counter, weight = 1)

		objects["available_listboxes"][-1].append(
			Label(objects["available_listboxes"][-1][0], text = name, font = ("Helvetica", 15))
		)
		objects["available_listboxes"][-1][1].pack(pady = (10, 5), side = TOP, anchor = NW)

		objects["available_listboxes"][-1].append(
			Listbox(objects["available_listboxes"][-1][0], exportselection = False)
		)
		objects["available_listboxes"][-1][2].pack(expand = True, fill = BOTH, side = LEFT)
		listboxAvList.append(objects["available_listboxes"][-1][2])

		objects["available_listboxes"][-1].append(
			Scrollbar(objects["available_listboxes"][-1][0],
			width = dpi_scrollbar_width, command = objects["available_listboxes"][-1][2].yview)
		)
		objects["available_listboxes"][-1][3].pack(side = RIGHT, fill = BOTH)
		objects["available_listboxes"][-1][2].config(
			yscrollcommand = objects["available_listboxes"][-1][3].set
		)

		counter += 1   
	
	objects["selected_listboxes"] = []
	objects["selected_listboxes"].append([Frame(objects["selected_frame"])])
	objects["selected_listboxes"][-1][0].pack(expand = True, fill = BOTH)		

	objects["selected_listboxes"][-1].append(
		Label(objects["selected_listboxes"][-1][0],
		text = "Selected", font = ("Helvetica", 15))
	)
	objects["selected_listboxes"][-1][1].pack(pady = (10, 5), side = TOP, anchor = NW)

	if parameters_content == "AnalysisMethods":
		# for analysis methods, use a Treeview object to display selections.
		objects["selected_listboxes"][-1].append(ttk.Treeview(objects["selected_listboxes"][-1][0],
			columns = ("AM", "DF")))
		objects["selected_listboxes"][-1][2].column("#0", width = 0, stretch = NO)
		objects["selected_listboxes"][-1][2].heading("AM", text = "Method", anchor = W)
		objects["selected_listboxes"][-1][2].heading("DF", text = "Distance", anchor = W)
		objects["selected_listboxes"][-1][2].pack(expand = True, fill = BOTH, side = LEFT)

		objects["selected_listboxes"][-1].append(
			Scrollbar(objects["selected_listboxes"][-1][0], width = dpi_scrollbar_width,
			command = objects["selected_listboxes"][-1][2].yview))
		objects["selected_listboxes"][-1][3].pack(side = RIGHT, fill = BOTH)
		objects["selected_listboxes"][-1][2].config(yscrollcommand = objects["selected_listboxes"][-1][3].set)

	else:
		# for canonicizers, event cullers/drivers, use a Listbox to display selections.
		objects["selected_listboxes"][-1].append(Listbox(objects["selected_listboxes"][-1][0]))
		objects["selected_listboxes"][-1][2].pack(expand = True, fill = BOTH, side = LEFT)

		objects["selected_listboxes"][-1].append(
			Scrollbar(objects["selected_listboxes"][-1][0], width = dpi_scrollbar_width,
			command = objects["selected_listboxes"][-1][2].yview))
		objects["selected_listboxes"][-1][3].pack(side = RIGHT, fill = BOTH)
		objects["selected_listboxes"][-1][2].config(yscrollcommand = objects["selected_listboxes"][-1][3].set)

	Label(objects["buttons_frame"], text = "", height = 2).pack()
	# empty label to create space above buttons
	counter = 0

	if parameters_content == "Canonicizers":
		extra.get("canonicizers_format")
		extra.get("canonicizers_format").set("All")
		canonicizer_format_options = ["All", "Generic", "Doc", "PDF", "HTML"]
		objects["Canonicizers_format"] = OptionMenu(objects["buttons_frame"],
			extra.get("canonicizers_format"), *canonicizer_format_options)
		objects["Canonicizers_format"].config(width = dpi_option_menu_width)
		objects["Canonicizers_format"].pack(anchor = W)
		counter = 1
	

	RP_listbox = extra.get("RP_listbox")
	# this is the listbox in the "Review and process" page to update when
	# the user adds a module in previous pages.

	
	objects["buttons_add"] = Button(
		objects["buttons_frame"], width = "11", text = ">>Add", anchor = 's',
		command = lambda:select_modules(
			listboxAvList,
			[objects["selected_listboxes"][0][2], RP_listbox],
			"add",
			module_type = parameters_content
			)
		)
	objects["buttons_add"].pack(anchor = CENTER, fill = X)

	objects["buttons_remove"] = Button(
		objects["buttons_frame"], width = "11", text = "<<Remove", anchor = 's',
		command = lambda:select_modules(
			None, [objects["selected_listboxes"][0][2], RP_listbox], "remove",
			module_type = parameters_content,
			)
		)
	objects["buttons_remove"].pack(anchor = CENTER, fill = X)

	objects["buttons_clear"] = Button(
		objects["buttons_frame"], width = "11", text = "Clear", anchor = 's',
		command = lambda:select_modules(
			None,
			[objects["selected_listboxes"][0][2], RP_listbox],
			"clear",
			module_type = parameters_content,
			)
		)
	objects["buttons_clear"].pack(anchor = CENTER, fill = X)


	objects["description_label"] = Label(
		objects["description_frame"], text = "Description", font = ("helvetica", 15), anchor = 'nw'
	)
	objects["description_label"].pack(anchor = NW, pady = (20, 5))
	objects["description_box"] = Text(
		objects["description_frame"], bd = dpi_description_box_border,
		relief = "groove", bg = topwindow.cget("background"), state = DISABLED
	)
	objects["description_box"].pack(fill = BOTH, expand = True, side = LEFT)
	objects["description_box_scrollbar"] = Scrollbar(
		objects["description_frame"], width = dpi_scrollbar_width, command = objects["description_box"].yview
	)
	objects["description_box"].config(yscrollcommand = objects["description_box_scrollbar"].set)
	objects["description_box_scrollbar"].pack(side = LEFT, fill = BOTH)

	if parameters_content == "EventDrivers" or parameters_content == "EventCulling":
		displayed_parameters = extra.get("displayed_parameters")
		objects['parameters_label'] = Label(
			objects["parameters_frame"], text = "Parameters", font = ("helvetica", 15), anchor = NW
		)
		objects['parameters_label'].pack(pady = (10, 5),anchor = W)

		objects['displayed_parameters_frame'] = Frame(objects["parameters_frame"])
		objects['displayed_parameters_frame'].pack(padx = 20, pady = 20)


		objects["selected_listboxes"][-1][2].bind("<<ListboxSelect>>",
			lambda event, frame = objects['displayed_parameters_frame'],
			lb = objects["selected_listboxes"][-1][2],
			dp = displayed_parameters:
			find_parameters(frame, lb, dp, module_type = parameters_content), add = "+"
		)
		objects["selected_listboxes"][-1][2].bind("<<Unmap>>",
			lambda event, frame = objects['displayed_parameters_frame'],
			lb = objects["selected_listboxes"][-1][2],
			dp = displayed_parameters:
			find_parameters(frame, lb, dp, module_type = parameters_content), add = "+"
		)
			
	elif parameters_content == "AnalysisMethods":
		displayed_parameters = extra.get("displayed_parameters")
		objects['parameters_label'] = Label(
			objects["parameters_frame"], text = "Parameters", font = ("helvetica", 15), anchor = NW
		)
		objects['parameters_label'].pack(pady = (10, 5),anchor = W)

		objects['displayed_parameters_frame'] = Frame(objects["parameters_frame"])
		objects['displayed_parameters_frame'].pack(padx = 20, pady = 20)
		# bind treeview widget so the description updates when an item is selected.
		objects["selected_listboxes"][0][2].bind(
			"<<TreeviewSelect>>",
			lambda event, d = objects["description_box"],
			lb = objects["selected_listboxes"][0][2],
			di = backend_API.analysisMethods:
			find_description(d, lb, di), add = "+"
		)
		
		objects["selected_listboxes"][-1][2].bind("<<TreeviewSelect>>",\
			lambda event, frame = objects['displayed_parameters_frame'],
			lb = objects["selected_listboxes"][-1][2],
			dp = displayed_parameters:
			find_parameters(frame, lb, dp, module_type = parameters_content), add = "+")


	if parameters_content != "AnalysisMethods":
		API_dict = {
			"Canonicizers": backend_API.canonicizers,
			"EventDrivers": backend_API.eventDrivers,
			"EventCulling": backend_API.eventCulling
		}
		for f in objects["available_listboxes"]:
			f[2].bind("<<ListboxSelect>>",
				lambda event, t = objects["description_box"],
				l = f[2], d = API_dict[parameters_content]:
				find_description(t, l, d), add = "+"
			)
		for f in objects["selected_listboxes"]:
			f[2].bind("<<ListboxSelect>>",
				lambda event, t = objects["description_box"],
				l = f[2], d = API_dict[parameters_content]:
				find_description(t, l, d), add = "+"
			)
	else:
		objects["available_listboxes"][0][2].bind(
			"<<ListboxSelect>>",
			lambda event,
			lbAv = objects["available_listboxes"][0][2],
			lbOp = objects["available_listboxes"][1][2]:
			check_DF_listbox(lbAv, lbOp), add = "+"
		)
		objects["available_listboxes"][0][2].bind(
			"<<ListboxSelect>>",
			lambda event,
			t = objects["description_box"],
			l = objects["available_listboxes"][0][2],
			d = backend_API.analysisMethods:
			find_description(t, l, d), add = "+")
		objects["available_listboxes"][1][2].bind(
			"<<ListboxSelect>>",
			lambda event,
			t = objects["description_box"],
			l = objects["available_listboxes"][1][2],
			d = backend_API.distanceFunctions:
			find_description(t, l, d), add = "+")

	return objects

generated_widgets = dict()

CanonicizerFormat = StringVar()
generated_widgets['Canonicizers'] = create_module_tab(
	Tabs_Frames["Tab_Canonicizers"],
	["Canonicizers"],
	"Canonicizers",
	canonicizers_format = CanonicizerFormat,
	RP_listbox = Tab_RP_Canonicizers_Listbox)

Tab_EventDrivers_parameters_displayed = []
generated_widgets['EventDrivers'] = create_module_tab(
	Tabs_Frames["Tab_EventDrivers"],
	["Event Drivers"],
	"EventDrivers",
	displayed_parameters = Tab_EventDrivers_parameters_displayed,
	RP_listbox = Tab_RP_EventDrivers_Listbox)

Tab_EventCulling_parameters_displayed = []
generated_widgets['EventCulling'] = create_module_tab(
	Tabs_Frames["Tab_EventCulling"],
	["Event Culling"],
	"EventCulling",
	displayed_parameters = Tab_EventCulling_parameters_displayed,
	RP_listbox = Tab_RP_EventCulling_Listbox)

Tab_AnalysisMethods_parameters_displayed = []
generated_widgets['AnalysisMethods'] = create_module_tab(
	Tabs_Frames["Tab_AnalysisMethods"],
	["Analysis Methods",
	"Distance Functions"],
	"AnalysisMethods",
	RP_listbox = Tab_RP_AnalysisMethods_Listbox,
	displayed_parameters = Tab_AnalysisMethods_parameters_displayed)

def load_modules_to_GUI(startup=False):

	# first clear everthing in listboxes.
	# the "DistanceFunctions" Treeview is in the "AnalysisMethods" tkinter frame.
	for module_type in ["Canonicizers", "EventDrivers", "EventCulling"]:
		generated_widgets[module_type]["available_listboxes"][0][2].delete(0, END)
		generated_widgets[module_type]["selected_listboxes"][0][2].delete(0, END)
	for listbox in [Tab_RP_Canonicizers_Listbox, Tab_RP_EventDrivers_Listbox, Tab_RP_EventCulling_Listbox]:
		listbox.delete(0, END)

	Tab_RP_AnalysisMethods_Listbox.delete(*Tab_RP_AnalysisMethods_Listbox.get_children())
	generated_widgets["AnalysisMethods"]["available_listboxes"][1][2].delete(0, END)
	generated_widgets["AnalysisMethods"]["available_listboxes"][0][2].delete(0, END)
	amdf = generated_widgets["AnalysisMethods"]["selected_listboxes"][0][2]
	amdf.delete(*amdf.get_children())

	try:
		# adding items to listboxes from the backend_API.
		for canonicizer in sorted(list(backend_API.canonicizers.keys())):
			generated_widgets["Canonicizers"]["available_listboxes"][0][2].insert(END, canonicizer)
		for driver in sorted(list(backend_API.eventDrivers.keys())):
			generated_widgets["EventDrivers"]["available_listboxes"][0][2].insert(END, driver)
		for distancefunc in sorted(list(backend_API.distanceFunctions.keys())):
			assert distancefunc != "NA", 'Distance Function cannot have a name of "NA" ' \
			+ '(Reserved for Analysis methods that do not use a distance function).\n' \
			+ 'Please check the file containing the definition of the distance function class, ' \
			+ 'most likely in or imported to DistanceFunction.py,\nand change the return of displayName().'
			generated_widgets["AnalysisMethods"]["available_listboxes"][1][2].insert(END, distancefunc)
		for culling in sorted(list(backend_API.eventCulling.keys())):
			generated_widgets["EventCulling"]["available_listboxes"][0][2].insert(END, culling)
		for method in sorted(list(backend_API.analysisMethods.keys())):
			generated_widgets["AnalysisMethods"]["available_listboxes"][0][2].insert(END, method)
		if startup == False: status_update("Modules reloaded")
		return
	except Exception as e:
		error_window = Toplevel()
		error_window.geometry(dpi_process_window_geometry_finished)
		error_window.title("Error while loading modules")
		error_text_field = Text(error_window)
		error_text_field.pack(fill=BOTH, expand=True)
		
		error_text = "An error occurred while loading the modules:\n\n"
		error_text += str(exc_info()[0]) + "\n" + str(exc_info()[1]) + "\n" + str(exc_info()[2].tb_frame.f_code)
		error_text += "\n\nDevelopers: you can reload the modules by going to the "\
			+ "Canonicizers tab, pressing the right ctrl key, and clicking the "\
			+ "\"Reload all modules\" button."
		error_text_field.insert(END, error_text)
		error_window.after(1200, error_window.lift)
		if startup == False: status_update("Error while loading modules, see pop-up window.")
		#exc_type, exc_obj, exc_tb = exc_info()
		return
	#######

load_modules_to_GUI(True)

def reload_modules():
	global backend_API
	for module_type in [
		"generics.AnalysisMethod", "generics.Canonicizer", "generics.DistanceFunction",
		"generics.EventCulling", "generics.EventDriver"
	]:
		for external_module in sys_modules[module_type].external_modules:
			sys_modules.pop(external_module)
		sys_modules.pop(module_type)
	sys_modules.pop("backend.API")

	from backend.API import API
	backend_API = API("place-holder")
	load_modules_to_GUI()


reload_button_shown=[]
topwindow.bind_all(
	"<Control_R>",
	lambda event,
		fr=generated_widgets["Canonicizers"]["parameters_frame"],
		b=reload_button_shown:
	reload_modules_button(fr, b)
)

if GUI_debug >= 2:
	_ = 0
	for j in generated_widgets:
		_ += len(j)
	print("size of 'generated_widgets' dict:", _)



#ABOVE ARE THE CONFIGS FOR EACH TAB

bottomframe = Frame(topwindow, height = 150, width = 570)
bottomframe.columnconfigure(0, weight = 1)
bottomframe.rowconfigure(1, weight = 1)
bottomframe.grid(pady = 10, row = 1, sticky = 'swen')

for c in range(6):
	bottomframe.columnconfigure(c, weight = 10)

finish_button = Button(bottomframe, text = "Finish & Review", command = lambda:switch_tabs(tabs, "choose", 5))
#note: this button has a hard-coded tab number
previous_button = Button(bottomframe, text = "<< Previous", command = lambda:switch_tabs(tabs, "previous"))
next_button = Button(bottomframe, text = "Next >>", command = lambda:switch_tabs(tabs, "next"))
notes_button = Button(bottomframe, text = "Notes", command = notepad)

Label(bottomframe).grid(row = 0, column = 0)
Label(bottomframe).grid(row = 0, column = 5)

previous_button.grid(row = 0, column = 1, sticky = 'swen')
next_button.grid(row = 0, column = 2, sticky = 'swen')
notes_button.grid(row = 0, column = 3, sticky = 'swen')
finish_button.grid(row = 0, column = 4, sticky = 'swen')

statusbar = Frame(topwindow, bd = 1, relief = SUNKEN)
statusbar.grid(row = 2, sticky = "swe")

welcome_message = "By David Berdik and Michael Fang. Version date: %s." %(Constants.versiondate)
statusbar_label = Label(statusbar, text = welcome_message, anchor = W)
statusbar_label.pack(anchor = "e")
statusbar_label.after(3000, lambda:status_update("", welcome_message))



def change_style(parent_widget):
	"""This changes the colors of the widgets."""
	if GUI_debug >= 4: print("change_style(parent_widget = %s)"%(parent_widget))
	if len(parent_widget.winfo_children()) == 0: return None
	for widget in parent_widget.winfo_children():
		if isinstance(widget, Button) and "excludestyle" not in widget.__dict__:
			widget.configure(
				activebackground = styles[style_choice]["accent_color_mid"],
				bg = styles[style_choice]["accent_color_mid"],
				foreground = styles[style_choice]["text"]
			)
		elif isinstance(widget, Scrollbar): widget.configure(
			background = styles[style_choice]["accent_color_mid"]
		)
		elif isinstance(widget, Listbox):
			widget.configure(
				selectbackground = styles[style_choice]["accent_color_mid"],
				selectforeground = styles[style_choice]["text"]
			)
		elif isinstance(widget, OptionMenu):
			widget.configure(
				bg = styles[style_choice]["accent_color_mid"],
				activebackground = styles[style_choice]["accent_color_light"]
			)
		else: change_style(widget)
	ttk_style.map(
		'Treeview',
		background = [('selected', styles[style_choice]["accent_color_mid"])],
		foreground = [('selected', "#000000")]
	)

change_style(topwindow)

def change_style_live(themeString):
	"""This calls the change_style function to enable theme switching in the menu bar."""
	if GUI_debug >= 3: print("change_style_live(themeString = %s)"%(themeString))
	global style_choice
	style_choice = themeString
	for entry in range(len(known_authors_list)):
		if known_authors_list[entry] != -1:
			Tab_Documents_KnownAuthors_listbox.itemconfig(
				entry,
				background = styles[style_choice]["accent_color_light"],
				selectbackground = styles[style_choice]["accent_color_mid"]
			)
	change_style(topwindow)

if platform != "win32":
	pass
	#p.join()
pipe_from.send("Starting GUI")
pipe_from.send(0)

#starts app
topwindow.mainloop()
