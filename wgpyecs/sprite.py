import pygame
from pygame import Surface, Vector2

from . import essentials, transform
from .essentials import Screen
from .transform import GlobalTransform, Size

class Sprite:
    def __init__(self, surface):
        self.surface = surface
        self.flip_x = False
        self.flip_y = False
        self.visible = True

def init(world):
    world.system(
        draw,
        after=[transform.propagate],
        before=[essentials.frame_end],
    )

def spawn_sprite(world, surface, size=None):
    entity = transform.spawn_transform(world).add(Sprite(surface))
    if size is not None:
        entity.add(Size(size))
    return entity

def draw(world):
    screen = world.get(Screen).v

    entities = world.query(Sprite, GlobalTransform)
    entities.sort(key=lambda entity: entity[1][1].z)
    for entity, (sprite, transform) in entities:
        if not sprite.visible:
            continue
        if entity.has(Size):
            size = entity.get(Size).v
        else:
            size = sprite.surface.get_size()
        size = transform.scl.elementwise() * size
        screen.blit(
            pygame.transform.scale(
                pygame.transform.flip(
                    sprite.surface,
                    sprite.flip_x,
                    sprite.flip_y,
                ),
                size,
            ),
            transform.apply(0, 0) - size / 2,
        )
