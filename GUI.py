import tkinter as tk
from tkinter import filedialog, Text
from yaml import load, FullLoader
import sys

# region Config
window_title = "Stock Market AI"
window_width = 800
window_height = 500
background_color = "#091726"

with open("config.yaml") as config:
    data = load(config, Loader=FullLoader)

    if "window_title" in data:
        window_title = data["window_title"]

    if "start_window_height" in data:
        window_height = data["start_window_height"]
    if "start_window_width" in data:
        window_width = data["start_window_width"]

    if "background_color" in data:
        background_color = data["background_color"]
# endregion


root = tk.Tk()
root.iconbitmap("./icon.ico")


def quit_app():
    sys.exit()


canvas = tk.Canvas(root, height=window_height, width=window_width, bg=background_color)
canvas.pack()

frame = tk.Frame(root, bg="white")
frame.place(relwidth=0.8, relheight=0.8, relx=0.1, rely=0.1)

quitApp = tk.Button(frame, text="Quit", padx=10, pady=5, fg="white", bg="#040f1a", command=quit_app)
quitApp.pack()

root.mainloop()
