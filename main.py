import pygame

import wgpyecs
from wgpyecs import Parent, World
from wgpyecs.essentials import FillColor

import platform
import player
import ui

def init(world):
    wgpyecs.init(world, (450, 800))
    world.add(FillColor((127, 127, 127)))

    platform.init(world)
    player.init(world)
    ui.init(world)

    ui.show_menu(world)

def main():
    try:
        pygame.init()
        world = World()
        init(world)
        while True:
            world.run()
    finally:
        pygame.quit()

if __name__ == '__main__':
    main()
