

class Color:

    def __init__(self, r: int, g: int, b: int, a: int=255) -> None:
        self.r = int(r)
        self.g = int(g)
        self.b = int(b)
        self.a = int(a)

    @staticmethod
    def from_hsv(h: int, s: int, v: int):
        return Color(0,0,0)

    @staticmethod
    def from_hex(hex_str: str):
        return Color(0,0,0)

