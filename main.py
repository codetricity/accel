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

SCREEN = pygame.display.set_mode((480, 320))
RED=(255, 0, 0)
BLACK=(0,0,0)
speed = 5

player_down = pygame.image.load("img/down.png").convert_alpha()
player_up = pygame.image.load("img/up.png").convert_alpha()
player_right = pygame.image.load("img/right.png").convert_alpha()
player_left = pygame.image.load("img/left.png").convert_alpha()
player = player_down

player_rect = pygame.Rect(0,0,64,64)
player_rect.center = SCREEN.get_rect().center


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

    if accel_reading[1] > 1 and player_rect.right < 480:
        player_rect.centerx += speed
        player = player_right
    if accel_reading[1] < -1 and player_rect.left > 0:
        player_rect.centerx -= speed
        player = player_left

    if accel_reading[0] > 1 and player_rect.centery < 320:
        player_rect.centery += speed
        player = player_down
    if accel_reading[0] < -1 and player_rect.centery > 0:
        player_rect.centery -= speed
        player = player_up

    SCREEN.fill(BLACK)
    SCREEN.blit(player, player_rect)

    pygame.display.update()
