# FlapGUI
Flap is a GUI framework for creating cross-platform GUI applications easily using Tkinter. 
# Purpose
FlapGUI is designed to make writing GUI applications as simple as possible, eliminating the learning curve for making functional programs. 

Most GUI frameworks (tkinter, qt, gtk, etc.) have a steep learning curve, which FlapGUI intends to fix.

**Flap is an Alpha framework and is not complete. It is subject to rapid and signigicant change at the moment.**

# Tutorial
This section explains how to make applications using FlapGUI.
## Installing
To install it, simply run:  
```
pip install flapgui
```
## Importing
It is recommended to place the following line at the top of your script:
```
import flapgui as fl
```
This is the "correct" way to do it, but you can do it however you like. If you're following the tutorial, however, you should do it this way.
## Making a Basic Window
To create a basic window, you can use the fl.window() function.

fl.window() takes 3 parameters, a title, height, and width, but none are required.

### Example
```
import flapgui as fl
root = fl.window("Tutorial Window")
```
This will create a blank window with the title "Tutorial Window".
## Adding text to a window
To add some text, you use the fl.pack() function:  
```
import flapgui as fl
root = fl.window("Tutorial Window")
fl.pack("This is some text")
fl.pack("This is some more")
```
## Adding a button
You can also add a button that performs an action when it is pressed.

You do this with the create_button() function.

```
create_button(window, text, command=None)
```

Window is the window you specified, text is the text that will appear on it, and command is the function that is called when you press it.
```
import flapgui as fl
root=fl.window("Tutorial #2: Buttons")
fl.pack("The below button will print stuff to the terminal")
b = fl.create_button(root, "Press Me",lambda: print("hello world"))
```
As you can see, in the above example, I used an anonymous function. 
## Menu Bars
Creating a menu bar allows you to add menus to the top of the program, and can let you add more functionality to it easily.

First, you add a menu bar:  

```
root=fl.window()
menu = fl.create_menu_bar(root)
```
Then, you add cascades to the menu:
```
fileMenu = fl.add_cascade(menu,"File")
editMenu = fl.add_cascade(menu,"Edit")
helpMenu = fl.add_cascade(menu,"Help")
```
Once you've done that, you add commands to those cascades:
```
fl.add_command(fileMenu,"Exit",exit_application,"Ctrl+Q")
```
The above command calls exit_application() and shows "Ctrl+Q" as an accelerator.
### Final Application
```
# Final application
root = fl.window("Tutorial #3: Menu Bar")
menu = fl.create_menu(root)
fileMenu = fl.add_cascade(menu,"File")
editMenu = fl.add_cascade(menu,"Edit")
helpMenu = fl.add_cascade(menu,"Help")
fl.add_command(fileMenu,"Exit",None,"Ctrl+Q")
```

## Adding text entries
Text entries are by far the most complete feature of FlapGUI. There are several ways of adding text entry boxes, which allow the user to add text. 
### new_text()
FlapGUI's new_text() creates a frame and a text entry box inside it, so that it automatically scales to the size of the window, no matter how the user resizes it.
```
root = fl.window()
text = fl.new_text(root)
```
```
fl.new_text(root,width=40, bg="#FFFFFF", fg="#000000")
Creates a new text entry box with a specified width.
```
### tbox()
The fl.tbox() function is a more simple one:
```
tbox(width, height,fg=None,bg=None)
Creates a text box with a specified width and height (numbers refer to the amount of characters).
```
```
root=fl.window(width=500,height=500)
text = fl.tbox(50,1)
```
## Functions for manipulating text entries
There are several functions for manipulating the contents of a text entry box.
### select_all_text(text)
Selects all text in the specified text box.
### get_text(text)
Returns the contents of the specified text box.
### set_text(text_widget, text):
Sets the contents of a text widget to a string.
### add_scrollbar(window, text_widget)
**Note: This function is a work in progress**

Adds a scrollbar to a specified text widget.
## Grids
**Note: grids are a work in progress.**

Grids allow you to place items inside of a grid, creating an evenly-distributed plane of items.
### Creating a grid
```
root = fl.window()
grid = fl.createGrid(root)
```
This will create a grid that you can place objects inside of.
### Adding buttons to a grid
You can create grid buttons!
```
root=fl.window()
grid =fl.createGrid(root)
fl.addGridButon(grid, "Press Me",None,0,0)
```
The last line creates a grid button at a specified x/y location.

Format:
```
addGridButton(grid, label, function, x, y, buttonDimensionX=2, buttonDimentsionY=1)
```

### Note about grids
Grids are a recent implementation and will be updated with more stuff at some point.
## Miscellaneous Functions
### autoScaleResolution(window)
Automatically expands or shrinks the window to fit its contents perfectly.
### scaleResolution, window, width, height)
Sets the resolution to width x height.
### file_selector(is_file=True)
Allows the user to select a file. Returns its path or None if nothing was selected.

Passing False to it gets the user to select a directory instead.

### make_binding(root,binding,command)
This creates a binding with a specified binding and function associated with it.

(Binding guide coming soon)
### close_window(window)
Closes the window specified.
### clear_window(window)
Deletes all of a window's widgets.
### get_flap_version()
Returns the version of FlapGUI used as a list, for example [0,0,3] for version 0.0.3. 
### check_version(check)
Returns whether app_version is equal to check.
### choose_color()
Returns a colour that the user chooses in HTML format.
### maximiseWindow(window)
Maximises the specified window.
### verbose
Not a function, just a bool. Set to True by default. Set to False to hide all the text in the console.
```
fl.verbose = False
```
## Conclusion
FlapGUI may not be complete, but it can already be used to make basic applications with. Future updates will add more widget types, more customisations, and will also update the functionality to be more consistent with itself.