from vector import Vec2d
import better

class Tile():
    def __init__(self, pos: Vec2d, size: Vec2d, tm: 0 | 1 | 2 | better.Tilemap, colkey: int):
        self.pos = pos
        self.size = size
        self.colkey = colkey
        self.tm = tm

    def get_pos(self) -> Vec2d:
        return self.pos

    def get_size(self) -> Vec2d:
        return self.size

    def get_colkey(self) -> int:
        return self.colkey

    def bltm(self, pos: Vec2d):
        better.bltm(pos.x, pos.y, self.tm, self.pos.x, self.pos.y, self.size.x, self.size.y, self.colkey)
