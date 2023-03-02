from pygame import Vector2

from .ecs import Parent, Wrapper

class Size(Wrapper):
    def __init__(self, v, h=None, /):
        if h is None:
            w, h = v
        else:
            w = v
        self.v = Vector2(w, h)

class Transform:
    def __init__(self):
        self.pos = Vector2(0, 0)
        self.scl = Vector2(1, 1)
        self.z = 0

    def set(self, transform):
        self.setpos(transform.pos).setscl(transform.scl).setz(transform.z)
        return self

    def setpos(self, pos, y=None, /):
        if y is None:
            self.pos.x, self.pos.y = pos
        else:
            self.pos.x, self.pos.y = pos, y
        return self

    def setscl(self, scl, y=None, /):
        if y is None:
            self.scl.x, self.scl.y = scl
        else:
            self.scl.x, self.scl.y = scl, y
        return self

    def setz(self, z):
        self.z = z
        return self

    def mul(self, transform):
        self.pos.x += self.scl.x * transform.pos.x
        self.pos.y += self.scl.y * transform.pos.y
        self.scl.x *= transform.scl.x
        self.scl.y *= transform.scl.y
        self.z += transform.z
        return self

    def apply(self, point, y=None, /):
        if y is None:
            x, y = point
        else:
            x = point
        return (x, y) * self.scl.elementwise() + self.pos

    def unapply(self, point, y=None, /):
        if y is None:
            x, y = point
        else:
            x = point
        return ((x, y) - self.pos).elementwise() / self.scl

class GlobalTransform(Transform): pass

def init(world):
    world.system(propagate)

def spawn_transform(world):
    return world.spawn().add(Transform()).add(GlobalTransform())

def _propagate(world, entity, ptransform):
    for child, (parent, local, transform) in (
        world.query(Parent, Transform, GlobalTransform)
    ):
        if parent.v is entity:
            transform.set(ptransform).mul(local)
            _propagate(world, child, transform)

def propagate(world):
    for entity, (local, transform) in world.query(Transform, GlobalTransform):
        if not entity.has(Parent):
            transform.set(local)
            for child, (parent, clocal, ctransform) in (
                world.query(Parent, Transform, GlobalTransform)
            ):
                if parent.v is entity:
                    ctransform.set(transform).mul(clocal)
                    _propagate(world, child, ctransform)
