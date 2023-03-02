from . import transform
from .ecs import Wrapper
from .essentials import Timer
from .transform import Transform

class Acceleration(Wrapper): pass
class Velocity(Wrapper): pass

def init(world):
    world.system(acceleration, before=[velocity])
    world.system(velocity, before=[transform.propagate])

def acceleration(world):
    delta = world.get(Timer).v.get_time() / 1000
    for _, (acceleration, velocity) in world.query(Acceleration, Velocity):
        velocity.v += acceleration.v * delta

def velocity(world):
    delta = world.get(Timer).v.get_time() / 1000
    for _, (velocity, transform) in world.query(Velocity, Transform):
        transform.pos += velocity.v * delta
