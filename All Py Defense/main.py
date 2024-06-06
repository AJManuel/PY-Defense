import pygame as pg
import json
from enemy import Enemy
from world import World
from turret import Turret
from cannon import Cannon
from button import Button
import constants as c


#initialise pygame
pg.init()

#create clock
clock = pg.time.Clock()

#create game window
screen = pg.display.set_mode((c.SCREEN_WIDTH + c.SIDE_PANEL,c.SCREEN_HEIGHT))
pg.display.set_caption("Py Defense")


#game variables
game_over = False
game_outcome = 0
level_started = False
last_enemy_spawn = pg.time.get_ticks()
placing_turrets = False
placing_cannons = False
selected_turret = None
selected_cannon = None

#load images
#map
map_image = pg.image.load('levels/level.png').convert_alpha()
#turret spritesheet
turret_spritesheets = []
for x in range(1, c.TURRET_LEVELS + 1):
  turret_sheet = pg.image.load(f'assets/images/turrets/turret_{x}.png').convert_alpha()
  turret_spritesheets.append(turret_sheet)
#indiv turret image for cursor
cursor_turret = pg.image.load('assets/images/turrets/cursor_turret.png').convert_alpha()
# nannon spritesheet
cannon_spritesheets = []
for y in range(1, c.CANNON_LEVELS + 1):
  cannon_sheet = pg.image.load(f'assets/images/cannons/cannon_{y}.png').convert_alpha()
  cannon_spritesheets.append(cannon_sheet)
#indiv turret image for cursor
cursor_cannon = pg.image.load('assets/images/cannons/cursor_cannon.png').convert_alpha()
#enemies
enemy_images = {
  'weak': pg.image.load('assets/images/enemies/enemy_1.png').convert_alpha(),
  'medium': pg.image.load('assets/images/enemies/enemy_2.png').convert_alpha(),
  'strong': pg.image.load('assets/images/enemies/enemy_3.png').convert_alpha(),
  'elite': pg.image.load('assets/images/enemies/enemy_4.png').convert_alpha()
}
#buttons
buy_turret_image = pg.image.load('assets/images/buttons/buy_turret.png').convert_alpha()
buy_cannon_image = pg.image.load('assets/images/buttons/buy_cannon.png').convert_alpha()
cancel_image = pg.image.load('assets/images/buttons/cancel.png').convert_alpha()
upgrade_turret = pg.image.load('assets/images/buttons/upgrade_turret.png').convert_alpha()
upgrade_cannon = pg.image.load('assets/images/buttons/upgrade_cannon.png').convert_alpha()
begin_image = pg.image.load('assets/images/buttons/begin.png').convert_alpha()
restart_image = pg.image.load('assets/images/buttons/restart.png').convert_alpha()
fast_foward_image = pg.image.load('assets/images/buttons/fast_forward.png').convert_alpha()
#gui
heart_image = pg.image.load('assets/images/gui/heart.png').convert_alpha()
coin_image = pg.image.load('assets/images/gui/coin.png').convert_alpha()
logo_image = pg.image.load('assets/images/gui/logo.png').convert_alpha()
#load sounds
shot_fx = pg.mixer.Sound('assets/audio/shot.wav')
shot_fx.set_volume(0.5)

#load json data
with open('levels/level.tmj') as file:
  world_data = json.load(file)

#LOAD FONTS FOR DISPLAYING TEXT
text_font = pg.font.SysFont('Consolas', 24, bold = True)
large_font = pg.font.SysFont('Consolas', 36)

#function for outputting text on screen
def draw_text(text, font, text_col, x, y):
  img = font.render(text, True, text_col)
  screen.blit(img, (x, y))

def display_data():
  #draw panel
  pg.draw.rect(screen, 'dodgerblue', (c.SCREEN_WIDTH, 0, c.SIDE_PANEL, c.SCREEN_HEIGHT), 0)
  pg.draw.rect(screen, 'grey0', (c.SCREEN_WIDTH, 0, c.SIDE_PANEL, 400), 2)
  screen.blit(logo_image, (c.SCREEN_WIDTH, 400))
  #display data
  draw_text('LEVEL: ' + str(world.level), text_font, 'grey100',c.SCREEN_WIDTH + 5, 10)
  screen.blit(heart_image, (c.SCREEN_WIDTH + 10, 35))
  draw_text(str(world.health), text_font, 'grey100',c.SCREEN_WIDTH + 50, 40)
  screen.blit(coin_image, (c.SCREEN_WIDTH+10, 65))
  draw_text(str(world.money), text_font, 'grey100', c.SCREEN_WIDTH + 50, 70)

def create_turret(mouse_pos):
  mouse_tile_x = mouse_pos[0] // c.TILE_SIZE
  mouse_tile_y = mouse_pos[1] // c.TILE_SIZE
  #calc the seq numer of tile
  mouse_tile_num = (mouse_tile_y * c.COLS) + mouse_tile_x
  #check if tile is grass
  if world.tile_map[mouse_tile_num] == 7:
    #check if tile is free
    space_is_free = True
    for turret in turret_group:
      if (mouse_tile_x, mouse_tile_y) == (turret.tile_x, turret.tile_y):
        space_is_free = False
    #if is free create
    if space_is_free == True:
      new_turret = Turret(turret_spritesheets, mouse_tile_x, mouse_tile_y, shot_fx)
      turret_group.add(new_turret)
      #deduct cost
      world.money -= c.BUY_COST


def select_turret(mouse_pos):
  mouse_tile_x = mouse_pos[0] // c.TILE_SIZE
  mouse_tile_y = mouse_pos[1] // c.TILE_SIZE
  for turret in turret_group:
    if (mouse_tile_x, mouse_tile_y) == (turret.tile_x, turret.tile_y):
      return turret

def create_cannon(mouse_pos):
  mouse_tile_x = mouse_pos[0] // c.TILE_SIZE
  mouse_tile_y = mouse_pos[1] // c.TILE_SIZE
  #calc the seq numer of tile
  mouse_tile_num = (mouse_tile_y * c.COLS) + mouse_tile_x
  #check if tile is grass
  if world.tile_map[mouse_tile_num] == 7:
    #check if tile is free
    space_is_free = True
    for cannon in cannon_group:
      if (mouse_tile_x, mouse_tile_y) == (cannon.tile_x, cannon.tile_y):
        space_is_free = False
    #if is free create
    if space_is_free == True:
      new_cannon = Cannon(cannon_spritesheets, mouse_tile_x, mouse_tile_y, shot_fx)
      cannon_group.add(new_cannon)
      #deduct cost
      world.money -= c.CANNON_BUY_COST


def select_cannon(mouse_pos):
  mouse_tile_x = mouse_pos[0] // c.TILE_SIZE
  mouse_tile_y = mouse_pos[1] // c.TILE_SIZE
  for cannon in cannon_group:
    if (mouse_tile_x, mouse_tile_y) == (cannon.tile_x, cannon.tile_y):
      return cannon

def clear_selection():
  for turret in turret_group:
    turret.selected = False

def clear_cannon_selection():
  for cannon in cannon_group:
    cannon.selected = False


#create world
world = World(world_data, map_image)
world.process_data()
world.process_enemies()

#create groups
enemy_group = pg.sprite.Group()
turret_group = pg.sprite.Group()
cannon_group = pg.sprite.Group()

#create buttons
turret_button = Button(c.SCREEN_WIDTH + 30, 120, buy_turret_image, True)
cancel_button = Button(c.SCREEN_WIDTH + 50, 275, cancel_image, True)
upgrade_button = Button(c.SCREEN_WIDTH + 5, 180, upgrade_turret, True)
cannon_button = Button(c.SCREEN_WIDTH + 30, 210, buy_cannon_image, True)
upgrade_cannon_button = Button(c.SCREEN_WIDTH + 5, 270, upgrade_cannon, True)
begin_button = Button(c.SCREEN_WIDTH + 60, 340, begin_image, True)
restart_button = Button(310, 300, restart_image, True)
fast_foward_button = Button(c.SCREEN_WIDTH + 50, 340, fast_foward_image, False)

#game loop
run = True
while run:

  clock.tick(c.FPS)

  #---------------------------------------------------------
  #UPDATING
  #---------------------------------------------------------

  if game_over == False:
    if world.health <= 0:
      game_over = True
      game_outcome = -1
    #check if win
    if world.level > c.TOTAL_LEVELS:
      game_over = True
      game_outcome = 1
  #update groups
    enemy_group.update(world)
    turret_group.update(enemy_group, world)
    cannon_group.update(enemy_group, world)

    #highlight seleceted turret
    if selected_turret:
      selected_turret.selected = True

    #highlight selected cannon
    if selected_cannon:
      selected_cannon.selected = True

  #---------------------------------------------------------
  #DRAWING
  #---------------------------------------------------------

  #draw level
  world.draw(screen)

  #draw groups
  enemy_group.draw(screen)
  for turret in turret_group:
    turret.draw(screen)

  for cannon in cannon_group:
    cannon.draw(screen)

  display_data()



  if game_over == False:
    #check if level is started
    if level_started == False:
      if begin_button.draw(screen):
        level_started = True
    else:
      #fast forward
      world.game_speed = 1
      if fast_foward_button.draw(screen):
        world.game_speed = 2
      #spawn enemies
      if pg.time.get_ticks() - last_enemy_spawn > c.SPAWN_COOLDOWN:
        if world.spawned_enemies < len(world.enemy_list):
          enemy_type = world.enemy_list[world.spawned_enemies]
          enemy = Enemy(enemy_type, world.waypoints, enemy_images)
          enemy_group.add(enemy)
          world.spawned_enemies += 1
          last_enemy_spawn = pg.time.get_ticks()

    #check if wave done
    if world.check_level_complete() == True:
      world.money += c.LEVEL_COMPLETE_REWARD
      world.level += 1
      level_started = False
      last_enemy_spawn = pg.time.get_ticks()
      world.reset_level()
      world.process_enemies()

    #draw buttons
    #button for placing turret
    #for turrent button show price and draw
    draw_text(str(c.BUY_COST), text_font, 'grey100', c.SCREEN_WIDTH + 205, 135)
    screen.blit(coin_image, (c.SCREEN_WIDTH + 260, 130))
    if turret_button.draw(screen):
      placing_turrets = True
    #if placing turrets show cancel button
    if placing_turrets == True:
      #show cursor turret
      cursor_rect = cursor_turret.get_rect()
      cursor_pos = pg.mouse.get_pos()
      cursor_rect.center = cursor_pos
      if cursor_pos[0] <= c.SCREEN_WIDTH:
        screen.blit(cursor_turret, cursor_rect)
      #button for cancelling turret
      if cancel_button.draw(screen):
        placing_turrets = False
    #if turreet selected show upgrade
    if selected_turret:
      #If a turret can be upgraded show upgrade
      if selected_turret.upgrade_level < c.TURRET_LEVELS:
        draw_text(str(c.UPGRADE_COST), text_font, 'grey100', c.SCREEN_WIDTH + 215, 195)
        screen.blit(coin_image, (c.SCREEN_WIDTH + 260, 190))
        if upgrade_button.draw(screen):
          if world.money >= c.UPGRADE_COST:
            selected_turret.upgrade()
            world.money -= c.UPGRADE_COST

    # button for placing cannon
    # for cannon button show price and draw
    draw_text(str(c.CANNON_BUY_COST), text_font, 'grey100', c.SCREEN_WIDTH + 205, 225)
    screen.blit(coin_image, (c.SCREEN_WIDTH + 260, 220))
    if cannon_button.draw(screen):
      placing_cannons = True
    # if placing cannons show cancel button
    if placing_cannons == True:
      # show cursor cannon
      cursor_rect = cursor_cannon.get_rect()
      cursor_pos = pg.mouse.get_pos()
      cursor_rect.center = cursor_pos
      if cursor_pos[0] <= c.SCREEN_WIDTH:
        screen.blit(cursor_cannon, cursor_rect)
      # button for cancelling cannon
      if cancel_button.draw(screen):
        placing_cannons = False
    # if cannon selected show upgrade
    if selected_cannon:
      # If a cannon can be upgraded show upgrade
      if selected_cannon.upgrade_level < c.CANNON_LEVELS:
        draw_text(str(c.CANNON_UPGRADE_COST), text_font, 'grey100', c.SCREEN_WIDTH + 215, 295)
        screen.blit(coin_image, (c.SCREEN_WIDTH + 260, 290))
        if upgrade_cannon_button.draw(screen):
          if world.money >= c.CANNON_UPGRADE_COST:
            selected_cannon.upgrade()
            world.money -= c.CANNON_UPGRADE_COST
  else:
    pg.draw.rect(screen, 'dodgerblue', (200,200,400,200), border_radius = 30)
    if game_outcome == -1:
      draw_text('GAME OVER', large_font, 'grey0', 310, 230)
    elif game_outcome == 1:
      draw_text('YOU WIN', large_font, 'grey0', 315, 230)

    #restart
    if restart_button.draw(screen):
      game_over = False
      level_started = False
      placing_turrets = False
      placing_cannons = False
      selected_turret = None
      selected_cannon = None
      last_enemy_spawn = pg.time.get_ticks()
      world = World(world_data, map_image)
      world.process_data()
      world.process_enemies()
      #empty groups
      enemy_group.empty()
      turret_group.empty()
      cannon_group.empty()

  #event handler
  for event in pg.event.get():
    #quit game
    if event.type == pg.QUIT:
      run = False
    #mouse click
    if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
      mouse_pos = pg.mouse.get_pos()
      #check if on map
      if mouse_pos[0] < c.SCREEN_WIDTH and mouse_pos[1] < c.SCREEN_HEIGHT:
        #clear selected turret
        selected_turret = None
        selected_cannon = None
        clear_selection()
        clear_cannon_selection()
        if placing_turrets == True:
          #CHECK IF YOU HAVE ENOUGH MOENY
          if world.money >= c.BUY_COST:
            create_turret(mouse_pos)
        else:
          selected_turret = select_turret(mouse_pos)
        if placing_cannons == True:
          if world.money >= c.CANNON_BUY_COST:
            create_cannon(mouse_pos)
        else:
          selected_cannon = select_cannon(mouse_pos)

  #update
  pg.display.flip()
pg.quit()
