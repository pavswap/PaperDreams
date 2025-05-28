import pygame
import sys
import random

pygame.init()

#Added Music
pygame.mixer.init()
pygame.mixer.music.load("music/paperdreams.mp3") 
pygame.mixer.music.set_volume(0.5) 
pygame.mixer.music.play(-1)

# Screen setup
screen = pygame.display.set_mode((750, 600))
pygame.display.set_caption("Paper Dreams")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 40)

# Load images
menu_background = pygame.image.load("graphics/main_menu.png").convert()
menu_background = pygame.transform.scale(menu_background, (750, 600))

sky_image = pygame.image.load("graphics/background.png").convert()
sky_image = pygame.transform.scale(sky_image, (750, 500))

ground_image = pygame.image.load("graphics/floor.png").convert()
ground_image = pygame.transform.scale(ground_image, (750, 100))

player_image = pygame.image.load("graphics/player_final.png").convert_alpha()
player_image = pygame.transform.scale(player_image, (50, 100))
player_rect = player_image.get_rect(midbottom=(100, 500))

enemy_image = pygame.image.load("graphics/enemy_final.png").convert_alpha()
enemy_image = pygame.transform.scale(enemy_image, (50, 100))
enemy_rect = enemy_image.get_rect(midbottom=(800, 500))
enemy2_rect = enemy_image.get_rect(midbottom=(1000, 500))
enemy_speed = 4
enemy2_active = False

# Player physics
player_gravity = 0
jump_force = -25

# Score
score = 0
score_timer = pygame.USEREVENT + 1
pygame.time.set_timer(score_timer, 1000)

# Game states
game_active = False
menu_active = True

# Buttons (moved right by 100px from original)
start_button = pygame.Rect(375, 250, 200, 60)
quit_button = pygame.Rect(375, 350, 200, 60)

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if menu_active:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    game_active = True
                    menu_active = False
                    player_rect.midbottom = (100, 500)
                    enemy_rect.midbottom = (800, 500)
                    enemy2_rect.midbottom = (1000, 500)
                    player_gravity = 0
                    score = 0

                    # Randomize speed and decide if second enemy is active
                    enemy_speed = random.randint(3, 10)
                    enemy2_active = enemy_speed <= 5

                elif quit_button.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

        elif game_active:
            if event.type == score_timer:
                score += 1

    if menu_active:
        screen.blit(menu_background, (0, 0))

        pygame.draw.rect(screen, 'gray', start_button)
        pygame.draw.rect(screen, 'gray', quit_button)

        start_text = font.render("Start Game", True, 'white')
        quit_text = font.render("Quit Game", True, 'white')

        screen.blit(start_text, (start_button.x + 40, start_button.y + 15))
        screen.blit(quit_text, (quit_button.x + 50, quit_button.y + 15))

    elif game_active:
        # Input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and player_rect.bottom >= 500:
            player_gravity = jump_force

        # Apply gravity
        player_gravity += 1
        if player_gravity > 20:
            player_gravity = 20
        player_rect.y += player_gravity

        if player_rect.bottom >= 500:
            player_rect.bottom = 500
            player_gravity = 0

        # Move enemies
        enemy_rect.right -= enemy_speed
        if enemy_rect.right < -100:
            enemy_rect.right = 800
            enemy_speed = random.randint(3, 10)
            enemy2_active = enemy_speed <= 5
            if enemy2_active:
                enemy2_rect.right = 1000

        if enemy2_active:
            enemy2_rect.right -= enemy_speed
            if enemy2_rect.right < -100:
                enemy2_rect.right = 1000

        # Collision detection
        if player_rect.colliderect(enemy_rect) or (enemy2_active and player_rect.colliderect(enemy2_rect)):
            game_active = False
            menu_active = True

        # Draw background
        screen.blit(sky_image, (0, 0))
        screen.blit(ground_image, (0, 500))

        screen.blit(enemy_image, enemy_rect)
        if enemy2_active:
            screen.blit(enemy_image, enemy2_rect)
        screen.blit(player_image, player_rect)

        score_surface = font.render(f"Score: {score}", True, 'black')
        screen.blit(score_surface, (10, 10))

    pygame.display.update()
    clock.tick(60)
