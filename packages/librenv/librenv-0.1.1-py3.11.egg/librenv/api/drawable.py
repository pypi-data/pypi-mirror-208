
class Drawable:

    DRAWABLES = list()

    def __init__(self, obj) -> None:
        self.is_hidden  = False
        Drawable.DRAWABLES.append(obj)

    def _draw(self, renderer, window):
        pass

    def show(self) -> None:
        self.is_hidden = False

    def hide(self) -> None:
        self.is_hidden = True


