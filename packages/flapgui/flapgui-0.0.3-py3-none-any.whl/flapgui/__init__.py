import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import tkinter.colorchooser

global app_version
app_version = [0,0,3]

global verbose
verbose = True

def window(title="flapWindow", width=250, height=250):
    if verbose:
        print(f"Flap: Created window \"{title}\" with resolution {width}x{height}")
    window = tk.Tk()
    window.title(title)
    window.geometry(f"{width}x{height}")
    return window
def getText(text_widget):
    text = text_widget.get("1.0", tk.END).strip()
    return text
def calcTextDimensions(text):
    root = tk.Tk()
    text_widget = tk.Text(root, width=1, height=1)
    text_widget.insert(tk.END, text)
    text_widget.pack()

    text_widget.update_idletasks()
    width = text_widget.winfo_reqwidth()
    height = text_widget.winfo_reqheight()

    root.destroy()

    return width, height
def maximiseWindow(window):
    window.attributes('-zoomed', True)
def createTextEntry(window, height, width):
    text_entry = tk.Text(window, height=height, width=width)
    text_entry.pack()
    return text_entry
def autoScaleResolution(window):
    window.update_idletasks()  # Update window to ensure accurate widget sizes
    width = window.winfo_reqwidth()
    height = window.winfo_reqheight()
    scaleResolution(window,width,height)
def scaleResolution(window, width, height):
    if verbose:
        print(f"Flap: Scaled Resolution to {width}x{height}")
    window.geometry(f"{width}x{height}")
def label(text):
    if verbose:
        print("Flap: Created Label",text)
    label = tk.Label(text=text)
    return label
def tbox(width, height,fg=None,bg=None):
    text_box = tk.Text(width=width, height=height,fg=fg,bg=bg,insertbackground=fg)
    return text_box
def pack(text):
    if verbose:
        print("Flap: Added Text",text)
    l = label(text)
    l.pack()

def file_selector(is_file=True):
    if verbose:
        print("Flap: Open File Selector: IsFile",str(is_file))
    root = tk.Tk()
    root.withdraw()
    if is_file:
        file_path = filedialog.askopenfilename()
    else:
        file_path = filedialog.askdirectory()
    if verbose:
        print("Flap: User Selected",file_path)
    return file_path

def create_button(window, text, command=None):
    if verbose:
        print(f"Flap: Made button \"{text}\"")
    button = tk.Button(window, text=text, command=command)
    button.pack()
    return button
def create_frame(window):
    frame = tk.Frame(window)
    frame.pack()
    return frame
from tkinter import ttk
import tkinter as tk
from tkinter import ttk

def new_text(window, width=40, bg="#FFFFFF", fg="#000000"):
    if verbose:
        print(f"Flap: Made new text input field: bg {bg} fg {fg}")

    # Create a frame to hold the Text widget and scrollbar
    frame = tk.Frame(window)
    frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Create a Text widget with the specified width
    text = tk.Text(frame, width=width, bg=bg, fg=fg, insertbackground=fg)
    text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Create a Scrollbar widget
    scrollbar = ttk.Scrollbar(frame, command=text.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Configure the Text widget to use the Scrollbar
    text.configure(yscrollcommand=scrollbar.set)

    return text
def create_menu_bar(parent):
    if verbose:
        print(f"Flap: Added Menu Bar")
    # create the menu bar widget
    menu_bar = tk.Menu(parent)
    parent.config(menu=menu_bar)
    return menu_bar
def append_text(text_widget,string):
    if verbose:
        print(f"Flap: Added \"{string}\" to text widget")
    text.insert(tk.END,string)
def add_cascade(menu_bar, label):
    if verbose:
        print(f"Flap: New Cascade \"{label}\"")
    # create a new menu
    cascade_menu = tk.Menu(menu_bar, tearoff=0)
    # add the cascade menu to the menu bar
    menu_bar.add_cascade(label=label, menu=cascade_menu)
    return cascade_menu

def add_command(cascade_menu, label, command,accelerator=None):
    if verbose:
        print(f"Flap: Added Command To Cascade: {label}")
    cascade_menu.add_command(label=label, command=command,accelerator=accelerator)
def close_window(window):
    window.destroy()
def make_binding(master,binding,command):
    if verbose:
        print(f"Flap: Added Binding: {binding}")
    master.bind(binding,command)
def clear_window(window):
    for widget in window.winfo_children():
        widget.destroy()
def message_box(title, message):
    msg=message.replace("\n","\\n")
    print(f"Flap: Message Box: {title} :: \"{msg}\"")
    root = tk.Tk()
    root.withdraw() # hide the main window

    messagebox.showinfo(title, message)

    root.destroy() # clean up the window
def add_scrollbar(window, text_widget):
    scrollbar = tk.Scrollbar(window)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    scrollbar.config(command=text_widget.yview)
    text_widget.config(yscrollcommand=scrollbar.set)
    text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
def select_all_text(text, event=None):
    if verbose:
        print("Flap: Selected All Text")
    text.tag_add(tk.SEL, "1.0", tk.END)
    text.mark_set(tk.INSERT, "1.0")
    text.see(tk.INSERT)
def set_text(text_widget, text):
    if verbose:
        print(f"Set Text To {text}")
    text_widget.delete('1.0', tk.END)
    text_widget.insert(tk.END, text)
def add_menu_separator(cascade):
    if verbose:
        print("Flap: Added Menu Separator")
    cascade.add_separator()
def get_flap_version():
    return app_version
def check_version(check):
    if check == app_version:
        return True
    else:
        return False
def choose_color():
    color = tk.colorchooser.askcolor(title="Choose color")
    if color:
        r, g, b = map(int, color[0])
        return f"#{r:02x}{g:02x}{b:02x}"
    else:
        return None
def createGrid(window):
    grid = tk.Frame(window)
    grid.pack()
    return grid
def addGridButton(grid, label, function, x, y, buttonDimensionX=2, buttonDimensionY=1):
    button = tk.Button(grid, text=label, command=function)
    button.config(width=buttonDimensionX, height=buttonDimensionY)
    button.grid(row=x, column=y)
if verbose:
    print(f"Flap: Initialised Framework ({app_version[0]}.{app_version[1]}.{app_version[2]})")
