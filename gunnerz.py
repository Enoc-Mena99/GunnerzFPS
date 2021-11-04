"""
Creator: Enoc Mena
Version: 1.0.0
"""

import pygame
import os

pygame.init()

# screen size
screen_width = 800
screen_height = int(screen_width * 0.8)

# initialize window
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Gunnerz')  # name of game

# framerate
clock = pygame.time.Clock()
FPS = 60

# define game variables
GRAVITY = 0.75

# define player action variables
movingLeft = False
movingRight = False
shoot = False
grenade = False
grenade_thrown = False

# load images
bullet_img = pygame.image.load('images/icons/bullet.png').convert_alpha()
grenade_img = pygame.image.load('images/icons/grenade.png').convert_alpha()

# define game colors
BG = (144, 201, 120)
RED = (255, 0, 0)

def draw_background():
    screen.fill(BG)
    pygame.draw.line(screen, RED, (0, 225), (screen_width, 225))

#player class
class Soldier(pygame.sprite.Sprite):
    def __init__(self, character_type, x, y, scale, speed, ammo, grenades):
        pygame.sprite.Sprite.__init__(self)

        self.alive = True
        self.character_type = character_type

        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.grenades = grenades
        self.health = 100  # player and enemy health
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()

        # load all images for players
        animation_types = ['Idle', 'Run', 'Jump', 'Death']
        for animation in animation_types:
            # reset temporary list of images
            temp_list = []
            # count number of files in folder
            num_of_frames = len(os.listdir(F'images/{self.character_type}/{animation}/')) - 1
            for i in range(num_of_frames):
                img = pygame.image.load(F'images/{self.character_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width()) * scale, int(img.get_height()) * scale))
                temp_list.append(img)
            self.animation_list.append(temp_list)
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        self.update_animation()
        self.check_alive()
        # update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, movingLeft, movingRight):
        # reset the movement variables
        rx = 0
        ry = 0

        # moving variables
        if movingLeft:
            rx = -self.speed
            self.flip = True
            self.direction = -1
        if movingRight:
            rx = self.speed
            self.flip = False
            self.direction = 1

        # jump
        if self.jump == True and self.in_air == False:
            self.vel_y = -11
            self.jump = False
            self.in_air = True

        # apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y
        ry += self.vel_y

        # check collision with floor
        if self.rect.bottom + ry > 225:
            ry = 225 - self.rect.bottom
            self.in_air = False

        # update rectangle position
        self.rect.x += rx
        self.rect.y += ry

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (0.6 * self.rect.size[0] * self.direction), self.rect.centery + 10,
                            self.direction)
            bullet_group.add(bullet)
            # reduce ammo
            self.ammo -= 1

    def update_animation(self):
        # update animation
        ANIMATION_COOLDOWN = 100
        # update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        # check if enough time has passed since last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        # if animation has run out reset back to start
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        # check if new action is different to previous one
        if new_action != self.action:
            self.action = new_action
            # update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)


    def drawCharacters(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

#bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        # move bullet
        self.rect.x += (self.direction * self.speed)
        # check if bullet has gone off screen
        if self.rect.right < 0 or self.rect.left > screen_width:
            self.kill()

        # check collision with characters
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 5
                self.kill()

        if pygame.sprite.spritecollide(enemy, bullet_group, False):
            if enemy.alive:
                enemy.health -= 25
                self.kill()

#grenade class
class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -11
        self.speed = 7
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        self.vel_y += GRAVITY
        rx = self.direction * self.speed
        ry = self.vel_y

        # check collision with floor
        if self.rect.bottom + ry > 225:
            ry = 225 - self.rect.bottom
            self.speed = 0

        # check collision with walls
        if self.rect.left + rx < 0 or self.rect.right + rx > screen_width:
            self.direction *= -1
            rx = self.direction * self.speed

        # update grenade position
        self.rect.x += rx
        self.rect.y += ry


# create sprite groups
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()

######################PLAYERS########################

player = Soldier('player', 200, 200, 1, 3, 20, 3)
enemy = Soldier('enemy', 400, 200, 1, 3, 20, 0)

#####################################################


##################################################Game*Runs*Here##################################################
loop = True
while loop:

    draw_background()

    player.update()
    player.drawCharacters()

    enemy.update()
    enemy.drawCharacters()

    # update and draw groups
    bullet_group.update()
    grenade_group.update()
    bullet_group.draw(screen)
    grenade_group.draw(screen)

    # update player actions
    if player.alive:
        # shoot bullets
        if shoot:
            player.shoot()
        # throw grenades
        elif grenade and grenade_thrown == False and player.grenades > 0:
            grenade = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction),
                              player.rect.top, player.direction)
            grenade_group.add(grenade)
            # reduce grenades
            grenade_thrown = True
            player.grenades -= 1
        if player.in_air:
            player.update_action(2)  # 2: jump
        elif movingLeft or movingRight:
            player.update_action(1)  # 1: run
        else:
            player.update_action(0)  # 0: idle
        player.move(movingLeft, movingRight)

    for event in pygame.event.get():
        # quit game
        if event.type == pygame.QUIT:
            loop = False

        # keyboard input
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                movingLeft = True
            if event.key == pygame.K_d:
                movingRight = True
            if event.key == pygame.K_w and player.alive:
                player.jump = True
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_q:
                grenade = True
            if event.key == pygame.K_ESCAPE:
                loop = False

        # keyboard buttons released by player
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                movingLeft = False
            if event.key == pygame.K_d:
                movingRight = False
            if event.key == pygame.K_q:
                grenade = False
                grenade_thrown = False
            if event.key == pygame.K_SPACE:
                shoot = False

    clock.tick(FPS)
    pygame.display.update()

pygame.quit()