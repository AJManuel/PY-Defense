import pygame as pg
import constants as c
import math
from cannon_data import CANNON_DATA

class Cannon(pg.sprite.Sprite):
    def __init__(self, sprite_sheets, tile_x, tile_y, shot_fx):
        pg.sprite.Sprite.__init__(self)
        self.upgrade_level = 1
        self.range = CANNON_DATA[self.upgrade_level - 1].get('range')
        self.cooldown = CANNON_DATA[self.upgrade_level - 1].get('cooldown')
        self.last_shot = pg.time.get_ticks()
        self.selected = False
        self.target = None
        #position variables
        self.tile_x = tile_x
        self.tile_y = tile_y
        #calc center coord
        self.x = (self.tile_x + 0.5) * c.TILE_SIZE
        self.y = (self.tile_y + 0.5) * c.TILE_SIZE
        #shot sound
        self.shot_fx = shot_fx

        #animation variables
        self.sprite_sheets = sprite_sheets
        self.animation_list = self.load_images(self.sprite_sheets[self.upgrade_level - 1])
        self.frame_index = 0
        self.update_time = pg.time.get_ticks()

        #update image
        self.angle = 90
        self.original_image = self.animation_list[self.frame_index]
        self.image = pg.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)

        #create transparent range
        self.range_image = pg.Surface((self.range * 2, self.range * 2))
        self.range_image.fill((0,0,0))
        self.range_image.set_colorkey((0,0,0))
        pg.draw.circle(self.range_image, 'grey100', (self.range, self.range), self.range)
        self.range_image.set_alpha(100)
        self.range_rect = self.range_image.get_rect()
        self.range_rect.center = self.rect.center

    def load_images(self, sprite_sheet):
        #extract sprite sheet images
        size = sprite_sheet.get_height()
        animation_list = []
        for x in range(c.ANIMATION_STEPS):
            temp_img = sprite_sheet.subsurface(x * size, 0, size, size)
            animation_list.append(temp_img)

        return animation_list

    def update(self, enemy_group, world):
        #if target picked, play fire
        if self.target:
            self.play_animation()
        else:
            #search for new target after cooldown
            if pg.time.get_ticks() - self.last_shot > (self.cooldown / world.game_speed):
                self.pick_target(enemy_group)

    def pick_target(self, enemy_group):
        #find an enemy to target
        x_dist = 0
        y_dist = 0
        #check distance to each enemy
        for enemy in enemy_group:
            if enemy.health > 0:
                x_dist = enemy.pos[0] - self.x
                y_dist = enemy.pos[1] - self.y
                dist = math.sqrt(x_dist**2 + y_dist**2)
                if dist < self.range:
                    self.target = enemy
                    self.angle = math.degrees(math.atan2(-y_dist, x_dist))
                    #damage enmy
                    self.target.health -= c.DAMAGE
                    #play sound
                    self.shot_fx.play()
                    break


    def play_animation(self):
        #update image
        self.original_image = self.animation_list[self.frame_index]
        #check if delay has happened
        if pg.time.get_ticks() - self.update_time > c.ANIMATION_DELAY:
            self.update_time = pg.time.get_ticks()
            self.frame_index += 1
            #check if animation is over
            if self.frame_index >= len(self.animation_list):
                self.frame_index = 0
                #start cooldown
                self.last_shot = pg.time.get_ticks()
                self.target = None


    def upgrade(self):
        self.upgrade_level += 1
        self.range = CANNON_DATA[self.upgrade_level - 1].get('range')
        self.cooldown = CANNON_DATA[self.upgrade_level - 1].get('cooldown')
        #upgrade image
        self.animation_list = self.load_images(self.sprite_sheets[self.upgrade_level - 1])
        self.original_image = self.animation_list[self.frame_index]
        # upgrade range circle
        self.range_image = pg.Surface((self.range * 2, self.range * 2))
        self.range_image.fill((0, 0, 0))
        self.range_image.set_colorkey((0, 0, 0))
        pg.draw.circle(self.range_image, 'grey100', (self.range, self.range), self.range)
        self.range_image.set_alpha(100)
        self.range_rect = self.range_image.get_rect()
        self.range_rect.center = self.rect.center


    def draw(self, surface):
        self.image = pg.transform.rotate(self.original_image, self.angle - 90)
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)
        surface.blit(self.image, self.rect)
        if self.selected:
            surface.blit(self.range_image, self.range_rect)
