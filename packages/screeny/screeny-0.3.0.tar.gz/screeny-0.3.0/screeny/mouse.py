from PySide6 import QtGui
from PySide6.QtGui import QGuiApplication


class Mouse:

    def __init__(self, q_screen: QtGui.QScreen = None):
        if q_screen is None:
            self.q_screen = QGuiApplication().primaryScreen()
        else:
            self.q_screen = q_screen

        self.q_cursor = QtGui.QCursor(self.q_screen.grabWindow(window=0))

    def get_pos(self):
        return self.q_cursor.pos().x(), self.q_cursor.pos().y()
