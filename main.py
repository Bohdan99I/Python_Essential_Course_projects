# pylint: disable=no-member
import pygame
import random
import os

pygame.init()

WIDTH, HEIGHT = 800, 600
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

PLAYER_SIZE = (80, 50)
ENEMY_SIZE = (50, 30)
BONUS_SIZE = (30, 30)

FONT = pygame.font.SysFont("Arial", 36)
HIGHSCORE_FILE = "highscore.txt"


class GameObject:
    """Base class for all objects"""

    def __init__(self, image, rect, speed):
        self._image = image
        self._rect = rect
        self._speed = speed

    def draw(self, surface):
        surface.blit(self._image, self._rect)

    def update(self):
        raise NotImplementedError


class Player(GameObject):
    """Player-controlled goose"""

    def __init__(self, images, speed):
        self._images = images
        self._img_index = 0
        rect = images[0].get_rect(center=(WIDTH // 2, HEIGHT - 70))
        super().__init__(images[0], rect, speed)

    @property
    def images(self):
        return self._images

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


class Enemy(GameObject):
    """Enemy object"""

    def update(self):
        self._rect = self._rect.move(-self._speed, 0)


class Bonus(GameObject):
    """Bonus object"""

    def update(self):
        self._rect = self._rect.move(0, self._speed)


class Game:
    """Main game class"""

    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Goose Game")

        self.clock = pygame.time.Clock()
        self.bg = pygame.transform.scale(
            pygame.image.load("background.png"), (WIDTH, HEIGHT)
        )

        goose_images = [
            pygame.transform.scale(pygame.image.load("goose1.png"), PLAYER_SIZE),
            pygame.transform.scale(pygame.image.load("goose2.png"), PLAYER_SIZE),
        ]
        self.player = Player(goose_images, speed=10)

        self.enemies = []
        self.bonuses = []
        self.scores = 0
        self.high_score = self.load_highscore()
        self.game_started = False
        self.game_over = False

        pygame.time.set_timer(pygame.USEREVENT + 1, 1500)
        pygame.time.set_timer(pygame.USEREVENT + 2, 2500)
        pygame.time.set_timer(pygame.USEREVENT + 3, 200)

    def run(self):
        """Main loop"""
        while True:
            self.clock.tick(FPS)
            self.handle_gameplay()

    def handle_gameplay(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.save_highscore()
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if not self.game_started:
                    self.game_started = True
                elif self.game_over and event.key == pygame.K_RETURN:
                    self.reset_game()
            if (
                event.type == pygame.USEREVENT + 1
                and self.game_started
                and not self.game_over
            ):
                self.create_enemy()
            if (
                event.type == pygame.USEREVENT + 2
                and self.game_started
                and not self.game_over
            ):
                self.create_bonus()
            if (
                event.type == pygame.USEREVENT + 3
                and self.game_started
                and not self.game_over
            ):
                self.player.change_image()

        self.screen.blit(self.bg, (0, 0))

        if not self.game_started:
            self.draw_start_screen()
        elif self.game_over:
            self.draw_game_over()
        else:
            keys = pygame.key.get_pressed()
            self.player.move(keys)

            for enemy in self.enemies[:]:
                enemy.update()
                if enemy._rect.right < 0:
                    self.enemies.remove(enemy)

            for bonus in self.bonuses[:]:
                bonus.update()
                if bonus._rect.top > HEIGHT:
                    self.bonuses.remove(bonus)

            for enemy in self.enemies:
                if self.player._rect.colliderect(enemy._rect):
                    self.game_over = True
                    if self.scores > self.high_score:
                        self.high_score = self.scores
                        self.save_highscore()

            for bonus in self.bonuses[:]:
                if self.player._rect.colliderect(bonus._rect):
                    self.scores += 1
                    self.bonuses.remove(bonus)

            self.player.draw(self.screen)
            for enemy in self.enemies:
                enemy.draw(self.screen)
            for bonus in self.bonuses:
                bonus.draw(self.screen)

            score_text = FONT.render(f"Score: {self.scores}", True, WHITE)
            self.screen.blit(score_text, (10, 10))

            high_score_text = FONT.render(
                f"High Score: {self.high_score}", True, YELLOW
            )
            self.screen.blit(high_score_text, (10, 50))

        pygame.display.flip()

    def create_enemy(self):
        enemy_img = pygame.transform.scale(pygame.image.load("enemy.png"), ENEMY_SIZE)
        enemy_rect = pygame.Rect(WIDTH, random.randint(50, HEIGHT - 50), *ENEMY_SIZE)
        self.enemies.append(Enemy(enemy_img, enemy_rect, speed=random.randint(3, 6)))

    def create_bonus(self):
        bonus_img = pygame.transform.scale(pygame.image.load("bonus.png"), BONUS_SIZE)
        bonus_rect = pygame.Rect(
            random.randint(50, WIDTH - 50), -BONUS_SIZE[1], *BONUS_SIZE
        )
        self.bonuses.append(Bonus(bonus_img, bonus_rect, speed=random.randint(2, 5)))

    def draw_text_center(self, text, color, y_offset=0):
        label = FONT.render(text, True, color)
        rect = label.get_rect(center=(WIDTH // 2, HEIGHT // 2 + y_offset))
        self.screen.blit(label, rect)

    def draw_start_screen(self):
        self.draw_text_center("Press any key to start", WHITE)

    def draw_game_over(self):
        self.draw_text_center("GAME OVER", RED, -50)
        self.draw_text_center(f"Your Score: {self.scores}", WHITE, 0)
        self.draw_text_center(f"High Score: {self.high_score}", YELLOW, 50)
        self.draw_text_center("Press Enter to Restart", GREEN, 100)

    def reset_game(self):
        self.player = Player(self.player.images, speed=10)
        self.enemies = []
        self.bonuses = []
        self.scores = 0
        self.game_over = False

    def load_highscore(self):
        if os.path.exists(HIGHSCORE_FILE):
            with open(HIGHSCORE_FILE, "r", encoding="utf-8") as f:
                return int(f.read().strip())
        return 0

    def save_highscore(self):
        with open(HIGHSCORE_FILE, "w", encoding="utf-8") as f:
            f.write(str(self.high_score))


if __name__ == "__main__":
    Game().run()
