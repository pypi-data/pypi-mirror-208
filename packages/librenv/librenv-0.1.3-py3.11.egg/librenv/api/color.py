import colorsys

class Color:

    def __init__(self, r: int=255, g: int=255, b: int=255, a: int=255) -> None:
        self.r = int(r)
        self.g = int(g)
        self.b = int(b)
        self.a = int(a)

    @staticmethod
    def from_hsv(h: int, s: int, v: int):
        r, g, b = tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h,s,v))
        return Color(r, g, b)

    @staticmethod
    def from_hex(hex_str: str):
        r, g, b = tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
        return Color(r, g, b)

