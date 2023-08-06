from vector import Vec2d
import better

class Sprite():
    def __init__(self, pos: Vec2d, size: Vec2d, img: better.Image, colkey: int):
        self.pos = pos
        self.size = size
        self.colkey = colkey
        self.img = img

    def get_pos(self) -> Vec2d:
        return self.pos

    def get_size(self) -> Vec2d:
        return self.size

    def get_colkey(self) -> int:
        return self.colkey

    def blt(self, pos: Vec2d):
        better.blt(pos.x, pos.y, self.img, self.pos.x, self.pos.y, self.size.x, self.size.y, self.colkey)

    def blt_scaled(self, pos: Vec2d, scale: float):
        for x in range(self.size.x * scale):
            for y in range(self.size.y * scale):
                better.pset(pos.x + x, pos.y + y, better.pget(self.pos.x + x // scale, self.pos.y + y // scale))

    def colliding(other: Sprite) -> bool:
        return self.pos.x < other.pos.x + other.size.x and self.pos.x + self.size.x > other.pos.x and self.pos.y < other.pos.y + other.size.y and self.pos.y + self.size.y > other.pos.y
