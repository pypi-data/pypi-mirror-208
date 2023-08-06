from sdl2.ext import Texture
from sdl2.sdlimage import IMG_Load
from sdl2 import *

from .drawable import Drawable
from .vector2 import Vector2

class Sprite(Drawable):

    def __init__(self, image_path: str="", position: Vector2=Vector2()) -> None:
        self.image      = IMG_Load(bytes(image_path, 'utf-8'))
        self.position   = position
        super().__init__(self)

    def _draw(self, renderer, _):
        texture = Texture(renderer, self.image)
        renderer.copy(texture, dstrect=(self.position.x, self.position.y))

