import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
import tkinter.colorchooser
import webbrowser

global app_version
app_version = [0,4,0]
global verbose
verbose = False

def window(title="flapWindow", width=250, height=250):
    """
Creates a window.
    """
    if verbose:
        print(f"Flap: Created window \"{title}\" with resolution {width}x{height}")
    window = tk.Tk()
    #setattr(root,"defaultColor",root.cget("background"))
    window.title(title)
    window.geometry(f"{width}x{height}")
    return window

def subWindow(root, title=None, width=250, height=250, close_parent=True):
    child_window = tk.Toplevel(root)
    child_window.title(title)
    child_window.geometry(f"{width}x{height}")
    
    if close_parent:
        child_window.protocol("WM_DELETE_WINDOW", child_window.destroy)
    else:
        child_window.protocol("WM_DELETE_WINDOW", root.destroy)
    
    return child_window
def disableElement(element):
    """
    Makes the element specified greyed out/disabled.
    
    Args:
        element (tkinter.Widget): The tkinter widget to be disabled.
    """
    if isinstance(element, tk.Menu):
        element.entryconfig(0, foreground='gray')
    else:
        element.configure(state='disabled')
##class CheckBox:
##    def __init__(self, root, label, defaultState=False, boxColor=None, checkColor=None):
##        self.var = tk.BooleanVar(value=defaultState)
##        
##        if ttk.Style().theme_use() == 'default':
##            self.checkbox = ttk.Checkbutton(root, text=label, variable=self.var)
##            changeWidgetColor(self.checkbox, boxColor, checkColor)
##        else:
##            style = ttk.Style()
##            style.configure('Custom.TCheckbutton', background=boxColor, indicatorcolor=checkColor)
##            self.checkbox = ttk.Checkbutton(root, text=label, variable=self.var, style='Custom.TCheckbutton')
##        
##        self.checkbox.pack()
##
##    def get_state(self):
##        return self.var.get()
##
##class StyledCheckbox(tk.Frame):
##    def __init__(self, master=None, cnf={}, **kw):
##        super().__init__(master, cnf, **kw)
##        self.toggle_var = tk.BooleanVar(value=False)
##
##        self.checkbox_frame = tk.Frame(self)
##        self.checkbox_frame.pack(side='left')
##
##        self.checkbox_label = tk.Label(
##            self.checkbox_frame,
##            text='\u2713',  # Unicode character for checkmark
##            font=('Arial', 12),
##            bg=self['bg']
##        )
##        self.checkbox_label.pack()
##
##        self.checkbox_text = tk.Label(
##            self,
##            text=self['text'],
##            font=self['font'],
##            bg=self['bg']
##        )
##        self.checkbox_text.pack(side='left')
##
##        self.bind('<Button-1>', self.toggle)
##
##    def toggle(self, event):
##        self.toggle_var.set(not self.toggle_var.get())
##        if self.toggle_var.get():
##            self.checkbox_label.config(fg='green')
##        else:
##            self.checkbox_label.config(fg='black')
##
##    def get_state(self):
##        return self.toggle_var.get()
##
##
##    def get_state(self):
##        return self.toggle_var.get()
##class CustomCheckBox(ttk.Checkbutton):
##    def __init__(self, master=None, accent_color=None, *args, **kwargs):
##        self.accent_color = accent_color
##        super().__init__(master, *args, **kwargs)
##        self.style = ttk.Style()
##        self.style.theme_use('clam')  # Use 'clam' theme for consistent look across platforms
##
##        # Configure the style for the checkbox
##        self.style.configure('CustomCheckBox.TCheckbutton',
##                             indicatorsize=20,
##                             background='white',
##                             relief='flat',
##                             borderwidth=0)
##        self.style.map('CustomCheckBox.TCheckbutton',
##                       foreground=[('active', self.accent_color)],
##                       background=[('active', 'white')])
##
##        # Create the checkbox with the custom style
##        self.configure(style='CustomCheckBox.TCheckbutton')
##
##    def set_accent_color(self, accent_color):
##        self.accent_color = accent_color
##        self.style.map('CustomCheckBox.TCheckbutton',
##                       foreground=[('active', self.accent_color)])
##
##
class Checkbox:
    def __init__(self, root, label, isChecked=False, boxColor=None, textColor=None, fillColor=None, bgColor=None):
        self.root = root
        self.label = label
        self.isChecked = isChecked
        self.boxColor = boxColor
        self.textColor = textColor
        self.fillColor = fillColor
        self.bgColor = bgColor
        
        self.checkbox_var = tk.BooleanVar(value=self.isChecked)
        self.checkbox = tk.Checkbutton(
            self.root,
            text=self.label,
            variable=self.checkbox_var,
            onvalue=True,
            offvalue=False,
            command=self._on_checkbox_changed
        )
        self.checkbox.pack()
        
        if self.boxColor:
            self.checkbox.config(activeforeground=self.boxColor, fg=self.boxColor)
            self.checkbox.config(selectcolor=self.boxColor)
        if self.textColor:
            self.checkbox.config(activeforeground=self.textColor)
        if self.fillColor:
            self.checkbox.config(activebackground=self.fillColor)
        if self.bgColor:
            self.checkbox.config(background=self.bgColor)
        
    def _on_checkbox_changed(self):
        self.isChecked = self.checkbox_var.get()
        
    def getCheckboxState(self):
        return self.isChecked

def changeWidgetColor(widget, background_color, text_color=None):
    widget.config(selectcolor=background_color)
    if text_color:
        widget.config(fg=text_color)
    widget.update_idletasks()

def changeAccentColor(root, background_color, text_color=None):
    root.tk_setPalette(background=background_color)
    for widget in root.winfo_children():
        if isinstance(widget, tk.Checkbutton):
            changeWidgetColor(widget, background_color, text_color)
        else:
            changeWidgetColor(widget, background_color, text_color)
            if isinstance(widget, tk.Toplevel):
                changeAccentColor(widget, background_color, text_color)
def resetAccentColor(root):
    r = window()
    x = root.cget("background")
    print("DefaultBGColor:",x)
    r.destroy()
    changeAccentColor(root,x)
def createFrame(root):
    frame = tk.Frame(root)
    frame.pack()
    return frame
def createHyperlinkText(root, label_text, url):
    label = tk.Label(root, text=label_text, fg='blue', cursor='hand2')
    label.pack()
    label.bind('<Button-1>', lambda e: webbrowser.open(url))
def changeTitle(root, new_title):
    root.title(new_title)
def autoScaleResolution(window):
    window.update_idletasks()  # Update window to ensure accurate widget sizes
    width = window.winfo_reqwidth()
    height = window.winfo_reqheight()
    scaleResolution(window,width,height)
def scaleResolution(window, width, height):
    if verbose:
        print(f"Flap: Scaled Resolution to {width}x{height}")
    window.geometry(f"{width}x{height}")
def maximiseWindow(window):
    window.attributes('-zoomed', True)
def addText(root, text):
    label = tk.Label(root, text=text)
    label.pack()
def textEntry(width, height,fg=None,bg=None):
    if verbose:
        print(f"Flap: Made new text entry: bg {bg} fg {fg}")
    text_box = tk.Text(width=width, height=height,fg=fg,bg=bg,insertbackground=fg)
    return text_box
def framedTextEntry(window, width=40, bg="#FFFFFF", fg="#000000"):
    if verbose:
        print(f"Flap: Made new framed text entry: bg {bg} fg {fg}")

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
def lockText(text):
    if verbose:
        print("Flap: Locked text")
    text.config(state="disabled")

def unlockText(text):
    text.config(state="normal")
def makeTabbable(text):
    def handle_tab(event):
        event.widget.tk_focusNext().focus()
        return "break"  # Prevent default tab behavior

    text.bind("<Tab>", handle_tab)

def makeUnclosable(root):
    if verbose:
        print("Made window unclosable")
    def disable_close_button():
        pass

    root.protocol("WM_DELETE_WINDOW", disable_close_button)
def makeReclosable(root):
    if verbose:
        print("Made window closable")
    root.protocol("WM_DELETE_WINDOW", root.destroy)
def menuBar(root):
    if verbose:
        print(f"Flap: Added Menu Bar")
    # create the menu bar widget
    menu_bar = tk.Menu(root)
    root.config(menu=menu_bar)
    return menu_bar
def addCascade(menuBar,label):
    if verbose:
        print(f"Flap: New Cascade \"{label}\"")
    # create a new menu
    cascade_menu = tk.Menu(menuBar, tearoff=0)
    # add the cascade menu to the menu bar
    menuBar.add_cascade(label=label, menu=cascade_menu)
    return cascade_menu
def addCommand(cascade, label, command=None, accelerator=None):
    if verbose:
        print(f"Flap: Added Command To Cascade: {label}")
    cascade.add_command(label=label, command=command,accelerator=accelerator)  
def keyBind(root,binding,command=None):
    if verbose:
        print(f"Flap: Added Binding: {binding}")
    root.bind(binding,command)
def addText(root, label_text):
    label = tk.Label(root, text=label_text)
    label.pack()
def addFrameScrollbar(frame):
    scrollbar = tk.Scrollbar(frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    canvas = tk.Canvas(frame, yscrollcommand=scrollbar.set)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar.config(command=canvas.yview)

    content_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=content_frame, anchor="nw")

    def configure_scrollbar(event):
        canvas.configure(scrollregion=canvas.bbox("all"), width=200, height=200)

    content_frame.bind("<Configure>", configure_scrollbar)

    return content_frame
def messageBox(title,message):
    msg=message.replace("\n","\\n")
    print(f"Flap: Message Box: {title} :: \"{msg}\"")
    root = tk.Tk()
    root.withdraw() # hide the main window

    messagebox.showinfo(title, message)
def addScrollbar(root, text):
    scrollbar = tk.Scrollbar(root)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    scrollbar.config(command=text.yview)
    text.config(yscrollcommand=scrollbar.set)
    text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
def selectAll(text,event=None):
    if verbose:
        print("Flap: Selected All Text")
    text.tag_add(tk.SEL, "1.0", tk.END)
    text.mark_set(tk.INSERT, "1.0")
    text.see(tk.INSERT)
def disallowEnter(text):
    def handle_return(event):
        return "break"  # Prevent newline insertion

    text.bind("<Return>", handle_return)
def setText(text_widget, text):
    if verbose:
        print(f"Set Text To {text}")
    
    # Check if the text widget is locked
    is_locked = text_widget.cget("state") == "disabled"
    
    # Temporarily unlock the text widget if it is locked
    if is_locked:
        text_widget.config(state="normal")
    
    text_widget.delete('1.0', tk.END)
    text_widget.insert(tk.END, text)
    
    # Lock the text widget again if it was initially locked
    if is_locked:
        text_widget.config(state="disabled")
def getText(text_widget):
    text = text_widget.get("1.0", tk.END).strip()
    return text
def createButton(root,label,command=None):
    if verbose:
        print(f"Flap: Made button \"{label}\"")
    button = tk.Button(root, text=label, command=command)
    button.pack()
    return button
def appendText(text_widget,string):
    if verbose:
        print(f"Flap: Added \"{string}\" to text widget")
    set_text(text_widget,getText(text_widget)+string)
def createGrid(root):
    grid = tk.Frame(root)
    grid.pack()
    return grid
def addGridButton(grid, label, function, x, y, buttonDimensionX=2, buttonDimensionY=1):
    button = tk.Button(grid, text=label, command=function)
    button.config(width=buttonDimensionX, height=buttonDimensionY)
    button.grid(row=x, column=y)

def fileSelector(is_file=True):
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
def colorChoose():
    color = tk.colorchooser.askcolor(title="Choose color")
    if color:
        r, g, b = map(int, color[0])
        return f"#{r:02x}{g:02x}{b:02x}"
    else:
        return None
def getVersion():
    return app_version

class FlowLayout(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.widgets = []

    def add_widget(self, widget):
        self.widgets.append(widget)
        self._update_layout()

    def _update_layout(self):
        # Clear the frame
        for widget in self.winfo_children():
            widget.pack_forget()

        # Add widgets to the frame
        for widget in self.widgets:
            widget.pack(side=tk.LEFT)

        # Update the frame's size
        self.update_idletasks()
        self.config(width=self.winfo_reqwidth(), height=self.winfo_reqheight())
def addFlowButton(flowLayout, label, command=None, width=2, height=1):
    button = tk.Button(flowLayout, text=label, command=command, width=width, height=height)
    button.pack()
    flowLayout.add_widget(button)

def addFlowText(flowLayout, label):
    text = tk.Label(flowLayout, text=label)
    text.pack()
    flowLayout.add_widget(text)

if verbose:
    print(f"Flap: Initialised Framework ({app_version[0]}.{app_version[1]}.{app_version[2]})")
