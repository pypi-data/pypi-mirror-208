from screeny import *
from typing import Union

import copy
import numpy as np, cv2, pytesseract
# pytesseract.pytesseract.tesseract_cmd = r'/usr/local/Cellar/tesseract/5.3.1/bin/tesseract'


class Image:

    def __init__(self, image: Union[str, np.ndarray, "Image"]):
        if type(image) is str:
            self.data = cv2.imread(image)
            self.color_code = "BGR"
        elif type(image) is np.ndarray:
            self.data = image
            self.color_code = "BGR"
        elif type(image) is Image:
            self.data = image.get_data()
            self.color_code = image.color_code
        else:
            raise Exception("Unknown image-type!")

    def get_data(self):
        return self.data

    def to_grayscale(self) -> 'Image':
        if self.color_code == "RGB":
            self.data = cv2.cvtColor(self.data, cv2.COLOR_RGB2GRAY)
        elif self.color_code == "BGR":
            self.data = cv2.cvtColor(self.data, cv2.COLOR_BGR2GRAY)
        elif self.color_code == "HSV":
            self.data = cv2.cvtColor(self.data, cv2.COLOR_HSV2GRAY)
        elif self.color_code == "GRAY":
            pass
        else:
            raise Exception(f"Colorcode {self.color_code} is unknown!")

        self.color_code = "GRAY"
        return self

    def to_hsv(self) -> "Image":
        if self.color_code == "RGB":
            self.data = cv2.cvtColor(self.data, cv2.COLOR_RGB2HSV)
        elif self.color_code == "BGR":
            self.data = cv2.cvtColor(self.data, cv2.COLOR_BGR2HSV)
        elif self.color_code == "HSV":
            pass
        elif self.color_code == "GRAY":
            self.data = cv2.cvtColor(self.data, cv2.COLOR_GRAY2HSV)
        else:
            raise Exception(f"Colorcode {self.color_code} is unknown!")

        self.color_code = "HSV"
        return self

    def locate_image(self, image_to_find: Union[str, np.ndarray, "Image"], confidence: float = 0.8) -> Point | bool:
        template = Image(image_to_find).to_grayscale()
        image = copy.copy(self)
        image.to_grayscale()

        heat_map = cv2.matchTemplate(image.get_data(), template.get_data(), cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(heat_map)
        if max_val >= confidence:
            w, h = template.get_data().shape
            return Point(max_loc[0] + (w / 2), max_loc[1] + (h / 2))
        else:
            return False

    def resize(self, factor: int) -> "Image":
        self.data = cv2.resize(self.data, None, fx=factor, fy=factor, interpolation=cv2.INTER_CUBIC)
        return self

    def binarize(self, method: str, threshold: int = 127) -> "Image":
        if self.color_code != "GRAY":
            raise Exception("Colorcode should be 'GRAY' for binarizing image!")

        if method == "simple_thresholding":
            ret, self.data = cv2.threshold(self.data, threshold, 255, cv2.THRESH_BINARY_INV)
        elif method == "adaptive_thresholding":
            self.data = cv2.adaptiveThreshold(self.data, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
        elif method == "otsus_thresholding":
            # The threshold-value will be automatically detected
            ret, self.data = cv2.threshold(self.data, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        else:
            raise Exception(f"Binarization-metho '{method}' is unknown!")

        return self

    def denoise(self) -> "Image":
        self.data = cv2.fastNlMeansDenoising(self.data, None, 10, 21, 7)
        return self

    def read_text(
            self, resize_factor: int = None,
            whitelist: str = "._0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    ):
        image = copy.copy(self)
        image.to_grayscale()

        if resize_factor:
            image.resize(resize_factor)

        image.binarize("otsus_thresholding")
        image.denoise()

        # psm:
        # 3     - Fully automatic page segmentation, but no OSD. (Default)
        # 13    - (Raw line. Treat the image as a single text line, bypassing hacks that are Tesseract-specific.)
        text = pytesseract.image_to_string(
            image.get_data(),
            config="-c tessedit_char_whitelist=" + whitelist + " --psm 3 load_system_dawg=0 load_freq_dawg=0"
        ).strip("\n\r")
        return text

    def show(self, title: str = ""):
        cv2.imshow(title, self.data)
        cv2.waitKey(0)

    def invert(self) -> "Image":
        self.data = cv2.bitwise_not(self.data)
        return self
