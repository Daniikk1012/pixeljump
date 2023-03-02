import sys

import pygame
from pygame import Vector2

import wgpyecs
from wgpyecs import Parent, Wrapper
from wgpyecs.motion import Acceleration, Velocity
from wgpyecs.sprite import Size, Sprite
from wgpyecs.transform import Transform
from wgpyecs.viewport import Camera

import ui
from ui import GameCamera

class PlayerSurface(Wrapper): pass
class Player: pass

def init(world):
    world.add(PlayerSurface(pygame.image.load('assets/player.png')))

def show_menu(world):
    try:
        world.query_single(Player)[0].despawn()
    except:
        pass
    world.unsystem(movement).unsystem(wrap).unsystem(camera).unsystem(death)

def start_game(world):
    world.system(movement, before=[wgpyecs.motion.velocity])
    world.system(
        wrap,
        after=[wgpyecs.motion.velocity],
        before=[wgpyecs.transform.propagate],
    )
    world.system(
        camera,
        after=[wgpyecs.motion.velocity],
        before=[wgpyecs.viewport.camera],
    )
    world.system(death, after=[wgpyecs.transform.propagate])

    (wgpyecs.sprite
        .spawn_sprite(
            world,
            world.get(PlayerSurface).v,
            (128, 128),
        )
        .add(Transform().setz(1))
        .add(Acceleration(Vector2(0, 1024)))
        .add(Velocity(Vector2(0, 0)))
        .add(Parent(world.query_single(GameCamera)[0]))
        .add(Player()))

def movement(world):
    direction = 0
    pressed = pygame.key.get_pressed()

    if pressed[pygame.K_LEFT]:
        direction -= 1
    if pressed[pygame.K_RIGHT]:
        direction += 1

    _, (_, velocity, sprite) = world.query_single(Player, Velocity, Sprite)

    if direction < 0:
        sprite.flip_x = True
    if direction > 0:
        sprite.flip_x = False

    velocity.v.x = direction * 1024

def wrap(world):
    _, (_, transform, size) = world.query_single(Player, Transform, Size)
    _, (_, camera) = world.query_single(GameCamera, Camera)

    if transform.pos.x + size.v.x / 2 < -camera.size.x / 2:
        transform.pos.x += camera.size.x + size.v.x
    if transform.pos.x - size.v.x / 2 > camera.size.x / 2:
        transform.pos.x -= camera.size.x + size.v.x

def camera(world):
    _, (_, transform) = world.query_single(Player, Transform)
    _, (_, camera) = world.query_single(GameCamera, Camera)

    if camera.center.y > transform.pos.y:
        camera.center.y = transform.pos.y

def death(world):
    player, (_, transform, size) = world.query_single(Player, Transform, Size)
    _, (_, cam) = world.query_single(GameCamera, Camera)

    if transform.pos.y - size.v.y / 2 > cam.center.y + cam.size.y / 2:
        ui.show_menu(world)
