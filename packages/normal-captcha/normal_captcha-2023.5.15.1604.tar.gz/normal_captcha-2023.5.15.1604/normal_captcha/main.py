import pytesseract
from PIL import Image


class NormalCaptcha:

    def __init__(self):
        self.path = None

    def main(self, path: str, tesseract_path: str):
        if path is [None, '']:
            raise ValueError('All the params are requireds')

        pytesseract.pytesseract.tesseract_cmd = tesseract_path
        self.path = path

    def process(self):
        image = Image.open(self.path).convert("L")
        return pytesseract.image_to_string(image)
