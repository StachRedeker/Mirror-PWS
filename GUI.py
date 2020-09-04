from PySide2.QtWidgets import QApplication, QWidget
from PySide2.QtGui import QIcon, QGuiApplication, QCursor
from yaml import load, dump, FullLoader
import sys

window_title = "Stock Market AI"
window_width = 800
window_height = 500

with open("config.yaml") as config:
    data = load(config, Loader=FullLoader)

    if "window_title" in data:
        window_title = data["window_title"]

    if "start_window_width" in data:
        window_width = data["start_window_width"]
    if "start_window_height" in data:
        window_height = data["start_window_height"]


class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(window_title)
        self.setGeometry(0, 0, window_width, window_height)

        self.center()

        icon = QIcon("icon.png")
        self.setWindowIcon(icon)

        print(window_height, window_width)

    def center(self):
        screen = QGuiApplication.screenAt(QCursor.pos())
        frame_geo = self.frameGeometry()
        frame_geo.moveCenter(screen.geometry().center())
        self.move(frame_geo.topLeft())


app = QApplication(sys.argv)
window = Window()
window.show()

app.exec_()
sys.exit(0)

