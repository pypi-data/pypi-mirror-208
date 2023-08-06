from .sprite import Sprite
from .color import Color

class Character:

    def __init__(self, name: str, avatar: Sprite | None=None,
                 name_font_size: int=20, text_font_size: int=12,
                 name_color: Color=Color(), text_color: Color=Color()
        ):
        self.name = name
        self.avatar = avatar
        self.name_font_size = name_font_size
        self.text_font_size = text_font_size
        self.name_color = name_color
        self.text_color = text_color


