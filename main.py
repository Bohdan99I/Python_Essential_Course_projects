import random
from os import listdir, path

import pygame
from pygame.constants import (
    QUIT,
    K_DOWN,
    K_UP,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    K_RETURN,
    K_r,
)

pygame.init()

FPS = pygame.time.Clock()
screen = width, height = 800, 600

# Кольори
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Шрифти
font = pygame.font.SysFont("Verdana", 20)
big_font = pygame.font.SysFont("Verdana", 50, bold=True)

main_surface = pygame.display.set_mode(screen)

IMGS_PATH = "goose"

# Завантаження картинок гравця
player_imgs = [
    pygame.image.load(IMGS_PATH + "/" + file).convert_alpha()
    for file in listdir(IMGS_PATH)
]
player = player_imgs[0]
player_rect = player.get_rect()
player_speed = 10


def create_enemy():
    enemy = pygame.image.load("enemy.png").convert_alpha()
    enemy_rect = pygame.Rect(
        width, random.randint(0, height - enemy.get_height()), *enemy.get_size()
    )
    enemy_speed = random.randint(4, 6)
    return [enemy, enemy_rect, enemy_speed]


def create_bonus():
    bonus = pygame.image.load("bonus.png").convert_alpha()
    bonus_rect = pygame.Rect(
        random.randint(0, width - bonus.get_width()), 0, *bonus.get_size()
    )
    bonus_speed = random.randint(4, 6)
    return [bonus, bonus_rect, bonus_speed]


# Фон
bg = pygame.transform.scale(pygame.image.load("background.png").convert(), screen)
bgX = 0
bgX2 = bg.get_width()
bg_speed = 3

# Події
CREATE_ENEMY = pygame.USEREVENT + 1
pygame.time.set_timer(CREATE_ENEMY, 1500)

CREATE_BONUS = pygame.USEREVENT + 2
pygame.time.set_timer(CREATE_BONUS, 1500)

CHANGE_IMG = pygame.USEREVENT + 3
pygame.time.set_timer(CHANGE_IMG, 125)

# --- Глобальні змінні ---
img_index = 0
scores = 0
high_score = 0
enemies = []
bonuses = []

is_working = True
game_started = False
game_over = False

# --- High Score ---
HIGHSCORE_FILE = "highscore.txt"
if path.exists(HIGHSCORE_FILE):
    with open(HIGHSCORE_FILE, "r") as f:
        try:
            high_score = int(f.read())
        except ValueError:
            high_score = 0


def save_highscore():
    global scores, high_score
    if scores > high_score:
        high_score = scores
        with open(HIGHSCORE_FILE, "w") as f:
            f.write(str(high_score))


def reset_game():
    global enemies, bonuses, scores, player_rect, player, img_index, game_over, bgX, bgX2
    enemies = []
    bonuses = []
    scores = 0
    img_index = 0
    player = player_imgs[0]
    player_rect = player.get_rect()
    bgX = 0
    bgX2 = bg.get_width()
    game_over = False


def draw_text_center(text, font_obj, color, y):
    surf = font_obj.render(text, True, color)
    main_surface.blit(surf, (width // 2 - surf.get_width() // 2, y))


def draw_start_screen():
    main_surface.fill(BLACK)
    draw_text_center("GOOSE GAME", big_font, GREEN, height // 3)
    draw_text_center("Press ENTER to Start", font, WHITE, height // 2)
    draw_text_center(
        "Use arrows to move, collect bonuses, avoid enemies",
        font,
        WHITE,
        height // 2 + 40,
    )
    draw_text_center(f"High Score: {high_score}", font, GREEN, height // 2 + 80)
    pygame.display.flip()


def draw_game_over():
    main_surface.fill(BLACK)
    draw_text_center("GAME OVER", big_font, RED, height // 3)
    draw_text_center(f"Your score: {scores}", font, WHITE, height // 2)
    draw_text_center(f"High Score: {high_score}", font, GREEN, height // 2 + 40)
    draw_text_center("Press R to Restart or ESC to Quit", font, WHITE, height // 2 + 80)
    pygame.display.flip()


# --- Основний цикл ---
while is_working:
    FPS.tick(60)

    if not game_started:
        # Стартовий екран
        draw_start_screen()

        for event in pygame.event.get():
            if event.type == QUIT:
                is_working = False
            elif event.type == pygame.KEYDOWN:
                if event.key == K_RETURN:
                    game_started = True
                    reset_game()

    elif not game_over:
        for event in pygame.event.get():
            if event.type == QUIT:
                is_working = False

            if event.type == CREATE_ENEMY:
                enemies.append(create_enemy())

            if event.type == CREATE_BONUS:
                bonuses.append(create_bonus())

            if event.type == CHANGE_IMG:
                img_index = (img_index + 1) % len(player_imgs)
                player = player_imgs[img_index]

        pressed_keys = pygame.key.get_pressed()

        # Рух фону
        bgX -= bg_speed
        bgX2 -= bg_speed

        if bgX < -bg.get_width():
            bgX = bg.get_width()

        if bgX2 < -bg.get_width():
            bgX2 = bg.get_width()

        main_surface.blit(bg, (bgX, 0))
        main_surface.blit(bg, (bgX2, 0))

        main_surface.blit(player, player_rect)

        main_surface.blit(font.render(str(scores), True, RED), (width - 50, 20))
        main_surface.blit(font.render(f"High: {high_score}", True, GREEN), (20, 20))

        # Вороги
        for enemy in enemies[:]:
            enemy[1] = enemy[1].move(-enemy[2], 0)
            main_surface.blit(enemy[0], enemy[1])

            if enemy[1].right < 0:
                enemies.remove(enemy)

            if player_rect.colliderect(enemy[1]):
                game_over = True
                save_highscore()

        # Бонуси
        for bonus in bonuses[:]:
            bonus[1] = bonus[1].move(0, bonus[2])
            main_surface.blit(bonus[0], bonus[1])

            if bonus[1].top >= height:
                bonuses.remove(bonus)

            if player_rect.colliderect(bonus[1]):
                bonuses.remove(bonus)
                scores += 1

        # Управління гравцем
        if pressed_keys[K_DOWN] and player_rect.bottom < height:
            player_rect = player_rect.move(0, player_speed)

        if pressed_keys[K_UP] and player_rect.top > 0:
            player_rect = player_rect.move(0, -player_speed)

        if pressed_keys[K_RIGHT] and player_rect.right < width:
            player_rect = player_rect.move(player_speed, 0)

        if pressed_keys[K_LEFT] and player_rect.left > 0:
            player_rect = player_rect.move(-player_speed, 0)

        pygame.display.flip()

    else:
        # Екран Game Over
        draw_game_over()

        for event in pygame.event.get():
            if event.type == QUIT:
                is_working = False
            elif event.type == pygame.KEYDOWN:
                if event.key == K_r:  # Restart
                    reset_game()
                elif event.key == K_ESCAPE:
                    is_working = False
