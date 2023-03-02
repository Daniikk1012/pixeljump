import sys

import pygame
from pygame import Surface
from pygame.time import Clock

from .ecs import Wrapper

class Events(Wrapper): pass
class Screen(Wrapper): pass
class FillColor(Wrapper): pass
class Timer(Wrapper): pass

def init(world, size=None):
    world.add(Events([]))
    world.add(Screen(pygame.display.set_mode(
        size if size is not None else (800, 450),
        pygame.RESIZABLE,
        vsync=True,
    )))
    world.add(Timer(Clock()))

    world.system(events)
    world.system(fill)
    world.system(frame_start, after=[events, fill])
    world.system(frame_end, after=[frame_start], before=[flip, tick])
    world.system(flip)
    world.system(tick)

def events(world):
    events = world.get(Events).v
    events.clear()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        events.append(event)

def fill(world):
    fill_color = world.get(FillColor).v if world.has(FillColor) else 'black'
    world.get(Screen).v.fill(fill_color)

def tick(world):
    world.get(Timer).v.tick()

def frame_start(world): pass

def flip(world):
    pygame.display.flip()

def frame_end(world): pass
