from tkinter import Tk, Label
from tkinter.ttk import Progressbar

def receive_info(
		pipe_connection,
		tkinter_user,
		text_label
		):
	if not pipe_connection.poll():
		tkinter_user.after(20, lambda
			p=pipe_connection,
			u=tkinter_user,
			t=text_label:
				receive_info(p, u, t)
		)
	else:
		info = pipe_connection.recv()
		if info == 0:
			pipe_connection.close()
			tkinter_user.destroy()
			return
		else:
			tkinter_user.after(50, lambda
				p=pipe_connection,
				u=tkinter_user,
				t=text_label:
					receive_info(p, u, t)
			)
			text_label.configure(text=info)
			return

def splash(pto):
	loading_window = Tk()
	loading_window.geometry("300x200")
	loading_window.title("Loading")
	#loading_window.attributes('-type', 'splash')
	Label(text="Starting PyGAAP").pack(pady=(30,5))
	text_label = Label(text="")
	text_label.pack()
	progress = Progressbar(loading_window, mode="indeterminate", length=100)
	progress.pack(padx=100, pady=(5,30))

	receive_info(pto, loading_window, text_label)

	progress.start()
	loading_window.mainloop()

def process_window(geometry, pto):
	window = Tk()
	window.geometry(geometry)
	window.title("Processing")
	Label(text="Running experiment").pack(pady=(30,5))
	text_label = Label(text="")
	text_label.pack()
	progress = Progressbar(window, mode="indeterminate", length=100)
	progress.pack(padx=100, pady=(5,30))

	receive_info(pto, window, text_label)

	progress.start()
	window.mainloop()
