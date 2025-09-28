# pylint: disable=no-member
import pygame
import random
import os

pygame.init()

# --- Налаштування ---
WIDTH, HEIGHT = 800, 600
FPS = 60

# Кольори
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Розміри об'єктів
PLAYER_SIZE = (100, 60)
ENEMY_SIZE = (60, 40)
BONUS_SIZE = (40, 40)

# Шрифти
FONT = pygame.font.SysFont("Verdana", 20)
BIG_FONT = pygame.font.SysFont("Verdana", 50, bold=True)

# Файли
HIGHSCORE_FILE = "highscore.txt"
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
GOOSE_DIR = os.path.join(ASSETS_DIR, "goose")


# --- Базовий клас об'єктів ---
class GameObject:
    def __init__(self, image, rect, speed):
        self._image = image
        self._rect = rect
        self._speed = speed

    @property
    def rect(self):
        return self._rect

    def draw(self, surface):
        surface.blit(self._image, self._rect)

    def update(self):
        pass


# --- Гравець ---
class Player(GameObject):
    def __init__(self, images, speed):
        self._images = images
        self._img_index = 0
        self._speed = speed
        self._image = images[0]
        self._rect = self._image.get_rect(center=(WIDTH // 2, HEIGHT - 70))

    def move(self, keys):
        if keys[pygame.K_DOWN] and self._rect.bottom < HEIGHT:
            self._rect.y += self._speed
        if keys[pygame.K_UP] and self._rect.top > 0:
            self._rect.y -= self._speed
        if keys[pygame.K_RIGHT] and self._rect.right < WIDTH:
            self._rect.x += self._speed
        if keys[pygame.K_LEFT] and self._rect.left > 0:
            self._rect.x -= self._speed

    def change_image(self):
        self._img_index = (self._img_index + 1) % len(self._images)
        self._image = self._images[self._img_index]


# --- Вороги ---
class Enemy(GameObject):
    def update(self):
        self._rect.x -= self._speed


# --- Бонуси ---
class Bonus(GameObject):
    def update(self):
        self._rect.y += self._speed


# --- Головний клас гри ---
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("GOOSE GAME")
        self.clock = pygame.time.Clock()

        # Фон
        self.bg = pygame.transform.scale(
            pygame.image.load(os.path.join(ASSETS_DIR, "background.png")).convert(),
            (WIDTH, HEIGHT),
        )
        self.bgX = 0
        self.bgX2 = self.bg.get_width()
        self.bg_speed = 3

        # Гравець
        player_images = [
            pygame.transform.scale(
                pygame.image.load(
                    os.path.join(GOOSE_DIR, f"goose{i}.png")
                ).convert_alpha(),
                PLAYER_SIZE,
            )
            for i in range(1, 6)
        ]
        self.player = Player(player_images, speed=10)

        # Вороги та бонуси
        self.enemies = []
        self.bonuses = []

        # Стани гри
        self.is_running = True
        self.game_started = False
        self.game_over = False
        self.scores = 0
        self.high_score = self.load_highscore()

        # Події
        self.CREATE_ENEMY = pygame.USEREVENT + 1
        pygame.time.set_timer(self.CREATE_ENEMY, 1500)
        self.CREATE_BONUS = pygame.USEREVENT + 2
        pygame.time.set_timer(self.CREATE_BONUS, 1500)
        self.CHANGE_IMG = pygame.USEREVENT + 3
        pygame.time.set_timer(self.CHANGE_IMG, 125)

    # --- Highscore ---
    def load_highscore(self):
        if os.path.exists(HIGHSCORE_FILE):
            with open(HIGHSCORE_FILE, "r") as f:
                try:
                    return int(f.read())
                except ValueError:
                    return 0
        return 0

    def save_highscore(self):
        if self.scores > self.high_score:
            self.high_score = self.scores
            with open(HIGHSCORE_FILE, "w") as f:
                f.write(str(self.high_score))

    # --- Створення ворогів та бонусів ---
    def create_enemy(self):
        img = pygame.transform.scale(
            pygame.image.load(os.path.join(ASSETS_DIR, "enemy.png")).convert_alpha(),
            ENEMY_SIZE,
        )
        rect = img.get_rect(midtop=(WIDTH, random.randint(0, HEIGHT - ENEMY_SIZE[1])))
        speed = random.randint(4, 6)
        self.enemies.append(Enemy(img, rect, speed))

    def create_bonus(self):
        img = pygame.transform.scale(
            pygame.image.load(os.path.join(ASSETS_DIR, "bonus.png")).convert_alpha(),
            BONUS_SIZE,
        )
        rect = img.get_rect(midtop=(random.randint(0, WIDTH - BONUS_SIZE[0]), 0))
        speed = random.randint(4, 6)
        self.bonuses.append(Bonus(img, rect, speed))

    # --- Текст ---
    def draw_text_center(self, text, font_obj, color, y):
        surf = font_obj.render(text, True, color)
        self.screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, y))

    # --- Стартовий екран ---
    def draw_start_screen(self):
        self.screen.fill(BLACK)
        self.draw_text_center("GOOSE GAME", BIG_FONT, GREEN, HEIGHT // 3)
        self.draw_text_center("Press ENTER to Start", FONT, WHITE, HEIGHT // 2)
        self.draw_text_center(
            "Use arrows to move, collect bonuses, avoid enemies",
            FONT,
            WHITE,
            HEIGHT // 2 + 40,
        )
        self.draw_text_center(
            f"High Score: {self.high_score}", FONT, GREEN, HEIGHT // 2 + 80
        )
        pygame.display.flip()

    # --- Game Over ---
    def draw_game_over(self):
        self.screen.fill(BLACK)
        self.draw_text_center("GAME OVER", BIG_FONT, RED, HEIGHT // 3)
        self.draw_text_center(f"Your Score: {self.scores}", FONT, WHITE, HEIGHT // 2)
        self.draw_text_center(
            f"High Score: {self.high_score}", FONT, GREEN, HEIGHT // 2 + 40
        )
        self.draw_text_center(
            "Press R to Restart or ESC to Quit", FONT, WHITE, HEIGHT // 2 + 80
        )
        pygame.display.flip()

    # --- Reset гри ---
    def reset_game(self):
        self.enemies.clear()
        self.bonuses.clear()
        self.scores = 0
        self.player = Player(self.player._images, speed=10)
        self.bgX = 0
        self.bgX2 = self.bg.get_width()
        self.game_over = False

    # --- Основний цикл ---
    def run(self):
        while self.is_running:
            self.clock.tick(FPS)
            if not self.game_started:
                self.draw_start_screen()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.is_running = False
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        self.game_started = True
                        self.reset_game()
            elif not self.game_over:
                self.handle_gameplay()
            else:
                self.draw_game_over()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.is_running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            self.reset_game()
                        elif event.key == pygame.K_ESCAPE:
                            self.is_running = False

    # --- Логіка гри ---
    def handle_gameplay(self):
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            elif event.type == self.CREATE_ENEMY:
                self.create_enemy()
            elif event.type == self.CREATE_BONUS:
                self.create_bonus()
            elif event.type == self.CHANGE_IMG:
                self.player.change_image()

        # Рух фону
        self.bgX -= self.bg_speed
        self.bgX2 -= self.bg_speed
        if self.bgX < -self.bg.get_width():
            self.bgX = self.bg.get_width()
        if self.bgX2 < -self.bg.get_width():
            self.bgX2 = self.bg.get_width()

        # Малюємо фон та гравця
        self.screen.blit(self.bg, (self.bgX, 0))
        self.screen.blit(self.bg, (self.bgX2, 0))
        self.player.move(keys)
        self.player.draw(self.screen)

        # Відображення рахунку
        score_surf = FONT.render(str(self.scores), True, RED)
        high_surf = FONT.render(f"High: {self.high_score}", True, GREEN)
        self.screen.blit(score_surf, (WIDTH - 50, 20))
        self.screen.blit(high_surf, (20, 20))

        # Оновлення ворогів
        for enemy in self.enemies[:]:
            enemy.update()
            enemy.draw(self.screen)
            if enemy.rect.right < 0:
                self.enemies.remove(enemy)
            if self.player.rect.colliderect(enemy.rect):
                self.game_over = True
                self.save_highscore()

        # Оновлення бонусів
        for bonus in self.bonuses[:]:
            bonus.update()
            bonus.draw(self.screen)
            if bonus.rect.top >= HEIGHT:
                self.bonuses.remove(bonus)
            if self.player.rect.colliderect(bonus.rect):
                self.bonuses.remove(bonus)
                self.scores += 1

        pygame.display.flip()


if __name__ == "__main__":
    game = Game()
    game.run()
