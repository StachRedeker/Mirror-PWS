import tkinter as tk
from tkinter import filedialog, Text
from yaml import load, FullLoader

from Components import Buttons
import sys

window_title = "Stock Market AI"
window_width = 1280
window_height = 720
background_color = "#356e78"
navbar_color = "#063842"

#
# with open("config.yaml") as config:
#     data = load(config, Loader=FullLoader)
#
#     if "window_title" in data:
#         window_title = data["window_title"]
#
#     if "start_window_height" in data:
#         window_height = data["start_window_height"]
#     if "start_window_width" in data:
#         window_width = data["start_window_width"]
#
#     if "background_color" in data:
#         background_color = data["background_color"]
#     if "navbar_color" in data:
#         navbar_color = data["navbar_color"]


root = tk.Tk()
root.iconbitmap("./icon.ico")


def quit_app():
    sys.exit()


canvas = tk.Canvas(root, height=window_height, width=window_width, bg=background_color)
canvas.pack()

frame = tk.Frame(root, bg=background_color)
frame.place(relwidth=1, relheight=1)

navbar = tk.Frame(root, bg=navbar_color)
navbar.place(width=window_width * 0.2, relheight=1)

quit_button = Buttons.QuitButton.quit_button
quit_button.pack()

root.mainloop()
