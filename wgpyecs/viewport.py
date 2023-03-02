from pygame import Vector2

from . import essentials, transform
from .essentials import Screen
from .transform import Transform

class Camera:
    def __init__(self, center, size):
        self.center = Vector2(center)
        self.size = Vector2(size)

class Viewport(Camera):
    def __init__(self, size, h=None, /):
        if h is None:
            w, h = size
        else:
            w = size
        self.size = Vector2(w, h)

def init(world):
    world.system(camera, before=[transform.propagate])
    world.system(viewport, before=[camera])

def spawn_viewport(world, size):
    return (transform.spawn_transform(world)
        .add(Camera((0, 0), size))
        .add(Viewport(size)))

def camera(world):
    size = world.get(Screen).v.get_size()

    for _, (camera, transform) in world.query(Camera, Transform):
        scl = size / camera.size.elementwise()
        transform.setscl(scl).setpos(
            -(scl.elementwise() * (camera.center - camera.size / 2)),
        )

def viewport(world):
    width, height = world.get(Screen).v.get_size()

    for _, (camera, viewport) in world.query(Camera, Viewport):
        if viewport.size.x / viewport.size.y < width / height:
            camera.size.x = viewport.size.y * width / height
            camera.size.y = viewport.size.y
        else:
            camera.size.x = viewport.size.x
            camera.size.y = viewport.size.x * height / width 
