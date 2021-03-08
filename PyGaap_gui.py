#My attempt at creating a PyGaap GUI. Unfinished, do not redistribute. (no-one wants to see this)
#PyGaap is the Python port of JGAAP, Java Graphical Authorship Attribution Program by Patrick Juola
#See https://evllabs.github.io/JGAAP/
#
#2021.03.07
#Michael Fang, Boston University.

#REQUIRED MODULES BELOW. USE pip OR pip3 IN YOUR TERMINAL TO INSTALL.

from tkinter import *
from tkinter import ttk

topwindow=Tk() #this is the top-level window when you first open PyGAAP
topwindow.title("PyGAAP (GUI, underconstruction)")
topwindow.geometry("1000x620")
#topwindow.iconbitmap()
#topwindow.option_add("*Font", "20")

#BELOW ARE ALL THE FUNCTIONS
def todofunc(): #place holder "to-do function"
    return None

def select_features(ListBoxAv, ListBoxOp, feature, function):
    """Used by Event Drivers, Event culling etc to add/remove/clear selected features.
    Needs to check if feature is already added."""
    #ListBoxAv: "listbox selection", listbox to choose from
    #ListBoxOp: "listbox operate-on", listbox to modify: the selectd listbox.
    #feature: is the return of listbox.curselection()
    if function=="clear":
        ListBoxOp.delete(0, END)
    elif function=="remove":
        try:
            ListBoxOp.delete(feature)
        except:
            print("remove from list: nothing selected")
            return None
        try:
            ListBoxOp.select_set(END)
        except:
            return None
    elif function=="add":
        try:
            ListBoxOp.insert(END, ListBoxAv.get(feature))
        except:
            print("add to list: nothing selected")

    return None

def find_parameters(feature):
    """find parameters in some features to display and set"""
    pass

def find_feature(section, directory):
    """Universal find feature function for:
    canonicizers, event drivers, event culling, analysis methods, and distance functions.
    As the app is starting up,
    this function looks for py or text files (or both?) in PyGaap Directory for those features and extracts information like:
    description to display in the discription textbox;
    location of those py files so PyGAAP GUI can use it;
    parameters of a feature to be stored for execution;

    -others to be determined
    """
    #section: categories in which to find the features like Canonicizers, Event Drivers, Event Cullers etc.
    pass

def displayAbout():
    AboutPage=Toplevel()
    AboutPage.title("About PyGaap")
    AboutPage.geometry("600x300")
    AboutPage.resizable(False, False)
    AboutPage_logosource=PhotoImage(file="logo.png")
    AboutPage_logosource=AboutPage_logosource.subsample(2, 2)
    AboutPage_logo=Label(AboutPage, image=AboutPage_logosource)
    AboutPage_logo.pack(side="top", fill="both", expand="yes")

    textinfo="THIS IS AN UNFINISHED VERSION OF PyGAAP GUI.\n\
    See source code for version date.\n\
    PyGAAP is a Python port of JGAAP,\n\
    Java Graphical Authorship Attribution Program.\n\
    This is an open-source tool developed by the EVL Lab\n\
    (Evaluating Variation in Language Laboratory)."
    AboutPage_text=Label(AboutPage, text=textinfo)
    AboutPage_text.pack(side='bottom', fill='both', expand='yes')
    AboutPage.mainloop()

Notes_content=""


def notepad():
    """Notes button window"""
    global Notes_content
    NotepadWindow=Toplevel()
    NotepadWindow.title("Notes")
    #NotepadWindow.geometry("600x500")
    NotepadWindow_Textfield=Text(NotepadWindow)
    NotepadWindow_Textfield.insert("1.0", str(Notes_content))
    NotepadWindow_SaveButton=Button(NotepadWindow, text="Save",\
        command=lambda:Notepad_Save(NotepadWindow_Textfield.get("1.0", "end-1c")))
    NotepadWindow_Textfield.pack(padx=1, expand=True)
    NotepadWindow_SaveButton.pack(padx=1, expand=True)
    NotepadWindow.mainloop()
    return None

def Notepad_Save(text):
    global Notes_content
    Notes_content=text
    return None

def removeDoc():
    return None


#ABOVE ARE ALL THE FUNCTIONS

#Test List for features
testfeatures=["first", "second", "third", "fourth", 'fifth', 'sixth', 'seventh', 'eighth', 'ninth', 'tenth', 'eleventh', 'twelfth', 'thirteenth']

menubar=Menu(topwindow)#adds top menu bar
filemenu=Menu(menubar, tearoff=0)

#tkinter menu building goes from bottom to top / leaves to root
BatchDocumentsMenu=Menu(filemenu, tearoff=0)#batch documents menu
BatchDocumentsMenu.add_command(label="Save Documents", command=todofunc)
BatchDocumentsMenu.add_command(label="Load Documents", command=todofunc)
filemenu.add_cascade(label="Batch Documents", menu=BatchDocumentsMenu, underline=0)

AAACProblemsMenu=Menu(filemenu, tearoff=0)#problems menu
AAACProblemsMenu.add_command(label="Problem 1", command=todofunc)
filemenu.add_cascade(label="AAAC Problems", menu=AAACProblemsMenu, underline=0)

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
workspace.pack()

tabs=ttk.Notebook(workspace)
tabs.pack(pady=1, expand=True)

#size for all the main tabs.
tabheight=550
tabwidth=950


#below is the tabs framework
Tab_Documents=Frame(tabs, height=tabheight, width=tabwidth)
#Tab_Documents.rowconfigure((1, 1), weight=1)
#Tab_Documents.columnconfigure((1, 1), weight=1)
Tab_Documents.pack(fill='both', expand=True)

Tab_Canonicizers=Frame(tabs, height=tabheight, width=tabwidth)
Tab_Canonicizers.pack(fill='both', expand=True)

Tab_EventDrivers=Frame(tabs, height=tabheight, width=tabwidth)
Tab_EventDrivers.pack(fill='both', expand=True)

Tab_EventCulling=Frame(tabs, height=tabheight, width=tabwidth)
Tab_EventCulling.pack(fill='both', expand=True)

Tab_AnalysisMethods=Frame(tabs, height=tabheight, width=tabwidth)
Tab_AnalysisMethods.pack(fill='both', expand=True)

Tab_ReviewProcess=Frame(tabs, height=tabheight, width=tabwidth)
Tab_ReviewProcess.pack(fill='both', expand=True)

tabs.add(Tab_Documents, text="Documents")
tabs.add(Tab_Canonicizers, text="Canonicizers")
tabs.add(Tab_EventDrivers, text="Event Drivers")
tabs.add(Tab_EventCulling, text="Event Culling")
tabs.add(Tab_AnalysisMethods, text="Analysis Methods")
tabs.add(Tab_ReviewProcess, text="Review & Process")
#above is the tabs framework


#BELOW ARE CONFIGS FOR EACH TAB
#DOCUMENTS TAB
Tab_Documents_Language_label=Label(Tab_Documents, text="Language", font='bold', anchor='nw')
Tab_Documents_Language_label.grid(row=1, column=1, sticky='NW')

#documents-language selection
analysisLanguage=StringVar()
analysisLanguage.set("English")
#may need a lookup function for the options below
analysisLanguageOptions=["Arabic (ISO-8859-6)", "Chinese (GB2123)", "English"]
Tab_Documents_language_dropdown=OptionMenu(Tab_Documents, analysisLanguage, *analysisLanguageOptions, )
Tab_Documents_language_dropdown['anchor']='nw'
Tab_Documents_language_dropdown.grid(row=2, column=1, sticky='NW')



#documents-unknown authors
Tab_Documents_UnknownAuthors_label=Label(Tab_Documents, text="Unknown Authors", font='bold', anchor='nw')
Tab_Documents_UnknownAuthors_label.grid(row=4, column=1, sticky="W")


Tab_Documents_UnknownAuthors_Frame=Frame(Tab_Documents)
Tab_Documents_UnknownAuthors_Frame.grid(row=5, column=1, sticky="W")


Tab_Documents_UnknownAuthors_listbox=Listbox(Tab_Documents_UnknownAuthors_Frame, width="100")
Tab_Documents_UnknownAuthors_listscrollbar=Scrollbar(Tab_Documents_UnknownAuthors_Frame)
#loop below: to be removed
for values in testfeatures[:5]:
    Tab_Documents_UnknownAuthors_listbox.insert(END, values)


Tab_Documents_UnknownAuthors_listbox.config(yscrollcommand=Tab_Documents_UnknownAuthors_listscrollbar.set)
Tab_Documents_UnknownAuthors_listscrollbar.config(command=Tab_Documents_UnknownAuthors_listbox.yview)


Tab_Documents_UnknownAuthors_listbox.pack(side=LEFT, fill=BOTH)
Tab_Documents_UnknownAuthors_listscrollbar.pack(side=RIGHT, fill=BOTH)

Tab_Documents_doc_buttons=Frame(Tab_Documents)
Tab_Documents_doc_buttons.grid(row=6, column=1, sticky="W")
Tab_Documents_UnknownAuthors_AddDoc_Button=Button(Tab_Documents_doc_buttons, text="Add Document", width="16", command=todofunc())
Tab_Documents_UnknownAuthors_RmvDoc_Button=Button(Tab_Documents_doc_buttons, text="Remove Document", width="16", command=\
    lambda:select_features(None, Tab_Documents_UnknownAuthors_listbox, Tab_Documents_UnknownAuthors_listbox.curselection(), "remove"))

Tab_Documents_UnknownAuthors_AddDoc_Button.grid(row=1, column=1, sticky="W")
Tab_Documents_UnknownAuthors_RmvDoc_Button.grid(row=1, column=2, sticky="W")

#documents-known authors
Tab_Documents_KnownAuthors_label=Label(Tab_Documents, text="Known Authors", font='bold', anchor='nw')
Tab_Documents_KnownAuthors_label.grid(row=7, column=1, sticky="W")


Tab_Documents_KnownAuthors_Frame=Frame(Tab_Documents)
Tab_Documents_KnownAuthors_Frame.grid(row=8, column=1, sticky="W")


Tab_Documents_KnownAuthors_listbox=Listbox(Tab_Documents_KnownAuthors_Frame, width="100")
Tab_Documents_KnownAuthors_listscroller=Scrollbar(Tab_Documents_KnownAuthors_Frame)
#loop below: to be removed
for values in testfeatures[:5]:
    Tab_Documents_KnownAuthors_listbox.insert(END, values)


Tab_Documents_KnownAuthors_listbox.config(yscrollcommand=Tab_Documents_KnownAuthors_listscroller.set)
Tab_Documents_KnownAuthors_listscroller.config(command=Tab_Documents_KnownAuthors_listbox.yview)


Tab_Documents_KnownAuthors_listbox.pack(side=LEFT, fill=BOTH)
Tab_Documents_KnownAuthors_listscroller.pack(side=RIGHT, fill=BOTH)

Tab_Documents_knownauth_buttons=Frame(Tab_Documents)
Tab_Documents_knownauth_buttons.grid(row=9, column=1, sticky="W")
Tab_Documents_KnownAuthors_AddAuth_Button=Button(Tab_Documents_knownauth_buttons, text="Add Author", width="15", command=todofunc())
Tab_Documents_KnownAuthors_EditAuth_Button=Button(Tab_Documents_knownauth_buttons, text="Edit Author", width="15", command=todofunc())
Tab_Documents_KnownAuthors_RmvAuth_Button=Button(Tab_Documents_knownauth_buttons, text="Remove Author", width="15", command=\
    lambda:select_features(None, Tab_Documents_KnownAuthors_listbox, Tab_Documents_KnownAuthors_listbox.curselection(), "remove"))

Tab_Documents_KnownAuthors_AddAuth_Button.grid(row=1, column=1, sticky="W")
Tab_Documents_KnownAuthors_EditAuth_Button.grid(row=1, column=2, sticky="W")
Tab_Documents_KnownAuthors_RmvAuth_Button.grid(row=1, column=3, sticky="W")



#CANONICIZERS TAB
Tab_Canon_Frame=Frame(Tab_Canonicizers)
Tab_Canon_Frame.grid(row=1, column=1)

#the height of the top section (everything except the "description at bottom")
Tab_Canon_topsection_height="20"

#####available canonicizers
Tab_Canon_Available=Frame(Tab_Canon_Frame)
Tab_Canon_Available.grid(row=1, column=1)

Tab_Canon_Available_label=Label(Tab_Canon_Available, text="Canonicizers", font='bold', anchor='nw')
Tab_Canon_Available_label.grid(row=1, column=1, sticky="NW")
Tab_Canon_Available_listbox=Listbox(Tab_Canon_Available, width="30", height=Tab_Canon_topsection_height)
for values in testfeatures[:10]:
    Tab_Canon_Available_listbox.insert(END, values)
Tab_Canon_Available_listbox.grid(row=2, column=1)
#####


#####buttons to choose or remove canonicizers
Tab_Canon_Buttons=Frame(Tab_Canon_Frame)
Tab_Canon_Buttons.grid(row=1, column=2)

Tab_Canon_ButtonWidth="11"
CanonicizerFormat=StringVar()
CanonicizerFormat.set("All")
CanonicizerFormatOptions=["All", "Generic", "Doc", "PDF", "HTML"]
Tab_Canon_Buttons_formatMenu=OptionMenu(Tab_Canon_Buttons, CanonicizerFormat, *CanonicizerFormatOptions)
Tab_Canon_Buttons_formatMenu.grid(row=1, column=1, sticky="NW")

Tab_Canon_Buttons_add=Button(Tab_Canon_Buttons, width=Tab_Canon_ButtonWidth, text="Add", command=todofunc)
#first initialize the buttons. Since the "selected listbox is not initialized yet, can't use the select_features function."
#need to reconfigure later.
Tab_Canon_Buttons_add.grid(row=2, column=1, sticky="NW")

Tab_Canon_Buttons_remove=Button(Tab_Canon_Buttons, width=Tab_Canon_ButtonWidth, text="Remove", command=todofunc)
Tab_Canon_Buttons_remove.grid(row=3, column=1, sticky="NW")

Tab_Canon_Buttons_clear=Button(Tab_Canon_Buttons, width=Tab_Canon_ButtonWidth, text="Clear", command=todofunc)
Tab_Canon_Buttons_clear.grid(row=4, column=1, sticky="NW")
#####

#####selected canonicizers
Tab_Canon_Selected=Frame(Tab_Canon_Frame)
Tab_Canon_Selected.grid(row=1, column=3)

Tab_Canon_Selected_label=Label(Tab_Canon_Selected, text="Selected", font='bold', anchor='nw')
Tab_Canon_Selected_label.grid(row=1, column=1, sticky="W")
Tab_Canon_Selected_listbox=Listbox(Tab_Canon_Selected, width="45", height=Tab_Canon_topsection_height)
for values in testfeatures[:2]:
    Tab_Canon_Selected_listbox.insert(END, values)
Tab_Canon_Selected_listbox.grid(row=2, column=1)

#reconfiguring the buttons after the seleted listboxes are initialized:
Tab_Canon_Buttons_add.configure(command=lambda:select_features(Tab_Canon_Available_listbox, Tab_Canon_Selected_listbox,\
    Tab_Canon_Available_listbox.curselection(), "add"))
Tab_Canon_Buttons_remove.configure(command=lambda:select_features(None, Tab_Canon_Selected_listbox,\
    Tab_Canon_Selected_listbox.curselection(), "remove"))
Tab_Canon_Buttons_clear.configure(command=lambda:select_features(None, Tab_Canon_Selected_listbox, None, "clear"))
#####

Tab_Canon_Description=Frame(Tab_Canonicizers)
Tab_Canon_Description.grid(row=2, column=1, sticky="NW")

Tab_Canon_DescriptionLabel=Label(Tab_Canon_Description, text="Description", anchor='nw')
Tab_Canon_DescriptionLabel.grid(row=1, column=1, sticky="NW")
Tab_Canon_DescriptionText=Text(Tab_Canon_Description, height='6')
Tab_Canon_DescriptionText.grid(row=2, column=1, sticky="NW")


#EVENT DRIVERS

Tab_EventDrivers_topframe=Frame(Tab_EventDrivers)
Tab_EventDrivers_topframe.grid(row=1, column=1, sticky='nw')
#Available Event Drivers
Tab_EventDrivers_available=Frame(Tab_EventDrivers_topframe)
Tab_EventDrivers_available.grid(row=1, column=1)

Tab_EventDrivers_topframe_height="20"

Tab_EventDrivers_available_label=Label(Tab_EventDrivers_available, text="Event Drivers", font='bold', anchor='nw')
Tab_EventDrivers_available_label.grid(row=1, column=1, sticky="NW")
Tab_EventDrivers_available_listbox=Listbox(Tab_EventDrivers_available, width="30", height=Tab_EventDrivers_topframe_height)
for values in testfeatures[:10]:
    Tab_EventDrivers_available_listbox.insert(END, values)
Tab_EventDrivers_available_listbox.grid(row=2, column=1)
#####

#####buttons to choose or remove Event drivers
Tab_EventDrivers_Buttons=Frame(Tab_EventDrivers_topframe)
Tab_EventDrivers_Buttons.grid(row=1, column=2)

Tab_EventDrivers_buttonwidth="11"

Tab_EventDrivers_Buttons_add=Button(Tab_EventDrivers_Buttons, width=Tab_EventDrivers_buttonwidth, text="Add", command=todofunc)
Tab_EventDrivers_Buttons_add.grid(row=1, column=1, sticky="NW")

Tab_EventDrivers_Buttons_remove=Button(Tab_EventDrivers_Buttons, width=Tab_EventDrivers_buttonwidth, text="Remove", command=todofunc)
Tab_EventDrivers_Buttons_remove.grid(row=2, column=1, sticky="NW")

Tab_EventDrivers_Buttons_clear=Button(Tab_EventDrivers_Buttons, width=Tab_EventDrivers_buttonwidth, text="Clear", command=todofunc)
Tab_EventDrivers_Buttons_clear.grid(row=3, column=1, sticky="NW")
#####

#####selected event drivers
Tab_EventDrivers_Selected=Frame(Tab_EventDrivers_topframe)
Tab_EventDrivers_Selected.grid(row=1, column=3)

Tab_EventDrivers_Selected_label=Label(Tab_EventDrivers_Selected, text="Selected", font='bold', anchor='nw')
Tab_EventDrivers_Selected_label.grid(row=1, column=1, sticky="W")
Tab_EventDrivers_Selected_listbox=Listbox(Tab_EventDrivers_Selected, width="45", height=Tab_EventDrivers_topframe_height)
for values in testfeatures[:2]:
    Tab_EventDrivers_Selected_listbox.insert(END, values)
Tab_EventDrivers_Selected_listbox.grid(row=2, column=1)
#####

#reconfiguring buttons for event drivers
Tab_EventDrivers_Buttons_add.configure(command=\
    lambda:select_features(Tab_EventDrivers_available_listbox, Tab_EventDrivers_Selected_listbox, Tab_EventDrivers_available_listbox.curselection(), "add"))
Tab_EventDrivers_Buttons_clear.configure(command=\
    lambda:select_features(None, Tab_EventDrivers_Selected_listbox, None, "clear"))
Tab_EventDrivers_Buttons_remove.configure(command=\
    lambda:select_features(None, Tab_EventDrivers_Selected_listbox, Tab_EventDrivers_Selected_listbox.curselection(), "remove"))



Tab_EventDrivers_Description=Frame(Tab_EventDrivers)
Tab_EventDrivers_Description.grid(row=2, column=1, sticky="NW")

Tab_EventDrivers_DescriptionLabel=Label(Tab_EventDrivers_Description, text="Description", anchor='nw')
Tab_EventDrivers_DescriptionLabel.grid(row=1, column=1, sticky="NW")
Tab_EventDrivers_DescriptionText=Text(Tab_EventDrivers_Description, height='6')
Tab_EventDrivers_DescriptionText.grid(row=2, column=1, sticky="NW")



#ABOVE ARE THE CONFIGS FOR EACH TAB

bottomframe=Frame(topwindow, height=150, width=570)
bottomframe.pack()

FinishButton=Button(bottomframe, text="Finish & Review", command=todofunc)
NextButton=Button(bottomframe, text="Next ->", command=todofunc)

FinishButton.pack(side=RIGHT)
NextButton.pack(side=RIGHT)

Notes_Button=Button(bottomframe, text="Notes", command=notepad)
Notes_Button.pack(side=RIGHT)


#starts app
topwindow.mainloop()
