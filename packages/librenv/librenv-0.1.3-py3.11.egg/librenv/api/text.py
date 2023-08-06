from sdl2.ext import Texture, FontTTF
from sdl2 import *

from .drawable import Drawable
from .vector2 import Vector2

class Text(Drawable):

    def __init__(self, text: str="", font_path: str="", ptsize: int=12, position: Vector2=Vector2()) -> None:
        self.text       = text
        self.font       = FontTTF(font_path, ptsize, SDL_Color())
        self.position   = position
        super().__init__(self)

    def _draw(self, renderer, _):
        surface = self.font.render_text(self.text, width=540)
        texture = Texture(renderer, surface)
        renderer.blit(texture, dstrect=(self.position.x, self.position.y))
        
