import uharfbuzz as hb
from tempfile import SpooledTemporaryFile

class harfbuzzFont:
    def __init__(
            self,
            font: SpooledTemporaryFile | str,
    ):
        font_data = None
        if type(font) is SpooledTemporaryFile:
            font.seek(0)
            font_data = font.read()
        else:
            font_file = open(font, "rb")
            font_data = font_file.read()
        self.hb_face = hb.Face(font_data)
        self.hb_font = hb.Font(self.hb_face)

