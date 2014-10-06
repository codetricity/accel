import pygame, sys 

try:
    import android
except ImportError:
    android = None




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
    img_d = pygame.Surface((64, 64)).convert_alpha()
    img_d.blit(sprite_sheet, (0, 0), rect)
    player_d.append(img_d)
    img_l = pygame.Surface((64, 64)).convert_alpha()
    rect = pygame.Rect(x, 64, 64, 64)
    img_l.blit(sprite_sheet, (0, 0) , rect)
    player_l.append(img_l)
    img_r = pygame.Surface((64, 64)).convert_alpha()
    rect = pygame.Rect(x, 128, 64, 64)
    img_r.blit(sprite_sheet, (0,0), rect)
    player_r.append(img_r)
    img_u = pygame.Surface((64, 64)).convert_alpha()
    rect = pygame.Rect(x, 192, 64, 64)
    img_u.blit(sprite_sheet, (0,0), rect)
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
    move_control.set_alpha(80)
    control_buttons={"left": control_left, "right": control_right, 
                  "up": control_up, "down": control_down, 
                  "stop": control_stop}
    return move_control, control_buttons

move_control, control_buttons = create_move_controller()


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
        mouse_pos = pygame.mouse.get_pos()

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


    SCREEN.fill(BLACK)
    SCREEN.blit(player, player_rect)
    if not android: 
        SCREEN.blit(move_control, (0, SCREENSIZE[1] - 120)) #show controller

    clock.tick(FPS)
    pygame.display.update()
