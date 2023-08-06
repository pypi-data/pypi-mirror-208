from sdl2.sdlimage import IMG_Load
from sdl2 import *

from .vector2 import Vector2

class Sprite:

    SPRITES = list()

    def __init__(self, image_path: str="", position: Vector2=Vector2()) -> None:
        self.image      = IMG_Load(bytes(image_path, 'utf-8'))
        self.position   = position
        self.is_hidden  = False
        Sprite.SPRITES.append(self)

    def show(self) -> None:
        self.is_hidden = False

    def hide(self) -> None:
        self.is_hidden = True


