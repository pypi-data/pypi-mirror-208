import pyxel
from vector import Vec2d
from sprite import Sprite
from tile import Tile
from manager import Manager

# flake8: noqa
from ctypes import POINTER, c_uint8
from typing import Callable, List, Optional, Tuple, Union

def init(
    width: int,
    height: int,
    *,
    title: Optional[str] = None,
    fps: Optional[int] = None,
    quit_key: Optional[int] = None,
    display_scale: Optional[int] = None,
    capture_scale: Optional[int] = None,
    capture_sec: Optional[int] = None,
) -> None:
    return pyxel.init(width, height, title, fps, quit_key, display_scale, capture_scale, capture_sec)
def title(title: str) -> None:
    return pyxel.title(title)
def icon(data: List[str], scale: int) -> None:
    return pyxel.icon(data, scale)
def fullscreen(full: bool) -> None:
    return pyxel.fullscreen(full)
def run(manager: Manager) -> None:
    return pyxel.run(manager.run_update, manager.run_draw)
def show() -> None:
    return pyxel.show()
def flip() -> None:
    return pyxel.flip()
def quit() -> None:
    return pyxel.quit()
def process_exists(pid: int) -> bool:
    return pyxel.process_exists(pid)

# Resource
def load(
    filename: str,
    *,
    image: Optional[bool] = None,
    tilemap: Optional[bool] = None,
    sound: Optional[bool] = None,
    music: Optional[bool] = None,
) -> None:
    return pyxel.load(filename, image, tilemap, sound, music)
def save(
    filename: str,
    *,
    image: Optional[bool] = None,
    tilemap: Optional[bool] = None,
    sound: Optional[bool] = None,
    music: Optional[bool] = None,
) -> None:
    return pyxel.save(filename, image, tilemap, sound, music)
def screenshot(scale: Optional[int] = None) -> None:
    return pyxel.screenshot(scale)
def reset_capture() -> None:
    return pyxel.reset_capture()
def screencast(scale: Optional[int] = None) -> None:
    return pyxel.screencast(scale)

def btn(key: int) -> bool:
    return pyxel.btn(key)
def btnp(
    key: int, *, hold: Optional[int] = None, repeat: Optional[int] = None
) -> bool:
    return pyxel.btnp(key, hold, repeat)
def btnr(key: int) -> bool:
    return pyxel.btnr(key)
def btnv(key: int) -> int:
    return pyxel.btnv(key)
def mouse(visible: bool) -> None:
    return pyxel.mouse(visible)
def set_btn(key: int, state: bool) -> None:
    return pyxel.set_btn(key, state)
def set_btnv(key: int, val: float) -> None:
    return pyxel.set_btnv(key, val)
def set_mouse_pos(pos: Vec2d) -> None:
    return pyxel.set_mouse_pos(pos.x, pos.y)

def image(img: int) -> Image:
    return pyxel.image(img)
def tilemap(tm: int) -> Tilemap:
    return pyxel.tilemap(tm)
def clip(
    pos: Vec2d, size: Vec2d
) -> None:
    return pyxel.clip(pos.x, pos.y, size.x, size.y)

def camera(
    pos: Vec2d
) -> None:
    return pyxel.camera(pos.x, pos.y)
def pal(col1: Optional[int] = None, col2: Optional[int] = None) -> None:
    return pyxel.pal(col1, col2)
def cls(col: int) -> None:
    return pyxel.cls(col)
def pget(pos: Vec2d) -> int:
    return pyxel.pget(pos.x, pos.y)
def pset(pos: Vec2d, col: int) -> None:
    return pyxel.pset(pos.x, pos.y, col)
def line(point1: Vec2d, point2: Vec2d, col: int) -> None:
    return pyxel.line(point1.x, point1.y, point2.x, point2.y, col)
def rect(pos: Vec2d, size: Vec2d, col: int) -> None:
    return pyxel.rect(pos.x, pos.y, size.x, size.y, col)
def rectb(pos: Vec2d, size: Vec2d, col: int) -> None:
    return pyxel.rectb(pos.x, pos.y, size.x, size.y, col)
def circ(pos: Vec2d, r: float, col: int) -> None:
    return pyxel.circ(pos.x, pos.y, r, col)
def circb(pos: Vec2d, r: float, col: int) -> None:
    return pyxel.circb(pos.x, pos.y, r, col)
def elli(self, pos: Vec2d, size: Vec2d, col: int) -> None:
    return pyxel.elli(pos.x, pos.y, size.x, size.y, col)
def ellib(self, pos: Vec2d, size: Vec2d, col: int) -> None:
    return pyxel.ellib(pos.x, pos.y, size.x, size.y, col)
def tri(
    point1: Vec2d,
    point2: Vec2d,
    point3: Vec2d,
    col: int,
) -> None:
    return pyxel.tri(point1.x, point1.y, point2.x, point2.y, point3.x, point3.y, col)
def trib(
    point1: Vec2d,
    point2: Vec2d,
    point3: Vec2d,
    col: int,
) -> None:
    return pyxel.trib(point1.x, point1.y, point2.x, point2.y, point3.x, point3.y, col)
def fill(pos: Vec2d, col: int) -> None:
    return pyxel.fill(pos.x, pos.y, col)
def blt(
    pos: Vec2d,
    sprite: Sprite,
) -> None:
    return pyxel.blt(pos.x, pos.y, sprite.img, sprite.u, sprite.v, sprite.w, sprite.h, sprite.colkey)
def bltm(
    pos: Vec2d,
    tile: Tile,
) -> None:
    return pyxel.bltm(pos.x, pos.y, tile.tm, tile.u, tile.v, tile.w, tile.h, tile.colkey)
def text(pos: Vec2d, s: str, col: int) -> None:
    return pyxel.text(pos.x, pos.y, s, col)

# Audio
Channel = pyxel.Channel
Sound = pyxel.Sound
Music = pyxel.Music

def channel(ch: int) -> Channel:
    return pyxel.channel(ch)
def sound(snd: int) -> Sound:
    return pyxel.sound(snd)
def music(msc: int) -> Music:
    return pyxel.music(msc)
def play_pos(ch: int) -> Optional[Tuple[int, int]]:
    return pyxel.play_pos(ch)
def play(
    ch: int,
    snd: Union[int, List[int], Sound, List[Sound]],
    *,
    tick: Optional[int] = None,
    loop: Optional[bool] = None,
) -> None:
    return pyxel.play(ch, snd, tick=tick, loop=loop)
def playm(
    msc: int, *, tick: Optional[int] = None, loop: Optional[bool] = None
) -> None:
    return pyxel.playm(msc, tick=tick, loop=loop)
def stop(ch: Optional[int] = None) -> None:
    return pyxel.stop(ch)

# Math
def ceil(x: float) -> int:
    return pyxel.ceil(x)
def floor(x: float) -> int:
    return pyxel.floor(x)
def sgn(x: float) -> float:
    return pyxel.sgn(x)
def sqrt(x: float) -> float:
    return pyxel.sqrt(x)
def sin(deg: float) -> float:
    return pyxel.sin(deg)
def cos(deg: float) -> float:
    return pyxel.cos(deg)
def atan2(y: float, x: float) -> float:
    return pyxel.atan2(y, x)
def rseed(seed: int) -> None:
    return pyxel.rseed(seed)
def rndi(a: int, b: int) -> int:
    return pyxel.rndi(a, b)
def rndf(a: float, b: float) -> int:
    return pyxel.rndf(a, b)
def nseed(seed: int) -> None:
    return pyxel.nseed(seed)
def noise(x: float, y: Optional[float] = None, z: Optional[float] = None) -> float:
    return pyxel.noise(x, y, z)

# Image class
class Image:
    size: Vec2d
    def __init__(self, size: Vec2d) -> None:
        self._image = pyxel.Image(size.x, size.y)
        self.size = size
    @staticmethod
    def from_image(filename: str) -> Image:
        return Image(pyxel.image(filename))
    def data_ptr(self) -> POINTER(c_uint8):
        return self._image.data_ptr
    def set(self, pos: Vec2d, data: List[str]) -> None:
        return self._image.set(pos.x, pos.y, data)
    def load(self, pos: Vec2d, filename: str) -> None:
        return self._image.load(pos.x, pos.y, filename)
    def save(self, filename: str, scale: int) -> None:
        return self._image.save(filename, scale)
    def clip(
        self,
        pos: Vec2d,
        size: Vec2d
    ) -> None:
        return self._image.clip(pos.x, pos.y, size.x, size.y)
    def camera(
        self,
        pos: Optional[Vec2d] = None
    ) -> None:
        if pos is None:
            return self._image.camera()
        else:
            return self._image.camera(pos.x, pos.y)
    def pal(self, col1: Optional[int] = None, col2: Optional[int] = None) -> None:
        self._image.pal(col1=col1, col2=col2)
    def cls(self, col: int) -> None:
        return self._image.cls(col)
    def pget(self, pos: Vec2d) -> int:
        return self._image.pget(pos.x, pos.y)
    def pset(self, pos: Vec2d, col: int) -> None:
        return self._image.pset(pos.x, pos.y, col)
    def line(self, pos1: Vec2d, pos2: Vec2d, col: int) -> None:
        return self._image.line(pos1.x, pos1.y, pos2.x, pos2.y, col)
    def rect(self, pos: Vec2d, size: Vec2d, col: int) -> None:
        return self._image.rect(pos.x, pos.y, size.x, size.y, col)
    def rectb(self, pos: Vec2d, size: Vec2d, col: int) -> None:
        return self._image.rectb(pos.x, pos.y, size.x, size.y, col)
    def circ(self, pos: Vec2d, r: float, col: int) -> None:
        return self._image.circ(pos.x, pos.y, r, col)
    def circb(self, pos: Vec2d, r: float, col: int) -> None:
        return self._image.circb(pos.x, pos.y, r, col)
    def elli(self, pos: Vec2d, size: Vec2d, col: int) -> None:
        return self._image.elli(pos.x, pos.y, size.x, size.y, col)
    def ellib(self, pos: Vec2d, size: Vec2d, col: int) -> None:
        return self._image.ellib(pos.x, pos.y, size.x, size.y, col)
    def tri(
        self, pos1: Vec2d, pos2: Vec2d, pos3: Vec2d, col: int
    ) -> None:
        return self._image.tri(pos1.x, pos1.y, pos2.x, pos2.y, pos3.x, pos3.y, col)
    def trib(
        self, pos1: Vec2d, pos2: Vec2d, pos3: Vec2d, col: int
    ) -> None:
        return self._image.trib(pos1.x, pos1.y, pos2.x, pos2.y, pos3.x, pos3.y, col)
    def fill(self, pos: Vec2d, col: int) -> None:
        return self._image.fill(pos.x, pos.y, col)
    def blt(
        self,
        pos: Vec2d,
        sprite: Sprite,
    ) -> None:
        if sprite.img != self:
            raise ValueError("Sprite image does not match image")
        return self._image.blt(pos.x, pos.y, sprite.img._image, sprite.u, sprite.v, sprite.w, sprite.h)
    def bltm(
        self,
        pos: Vec2d,
        tile: Tile
    ) -> None:
        if tile.img != self:
            raise ValueError("Tile image does not match image")
        return self._image.bltm(pos.x, pos.y, tile.img._image, tile.u, tile.v, tile.w, tile.h)
    def text(self, pos: Vec2d, s: str, col: int) -> None:
        return self._image.text(pos.x, pos.y, s, col)

# Tilemap class
class Tilemap:
    size = Vec2d
    image: Image
    refimg: Optional[int]
    def __init__(self, size: Vec2d, img: Image) -> None:
        self.size = size
        self.image = img
        self.refimg = None
        self._tilemap = pyxel.tilemap(size.x, size.y, self.image._image)
    def data_ptr(self) -> POINTER(c_uint8):
        return self._tilemap.data_ptr
    def set(self, pos: Vec2d, data: List[str]) -> None:
        return self._tilemap.set(pos.x, pos.y, data)
    def clip(
        self,
        pos: Optional[Vec2d] = None,
        size: Optional[Vec2d] = None
    ) -> None:
        self._tilemap.clip(x=pos.x, y=pos.y, w=size.x, h=size.y)
    def camera(
        self,
        pos: Optional[Vec2d] = None,
    ) -> None:
        if pos is None:
            return self._tilemap.camera()
        else:
            return self._tilemap.camera(pos.x, pos.y)
    def cls(self, tile: Vec2d) -> None:
        return self._tilemap.cls(tile.x, tile.y)
    def pget(self, pos: Vec2d) -> Tuple[int, int]:
        return self._tilemap.pget(pos.x, pos.y)
    def pset(self, pos: Vec2d, tile: Vec2d) -> None:
        return self._tilemap.pset(pos.x, pos.y, tile.x, tile.y)
    def line(
        self, pos1: Vec2d, pos2: Vec2d, tile: Vec2d
    ) -> None:
        return self._tilemap.line(pos1.x, pos1.y, pos2.x, pos2.y, tile.x, tile.y)
    def rect(
        self, pos: Vec2d, size: Vec2d, tile: Vec2d
    ) -> None:
        return self._tilemap.rect(pos.x, pos.y, size.x, size.y, tile.x, tile.y)
    def rectb(
        self, pos: Vec2d, size: Vec2d, tile: Vec2d
    ) -> None:
        return self._tilemap.rectb(pos.x, pos.y, size.x, size.y, tile.x, tile.y)
    def circ(self, pos: Vec2d, r: float, tile: Vec2d) -> None:
        return self._tilemap.circ(pos.x, pos.y, r, tile.x, tile.y)
    def circb(self, pos: Vec2d, r: float, tile: Vec2d) -> None:
        return self._tilemap.circb(pos.x, pos.y, r, tile.x, tile.y)
    def elli(
        self, pos: Vec2d, size: Vec2d, tile: Tuple[int, int]
    ) -> None:
        return self._tilemap.elli(pos.x, pos.y, size.x, size.y, tile.x, tile.y)
    def ellib(
        self, pos: Vec2d, size: Vec2d, tile: Tuple[int, int]
    ) -> None:
        return self._tilemap.ellib(pos.x, pos.y, size.x, size.y, tile.x, tile.y)
    def tri(
        self,
        pos1: Vec2d,
        pos2: Vec2d,
        pos3: Vec2d,
        tile: Vec2d,
    ) -> None:
        return self._tilemap.tri(pos1.x, pos1.y, pos2.x, pos2.y, pos3.x, pos3.y, tile.x, tile.y)
    def trib(
        self,
        pos1: Vec2d,
        pos2: Vec2d,
        pos3: Vec2d,
        tile: Vec2d,
    ) -> None:
        return self._tilemap.trib(pos1.x, pos1.y, pos2.x, pos2.y, pos3.x, pos3.y, tile.x, tile.y)
    def fill(self, pos: Vec2d, tile: Vec2d) -> None:
        return self._tilemap.fill(pos.x, pos.y, tile.x, tile.y)
    def blt(
        self,
        pos: Vec2d,
        tile: Tile
    ) -> None:
        if tile.tm != self:
            raise ValueError("Tile's tilemap does not match tilemap")
        return self._tilemap.blt(pos.x, pos.y, tile.img._image, tile.u, tile.v, tile.w, tile.h)

# Channel class
Channel = pyxel.Channel

Sound = pyxel.Sound

Music = pyxel.Music