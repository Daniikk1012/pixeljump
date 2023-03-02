import pygame

from . import essentials, transform
from .essentials import Events
from .transform import GlobalTransform, Size

class Clickable:
    def __init__(self):
        self.down = [False] * 3
        self.pressed = [False] * 3
        self.up = [False] * 3

def init(world):
    world.system(mouse, after=[transform.propagate])

def mouse(world):
    events = world.get(Events).v
    entities = world.query(Clickable, Size, GlobalTransform)
    entities.sort(key=lambda entity: entity[1][2].z, reverse=True)

    for _, clickable in world.query(Clickable):
        for index in range(len(clickable.down)):
            clickable.down[index] = False
            clickable.up[index] = False
    for index, event in enumerate(events.copy()):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for _, (clickable, size, transform) in entities:
                x, y = transform.unapply(event.pos)
                if abs(x) < size.v.x / 2 and abs(y) < size.v.y / 2:
                    clickable.down[event.button - 1] = True
                    clickable.pressed[event.button - 1] = True
                    clickable.up[event.button - 1] = False
                    del events[index]
                    break
        elif event.type == pygame.MOUSEBUTTONUP:
            found = False
            for _, (clickable, size, transform) in entities:
                x, y = transform.unapply(event.pos)
                if clickable.pressed[event.button - 1]:
                    if abs(x) < size.v.x / 2 and abs(y) < size.v.y / 2:
                        clickable.up[event.button - 1] = True
                    found = True
                clickable.down[event.button - 1] = False
                clickable.pressed[event.button - 1] = False
            if found:
                del events[index]
