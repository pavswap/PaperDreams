import pygame
import sys
import random
import os

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

pygame.init()
pygame.mixer.init()

pygame.mixer.music.load(resource_path("music/paperdreams.mp3"))
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

screen = pygame.display.set_mode((750, 600))
pygame.display.set_caption("Paper Dreams")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 40)

menu_background = pygame.image.load(resource_path("graphics/main_menu.png")).convert()
menu_background = pygame.transform.scale(menu_background, (750, 600))

sky_image = pygame.image.load(resource_path("graphics/background.png")).convert()
sky_image = pygame.transform.scale(sky_image, (750, 500))

ground_image = pygame.image.load(resource_path("graphics/floor.png")).convert()
ground_image = pygame.transform.scale(ground_image, (750, 100))

player_image = pygame.image.load(resource_path("graphics/player_final.png")).convert_alpha()
player_image = pygame.transform.scale(player_image, (50, 100))
player_rect = player_image.get_rect(midbottom=(100, 500))

enemy_image = pygame.image.load(resource_path("graphics/enemy_final.png")).convert_alpha()
enemy_image = pygame.transform.scale(enemy_image, (50, 100))

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

enemy1 = Enemy(enemy_image, start_x=800, y_pos=500, speed_range=(3, 10), active_chance=1.0)
enemy2 = Enemy(enemy_image, start_x=1000, y_pos=500, speed_range=(3, 10), active_chance=0.5)
enemy3 = Enemy(enemy_image, start_x=900, y_pos=500, speed_range=(13, 15), active_chance=0.5)

flying_enemy = Enemy(enemy_image, start_x=1200, y_pos=400, speed_range=(7, 10), active_chance=1.0, always_active=True)
flying_enemy.active = False

enemies = [enemy1, enemy2, enemy3]

player_gravity = 0
jump_force = -25
player_speed = 5

score = 0
score_timer = pygame.USEREVENT + 1
pygame.time.set_timer(score_timer, 1000)

game_active = False
menu_active = True

start_button = pygame.Rect(375, 250, 200, 60)
quit_button = pygame.Rect(375, 350, 200, 60)

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
        screen.blit(menu_background, (0, 0))
        pygame.draw.rect(screen, 'gray', start_button)
        pygame.draw.rect(screen, 'gray', quit_button)
        start_text = font.render("Start Game", True, 'white')
        quit_text = font.render("Quit Game", True, 'white')
        screen.blit(start_text, (start_button.x + 40, start_button.y + 15))
        screen.blit(quit_text, (quit_button.x + 50, quit_button.y + 15))
        highscore_text = font.render(f"High Score: {high_score}", True, 'white')
        screen.blit(highscore_text, (10, 10))

    elif game_active:
        keys = pygame.key.get_pressed()

        if keys[pygame.K_SPACE] and player_rect.bottom >= 500:
            player_gravity = jump_force

        if keys[pygame.K_DOWN]:
            player_gravity += 3

        if keys[pygame.K_LEFT]:
            player_rect.x -= player_speed
        if keys[pygame.K_RIGHT]:
            player_rect.x += player_speed

        if player_rect.left < 0:
            player_rect.left = 0
        if player_rect.right > 750:
            player_rect.right = 750

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

        collision = False
        for enemy in enemies:
            if enemy.check_collision(player_rect):
                collision = True
        if flying_enemy.check_collision(player_rect):
            collision = True

        if collision:
            if score > high_score:
                high_score = score
                save_high_score(high_score)
            game_active = False
            menu_active = True

        screen.blit(sky_image, (0, 0))
        screen.blit(ground_image, (0, 500))

        for enemy in enemies:
            enemy.draw(screen)
        flying_enemy.draw(screen)

        screen.blit(player_image, player_rect)

        score_surface = font.render(f"Score: {score}", True, 'black')
        screen.blit(score_surface, (10, 10))

        highscore_surface = font.render(f"High Score: {high_score}", True, 'black')
        screen.blit(highscore_surface, (10, 40))

    pygame.display.update()
    clock.tick(60)
