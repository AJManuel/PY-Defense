import pygame as pg
from pygame.math import Vector2
from enemy_data import ENEMY_DATA
from enemy_data import ENEMY_SPAWN_DATA
from world import World
import constants as c
import math

class Enemy(pg.sprite.Sprite):
    def __init__(self, enemy_type, waypoints, images, world):
        pg.sprite.Sprite.__init__(self)
        self.waypoints = waypoints
        self.pos = Vector2(self.waypoints[0])
        self.target_waypoint = 1
        self.health = ENEMY_DATA.get(enemy_type)['health']
        self.speed = ENEMY_DATA.get(enemy_type)['speed']
        self.angle = 0
        self.original_image = images.get(enemy_type)
        self.image = pg.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.world = world

    def update(self, world):
        self.move(world)
        self.rotate()
        self.check_alive(world)

    def move(self, world):
        #define a target
        if self.target_waypoint < len(self.waypoints):
            self.target = Vector2(self.waypoints[self.target_waypoint])
            self.movement = self.target - self.pos
        else:
            #enemy has reached end
            self.kill()
            world.health -= 1
            world.missed_enemies += 1

        #calc distance to target
        dist = self.movement.length()
        #check remaining dist
        if dist >= (self.speed * world.game_speed):
            self.pos += self.movement.normalize() * (self.speed * world.game_speed)
        else:
            if dist != 0:
                self.pos += self.movement.normalize() * dist
            self.target_waypoint += 1

    def rotate(self):
        #calc distance to next waypoint
        dist = self.target - self.pos
        #use distance to calc angle
        self.angle = math.degrees(math.atan2(-dist[1], dist[0]))
        #rotate image and update angle
        if self.world.level == 1 or 2 or 3 or 4 or 5 or 6 or 7 or 8 or 9 or 10 or 11 or 12 or 13 or 14 or 15:
            self.image = self.original_image
        else:
            self.image = pg.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

    def check_alive(self, world):
        if self.health <= 0:
            world.killed_enemies += 1
            world.money += c.KILL_REWARD
            self.kill()
