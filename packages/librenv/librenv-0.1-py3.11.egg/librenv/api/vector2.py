
class Vector2:

    def __init__(self, *args):
        """
        :param x    - int, x point
        :param y    - int, y point
        or
        :param pos  - (int, int) x,y points
        """
        if len(args) == 2:
            self.x = int(args[0])
            self.y = int(args[1])
        elif len(args) == 1:
            self.x = int(args[0][0])
            self.y = int(args[0][1])
        else:
            self.x, self.y = 0, 0


