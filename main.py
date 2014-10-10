import pygame, sys 
import math
import flock


try:
    import android
except ImportError:
    android = None

class Bullet(pygame.sprite.Sprite):
    def __init__(self, mouse_pos, player_pos):
        RED = (255, 0, 0)
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((3,3))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.player_pos = player_pos
        self.angle = shoot.angle(mouse_pos)
        self.distance = 32

    def update(self):
        self.rect.centerx = int(self.player_pos[0] + math.cos(self.angle) *self.distance)
        self.rect.centery = int(self.player_pos[1] - math.sin(self.angle) * self.distance)
        self.distance = self.distance +10



def create_move_controller():
    # create move controller for desktop environment
    move_control = pygame.Surface((120, 120))
    pygame.draw.circle(move_control, GREEN, (60, 20), 20, 3)
    control_up = pygame.Rect(40, SCREENSIZE[1]-120, 40, 40)
    pygame.draw.circle(move_control, GREEN, (60, 100), 20, 3)
    control_down = pygame.Rect(40, SCREENSIZE[1]-40, 40, 40)
    pygame.draw.circle(move_control, GREEN, (20, 60), 20, 3)
    control_left = pygame.Rect(0, SCREENSIZE[1]-80, 40, 40)
    pygame.draw.circle(move_control, GREEN, (100, 60), 20, 3)
    control_right = pygame.Rect(80, SCREENSIZE[1]-80, 40, 40)
    control_stop = pygame.Rect(40, SCREENSIZE[1]-80, 40, 40)
    stop_button = pygame.Rect(40, 40, 40, 40)
    pygame.draw.rect(move_control, RED, stop_button, 3)
    control_buttons={"left": control_left, "right": control_right, 
                  "up": control_up, "down": control_down, 
                  "stop": control_stop}
    move_control.set_colorkey((0,0,0))
    move_control.set_alpha(80)
    return move_control, control_buttons

class ShootController():
    def __init__(self):
        self.YELLOW = (131, 137, 24)
        self.GRAY = (123, 104, 104)
        self.image = self.draw()
        self.rect = self.image.get_rect()

    def draw(self):
        shoot_control = pygame.Surface((120, 120))
        shoot_control.fill((0,0,0))
        pygame.draw.circle(shoot_control, self.YELLOW, (60, 60), 3)
        pygame.draw.circle(shoot_control, self.GRAY, (60, 60), 50, 1)
#        pygame.draw.circle(shoot_control, self.YELLOW, (60, 60), 40, 1)
        shoot_control.set_colorkey((0,0,0))
        return shoot_control
        
    def angle(self, pos):
        x = pos[0]
        y = pos[1]
        self.centerx = 480- 60
        self.centery = 320 - 60
        adjacent = float(x - self.centerx)
        opposite = float(y - self.centery)
        if opposite < 0.0:
            opposite = opposite * -1.0
            if adjacent > 0.0:
                radians = math.atan(opposite/adjacent)
            elif adjacent == 0:
                radians = .5 * math.pi
            elif adjacent < 0.0:
                adjacent = adjacent * -1
                radians = (.5 * math.pi) +  (.5 * math.pi - math.atan(opposite/adjacent))
        elif opposite == 0:
            if adjacent > 0:
                radians = 0
            if adjacent < 0:
                radians = math.pi
        elif opposite > 0.0:
            if adjacent > 0.0:
                radians = math.pi + (.5 * math.pi) +  (.5 * math.pi - math.atan(opposite/adjacent))
            elif adjacent == 0:
                radians = 1.5 * math.pi
            elif adjacent < 0.0:
                adjacent = adjacent * -1
                radians = math.pi + math.atan(opposite/adjacent)
        return radians

    def point(self, pos):
        angle = self.angle(pos)
        hypotenuse = 50
        adjacent = math.cos(angle) * hypotenuse
        x = int(60 + adjacent)
        opposite = math.sin(angle) * hypotenuse
        y =  int(60-opposite)
        pygame.draw.circle(self.image, self.YELLOW, (x, y), 10, 2)

pygame.init()

if android:
    android.init()
    android.map_key(android.KEYCODE_BACK, pygame.K_ESCAPE)
    enable = True
    android.accelerometer_enable(enable)

SCREENSIZE=(480,320)
SCREENCENTER=(SCREENSIZE[0]/2, SCREENSIZE[1]/2)
SCREEN = pygame.display.set_mode((480, 320))
RED=(255, 0, 0)
GREEN=(0, 255, 0)
BLACK=(0,0,0)
speed = 5
direction = "stop"

sprite_sheet = pygame.image.load("img/sprite_sheet.png").convert_alpha()

player_d = []
player_r = []
player_l = []
player_u = []

seq_d = 1
seq_l = 1
seq_r = 1
seq_u = 1



for x in range (0, 256, 64):
    rect = pygame.Rect(x, 0, 64, 64)
    img_d = pygame.Surface((64, 64))
    img_d.blit(sprite_sheet, (0, 0), rect)
    img_d.unlock()
    img_d.set_colorkey((0,0,0))
    img_d.convert_alpha()
    player_d.append(img_d)
    img_l = pygame.Surface((64, 64))
    rect = pygame.Rect(x, 64, 64, 64)
    img_l.blit(sprite_sheet, (0, 0) , rect)
    img_l.unlock()
    img_l.set_colorkey((0,0,0))
    img_l.convert_alpha()
    player_l.append(img_l)
    img_r = pygame.Surface((64, 64))
    rect = pygame.Rect(x, 128, 64, 64)
    img_r.blit(sprite_sheet, (0,0), rect)
    img_r.unlock()
    img_r.set_colorkey((0,0,0))
    img_r.convert_alpha()
    player_r.append(img_r)
    img_u = pygame.Surface((64, 64))
    rect = pygame.Rect(x, 192, 64, 64)
    img_u.blit(sprite_sheet, (0,0), rect)
    img_u.unlock()
    img_u.set_colorkey((0,0,0))
    img_u.convert_alpha()
    player_u.append(img_u)

player_down = player_d[1]
player_up = player_u[1]
player_right = player_r[1]
player_left = player_l[1]
player = player_down

player_rect = pygame.Rect(0,0,64,64)
player_rect.center = SCREEN.get_rect().center

FPS = 30
clock = pygame.time.Clock()

move_control, control_buttons = create_move_controller()
shoot = ShootController()
shoot.rect.bottomright = SCREENSIZE

newBullet = False
bulletDelay = 10
bulletFirst = True
bullet_group = pygame.sprite.Group()
mouse_pos = pygame.mouse.get_pos()

# flock 
predator = False
f = flock.Flock(30, 100., 500)

while True:
    if android:
        if android.check_pause():
            android.wait_for_resume()
        accel_reading = android.accelerometer_reading()

    for event in pygame.event.get():
        if (event.type == pygame.QUIT) or (event.type == pygame.KEYDOWN 
                                         and event.key == pygame.K_ESCAPE):
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_pos = (0,0)


    if android:
        if accel_reading[1] > 1 or accel_reading[1] < -1 or accel_reading[0] > 6 or accel_reading[0] < 4:
            if accel_reading[1] > .8:
                direction = "right"
            if accel_reading[1] < -.8:
                direction = "left"
            if accel_reading[0] > 7:
                direction = "down"
            if accel_reading[0] < 4.5:
                direction ="up"
        else:
            direction = "stop"
    if not android: # for testing on desktop


        if control_buttons["right"].collidepoint(mouse_pos): 
            direction = "right"
        if control_buttons["left"].collidepoint(mouse_pos):
            direction = "left"
        if control_buttons["down"].collidepoint( mouse_pos):
            direction = "down"
        if control_buttons["up"].collidepoint(mouse_pos):
            direction = "up"
        if control_buttons["stop"].collidepoint(mouse_pos):
            direction = "stop"

    if direction =="right" and player_rect.right < 480:
        player_rect.centerx += speed
        player = player_r[seq_r]
        if seq_r < 3:
            seq_r += 1
        else:
            seq_r = 0
    if direction == "left" and player_rect.left > 0:
        player_rect.centerx -= speed
        player = player_l[seq_l]
        if seq_l < 3:
            seq_l += 1
        else:
            seq_l = 0

    if direction == "down" and player_rect.centery < 320:
        player_rect.centery += speed
        player = player_d[seq_d]
        if seq_d < 3:
            seq_d += 1
        else:
            seq_d = 0

    if direction == "up"  and player_rect.centery > 0:
        player_rect.centery -= speed
        player = player_u[seq_u]
        if seq_u < 3:
            seq_u += 1
        else:
            seq_u = 0

    if shoot.rect.collidepoint(mouse_pos):

        shoot.image = shoot.draw()
        shoot.point(mouse_pos)
        newBullet = True
    


    SCREEN.fill(BLACK)
    # flock
    f.update(player_rect.center, predator)
    flock_surface = f.draw() # draw the flock
    SCREEN.blit(flock_surface, (0,0))


    if newBullet:
        bullet = Bullet(mouse_pos, player_rect.center)
        bullet_group.add(bullet)
        newBullet = False
    
    bullet_group.update()
    for bullet in bullet_group:
        if (bullet.rect.centerx > 480 or bullet.rect.centerx < 0 or bullet.rect.centery < 0 or
            bullet.rect.centery) > 320:
            bullet_group.remove(bullet)
    bullet_group.draw(SCREEN)
    
    SCREEN.blit(shoot.image, shoot.rect)
    SCREEN.blit(player, player_rect)
    if not android: 
        SCREEN.blit(move_control, (0, SCREENSIZE[1] - 120)) #show controller

    clock.tick(FPS)
    pygame.display.update()
