from enum import Enum
import random

import pygame
from pygame import Vector2

import wgpyecs
from wgpyecs import Parent, Wrapper
from wgpyecs.motion import Velocity
from wgpyecs.sprite import Size
from wgpyecs.transform import Transform
from wgpyecs.viewport import Camera

import player
from player import Player
import ui
from ui import GameCamera, Score

PLATFORM_SIZE = Vector2(256, 64)
MOVABLE_SPEED_MAX = 1024

class PlatformSpawner:
    def __init__(self, y, step, step_step):
        self.y = y
        self.step = step
        self.step_step = step_step
        self.n = 0
    def spawn(self):
        self.y -= self.step
        self.step += self.step_step
        self.n += 1

class PlatformSurface(Wrapper): pass

class PlatformType(Enum):
    PLATFORM = 1
    HIGH = 2
    MOVABLE = 3
    BAD = 4

class Platform:
    def __init__(self, type, n):
        self.type = type
        self.n = n

def init(world):
    world.add(PlatformSurface({
        PlatformType.PLATFORM: pygame.image.load('assets/platform.png'),
        PlatformType.HIGH: pygame.image.load('assets/high.png'),
        PlatformType.MOVABLE: pygame.image.load('assets/movable.png'),
        PlatformType.BAD: pygame.image.load('assets/bad.png'),
    }))

    world.system(switch, before=[wgpyecs.motion.velocity])

def show_menu(world):
    world.unsystem(spawn).unsystem(collision).unsystem(score).unsystem(despawn)

def start_game(world):
    world.add(PlatformSpawner(512, PLATFORM_SIZE.y, 1))

    world.system(spawn, before=[wgpyecs.motion.velocity])
    world.system(
        collision,
        after=[wgpyecs.motion.acceleration],
        before=[wgpyecs.motion.velocity],
    )
    world.system(score, after=[wgpyecs.motion.velocity], before=[ui.score])
    world.system(despawn, after=[player.camera])

    for entity, _ in world.query(Platform):
        entity.despawn()

def spawn(world):
    spawner = world.get(PlatformSpawner)
    surface = world.get(PlatformSurface).v
    camera_entity, (_, camera) = world.query_single(GameCamera, Camera)

    while spawner.y + PLATFORM_SIZE.y / 2 > camera.center.y - camera.size.y / 2:
        if spawner.n < 50:
            platform = PlatformType.HIGH
        elif spawner.n < 150:
            if random.random() < (spawner.n - 50) / 100 / 2:
                platform = PlatformType.PLATFORM
            else:
                platform = PlatformType.HIGH
        elif spawner.n < 500:
            if random.random() < (spawner.n - 150) / 350 / 3:
                platform = PlatformType.MOVABLE
            else:
                platform = random.choice([
                    PlatformType.PLATFORM,
                    PlatformType.HIGH,
                ])
        elif spawner.n < 1000:
            if random.random() < (spawner.n - 500) / 500 / 4:
                platform = PlatformType.BAD
            else:
                platform = random.choice([
                    PlatformType.PLATFORM,
                    PlatformType.HIGH,
                    PlatformType.MOVABLE,
                ])
        else:
            platform = random.choice(list(Platform))
        entity = (wgpyecs.sprite
            .spawn_sprite(world, surface[platform], PLATFORM_SIZE)
            .add(Transform().setpos(
                random.uniform(
                    -camera.size.x / 2 + PLATFORM_SIZE.x / 2,
                    camera.size.x / 2 - PLATFORM_SIZE.x / 2,
                ),
                spawner.y,
            ))
            .add(Parent(camera_entity))
            .add(Platform(platform, spawner.n)))
        if platform == PlatformType.MOVABLE:
            entity.add(Velocity(Vector2(
                random.uniform(-MOVABLE_SPEED_MAX, MOVABLE_SPEED_MAX),
                0,
            )))
        spawner.spawn()

def switch(world):
    _, (_, camera) = world.query_single(GameCamera, Camera)

    for _, (platform, velocity, transform, size) in world.query(
        Platform,
        Velocity,
        Transform,
        Size,
    ):
        if platform.type == PlatformType.MOVABLE:
            if transform.pos.x - size.v.x / 2 < -camera.size.x / 2:
                velocity.v.x = abs(velocity.v.x)
            if transform.pos.x + size.v.x / 2 > camera.size.x / 2:
                velocity.v.x = -abs(velocity.v.x)

def collision(world):
    _, (_, velocity, player_transform, player_size) = world.query_single(
        Player,
        Velocity,
        Transform,
        Size,
    )

    if velocity.v.y < 0:
        return

    for entity, (platform, transform, size) in world.query(
        Platform,
        Transform,
        Size,
    ):
        if (transform.pos.x - size.v.x / 2
            < player_transform.pos.x + player_size.v.y / 2
            and player_transform.pos.x - player_size.v.y / 2
                < transform.pos.x + size.v.x / 2
            and transform.pos.y - size.v.y / 2
                < player_transform.pos.y + player_size.v.y / 2
                < transform.pos.y + size.v.y / 2
        ):
            if platform.type == PlatformType.HIGH:
                velocity.v.y = -4096
            elif platform.type == PlatformType.BAD:
                velocity.v.y = -512
                entity.despawn()
            else:
                velocity.v.y = -2048

def score(world):
    _, score = world.query_single(Score)
    _, (_, player_transform) = world.query_single(Player, Transform)

    for _, (platform, transform) in world.query(Platform, Transform):
        if (player_transform.pos.y < transform.pos.y
            and score.score < platform.n
        ):
            score.set(platform.n)

def despawn(world):
    _, (_, camera) = world.query_single(GameCamera, Camera)

    for entity, (_, transform, size) in world.query(Platform, Transform, Size):
        if transform.pos.y - size.v.y / 2 > camera.center.y + camera.size.y / 2:
            entity.despawn()
