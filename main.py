# pylint: disable=no-member
"""
Goose Game: Проста гра на Pygame, де гравець-гусак має збирати бонуси та уникати ворогів.
"""
import os
import random
import pygame

pygame.init()

# --- Константи та налаштування ---
WIDTH, HEIGHT = 800, 600
FPS = 60

# Кольори
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Розміри об'єктів
PLAYER_SIZE = (100, 60)
ENEMY_SIZE = (60, 40)
BONUS_SIZE = (40, 40)

# Шрифти
FONT = pygame.font.SysFont("Verdana", 20)
BIG_FONT = pygame.font.SysFont("Verdana", 50, bold=True)

# Файли та шляхи
HIGHSCORE_FILE = "highscore.txt"
# Примітка: Для коректної роботи коду має існувати папка 'assets'
# з 'background.png', 'enemy.png', 'bonus.png' та підпапка 'goose'
# з 'goose1.png' до 'goose5.png'.
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
GOOSE_DIR = os.path.join(ASSETS_DIR, "goose")


# --- Базовий клас об'єктів ---
class GameObject:
    """Базовий клас для всіх ігрових об'єктів (ворогів, бонусів, гравця)."""

    def __init__(self, image, rect, speed):
        """Ініціалізація об'єкта з зображенням, прямокутником та швидкістю."""
        self._image = image
        self._rect = rect
        self._speed = speed

    @property
    def rect(self):
        """Повертає прямокутник об'єкта для перевірки колізій."""
        return self._rect

    def draw(self, surface):
        """Малює об'єкт на заданій поверхні."""
        surface.blit(self._image, self._rect)

    def update(self):
        """
        Оновлює стан об'єкта (зазвичай рух).
        Базовий об'єкт не рухається за замовчуванням.
        """
        # FIX: Прибрано 'pass' для W0107
        pass


# --- Гравець ---
class Player(GameObject):
    """Об'єкт гравця (Гусак), який може рухатися та анімуватися."""

    def __init__(self, images, speed):
        """Ініціалізація гравця з набором зображень для анімації."""
        self._images = images
        self._img_index = 0
        self._speed = speed

        initial_image = images[0]
        initial_rect = initial_image.get_rect(center=(WIDTH // 2, HEIGHT - 70))

        # Виклик конструктора базового класу
        super().__init__(initial_image, initial_rect, speed)

    def move(self, keys):
        """Обробляє рух гравця на основі натискання клавіш."""
        if keys[pygame.K_DOWN] and self._rect.bottom < HEIGHT:
            self._rect.y += self._speed
        if keys[pygame.K_UP] and self._rect.top > 0:
            self._rect.y -= self._speed
        if keys[pygame.K_RIGHT] and self._rect.right < WIDTH:
            self._rect.x += self._speed
        if keys[pygame.K_LEFT] and self._rect.left > 0:
            self._rect.x -= self._speed

    def change_image(self):
        """Змінює зображення гравця для створення анімації."""
        self._img_index = (self._img_index + 1) % len(self._images)
        self._image = self._images[self._img_index]


# --- Вороги ---
class Enemy(GameObject):
    """Об'єкт ворога, що рухається по горизонталі."""

    def update(self):
        """Оновлює позицію ворога, рухаючи його вліво."""
        self._rect.x -= self._speed


# --- Бонуси ---
class Bonus(GameObject):
    """Об'єкт бонусу, що рухається по вертикалі."""

    def update(self):
        """Оновлює позицію бонусу, рухаючи його вниз."""
        self._rect.y += self._speed


# --- Головний клас гри ---
class Game:
    """Головний клас, що керує ігровим циклом, станом та об'єктами."""

    def __init__(self):
        """Ініціалізація гри, завантаження ресурсів та встановлення початкового стану."""
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("GOOSE GAME")
        self.clock = pygame.time.Clock()

        # Фон
        self.bg = pygame.transform.scale(
            pygame.image.load(os.path.join(ASSETS_DIR, "background.png")).convert(),
            (WIDTH, HEIGHT),
        )
        self.bg_x = 0
        self.bg_x2 = self.bg.get_width()
        self.bg_speed = 3

        # Гравець (Зберігаємо список зображень для подальшого скидання)
        self.player_images = [
            pygame.transform.scale(
                pygame.image.load(
                    os.path.join(GOOSE_DIR, f"goose{i}.png")
                ).convert_alpha(),
                PLAYER_SIZE,
            )
            for i in range(1, 6)
        ]
        self.player = Player(self.player_images, speed=10)

        # Вороги та бонуси
        self.enemies = []
        self.bonuses = []

        # Стани гри
        self.is_running = True
        self.game_started = False
        self.game_over = False
        self.scores = 0
        self.high_score = self.load_highscore()

        # Події (Константи)
        # FIX: Перейменовано для C0103
        self.create_enemy_event = pygame.USEREVENT + 1
        pygame.time.set_timer(self.create_enemy_event, 1500)
        self.create_bonus_event = pygame.USEREVENT + 2
        pygame.time.set_timer(self.create_bonus_event, 1500)
        self.change_img_event = pygame.USEREVENT + 3
        pygame.time.set_timer(self.change_img_event, 125)

    # --- Highscore ---
    def load_highscore(self):
        """Завантажує найкращий рахунок з файлу, якщо він існує."""
        if os.path.exists(HIGHSCORE_FILE):
            with open(HIGHSCORE_FILE, "r", encoding="utf-8") as file:
                try:
                    return int(file.read())
                except ValueError:
                    # Повертаємо 0, якщо файл містить невірні дані
                    return 0
        return 0

    def save_highscore(self):
        """Зберігає найкращий рахунок у файл."""
        if self.scores > self.high_score:
            self.high_score = self.scores
            with open(HIGHSCORE_FILE, "w", encoding="utf-8") as file:
                file.write(str(self.high_score))

    # --- Створення ворогів та бонусів ---
    def create_enemy(self):
        """Створює новий об'єкт ворога та додає його до списку."""
        img = pygame.transform.scale(
            pygame.image.load(os.path.join(ASSETS_DIR, "enemy.png")).convert_alpha(),
            ENEMY_SIZE,
        )
        rect = img.get_rect(midtop=(WIDTH, random.randint(0, HEIGHT - ENEMY_SIZE[1])))
        speed = random.randint(4, 6)
        self.enemies.append(Enemy(img, rect, speed))

    def create_bonus(self):
        """Створює новий об'єкт бонусу та додає його до списку."""
        img = pygame.transform.scale(
            pygame.image.load(os.path.join(ASSETS_DIR, "bonus.png")).convert_alpha(),
            BONUS_SIZE,
        )
        rect = img.get_rect(midtop=(random.randint(0, WIDTH - BONUS_SIZE[0]), 0))
        speed = random.randint(4, 6)
        self.bonuses.append(Bonus(img, rect, speed))

    # --- Текст ---
    def draw_text_center(self, text, font_obj, color, y):
        """Малює текст по центру екрана на заданій висоті."""
        surf = font_obj.render(text, True, color)
        self.screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, y))

    # --- Стартовий екран ---
    def draw_start_screen(self):
        """Малює стартовий екран гри."""
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
        """Малює екран Game Over."""
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
        """Скидає стан гри до початкового."""
        self.enemies.clear()
        self.bonuses.clear()
        self.scores = 0
        self.player = Player(self.player_images, speed=10)
        self.bg_x = 0
        self.bg_x2 = self.bg.get_width()
        self.game_over = False

    # --- Основний цикл ---
    def run(self):
        """Головний цикл гри, що керує подіями та станом."""
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
        """Обробляє ігрову логіку, рух об'єктів та колізії."""
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            # FIX: Використання нових імен подій
            elif event.type == self.create_enemy_event:
                self.create_enemy()
            elif event.type == self.create_bonus_event:
                self.create_bonus()
            elif event.type == self.change_img_event:
                self.player.change_image()

        # Рух фону
        self.bg_x -= self.bg_speed
        self.bg_x2 -= self.bg_speed
        if self.bg_x < -self.bg.get_width():
            self.bg_x = self.bg.get_width()
        if self.bg_x2 < -self.bg.get_width():
            self.bg_x2 = self.bg.get_width()

        # Малюємо фон та гравця
        self.screen.blit(self.bg, (self.bg_x, 0))
        self.screen.blit(self.bg, (self.bg_x2, 0))
        self.player.move(keys)
        self.player.draw(self.screen)

        # Відображення рахунку
        score_surf = FONT.render(str(self.scores), True, RED)
        high_surf = FONT.render(f"High: {self.high_score}", True, GREEN)
        self.screen.blit(score_surf, (WIDTH - 50, 20))
        self.screen.blit(high_surf, (20, 20))

        # Оновлення ворогів та колізії
        for enemy in self.enemies[:]:
            enemy.update()
            enemy.draw(self.screen)
            if enemy.rect.right < 0:
                self.enemies.remove(enemy)
            if self.player.rect.colliderect(enemy.rect):
                self.game_over = True
                self.save_highscore()

        # Оновлення бонусів та колізії
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
