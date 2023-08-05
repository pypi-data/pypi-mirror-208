from screeny import *
from PySide6.QtGui import QGuiApplication

import numpy as np
import mss as m


class Screeny:

    def __init__(self):
        """
        Initializing variables of the class.
        """
        self.mss = m.mss()
        self.mss_monitor = self.mss.monitors[1]

        # Because QGuiApplication is a singleton, it needs to be checked if already an instance exists of it.
        # Otherwise, it'll lead to a runtime error, if multiple instances of the screeny class will be created.
        if isinstance(QGuiApplication, type(None)):
            self.q_screen = QGuiApplication().primaryScreen()
        else:
            self.q_screen = QGuiApplication.primaryScreen()

        self.mouse = Mouse(self.q_screen)

    def locate_image(
            self, image: str | np.ndarray | Image, rect: Rect = None, confidence: float = 0.8
    ) -> Point | bool:
        """
        Search for an image on the screen and returns the location of the found image in pixel or False, if no image was found.

        :param image:       URL or numpy-array of the image to find.
        :param rect:        A rectangular area where to search for the image.
        :param confidence:  A threshold when an image is declared as found.
        :return:            Returns the location of the image or False, if no image was found.
        """
        screenshot = self.take_screenshot(rect)
        return screenshot.locate_image(image, confidence)

    def take_screenshot(self, rect: Rect = None) -> Image:
        """
        Takes a screenshot of the complete monitor or a given area.

        :param rect:    Rectangular area where the screenshot will be taken.
        :return:        Image as a numpy-array.
        """
        if rect is None:
            img = np.array(self.mss.grab(self.mss_monitor))
        else:
            img = np.array(self.mss.grab((rect.x(), rect.y(), rect.width(), rect.height())))
        return Image(img)

    def get_mouse_pos(self):
        """
        Returns the current position of the mouse.

        :return:    Tuple of xy-coordinates of the current mouse position. -> (x, y)
        """
        return self.mouse.get_pos()

    def read_text(self, rect: Rect):
        image = self.take_screenshot(rect)
        return image.read_text()
