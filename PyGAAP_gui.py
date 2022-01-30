# PyGaap is the Python port of JGAAP, Java Graphical Authorship Attribution Program by Patrick Juola
# For JGAAP see https://evllabs.github.io/JGAAP/
# 
# !! See PyGaap_gui_functions_map.txt for a rough outline of Tkinter widgets and function calls.
#
versiondate="2022.01.30"
#Michael Fang, Boston University.

debug=0 # debug level. 0 = no debug info. 3 = all function calls

from copy import deepcopy
from datetime import datetime
#REQUIRED MODULES BELOW. USE pip OR pip3 IN YOUR TERMINAL TO INSTALL.
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename

from backend.API import API
from backend.CSVIO import readDocument
from backend.Document import Document

topwindow=Tk() #this is the top-level window when you first open PyGAAP
topwindow.title("PyGAAP (GUI)")
try:topwindow.tk.call('wm', 'iconphoto', topwindow._w, PhotoImage(file='./applogo.png'))
except:pass

topwindow.rowconfigure(0, weight=1)
topwindow.rowconfigure(1, weight=0, minsize=50)
topwindow.columnconfigure(0, weight=1)

################### AESTHETICS
dpi=topwindow.winfo_fpixels('1i')
dpi_setting=None
if dpi>72:
    if debug>=2: print("1x UI scale")
    dpi_setting=1
    topwindow.geometry("1000x670")
    #topwindow.minsize(height=400, width=600)
    scrollbar_width=16
else:
    if debug>=2: print("2x UI scale")
    dpi_setting=2
    topwindow.geometry("2000x1150")
    #topwindow.minsize(height=800, width=1100)
    scrollbar_width=28

if dpi_setting==None: raise ValueError("Unknown DPI setting %s."% (str(dpi_setting)))

if dpi_setting==1:
    dpi_processWindowGeometry="200x100"
    dpi_progressBarLength=200
    dpi_aboutPageGeometry="600x300"
    dpi_authorWindowGeometry="550x340"
    dpi_treeviewEntryHeight=1
    dpi_processWindowGeometry_finished="700x900"

    ttkstyle= ttk.Style()
    ttkstyle.configure('Treeview', rowheight=20)

elif dpi_setting==2:
    dpi_processWindowGeometry="500x200"
    dpi_progressBarLength=400
    dpi_aboutPageGeometry="1200x600"
    dpi_authorWindowGeometry="1170x590"
    dpi_treeviewEntryHeight=2
    dpi_processWindowGeometry_finished="1300x1100"

    ttkstyle= ttk.Style()
    ttkstyle.configure('Treeview', rowheight=35)
    
style_choice="JGAAP_blue"
styles=dict()
styles["JGAAP_blue"]={"accent_color_dark":"#7eedfc", "accent_color_mid":"#c9f6fc", "accent_color_light":"#e0f9fc"}
styles["PyGAAP_pink"]={"accent_color_dark": "#e0b5e5", "accent_color_mid":"#f2e1f4", "accent_color_light":"#f7e5f9"}

if debug>=3: print("Accent colors:", styles[style_choice]["accent_color_dark"], styles[style_choice]["accent_color_mid"], styles[style_choice]["accent_color_mid"])
ttkstyle.map('Treeview', background=[('selected', styles[style_choice]["accent_color_mid"])], foreground=[('selected', "#000000")])

###############################
#### BACKEND API ##########################
backendAPI=API("docs lmao")
##########################################
###############################

#BELOW ARE UTILITY FUNCTIONS
def todofunc(): #place holder "to-do function"
    print("To-do function")
    return None

statusbar=None
statusbar_label=None
def status_update(displayed_text, ifsame=None):
    """
    updates the text in the status bar.
    ifsame: only update the text if the text is the same as this string.
    """
    if debug>=3: print("status_update(%s, condition=%s)" %(displayed_text, ifsame))
    global statusbar
    global statusbar_label
    if ifsame==None: # do not check if the status text is the same as "ifsame"
        if statusbar_label['text']==displayed_text:
            statusbar_label.config(text=" ")
            statusbar_label.after(20, lambda t=displayed_text:status_update(t))
        else: statusbar_label.config(text=displayed_text)
    else: # only change label if the text is the same as "ifsame"
        if statusbar_label['text']==ifsame:
            statusbar_label.config(text=displayed_text)
    return None

def select_modules(ListBoxAv: Listbox, ListBoxOp: list, function: str):
    """Used by Event Drivers, Event culling etc to add/remove/clear selected modules.
    Needs to check if module is already added."""
    #ListBoxAv: "listbox Available", listbox to choose from
    #ListBoxOp: "listbox operate-on", a list of listboxes to modify. Includes the one in the corresponding tab and the
    #   listbox in the Review & Process tab.
    #module: is the return of listbox.curselection()
    #function: can be "clear", "remove", or "add"
    if function=="clear":
        if debug>1: print("select_modules: clear")
        for listboxmember in ListBoxOp:
            if type(listboxmember)==Listbox: listboxmember.delete(0, END)
            else: listboxmember.delete(*listboxmember.get_children())
        return None
    elif function=="remove":
        if debug>1: print("select_modules: remove")
        try:
            if type(ListBoxOp[0])==Listbox: removed=ListBoxOp[0].curselection()
            else:
                removed=ListBoxOp[0].selection()
            assert len(removed)>0
            status_update("")
        except:
            if debug>0: print("remove from list: nothing selected or empty list.")
            status_update("Nothing selected.")
            return None
        for listboxmember in ListBoxOp:
            listboxmember.delete(removed)
        return None
    elif function=="add":
        if debug>1: print("select_modules: add")
        try:
            if type(ListBoxOp[0])==Listbox: selectedmodule=ListBoxAv[0].get(ListBoxAv[0].curselection())
            elif len(ListBoxAv)>1 and ListBoxAv[1]['state']==DISABLED: selectedmodule=selectedmodule=(ListBoxAv[0].get(ListBoxAv[0].curselection()), "NA")
            else: selectedmodule=[ListBoxAv[0].get(ListBoxAv[0].curselection()), ListBoxAv[1].get(ListBoxAv[1].curselection())]
            status_update("")
        except:
            status_update("Nothing selected or missing selection.")
            if debug>0: print("add to list: nothing selected")
            return None
        for listboxmember in ListBoxOp:
            if type(ListBoxOp[0])==Listbox:
                listboxmember.insert(END, selectedmodule)
            else:
                listboxmember.insert(parent="", index=END, text="", value=selectedmodule)
    else:
        raise ValueError("Bug: All escaped in 'select_modules' function.")
    return None

def CheckDistanceFunctionsListbox(lbAv, lbOp: Listbox):
    """Enable or disable the 'Distance Functions' listbox depending on whether the item selected in 'Analysis Methods' allows using DFs."""
    if backendAPI.analysisMethods[lbAv.get(lbAv.curselection())].__dict__.get("_NoDistanceFunction_")==True: lbOp.config(state=DISABLED)
    else: lbOp.config(state=NORMAL)

def find_description(desc: Text, listbox: Listbox or ttk.Treeview, APIdict: dict):
    """find description of a module."""
    # desc: the tkinter Text object to display the description.
    # listbox: the Listbox or Treeview object to get the selection from
    # APIdict: the API dictionary that contains the listed method classes from the backend.
    #   example -- APIdict could be backendAPI.canonicizers.
    
    if type(listbox)==Listbox:
        try:
            name=listbox.get(listbox.curselection())
            description_string=name+":\n"+APIdict[name].displayDescription()
        except: description_string="No description" # the module does not have description.
    if type(listbox)==ttk.Treeview:
        am_name=listbox.item(listbox.selection())["values"][0]
        df_name=listbox.item(listbox.selection())["values"][1]
        am_d, df_d="No description", "No description"
        try: am_d=backendAPI.analysisMethods[am_name].displayDescription()
        except: pass
        try: df_d=backendAPI.analysisMethods[df_name].displayDescription()
        except: pass
        if df_name=="NA": df_d="Not applicable"
        description_string=am_name+":\n"+am_d+"\n\n"+df_name+":\n"+df_d

    desc.config(state=NORMAL)
    desc.delete(1.0, END)
    desc.insert(END, description_string)
    desc.config(state=DISABLED)
    return None


all_parameters={"EventDrivers":{"modules":dict(), "API":backendAPI.eventDrivers},
                "EventCulling":{"modules":dict(), "API":backendAPI.eventCulling},
                "AnalysisMethods":{"modules":dict(), "API":backendAPI.analysisMethods},
                "DistanceFunctions":{"modules":dict(), "API":backendAPI.distanceFunctions}}
for moduleclass in all_parameters:
    for module in all_parameters[moduleclass]["API"]: # module: a processer used to process text
        all_parameters[moduleclass]["modules"][module]=[]
        for var in all_parameters[moduleclass]["API"][module].__dict__: # variable: associated with the module
            number_of_exposed_variables=0
            item=all_parameters[moduleclass]["API"][module].__dict__[var] # item: the object instance in the API. The object has the methods actually processing the text.
            if callable(item)==True or var[0]=="_": continue
            number_of_exposed_variables+=1
            _variable_options = all_parameters[moduleclass]["API"][module]._variable_options
            _variable_GUItype = all_parameters[moduleclass]["API"][module]._variable_GUItype
            if _variable_GUItype[var]=="OptionMenu":
                options=_variable_options[var]
                all_parameters[moduleclass]["modules"][module].append({"options":options, "default":item, "type": "OptionMenu", "label": var})


def set_parameters(stringvar, API_dict, module, variable_name):
    """sets parameters whenever the widget is touched."""
    value_to=stringvar.get()
    setattr(API_dict[module], variable_name, int(value_to))
    return None

def find_parameters(param_frame: Frame, listbox: Listbox or ttk.Treeview, displayed_params: list, clear: bool=False, **options):
    """find parameters and description in some modules to display and set"""
    # module: individual event drivers, event culling, or analysis methods.
    # param_frame: the tkinter frame that displays the parameters.
    # listbox: the tkinter listbox that has the selected parameters.
    # displayed_params: a list of currently displayed parameter options.

    if debug>=3: print("find_parameters(param_frame=%s, listbox=%s, displayed_params=%s, clear=%s)" %(param_frame, listbox, displayed_params, clear))
    global all_parameters
    if all_parameters==None or len(all_parameters)==0:
        list_of_params={"first": [{"options": range(1, 20), "default": 1, "type": "Entry", "label": "first, param 1"},
            {"options": ["option1", "option2"], "default": 0, "type": "OptionMenu", "label": "first, param 2"}],
            "fifth": [{"options": range(0, 10), "default": 0, "type": "Entry", "label": "fifth, param 1"}]}
        if debug>=1: print("Using place-holder list of parameters.")
        # structure: dictionary of list [modules] of dictionaries [parameters]
        # the "default" item is always used as a key to "options".
        # i.e. the default value of an entry is always "options"["default"] and never "default".value.

    APIdict=options.get("APIdict") # get dict of modules in the selected UI page.
    list_of_params=all_parameters[APIdict]['modules']
    APIobject=all_parameters[APIdict]['API'] # the API object has the module class dictionary that gets the actual module.
    if APIdict=="AnalysisMethods":
        list_of_params_DF=all_parameters["DistanceFunctions"]['modules']
        APIobject_DF=all_parameters["DistanceFunctions"]['API']

    # first get the parameters to display from list.
    if type(listbox)==Listbox and len(listbox.curselection())>0:
        module_name=listbox.get(listbox.curselection())
        parameters_to_display=list_of_params.get(module_name)
    elif type(listbox)==ttk.Treeview:
        am_name=listbox.item(listbox.selection())["values"][0]
        df_name=listbox.item(listbox.selection())["values"][1]
        module_name=am_name
        parameters_to_display=list_of_params[am_name]
        if df_name!="NA": parameters_to_display_DF=list_of_params_DF[df_name]
        else: parameters_to_display_DF=[]
    else: return None
    
    for params in displayed_params:
        params.destroy()
    displayed_params.clear()
    if clear==True:
        return None

    # currently only support OptionMenu variables

    param_options=[] # list of StringVars.
    if type(listbox)==Listbox: number_of_modules=len(parameters_to_display)
    else: number_of_modules, number_of_am=len(parameters_to_display_DF)+len(parameters_to_display), len(parameters_to_display)

    if number_of_modules==0: # if this module does not have parameters to be set, say so.
        displayed_params.append(Label(param_frame, text="No parameters for this module."))
        displayed_params[-1].pack()
    else: # if this module has parameters, find and display parameters.
        rowshift=0 # this is the row shift for widgets. It's one when there are two groups of parameters to display.
        displayed_params.append(Label(param_frame, text=str(module_name)+":", font=("Helvetica", 14)))
        displayed_params[-1].grid(row=0, column=0, columnspan=2, sticky=W)
        for i in range(number_of_modules):
            if type(listbox)==Listbox:
                parameter_i=parameters_to_display[i]
                param_options.append(StringVar(value=str(APIobject[module_name].__dict__[parameter_i['label']])))
            elif type(listbox)==ttk.Treeview:
                if i<number_of_am:
                    parameter_i=parameters_to_display[i]
                    param_options.append(StringVar(value=str(APIobject[module_name].__dict__[parameter_i['label']])))
                else:
                    rowshift=1
                    if df_name=="NA": break
                    module_name=df_name
                    APIobject=APIobject_DF
                    parameters_to_display=parameters_to_display_DF
                    parameter_i=parameters_to_display[i-number_of_am]
                    param_options.append(StringVar(value=str(APIobject[df_name].__dict__[parameter_i['label']])))
            displayed_params.append(Label(param_frame, text=parameter_i['label']))
            displayed_params[-1].grid(row=i+1+rowshift, column=0)

            if parameter_i['type']=='Entry':
                displayed_params.append(Entry(param_frame))
                displayed_params[-1].insert(0, str(parameter_i['options'][parameter_i['default']]))
                displayed_params[-1].grid(row=i+1+rowshift, column=1, sticky=W)
            elif parameter_i['type']=='OptionMenu':
                displayed_params.append(OptionMenu(param_frame, param_options[-1], *parameter_i['options']))
                displayed_params[-1].grid(row=i+1+rowshift, column=1, sticky=W)
                    
                param_options[-1].trace_add(("write"),
                    lambda useless1, useless2, useless3, stringvar=param_options[-1],
                    API_dict=APIobject, module=module_name, var=parameter_i['label']:\
                        set_parameters(stringvar, API_dict, module, var))
        if rowshift==1: #if the rows are shifted, there is an extra label for the DF parameters.
            displayed_params.append(Label(param_frame, text=str(module_name)+":", font=("Helvetica", 14)))
            displayed_params[-1].grid(row=number_of_am+1, column=0, columnspan=2, sticky=W)


    param_frame.columnconfigure(0, weight=1)
    param_frame.columnconfigure(1, weight=3)
    return None

Window=None
def process(params: dict, check_listboxes: list, check_labels: list, process_button: Button, click: bool=False):
    """
    Process all input files with the parameters in all tabs.
    input: unknown authors, known authors, all listboxes.
    """
    # check_listboxes: list of listboxes that shouldn't be empty.
    # check_labels: list of labels whose text colors need to be updated upon checking the listboxes.
    if debug>=3: print("process(params=%s, check_listboxes=%s, check_labels=%s, process_button=%s, click=%s)" %(params, check_listboxes, check_labels, process_button, click))
    all_set=True
    # first check if the listboxes in check_listboxes are empty. If empty
    process_button.config(state=NORMAL, text="Process", )
    for lb_index in range(len(check_listboxes)):
        try: size=len(check_listboxes[lb_index].get_children())
        except: size=check_listboxes[lb_index].size()
        if size==0:
            check_labels[lb_index].config(fg="#e24444", activeforeground="#e24444")
            all_set=False
            process_button.config(fg="#333333", state=DISABLED, text="Process [missing parameters]", activebackground="light grey", bg="light grey")
            # if something is missing
        else: # if all is ready
            check_labels[lb_index].config(fg="black", activeforeground="black")
    process_button.config(fg="black")
    if not all_set or click==False:
        return None

    status_update("Starting process...")

    unknownAuthors=params["UnknownAuthors"].get(0, END)
    
    
    global processWindow

    processWindow=Toplevel()
    processWindow.title("Process Window")
    processWindow.geometry(dpi_processWindowGeometry)
    progressBar=ttk.Progressbar(processWindow, length=dpi_progressBarLength, mode="indeterminate")
    
    progressBar.pack(anchor=CENTER, pady=40)
    processWindow.bind("<Destroy>", lambda event, b="":status_update(b))
    processWindow.grab_set()
    progressBar.start()

    # LOADING DOCUMENTS
    process_message=Label(processWindow, text="Loading documents")
    process_message.pack()

    # gathering the known (corpus) documents
    docs=[]
    docs_debug=[]
    for author in params["KnownAuthors"]:
        for authorDoc in author[1]:
            docs.append(Document(author[0], authorDoc.split("/")[-1], readDocument(authorDoc), authorDoc))
            docs_debug.append([author[0], authorDoc.split("/")[-1]])

    for d in unknownAuthors:
        docs.append(Document(None, d.split("/")[-1], readDocument(d), d))
        docs_debug.append([None, d.split("/")[-1]])

    process_message.configure(text="Loading parameters")
    if debug>=3: print("Loading parameters")
    
    # gathering all the selected analysis pipelines
    canonicizers=list(params["Canonicizers"].get(0, END))
    eventDrivers=list(params["EventDrivers"].get(0, END))
    eventCulling=list(params["EventCulling"].get(0, END))
    am_df=list(params["AnalysisMethods"].get_children())
    am_df=[params["AnalysisMethods"].item(j)["values"] for j in am_df]
    #analysisMethods=[j[0] for j in am_df]
    #DistanceFunctions=[j[1] for j in am_df]

    backendAPI.documents=docs
    if debug>=2: print(canonicizers, eventDrivers, eventCulling, am_df)

    # THESE ARE MODELED FROM LINES IN CLI.PY
    # RUN CANONICIZERS
    process_message.configure(text="Running canonicizers")
    if debug>=3: print("Running canonicizers")
    for c in canonicizers:
        run_canonicizer=backendAPI.canonicizers.get(c)()
        for doc in backendAPI.documents:
            doc.text=run_canonicizer.process(doc.text)
    
    # RUN EVENT DRIVERS
    process_message.configure(text="Running event drivers")
    if debug>=3: print("Running event drivers")
    for e in eventDrivers:
        run_eventdriver=backendAPI.eventDrivers.get(e)()
        for doc in backendAPI.documents:
            doc.setEventSet(run_eventdriver.createEventSet(doc.text))
    
    # RUN EVENT CULLERS
    process_message.configure(text="Running event cullers")
    if debug>=3: print("Running event cullers: not implemented yet")
    #######

    # RUN ANALYSIS ON UNKNOWN DOCS
    unknownDocs=[d for d in deepcopy(backendAPI.documents) if d.author==None]
    knownDocs=[d for d in deepcopy(backendAPI.documents) if d.author!=None]
    
    results=[]    
    for am_df_pair in am_df:
        process_message.configure(text="Running "+str(am_df_pair[0]))
        run_methods=backendAPI.analysisMethods.get(am_df_pair[0])()
        run_methods.setDistanceFunction(backendAPI.distanceFunctions.get(am_df_pair[1]))
        
        # for each method: first train models on known docs
        run_methods.train(knownDocs)
        # then for each unknown document, analyze and output results
        for d in unknownDocs:
            doc_result=run_methods.analyze(d)
            formatted_results=backendAPI.prettyFormatResults(canonicizers, eventDrivers, am_df_pair[0], am_df_pair[1], d, doc_result)
            results.append(formatted_results)

    process_message.configure(text="Displaying results...")
    status_update("Experiment complete. See the process window")

    results_text=""
    for r in results:
        results_text+=str(r+"\n")

    # create space to display results, release focus of process window.
    progressBar.destroy()
    process_message.destroy()
    results_display=Text(processWindow)
    results_display.pack(fill=BOTH, expand=True, side=LEFT)
    results_display.insert(END, results_text)
    #results_display.config(state=DISABLED)

    results_scrollbar=Scrollbar(processWindow, width=scrollbar_width, command=results_display.yview)
    results_display.config(yscrollcommand=results_scrollbar.set)
    results_scrollbar.pack(side=LEFT, fill=BOTH)
    processWindow.geometry(dpi_processWindowGeometry_finished)
    processWindow.title(str(datetime.now()))
    processWindow.grab_release()

    change_style(processWindow)

    return None

AboutPage=None
def displayAbout():
    global versiondate
    global AboutPage
    """Displays the About Page"""
    if debug>=3: print("displayAbout()")
    try:
        AboutPage.lift()
        return None
    except:
        pass
    AboutPage=Toplevel()
    AboutPage.title("About PyGAAP")
    AboutPage.geometry(dpi_aboutPageGeometry)
    AboutPage.resizable(False, False)
    AboutPage_logosource=PhotoImage(file="./logo.png")
    AboutPage_logosource=AboutPage_logosource.subsample(2, 2)
    AboutPage_logo=Label(AboutPage, image=AboutPage_logosource)
    AboutPage_logo.pack(side="top", fill="both", expand="yes")

    textinfo="THIS IS AN EARLY VERSION OF PyGAAP GUI.\n\
    Version date: "+versiondate+"\n\
    PyGAAP is a Python port of JGAAP,\n\
    Java Graphical Authorship Attribution Program.\n\
    This is an open-source tool developed by the EVL Lab\n\
    (Evaluating Variation in Language Laboratory)."
    AboutPage_text=Label(AboutPage, text=textinfo)
    AboutPage_text.pack(side='bottom', fill='both', expand='yes')
    AboutPage.mainloop()

Notes_content=""
NotepadWindow=None

def notepad():
    """Notes button window"""
    global Notes_content
    global NotepadWindow
    # prevents spam-spawning. took me way too long to figure this out
    if debug>=3: print("notepad()")
    try:
        NotepadWindow.lift()
    except:
        NotepadWindow=Toplevel()
        NotepadWindow.title("Notes")
        #NotepadWindow.geometry("600x500")
        NotepadWindow_Textfield=Text(NotepadWindow)
        NotepadWindow_Textfield.insert("1.0", str(Notes_content))
        NotepadWindow_SaveButton=Button(NotepadWindow, text="Save & Close",\
            command=lambda:Notepad_Save(NotepadWindow_Textfield.get("1.0", "end-1c"), NotepadWindow))
        NotepadWindow_Textfield.pack(padx=7, pady=7, expand=True)
        NotepadWindow_SaveButton.pack(pady=(0, 12), expand=True)
        NotepadWindow.mainloop()
    return None

def Notepad_Save(text, window):
    """saves the contents displayed in the notepad textfield when the button is pressed"""
    global Notes_content
    Notes_content=text
    window.destroy()
    if debug>=3: print("Notepad_Save()")
    return None

def switch_tabs(notebook, mode, tabID=0):
    """called by the next button and the tab lables themselves.
    if called by next button, returns the next tab. if called by tab label click, gets that tab"""
    if debug>=3: print("switch_tabs(mode=%s, tabID=%i)" %(mode, tabID))
    if mode=="next":
        try:
            notebook.select(notebook.index(notebook.select())+1)
            return None
        except:
            return None
    elif mode=="previous":
        try:
            notebook.select(notebook.index(notebook.select())-1)
            return None
        except:
            return None
    elif mode=="choose":
        try:
            notebook.select(tabID)
            return None
        except:
            return None

def addFile(WindowTitle, ListboxOp, AllowDuplicates, liftwindow=None):
    """Universal add file function to bring up the explorer window"""
    #WindowTitle is the title of the window, may change depending on what kind of files are added
    #ListboxOp is the listbox object to operate on
    #AllowDuplicates is whether the listbox allows duplicates.
    #if listbox does not allow duplicates, item won't be added to the listbox and this prints a message to the terminal.
    #liftwindow is the window to go back to focus when the file browser closes
    if debug>=1: print("addFile")
    elif debug>=3: print("addFile(ListboxOp=%s, AllowDuplicates=%s)", ListboxOp, AllowDuplicates)
    filename=askopenfilename(filetypes=(("Text File", "*.txt"), ("All Files", "*.*")), title=WindowTitle, multiple=True)
    if liftwindow != None:
        liftwindow.lift(topwindow)
    if AllowDuplicates and filename !="" and len(filename)>0:
        ListboxOp.insert(END, filename)
    else:
        for fileinlist in ListboxOp.get(0, END):
            if fileinlist==filename:
                status_update("File already in list.")
                if debug>0:
                    print("Add document: file already in list")
                liftwindow.lift()
                return None
        if filename != None and filename !="" and len(filename)>0:
            for file in filename:
                ListboxOp.insert(END, file)

    if liftwindow != None:
        liftwindow.lift()
    return None

KnownAuthors=[]
# KnownAuthors list format: [[author, [file-directory, file-directory]], [author, [file-directory, file directory]]]
KnownAuthorsList=[]
# this decides which in the 1-dimensionl listbox is the author and therefore can be deleted when using delete author
# format: [0, -1, -1. -1, 1, -1, ..., 2, -1, ..., 3, -1, ...] -1=not author; >=0: author index.

def authorsListUpdater(listbox):
    """This updates the ListBox from the KnownAuthors python-list"""
    global KnownAuthors
    global KnownAuthorsList
    listbox.delete(0, END)
    if debug>=3: print("authorsListUpdater()")
    KnownAuthorsList=[]
    for authorlistindex in range(len(KnownAuthors)):#Authors
        listbox.insert(END, KnownAuthors[authorlistindex][0])
        listbox.itemconfig(END, background="light cyan", selectbackground="sky blue")
        KnownAuthorsList+=[authorlistindex]
        for document in KnownAuthors[authorlistindex][1]:
            listbox.insert(END, document)#Author's documents
            listbox.itemconfig(END, background="gray90", selectbackground="gray77")
            KnownAuthorsList+=[-1]
    return None

def authorSave(window, listbox, author, documentsList, mode):
    """This saves author when adding/editing to the KnownAuthors list. Then uses authorsListUpdater to update the listbox
    """
    #Listbox: the authors listbox.
    #author: 
    #       "ADD MODE": the author's name entered in authorsList window
    #       "EDIT MODE": [original author name, changed author name]
    #documentsList: list of documents entered in the listbox in the authorsList window
    #mode: add or edit
    global KnownAuthors
    if debug>=3: print("authorSave(mode=%s)" %(mode))
    if mode=="add":
        if (author != None and author.strip() !="") and (documentsList !=None and len(documentsList)!=0):  
            AuthorIndex=0
            while AuthorIndex<len(KnownAuthors):#check if author already exists
                if KnownAuthors[AuthorIndex][0]==author:#when author is already in the list, merge.
                    KnownAuthors[AuthorIndex][1]=KnownAuthors[AuthorIndex][1]+list([doc for doc in documentsList if doc not in KnownAuthors[AuthorIndex][1]])
                    authorsListUpdater(listbox)
                    window.destroy()
                    return None
                AuthorIndex+=1
            KnownAuthors+=[[author, list([file for file in documentsList if type(file)==str])]]#no existing author found, add.
            authorsListUpdater(listbox)
        window.destroy()
        return None
    elif mode=='edit':
        if (author[1] != None and author[1].strip() !="") and (documentsList !=None and len(documentsList)!=0):
            AuthorIndex=0
            while AuthorIndex<len(KnownAuthors):
                if KnownAuthors[AuthorIndex][0]==author[0]:
                    KnownAuthors[AuthorIndex]=[author[1], documentsList]
                    authorsListUpdater(listbox)
                    window.destroy()
                    return None
                AuthorIndex+=1
            print("coding error: editing author: list of authors and documents changed unexpectedly when saving")
            return None
    else:
        print("coding error: unknown parameter passed to 'authorSave' function: ", str(mode))
    window.destroy()
    return None

AuthorWindow=None
def authorsList(authorList, mode):
    """Add, edit or remove authors
    This updates the global KnownAuthors list.
    This opens a window to add/edit authors; does not open a window to remove authors
    """
    #authorList: the listbox that displays known authors in the topwindow.
    #authorList calls authorSave (which calls authorListUpdater) when adding/editing author
    #
    global KnownAuthors
    global KnownAuthorsList
    if debug>=3: print("authorsList(mode=%s)"%(mode))
    if mode=="add":
        title="Add Author"
        mode='add'
    elif mode=='edit':
        try:
            authorList.get(authorList.curselection())
            title="Edit Author"
            mode='edit'
            selected=int(authorList.curselection()[0])
            if KnownAuthorsList[selected]==-1:
                status_update("Select the author instead of the document.")
                print("edit author: select the author instead of the document")
                return None
            else:
                AuthorIndex=KnownAuthorsList[selected]#gets the index in the 2D list
                insertAuthor=KnownAuthors[selected][0]#original author name
                insertDocs=KnownAuthors[selected][1]#original list of documents
        except:
            status_update("No author selected.")
            if debug>0:
                print("edit author: no author selected")
            return None

    elif mode=="remove":#remove author does not open a window
        try:
            selected=int(authorList.curselection()[0])#this gets the listbox selection index
            if KnownAuthorsList[selected]==-1:
                status_update("Select the author instead of the document.")
                print("remove author: select the author instead of the document")
                return None
            else:
                AuthorIndex=KnownAuthorsList[selected]#This gets the index in KnownAuthors nested list
                if AuthorIndex>=len(KnownAuthors)-1:
                    KnownAuthors=KnownAuthors[:AuthorIndex]
                else:
                    KnownAuthors=KnownAuthors[:AuthorIndex]+KnownAuthors[AuthorIndex+1:]
                authorsListUpdater(authorList)

        except:
            status_update("No author selected.")
            if debug>0:
                print("remove author: nothing selected")
            return None
        return None
    else:
        assert mode=="add" or mode=="remove" or mode=="edit", "bug: Internal function 'authorsList' has an unknown mode parameter "+str(mode)
        
        return None

    global AuthorWindow
    
    AuthorWindow=Toplevel()
    AuthorWindow.grab_set()#Disables main window when the add/edit author window appears
    AuthorWindow.title(title)
    AuthorWindow.geometry(dpi_authorWindowGeometry)
    
    AuthorWindow.rowconfigure(1, weight=1)
    AuthorWindow.columnconfigure(1, weight=1)

    Label(AuthorWindow, text="Author", font="bold", padx=10).grid(row=0, column=0, pady=7, sticky="NW")
    Label(AuthorWindow, text="Files", font="bold", padx=10).grid(row=1, column=0, pady=7, sticky="NW")

    AuthorNameEntry=Entry(AuthorWindow, width=40)
    if mode=="edit":
        AuthorNameEntry.insert(END, insertAuthor)
    AuthorNameEntry.grid(row=0, column=1, pady=7, sticky="swen", padx=(0, 10))

    AuthorListbox=Listbox(AuthorWindow, height=12, width=60)
    if mode=="edit":
        for j in insertDocs:
            AuthorListbox.insert(END, j)
    AuthorListbox.grid(row=1, column=1, sticky="swen", padx=(0, 10))

    AuthorButtonsFrame=Frame(AuthorWindow)
    
    AuthorAddDocButton=Button(AuthorButtonsFrame, text="Add Document",\
        command=lambda:addFile("Add Document For Author", AuthorListbox, False, AuthorWindow))
    AuthorAddDocButton.grid(row=0, column=0)
    AuthorRmvDocButton=Button(AuthorButtonsFrame, text="Remove Document",\
        command=lambda:select_modules(None, AuthorListbox, 'remove'))
    AuthorRmvDocButton.grid(row=0, column=1)
    AuthorButtonsFrame.grid(row=2, column=1, sticky='NW')

    AuthorBottomButtonsFrame=Frame(AuthorWindow)
    #OK button functions differently depending on "add" or "edit".
    AuthorOKButton=Button(AuthorBottomButtonsFrame, text="OK",)
    if mode=="add":
        AuthorOKButton.configure(command=lambda:authorSave(AuthorWindow, authorList, AuthorNameEntry.get(), AuthorListbox.get(0, END), mode))
    elif mode=="edit":
        AuthorOKButton.configure(command=lambda:authorSave(AuthorWindow, authorList, [insertAuthor, AuthorNameEntry.get()], AuthorListbox.get(0, END), mode))

    AuthorOKButton.grid(row=0, column=0, sticky="W")
    AuthorCancelButton=Button(AuthorBottomButtonsFrame, text="Cancel", command=lambda:AuthorWindow.destroy())
    AuthorCancelButton.grid(row=0, column=1, sticky="W")
    AuthorBottomButtonsFrame.grid(row=3, column=1, pady=7, sticky="NW")
    
    change_style(AuthorWindow)

    AuthorWindow.mainloop()
    return None

#ABOVE ARE UTILITY FUNCTIONS
menubar=Menu(topwindow)#adds top menu bar
filemenu=Menu(menubar, tearoff=0)

#tkinter menu building goes from bottom to top / leaves to root
BatchDocumentsMenu=Menu(filemenu, tearoff=0)#batch documents menu
BatchDocumentsMenu.add_command(label="Save Documents [under construction]", command=todofunc)
BatchDocumentsMenu.add_command(label="Load Documents [under construction]", command=todofunc)
filemenu.add_cascade(label="Batch Documents [under construction]", menu=BatchDocumentsMenu, underline=0)

AAACProblemsMenu=Menu(filemenu, tearoff=0)#problems menu
AAACProblemsMenu.add_command(label="Problem 1", command=todofunc)
filemenu.add_cascade(label="AAAC Problems [under construction]", menu=AAACProblemsMenu, underline=0)

filemenu.add_separator()#file menu
ThemesMenu=Menu(filemenu, tearoff=0)
ThemesMenu.add_command(label="PyGaap Pink", command=lambda thm="PyGAAP_pink":change_style_live(thm))
ThemesMenu.add_command(label="JGAAP Blue", command=lambda thm="JGAAP_blue":change_style_live(thm))
filemenu.add_cascade(label="Themes", menu=ThemesMenu, underline=0)

filemenu.add_separator()#file menu
filemenu.add_command(label="Exit", command=topwindow.destroy)
menubar.add_cascade(label="File", menu=filemenu)

helpmenu=Menu(menubar, tearoff=0)#help menu
helpmenu.add_command(label="About...", command=displayAbout)
menubar.add_cascade(label="Help", menu=helpmenu)

topwindow.config(menu=menubar)
#bottom of the main window is at the bottom of this file


#the middle workspace where the tabs are

workspace=Frame(topwindow, height=800, width=570)
workspace.grid(padx=10, pady=5, row=0, sticky="nswe")
workspace.columnconfigure(0, weight=1)
workspace.rowconfigure(0, weight=2)

tabs=ttk.Notebook(workspace)
tabs.pack(pady=1, padx=5, expand=True, fill="both")

#size for all the main tabs.
tabheight=570
tabwidth=1000

Tabs_names=["Tab_Documents", "Tab_Canonicizers", "Tab_EventDrivers", "Tab_EventCulling", "Tab_AnalysisMethods", "Tab_ReviewProcess"]
Tabs_Frames=dict() # this stores the main Frame objects for all the tabs.

#below is the tabs framework
for t in Tabs_names:
    Tabs_Frames[t]=Frame(tabs, height=tabheight, width=tabwidth)
    Tabs_Frames[t].pack(fill='both', expand=True, anchor=NW)


tabs.add(Tabs_Frames["Tab_Documents"], text="Documents")
tabs.add(Tabs_Frames["Tab_Canonicizers"], text="Canonicizers")
tabs.add(Tabs_Frames["Tab_EventDrivers"], text="Event Drivers")
tabs.add(Tabs_Frames["Tab_EventCulling"], text="Event Culling")
tabs.add(Tabs_Frames["Tab_AnalysisMethods"], text="Analysis Methods")
tabs.add(Tabs_Frames["Tab_ReviewProcess"], text="Review & Process")
#above is the tabs framework


#BELOW ARE CONFIGS FOR EACH TAB

#Note: the review & process tab is set-up first instead of last.

#####REVIEW & PROCESS TAB
#basic frames structure
Tab_ReviewProcess_Canonicizers=Frame(Tabs_Frames["Tab_ReviewProcess"])
Tab_ReviewProcess_Canonicizers.grid(row=0, column=0, columnspan=3, sticky="wens", padx=10, pady=10)

Tab_ReviewProcess_EventDrivers=Frame(Tabs_Frames["Tab_ReviewProcess"])
Tab_ReviewProcess_EventDrivers.grid(row=1, column=0, sticky="wens", padx=10, pady=10)

Tab_ReviewProcess_EventCulling=Frame(Tabs_Frames["Tab_ReviewProcess"])
Tab_ReviewProcess_EventCulling.grid(row=1, column=1, sticky="wens", padx=10, pady=10)

Tab_ReviewProcess_AnalysisMethods=Frame(Tabs_Frames["Tab_ReviewProcess"])
Tab_ReviewProcess_AnalysisMethods.grid(row=1, column=2, sticky="wens", padx=10, pady=10)

for n in range(3):
    Tabs_Frames["Tab_ReviewProcess"].columnconfigure(n, weight=1)
for n in range(2):
    Tabs_Frames["Tab_ReviewProcess"].rowconfigure(n, weight=1)

#RP = ReviewProcess
#note: the buttons below (that redirect to corresponding tabs) have hard-coded tab numbers
Tab_RP_Canonicizers_Button=Button(Tab_ReviewProcess_Canonicizers, text="Canonicizers", font=("helvetica", 16), relief=FLAT,\
    command=lambda:switch_tabs(tabs, "choose", 1), activeforeground="#333333")
Tab_RP_Canonicizers_Button.pack(anchor="n")
Tab_RP_Canonicizers_Button.excludestyle=True

Tab_RP_Canonicizers_Listbox=Listbox(Tab_ReviewProcess_Canonicizers)
Tab_RP_Canonicizers_Listbox.pack(side=LEFT, expand=True, fill=BOTH)
Tab_RP_Canonicizers_Listbox_scrollbar=Scrollbar(Tab_ReviewProcess_Canonicizers, width=scrollbar_width, command=Tab_RP_Canonicizers_Listbox.yview)
Tab_RP_Canonicizers_Listbox_scrollbar.pack(side=RIGHT, fill=BOTH)
Tab_RP_Canonicizers_Listbox.config(yscrollcommand=Tab_RP_Canonicizers_Listbox_scrollbar.set)

Tab_RP_EventDrivers_Button=Button(Tab_ReviewProcess_EventDrivers, text="Event Drivers", font=("helvetica", 16), relief=FLAT,\
    command=lambda:switch_tabs(tabs, "choose", 2))
Tab_RP_EventDrivers_Button.pack(anchor="n")
Tab_RP_EventDrivers_Button.excludestyle=True

Tab_RP_EventDrivers_Listbox=Listbox(Tab_ReviewProcess_EventDrivers)
Tab_RP_EventDrivers_Listbox.pack(side=LEFT, expand=True, fill=BOTH)
Tab_RP_EventDrivers_Listbox_scrollbar=Scrollbar(Tab_ReviewProcess_EventDrivers, width=scrollbar_width, command=Tab_RP_EventDrivers_Listbox.yview)
Tab_RP_EventDrivers_Listbox_scrollbar.pack(side=RIGHT, fill=BOTH)
Tab_RP_EventDrivers_Listbox.config(yscrollcommand=Tab_RP_EventDrivers_Listbox_scrollbar.set)
Tab_RP_EventCulling_Button=Button(Tab_ReviewProcess_EventCulling, text="Event Culling", font=("helvetica", 16), relief=FLAT,\
    command=lambda:switch_tabs(tabs, "choose", 3))
Tab_RP_EventCulling_Button.pack(anchor="n")
Tab_RP_EventCulling_Button.excludestyle=True

Tab_RP_EventCulling_Listbox=Listbox(Tab_ReviewProcess_EventCulling, )
Tab_RP_EventCulling_Listbox.pack(side=LEFT, expand=True, fill=BOTH)
Tab_RP_EventCulling_Listbox_scrollbar=Scrollbar(Tab_ReviewProcess_EventCulling, width=scrollbar_width, command=Tab_RP_EventCulling_Listbox.yview)
Tab_RP_EventCulling_Listbox_scrollbar.pack(side=RIGHT, fill=BOTH)
Tab_RP_EventCulling_Listbox.config(yscrollcommand=Tab_RP_EventCulling_Listbox_scrollbar.set)
Tab_RP_AnalysisMethods_Button=Button(Tab_ReviewProcess_AnalysisMethods, text="Analysis Methods", font=("helvetica", 16), relief=FLAT,\
    command=lambda:switch_tabs(tabs, "choose", 4))
Tab_RP_AnalysisMethods_Button.pack(anchor="n")
Tab_RP_AnalysisMethods_Button.excludestyle=True

Tab_RP_AnalysisMethods_Listbox=ttk.Treeview(Tab_ReviewProcess_AnalysisMethods, columns=("AM", "DF"))
Tab_RP_AnalysisMethods_Listbox.column("#0", width=0, stretch=NO)
Tab_RP_AnalysisMethods_Listbox.heading("AM", text="Method", anchor=W)
Tab_RP_AnalysisMethods_Listbox.heading("DF", text="Distance", anchor=W)

Tab_RP_AnalysisMethods_Listbox.pack(side=LEFT, expand=True, fill=BOTH)
Tab_RP_AnalysisMethods_Listbox_scrollbar=Scrollbar(Tab_ReviewProcess_AnalysisMethods, width=scrollbar_width, command=Tab_RP_AnalysisMethods_Listbox.yview)
Tab_RP_AnalysisMethods_Listbox_scrollbar.pack(side=RIGHT, fill=BOTH)
Tab_RP_AnalysisMethods_Listbox.config(yscrollcommand=Tab_RP_AnalysisMethods_Listbox_scrollbar.set)
Tab_RP_Process_Button=Button(Tabs_Frames["Tab_ReviewProcess"], text="Process", width=25)

# button command see after documents tab.

Tab_RP_Process_Button.grid(row=2, column=0, columnspan=3, sticky="se", pady=5, padx=20)

Tab_RP_Process_Button.bind("<Map>", lambda event, a=[], lb=[Tab_RP_EventDrivers_Listbox, Tab_RP_AnalysisMethods_Listbox],\
    labels=[Tab_RP_EventDrivers_Button, Tab_RP_AnalysisMethods_Button],\
    button=Tab_RP_Process_Button:process("", lb, labels, button))




############### DOCUMENTS TAB ########################################################################################################################

Tab_Documents_Language_label=Label(Tabs_Frames["Tab_Documents"], text="Language", font=("helvetica", 15), anchor='nw')
Tab_Documents_Language_label.grid(row=1, column=0, sticky='NW', pady=(10, 5))

for n in range(10):
    if n==5 or n==8:
        w=1
        Tabs_Frames["Tab_Documents"].columnconfigure(0, weight=1)

    else: w=0
    Tabs_Frames["Tab_Documents"].rowconfigure(n, weight=w)

#documents-language selection
analysisLanguage=StringVar()
analysisLanguage.set("English")
#may need a lookup function for the options below
analysisLanguageOptions=["Arabic (ISO-8859-6)", "Chinese (GB2123)", "English"]
Tab_Documents_language_dropdown=OptionMenu(Tabs_Frames["Tab_Documents"], analysisLanguage, *analysisLanguageOptions)
Tab_Documents_language_dropdown['anchor']='nw'
Tab_Documents_language_dropdown.grid(row=2, column=0, sticky='NW')



#documents-unknown authors
Tab_Documents_UnknownAuthors_label=Label(Tabs_Frames["Tab_Documents"], text="Unknown Authors", font=("helvetica", 15), anchor='nw')
Tab_Documents_UnknownAuthors_label.grid(row=4, column=0, sticky="W", pady=(10, 5))


Tab_Documents_UnknownAuthors_Frame=Frame(Tabs_Frames["Tab_Documents"])
Tab_Documents_UnknownAuthors_Frame.grid(row=5, column=0, sticky="wnse")


Tab_Documents_UnknownAuthors_listbox=Listbox(Tab_Documents_UnknownAuthors_Frame, width="100", )
Tab_Documents_UnknownAuthors_listscrollbar=Scrollbar(Tab_Documents_UnknownAuthors_Frame, width=scrollbar_width, )
#loop below: to be removed

Tab_Documents_UnknownAuthors_listbox.config(yscrollcommand=Tab_Documents_UnknownAuthors_listscrollbar.set)
Tab_Documents_UnknownAuthors_listscrollbar.config(command=Tab_Documents_UnknownAuthors_listbox.yview)


Tab_Documents_UnknownAuthors_listbox.pack(side=LEFT, fill=BOTH, expand=True)
Tab_Documents_UnknownAuthors_listscrollbar.pack(side=RIGHT, fill=BOTH, padx=(0, 30))

Tab_Documents_doc_buttons=Frame(Tabs_Frames["Tab_Documents"])
Tab_Documents_doc_buttons.grid(row=6, column=0, sticky="W")
Tab_Documents_UnknownAuthors_AddDoc_Button=Button(Tab_Documents_doc_buttons, text="Add Document", width="16", command=\
    lambda:addFile("Add a document to Unknown Authors", Tab_Documents_UnknownAuthors_listbox, False))
Tab_Documents_UnknownAuthors_RmvDoc_Button=Button(Tab_Documents_doc_buttons, text="Remove Document", width="16", command=\
    lambda:select_modules(None, [Tab_Documents_UnknownAuthors_listbox], "remove"))

Tab_Documents_UnknownAuthors_AddDoc_Button.grid(row=1, column=1, sticky="W")
Tab_Documents_UnknownAuthors_RmvDoc_Button.grid(row=1, column=2, sticky="W")

#documents-known authors
Tab_Documents_KnownAuthors_label=Label(Tabs_Frames["Tab_Documents"], text="Known Authors", font=("helvetica", 15), anchor='nw')
Tab_Documents_KnownAuthors_label.grid(row=7, column=0, sticky="W", pady=(10, 5))


Tab_Documents_KnownAuthors_Frame=Frame(Tabs_Frames["Tab_Documents"])
Tab_Documents_KnownAuthors_Frame.grid(row=8, column=0, sticky="wnse")


Tab_Documents_KnownAuthors_listbox=Listbox(Tab_Documents_KnownAuthors_Frame, width="100")
Tab_Documents_KnownAuthors_listscroller=Scrollbar(Tab_Documents_KnownAuthors_Frame, width=scrollbar_width, )

Tab_Documents_KnownAuthors_listbox.config(yscrollcommand=Tab_Documents_KnownAuthors_listscroller.set)
Tab_Documents_KnownAuthors_listscroller.config(command=Tab_Documents_KnownAuthors_listbox.yview)


Tab_Documents_KnownAuthors_listbox.pack(side=LEFT, fill=BOTH, expand=True)
Tab_Documents_KnownAuthors_listscroller.pack(side=RIGHT, fill=BOTH, padx=(0, 30))

#These are known authors
Tab_Documents_knownauth_buttons=Frame(Tabs_Frames["Tab_Documents"])
Tab_Documents_knownauth_buttons.grid(row=9, column=0, sticky="W")
Tab_Documents_KnownAuthors_AddAuth_Button=Button(Tab_Documents_knownauth_buttons, text="Add Author", width="15",\
    command=lambda:authorsList(Tab_Documents_KnownAuthors_listbox, 'add'))
Tab_Documents_KnownAuthors_EditAuth_Button=Button(Tab_Documents_knownauth_buttons, text="Edit Author", width="15",\
    command=lambda:authorsList(Tab_Documents_KnownAuthors_listbox, 'edit'))
Tab_Documents_KnownAuthors_RmvAuth_Button=Button(Tab_Documents_knownauth_buttons, text="Remove Author", width="15", command=\
    lambda:authorsList(Tab_Documents_KnownAuthors_listbox, "remove"))

Tab_Documents_KnownAuthors_AddAuth_Button.grid(row=1, column=1, sticky="W")
Tab_Documents_KnownAuthors_EditAuth_Button.grid(row=1, column=2, sticky="W")
Tab_Documents_KnownAuthors_RmvAuth_Button.grid(row=1, column=3, sticky="W")



selected_parameters={"KnownAuthors": KnownAuthors,
                    "UnknownAuthors": Tab_Documents_UnknownAuthors_listbox,
                    "Canonicizers": Tab_RP_Canonicizers_Listbox,
                    "EventDrivers": Tab_RP_EventDrivers_Listbox,
                    "EventCulling": Tab_RP_EventCulling_Listbox,
                    "AnalysisMethods": Tab_RP_AnalysisMethods_Listbox}

Tab_RP_Process_Button.config(\
    command=lambda lb=[Tab_RP_EventDrivers_Listbox, Tab_RP_AnalysisMethods_Listbox],\
        labels=[Tab_RP_EventDrivers_Button, Tab_RP_AnalysisMethods_Button],\
            button=Tab_RP_Process_Button:process(selected_parameters, lb, labels, button, True))




# This function creates canonicizers, event drivers, event culling, and analysis methods tabs.
def create_module_tab(tab_frame: Frame, available_content: list, parameters_content=None, **extra):
    """
    creates a tab of available-buttons-selected-description tab.
    tab_frame: the top-level frame in the notebook tab
    available_content: list of label texts for the available modules to go in.
    button_functions: list of buttons in the middle frame
    selected_content: list of names of listboxes for the selected modules to go in.
    parameters_content: governs how the parameters frame is displayed
    description_content: governs how the descriptions frame is displayed.
    """
    assert len(set(available_content))==len(available_content), "Bug: create_modules_tab: available_content can't have repeated names."
    global scrollbar_width

    # Layer 0
    objects=dict() # objects in the frame
    tab_frame.columnconfigure(0, weight=1)
    tab_frame.rowconfigure(0, weight=1)

    topheight=0.7
    bottomheight=1-topheight
    
    objects["top_frame"]=Frame(tab_frame)
    objects["top_frame"].place(relx=0, rely=0, relwidth=1, relheight=topheight)

    # Layer 1: main frames
    objects["available_frame"]=Frame(objects["top_frame"])
    objects["available_frame"].place(relx=0, rely=0, relwidth=0.3, relheight=1)

    objects["buttons_frame"]=Frame(objects["top_frame"])
    objects["buttons_frame"].place(relx=0.3, rely=0, relwidth=0.1, relheight=1)

    objects["selected_frame"]=Frame(objects["top_frame"])
    objects["selected_frame"].place(relx=0.4, rely=0, relwidth=0.3, relheight=1)

    if parameters_content!="Canonicizers":
        objects["parameters_frame"]=Frame(objects["top_frame"])
        objects["parameters_frame"].place(relx=0.7, rely=0, relwidth=0.3, relheight=1)

    objects["description_frame"]=Frame(tab_frame)
    objects["description_frame"].place(relx=0, rely=topheight, relheight=bottomheight, relwidth=1)

    # Layer 2: objects in main frames
    counter=0
    objects["available_listboxes"]=[]
    # each entry in objects["available_listboxes"]:
    # [frame, label, listbox, scrollbar]
    objects["available_frame"].columnconfigure(0, weight=1)

    listboxAvList=[] # list of "available" listboxes to pass into select_modules() later.
    for name in available_content:
        # "Available" listboxes
        objects["available_listboxes"].append([Frame(objects["available_frame"])])
        objects["available_listboxes"][-1][0].grid(row=counter, column=0, sticky="swen")

        objects["available_frame"].rowconfigure(counter, weight=1)

        objects["available_listboxes"][-1].append(Label(objects["available_listboxes"][-1][0], text=name, font=("Helvetica", 15)))
        objects["available_listboxes"][-1][1].pack(pady=(10, 5), side=TOP, anchor=NW)

        objects["available_listboxes"][-1].append(Listbox(objects["available_listboxes"][-1][0], exportselection=False))
        objects["available_listboxes"][-1][2].pack(expand=True, fill=BOTH, side=LEFT)
        listboxAvList.append(objects["available_listboxes"][-1][2])

        objects["available_listboxes"][-1].append(Scrollbar(objects["available_listboxes"][-1][0], width=scrollbar_width, command=objects["available_listboxes"][-1][2].yview))
        objects["available_listboxes"][-1][3].pack(side=RIGHT, fill=BOTH)
        objects["available_listboxes"][-1][2].config(yscrollcommand=objects["available_listboxes"][-1][3].set)

        counter+=1   
    
    objects["selected_listboxes"]=[]
    objects["selected_listboxes"].append([Frame(objects["selected_frame"])])
    objects["selected_listboxes"][-1][0].pack(expand=True, fill=BOTH)        

    objects["selected_listboxes"][-1].append(Label(objects["selected_listboxes"][-1][0], text="Selected", font=("Helvetica", 15)))
    objects["selected_listboxes"][-1][1].pack(pady=(10, 5), side=TOP, anchor=NW)

    if parameters_content=="AnalysisMethods":
        # for analysis methods, use two listboxes scrolled by the same scrollbar.
        objects["selected_listboxes"][-1].append(ttk.Treeview(objects["selected_listboxes"][-1][0],
            columns=("AM", "DF")))
        objects["selected_listboxes"][-1][2].column("#0", width=0, stretch=NO)
        objects["selected_listboxes"][-1][2].heading("AM", text="Method", anchor=W)
        objects["selected_listboxes"][-1][2].heading("DF", text="Distance", anchor=W)
        objects["selected_listboxes"][-1][2].pack(expand=True, fill=BOTH, side=LEFT)

        objects["selected_listboxes"][-1].append(Scrollbar(objects["selected_listboxes"][-1][0], width=scrollbar_width, command=objects["selected_listboxes"][-1][2].yview))
        objects["selected_listboxes"][-1][3].pack(side=RIGHT, fill=BOTH)
        objects["selected_listboxes"][-1][2].config(yscrollcommand=objects["selected_listboxes"][-1][3].set)

    else:
        objects["selected_listboxes"][-1].append(Listbox(objects["selected_listboxes"][-1][0]))
        objects["selected_listboxes"][-1][2].pack(expand=True, fill=BOTH, side=LEFT)

        objects["selected_listboxes"][-1].append(Scrollbar(objects["selected_listboxes"][-1][0], width=scrollbar_width, command=objects["selected_listboxes"][-1][2].yview))
        objects["selected_listboxes"][-1][3].pack(side=RIGHT, fill=BOTH)
        objects["selected_listboxes"][-1][2].config(yscrollcommand=objects["selected_listboxes"][-1][3].set)

    Label(objects["buttons_frame"], text="", height=2).pack() # empty label to create space above buttons
    counter=0

    if parameters_content=="Canonicizers":
        extra.get("canonicizers_format")
        extra.get("canonicizers_format").set("All")
        CanonicizerFormatOptions=["All", "Generic", "Doc", "PDF", "HTML"]
        objects["Canonicizers_format"]=OptionMenu(objects["buttons_frame"], extra.get("canonicizers_format"), *CanonicizerFormatOptions)
        objects["Canonicizers_format"].pack(anchor=W)
        counter=1
    

    RP_listbox=extra.get("RP_listbox") # this is the listbox in the "Review and process" page to update when user adds a module in previous pages.

    
    objects["buttons_add"]=Button(objects["buttons_frame"], width="11", text=">>Add", anchor='s',
        command=lambda:select_modules(listboxAvList, [objects["selected_listboxes"][0][2], RP_listbox], "add"))
    objects["buttons_add"].pack(anchor=CENTER, fill=X)

    objects["buttons_remove"]=Button(objects["buttons_frame"], width="11", text="<<Remove", anchor='s',
        command=lambda:select_modules(None, [objects["selected_listboxes"][0][2], RP_listbox], "remove"))
    objects["buttons_remove"].pack(anchor=CENTER, fill=X)

    objects["buttons_clear"]=Button(objects["buttons_frame"], width="11", text="Clear", anchor='s',
        command=lambda:select_modules(None, [objects["selected_listboxes"][0][2], RP_listbox], "clear"))
    objects["buttons_clear"].pack(anchor=CENTER, fill=X)


    objects["description_label"]=Label(objects["description_frame"], text="Description", font=("helvetica", 15), anchor='nw')
    objects["description_label"].pack(anchor=NW, pady=(20, 5))
    objects["description_box"]=Text(objects["description_frame"], bd=5, relief="groove", bg=topwindow.cget("background"), state=DISABLED)
    objects["description_box"].pack(fill=BOTH, expand=True, side=LEFT)
    objects["description_box_scrollbar"]=Scrollbar(objects["description_frame"], width=scrollbar_width, command=objects["description_box"].yview)
    objects["description_box"].config(yscrollcommand=objects["description_box_scrollbar"].set)
    objects["description_box_scrollbar"].pack(side=LEFT, fill=BOTH)

    if parameters_content=="EventDrivers" or parameters_content=="EventCulling":
        displayed_parameters=extra.get("displayed_parameters")
        objects['parameters_label']=Label(objects["parameters_frame"], text="Parameters", font=("helvetica", 15), anchor=NW)
        objects['parameters_label'].pack(pady=(10, 5),anchor=W)

        objects['displayed_parameters_frame']=Frame(objects["parameters_frame"])
        objects['displayed_parameters_frame'].pack(padx=20, pady=20)


        objects["selected_listboxes"][-1][2].bind("<<ListboxSelect>>",\
            lambda event, frame=objects['displayed_parameters_frame'], lb=objects["selected_listboxes"][-1][2], dp=displayed_parameters:find_parameters(frame, lb, dp, APIdict=parameters_content), add="+")
        objects["selected_listboxes"][-1][2].bind("<<Unmap>>",\
            lambda event, frame=objects['displayed_parameters_frame'], lb=objects["selected_listboxes"][-1][2], dp=displayed_parameters:find_parameters(frame, lb, dp, APIdict=parameters_content), add="+")
            
    elif parameters_content=="AnalysisMethods":
        displayed_parameters=extra.get("displayed_parameters")
        objects['parameters_label']=Label(objects["parameters_frame"], text="Parameters", font=("helvetica", 15), anchor=NW)
        objects['parameters_label'].pack(pady=(10, 5),anchor=W)

        objects['displayed_parameters_frame']=Frame(objects["parameters_frame"])
        objects['displayed_parameters_frame'].pack(padx=20, pady=20)
        # bind treeview widget so the description updates when an item is selected.
        objects["selected_listboxes"][0][2].bind("<<TreeviewSelect>>", lambda event, d=objects["description_box"], lb=objects["selected_listboxes"][0][2], di=backendAPI.analysisMethods:find_description(d, lb, di), add="+")
        
        objects["selected_listboxes"][-1][2].bind("<<TreeviewSelect>>",\
            lambda event, frame=objects['displayed_parameters_frame'], lb=objects["selected_listboxes"][-1][2], dp=displayed_parameters:find_parameters(frame, lb, dp, APIdict=parameters_content), add="+")


    if parameters_content!="AnalysisMethods":
        APIdict={"Canonicizers": backendAPI.canonicizers, "EventDrivers": backendAPI.eventDrivers, "EventCulling": backendAPI.eventCulling}
        for f in objects["available_listboxes"]:
            f[2].bind("<<ListboxSelect>>", lambda event, t=objects["description_box"], l=f[2], d=APIdict[parameters_content]: find_description(t, l, d), add="+")
        for f in objects["selected_listboxes"]:
            f[2].bind("<<ListboxSelect>>", lambda event, t=objects["description_box"], l=f[2], d=APIdict[parameters_content]: find_description(t, l, d), add="+")
    else:
        objects["available_listboxes"][0][2].bind("<<ListboxSelect>>", lambda event, lbAv=objects["available_listboxes"][0][2], lbOp=objects["available_listboxes"][1][2]:CheckDistanceFunctionsListbox(lbAv, lbOp), add="+")
        objects["available_listboxes"][0][2].bind("<<ListboxSelect>>", lambda event, t=objects["description_box"], l=objects["available_listboxes"][0][2], d=backendAPI.analysisMethods: find_description(t, l, d), add="+")
        objects["available_listboxes"][1][2].bind("<<ListboxSelect>>", lambda event, t=objects["description_box"], l=objects["available_listboxes"][1][2], d=backendAPI.distanceFunctions: find_description(t, l, d), add="+")

    return objects

generated_widgets=dict()

CanonicizerFormat=StringVar()
generated_widgets['Canonicizers']=create_module_tab(Tabs_Frames["Tab_Canonicizers"], ["Canonicizers"], "Canonicizers", canonicizers_format=CanonicizerFormat, RP_listbox=Tab_RP_Canonicizers_Listbox)
Tab_EventDrivers_parameters_displayed=[]
generated_widgets['EventDrivers']=create_module_tab(Tabs_Frames["Tab_EventDrivers"], ["Event Drivers"], "EventDrivers", displayed_parameters=Tab_EventDrivers_parameters_displayed, RP_listbox=Tab_RP_EventDrivers_Listbox)
Tab_EventCulling_parameters_displayed=[]
generated_widgets['EventCulling']=create_module_tab(Tabs_Frames["Tab_EventCulling"], ["Event Culling"], "EventCulling", displayed_parameters=Tab_EventCulling_parameters_displayed, RP_listbox=Tab_RP_EventCulling_Listbox)
Tab_AnalysisMethods_parameters_displayed=[]
generated_widgets['AnalysisMethods']=create_module_tab(Tabs_Frames["Tab_AnalysisMethods"], ["Analysis Methods", "Distance Functions"], "AnalysisMethods", RP_listbox=Tab_RP_AnalysisMethods_Listbox, displayed_parameters=Tab_AnalysisMethods_parameters_displayed)


# adding items to listboxes from the backendAPI.
for canonicizer in backendAPI.canonicizers:
    generated_widgets["Canonicizers"]["available_listboxes"][0][2].insert(END, canonicizer)
for driver in backendAPI.eventDrivers:
    generated_widgets["EventDrivers"]["available_listboxes"][0][2].insert(END, driver)
for distancefunc in backendAPI.distanceFunctions:
    assert distancefunc!="NA", 'Distance Function cannot have a name of "NA" (Reserved for Analysis methods that do not use a distance function).\nPlease check the file containing the definition of the distance function class, most likely in or imported to DistanceFunction.py,\nand change the return of displayName().'
    generated_widgets["AnalysisMethods"]["available_listboxes"][1][2].insert(END, distancefunc)
for culling in backendAPI.eventCulling:
    generated_widgets["EventCulling"]["available_listboxes"][0][2].insert(END, culling)
for method in backendAPI.analysisMethods:
    generated_widgets["AnalysisMethods"]["available_listboxes"][0][2].insert(END, method)
#######

if debug>=2:
    _=0
    for j in generated_widgets:
        _+=len(j)
    print("size of 'generated_widgets' dict:", _)



#ABOVE ARE THE CONFIGS FOR EACH TAB

bottomframe=Frame(topwindow, height=150, width=570)
bottomframe.columnconfigure(0, weight=1)
bottomframe.rowconfigure(1, weight=1)
bottomframe.grid(pady=10, row=1, sticky='swen')

for c in range(6):
    bottomframe.columnconfigure(c, weight=10)

FinishButton=Button(bottomframe, text="Finish & Review", command=lambda:switch_tabs(tabs, "choose", 5))#note: this button has a hard-coded tab number
PreviousButton=Button(bottomframe, text="<< Previous", command=lambda:switch_tabs(tabs, "previous"))
NextButton=Button(bottomframe, text="Next >>", command=lambda:switch_tabs(tabs, "next"))
Notes_Button=Button(bottomframe, text="Notes", command=notepad)

Label(bottomframe).grid(row=0, column=0)
Label(bottomframe).grid(row=0, column=5)

PreviousButton.grid(row=0, column=1, sticky='swen')
NextButton.grid(row=0, column=2, sticky='swen')
Notes_Button.grid(row=0, column=3, sticky='swen')
FinishButton.grid(row=0, column=4, sticky='swen')

statusbar=Frame(topwindow, bd=1, relief=SUNKEN)
statusbar.grid(row=2, sticky="swe")

welcome_message="By David Berdik and Michael Fang. Version date: %s." %(versiondate)
statusbar_label=Label(statusbar, text=welcome_message, anchor=W)
statusbar_label.pack(anchor="e")
statusbar_label.after(3000, lambda:status_update("", welcome_message))



def change_style(parent_widget):
    if len(parent_widget.winfo_children())==0: return None
    for widget in parent_widget.winfo_children():
        if isinstance(widget, Button) and "excludestyle" not in widget.__dict__: widget.configure(activebackground=styles[style_choice]["accent_color_mid"], bg=styles[style_choice]["accent_color_mid"])
        elif isinstance(widget, Scrollbar): widget.configure(background=styles[style_choice]["accent_color_mid"])
        elif isinstance(widget, Listbox): widget.configure(selectbackground=styles[style_choice]["accent_color_mid"])
        elif isinstance(widget, OptionMenu): widget.configure(bg=styles[style_choice]["accent_color_mid"], activebackground=styles[style_choice]["accent_color_light"])
        else: change_style(widget)
    ttkstyle.map('Treeview', background=[('selected', styles[style_choice]["accent_color_mid"])], foreground=[('selected', "#000000")])

change_style(topwindow)

def change_style_live(themeString):
    global style_choice
    style_choice=themeString
    change_style(topwindow)

#starts app
topwindow.mainloop()
