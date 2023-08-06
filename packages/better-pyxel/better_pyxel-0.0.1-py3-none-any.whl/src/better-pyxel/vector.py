class Vec2d():
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y


    def __repr__(self):
        return f"Vector2d({self.x}, {self.y})"


    # Math operations
    def __add__(self, other):
        return Vec2d(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vec2d(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        return Vec2d(self.x * other.x, self.y * other.y)

    def __truediv__(self, other):
        return Vec2d(self.x / other.x, self.y / other.y)

    def __floordiv__(self, other):
        return Vec2d(self.x // other.x, self.y // other.y)

    def __mod__(self, other):
        return Vec2d(self.x % other.x, self.y % other.y)


    def __pow__(self, other):
        return Vec2d(self.x ** other.x, self.y ** other.y)


    def __and__(self, other):
        return Vec2d(self.x & other.x, self.y & other.y)

    def __xor__(self, other):
        return Vec2d(self.x ^ other.x, self.y ^ other.y)

    def __or__(self, other):
        return Vec2d(self.x | other.x, self.y | other.y)


    def __lshift__(self, other):
        return Vec2d(self.x << other.x, self.y << other.y)

    def __rshift__(self, other):
        return Vec2d(self.x >> other.x, self.y >> other.y)

    # Comparison operations
    def __lt__(self, other):
        return self.x < other.x and self.y < other.y

    def __le__(self, other):
        return self.x <= other.x and self.y <= other.y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return self.x != other.x or self.y != other.y

    def __gt__(self, other):
        return self.x > other.x and self.y > other.y

    def __ge__(self, other):
        return self.x >= other.x and self.y >= other.y

    # Unary operations

    def __neg__(self):
        return Vec2d(-self.x, -self.y)

    def __pos__(self):
        return Vec2d(+self.x, +self.y)

    def __abs__(self):
        return Vec2d(abs(self.x), abs(self.y))

    def __invert__(self):
        return Vec2d(~self.x, ~self.y)


