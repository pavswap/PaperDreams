import pygame
import sys
import random
import os


# def resource_path(relative_path):
#     try:
#         base_path = sys._MEIPASS
#     except AttributeError:
#         base_path = os.path.abspath(".")
#     return os.path.join(base_path, relative_path)

pygame.init()
pygame.mixer.init()

# Music setup
menu_music = "music/paperdreams.mp3"
game_music = "music/deep sleep menu music.mp3"

def play_music(music_path):
    pygame.mixer.music.stop()
    pygame.mixer.music.load(music_path)
    pygame.mixer.music.set_volume(0.5 if music_path == menu_music else 1)
    pygame.mixer.music.play(-1)

play_music(menu_music)

# Screen setup
SCREEN_WIDTH, SCREEN_HEIGHT = 750, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Paper Dreams")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 40)

# Load images
menu_background = pygame.image.load("graphics/main_menu.png").convert()
menu_background = pygame.transform.scale(menu_background, (SCREEN_WIDTH, SCREEN_HEIGHT))

sky_image = pygame.image.load("graphics/background.png").convert()
sky_image = pygame.transform.scale(sky_image, (SCREEN_WIDTH, 500))

ground_image = pygame.image.load("graphics/floor.png").convert()
ground_image = pygame.transform.scale(ground_image, (SCREEN_WIDTH, 100))

player_image = pygame.image.load("graphics/player_final.png").convert_alpha()
player_image = pygame.transform.scale(player_image, (50, 100))
player_rect = player_image.get_rect(midbottom=(100, 500))

enemy_image = pygame.image.load("graphics/enemy_final.png").convert_alpha()
enemy_image = pygame.transform.scale(enemy_image, (50, 100))

# Enemy class
class Enemy:
    def __init__(self, image, start_x, y_pos, speed_range=(3, 10), active_chance=1.0, always_active=False):
        self.image = image
        self.rect = image.get_rect(midbottom=(start_x, y_pos))
        self.y_pos = y_pos
        self.speed_range = speed_range
        self.speed = random.randint(*self.speed_range)
        self.active_chance = active_chance
        self.always_active = always_active
        self.active = random.random() < self.active_chance or always_active

    def reset(self, start_x):
        self.rect.right = start_x
        self.speed = random.randint(*self.speed_range)
        self.active = random.random() < self.active_chance or self.always_active
        self.rect.bottom = self.y_pos

    def update(self):
        if self.active:
            self.rect.right -= self.speed
            if self.rect.right < -100:
                self.reset(random.randint(850, 1000))

    def draw(self, surface):
        if self.active:
            surface.blit(self.image, self.rect)

    def check_collision(self, player_rect):
        return self.active and self.rect.colliderect(player_rect)

# High score setup
highscore_file = "highscore.txt"

def load_high_score():
    if os.path.exists(highscore_file):
        with open(highscore_file, "r") as file:
            try:
                return int(file.read())
            except ValueError:
                return 0
    return 0

def save_high_score(score):
    with open(highscore_file, "w") as file:
        file.write(str(score))

high_score = load_high_score()

# Enemies
enemy1 = Enemy(enemy_image, 800, 500)
enemy2 = Enemy(enemy_image, 1000, 500, active_chance=0.5)
enemy3 = Enemy(enemy_image, 900, 500, speed_range=(13, 15), active_chance=0.5)
flying_enemy = Enemy(enemy_image, 1200, 400, speed_range=(7, 10), always_active=True)
flying_enemy.active = False
enemies = [enemy1, enemy2, enemy3]

# Player physics
player_gravity = 0
jump_force = -25
player_speed = 5

# Score
score = 0
score_timer = pygame.USEREVENT + 1
pygame.time.set_timer(score_timer, 1000)

# Game states
game_active = False
menu_active = True

# Buttons (bottom right corner)
button_width, button_height = 200, 60
start_button = pygame.Rect(SCREEN_WIDTH - button_width - 50, SCREEN_HEIGHT - 2 * button_height - 60, button_width, button_height)
quit_button = pygame.Rect(SCREEN_WIDTH - button_width - 50, SCREEN_HEIGHT - button_height - 40, button_width, button_height)

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if menu_active:
            if not pygame.mixer.music.get_busy() or pygame.mixer.music.get_pos() == -1:
                play_music(menu_music)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    game_active = True
                    menu_active = False
                    play_music(game_music)

                    player_rect.midbottom = (100, 500)
                    player_gravity = 0
                    score = 0
                    for i, enemy in enumerate(enemies):
                        enemy.reset(800 + i * 200)
                    flying_enemy.reset(1200)
                    flying_enemy.active = False

                elif quit_button.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

        elif game_active:
            if event.type == score_timer:
                score += 1
                if score > 30:
                    flying_enemy.active = True

    if menu_active:
        mouse_pos = pygame.mouse.get_pos()

        # If hovering over start button, show solid blue background
        if start_button.collidepoint(mouse_pos):
            screen.fill((0, 0, 255))  # Solid blue
        else:
            screen.blit(menu_background, (0, 0))

        # Draw buttons
        start_color = 'lightgray' if start_button.collidepoint(mouse_pos) else 'gray'
        pygame.draw.rect(screen, start_color, start_button)
        pygame.draw.rect(screen, 'gray', quit_button)

        # Button texts
        start_text = font.render("Start Game", True, 'white')
        quit_text = font.render("Quit Game", True, 'white')
        screen.blit(start_text, (start_button.x + 30, start_button.y + 15))
        screen.blit(quit_text, (quit_button.x + 30, quit_button.y + 15))

        # High score at bottom-left
        highscore_text = font.render(f"High Score: {high_score}", True, 'white')
        screen.blit(highscore_text, (10, SCREEN_HEIGHT - 40))

    elif game_active:
        keys = pygame.key.get_pressed()

        if keys[pygame.K_SPACE] and player_rect.bottom >= 500:
            player_gravity = jump_force
        if keys[pygame.K_a]:
            player_rect.x -= player_speed
        if keys[pygame.K_d]:
            player_rect.x += player_speed

        if player_rect.left < 0:
            player_rect.left = 0
        if player_rect.right > SCREEN_WIDTH:
            player_rect.right = SCREEN_WIDTH

        player_gravity += 1
        if player_gravity > 20:
            player_gravity = 20
        player_rect.y += player_gravity

        if player_rect.bottom >= 500:
            player_rect.bottom = 500
            player_gravity = 0

        for enemy in enemies:
            enemy.update()
        if flying_enemy.active:
            flying_enemy.update()

        collision = any(enemy.check_collision(player_rect) for enemy in enemies) or flying_enemy.check_collision(player_rect)

        if collision:
            if score > high_score:
                high_score = score
                save_high_score(high_score)
            game_active = False
            menu_active = True
            play_music(menu_music)

        screen.blit(sky_image, (0, 0))
        screen.blit(ground_image, (0, 500))

        for enemy in enemies:
            enemy.draw(screen)
        flying_enemy.draw(screen)

        screen.blit(player_image, player_rect)

        score_surface = font.render(f"Score: {score}", True, 'black')
        highscore_surface = font.render(f"High Score: {high_score}", True, 'black')
        screen.blit(score_surface, (10, 10))
        screen.blit(highscore_surface, (10, SCREEN_HEIGHT - 40))

    pygame.display.update()
    clock.tick(60)
