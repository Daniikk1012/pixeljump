import sys

import pygame
from pygame.font import Font

import wgpyecs
from wgpyecs import Parent, Wrapper
from wgpyecs.io import Clickable
from wgpyecs.sprite import Size, Sprite
from wgpyecs.transform import Transform
from wgpyecs.viewport import Camera

import platform
import player

class GameCamera: pass
class UiCamera: pass

class ScoreFont(Wrapper): pass
class Score:
    def __init__(self):
        self.score = 0
        self.changed = True

    def set(self, score):
        self.score = score
        self.changed = True

class Hint: pass
class Restart: pass

def init(world):
    font = Font('assets/pressstart2p-regular.ttf', 48)
    world.add(ScoreFont(font))

    world.system(score, before=[wgpyecs.sprite.draw])
    world.system(
        score_position,
        after=[score],
        before=[wgpyecs.transform.propagate],
    )
    world.system(restart, after=[wgpyecs.io.mouse])
    world.system(restart_position, before=[wgpyecs.transform.propagate])
    world.system(escape)

    wgpyecs.viewport.spawn_viewport(world, (1080, 1920)).add(GameCamera())
    camera = (wgpyecs.viewport.spawn_viewport(world, (1080, 1920))
        .add(Transform().setz(2))
        .add(UiCamera()))

    wgpyecs.sprite.spawn_sprite(world, None).add(Score()).add(Parent(camera))
    (wgpyecs.sprite
        .spawn_sprite(
            world,
            font.render('ESC to exit', False, 'white'),
        )
        .add(Parent(camera))
        .add(Hint()))
    (wgpyecs.sprite
        .spawn_sprite(
            world,
            pygame.image.load('assets/restart.png'),
            (128, 128),
        )
        .add(Clickable())
        .add(Parent(camera))
        .add(Restart()))

def show_menu(world):
    _, (_, sprite) = world.query_single(Hint, Sprite)
    sprite.visible = True
    platform.show_menu(world)
    player.show_menu(world)

def start_game(world):
    _, (_, camera) = world.query_single(GameCamera, Camera)
    _, score = world.query_single(Score)
    _, (_, sprite) = world.query_single(Hint, Sprite)
    camera.center.y = 0
    score.set(0)
    sprite.visible = False
    platform.start_game(world)
    player.start_game(world)

def score(world):
    font = world.get(ScoreFont).v
    _, (score, sprite) = world.query_single(Score, Sprite)

    if score.changed:
        sprite.surface = font.render(f'Score: {score.score}', False, 'white')
        score.changed = False

def score_position(world):
    _, (_, camera) = world.query_single(UiCamera, Camera)
    _, (_, transform, sprite) = world.query_single(Score, Transform, Sprite)
    transform.pos.y = -camera.size.y / 2 + sprite.surface.get_height() / 2 + 16

def restart(world):
    _, (_, clickable) = world.query_single(Restart, Clickable)

    if clickable.up[0]:
        show_menu(world)
        start_game(world)

def restart_position(world):
    _, (_, camera) = world.query_single(UiCamera, Camera)
    _, (_, transform, size) = world.query_single(Restart, Transform, Size)
    transform.setpos(camera.size / 2 - size.v / 2)

def escape(world):
    if pygame.key.get_pressed()[pygame.K_ESCAPE]:
        sys.exit()
