import tkinter as tk
from GUI import quit_app, navbar_color, navbar

quit_image = tk.PhotoImage(file="Images/QuitButton/Normal.png")
quit_image_hover = tk.PhotoImage(file="Images/QuitButton/Hover.png")
# quit_image_active = tk.PhotoImage(file="Images/QuitButton/Active.png")


class QuitButton:
    quit_button = tk.Button()

    def __init__(self):
        self.quit_button = tk.Button(navbar, borderwidth=0, image=quit_image, command=quit_app, bg=navbar_color)
        self.quit_button.bind("<Enter>", self.on_enter)
        self.quit_button.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        self.quit_button.config(image=quit_image_hover)

    def on_leave(self, e):
        self.quit_button.config(image=quit_image)