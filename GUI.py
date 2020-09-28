import tkinter as tk
from tkinter import filedialog, Text

import sys

window_title = "Stock Market AI"
window_width = 1280
window_height = 720
background_color = "#356e78"
navbar_color = "#063842"

root = tk.Tk()
root.iconbitmap("./icon.ico")
root.title(window_title)


def quit_app():
    sys.exit()


class QuitButton:
    quit_button = tk.Button()

    quit_image = tk.PhotoImage(file="Images/QuitButton/Normal.png")
    quit_image_hover = tk.PhotoImage(file="Images/QuitButton/Hover.png")
    quit_image_active = tk.PhotoImage(file="Images/QuitButton/Active.png")

    def __init__(self):
        self.quit_button = tk.Button(navbar, borderwidth=0, image=self.quit_image, command=quit_app,
                                     bg=navbar_color, activebackground=navbar_color, height=35, width=90)
        self.quit_button.bind("<Enter>", self.on_enter)
        self.quit_button.bind("<Leave>", self.reset)
        self.quit_button.bind("<Button-1>", self.on_mouse_down)
        self.quit_button.bind("<ButtonRelease-1>", self.reset)

        self.quit_button.pack()

    def on_enter(self, e):
        self.quit_button.config(image=self.quit_image_hover)

    def on_mouse_down(self, e):
        self.quit_button.config(image=self.quit_image_active)

    def reset(self, e):
        self.quit_button.config(image=self.quit_image)

    def update(self):
        self.quit_button.update()
        self.quit_button.place(x=navbar.winfo_width() - self.quit_button.winfo_width(), y=navbar.winfo_height() - self.quit_button.winfo_height())


canvas = tk.Canvas(root, height=window_height, width=window_width, bg=background_color)
canvas.pack()

frame = tk.Frame(root, bg=background_color)
frame.place(relwidth=1, relheight=1)

navbar = tk.Frame(root, bg=navbar_color)
navbar.place(width=window_width * 0.2, relheight=1)

navbar.update()

quit_button = QuitButton()
quit_button.update()

root.mainloop()
