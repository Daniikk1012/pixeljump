from . import essentials, io, motion, sprite, transform, viewport
from .ecs import *

def init(world, size=None):
    essentials.init(world, size)
    io.init(world)
    motion.init(world)
    sprite.init(world)
    transform.init(world)
    viewport.init(world)
