import random
import pygame
from db import save_result, get_personal_best


CELL = 20
WIDTH = 800
HEIGHT = 600
GRID_WIDTH = WIDTH // CELL
GRID_HEIGHT = HEIGHT // CELL

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (40, 40, 40)
RED = (220, 0, 0)
DARK_RED = (120, 0, 0)
BLUE = (0, 120, 255)
YELLOW = (230, 220, 0)
PURPLE = (150, 0, 200)
ORANGE = (255, 140, 0)


class SnakeGame:
    def __init__(self, username, settings):
        self.username = username or "Player"
        self.settings = settings
        self.snake_color = tuple(settings.get("snake_color", [0, 200, 0]))

        self.snake = [(10, 10), (9, 10), (8, 10)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)

        self.score = 0
        self.level = 1
        self.food_eaten = 0
        self.speed = 8

        self.food = None
        self.food_value = 1
        self.food_spawn_time = 0
        self.food_lifetime = 7000

        self.poison = None
        self.powerup = None
        self.powerup_type = None
        self.powerup_spawn_time = 0
        self.powerup_lifetime = 8000

        self.active_power = None
        self.power_end_time = 0
        self.shield = False

        self.obstacles = []
        self.game_over = False
        self.result_saved = False
        self.personal_best = get_personal_best(self.username)

        self.spawn_food()
        self.spawn_poison()

    def occupied(self):
        cells = set(self.snake)
        cells.update(self.obstacles)
        if self.food:
            cells.add(self.food)
        if self.poison:
            cells.add(self.poison)
        if self.powerup:
            cells.add(self.powerup)
        return cells

    def random_empty_cell(self, avoid_head=False):
        occupied = self.occupied()
        head = self.snake[0]

        for _ in range(1000):
            cell = (
                random.randint(1, GRID_WIDTH - 2),
                random.randint(1, GRID_HEIGHT - 2)
            )

            if cell in occupied:
                continue

            if avoid_head and abs(cell[0] - head[0]) + abs(cell[1] - head[1]) < 5:
                continue

            return cell

        return (5, 5)

    def spawn_food(self):
        self.food = self.random_empty_cell()
        self.food_value = random.choice([1, 2, 3])
        self.food_spawn_time = pygame.time.get_ticks()

    def spawn_poison(self):
        if random.random() < 0.6:
            self.poison = self.random_empty_cell()
        else:
            self.poison = None

    def spawn_powerup(self):
        if self.powerup is None and random.random() < 0.02:
            self.powerup = self.random_empty_cell()
            self.powerup_type = random.choice(["speed", "slow", "shield"])
            self.powerup_spawn_time = pygame.time.get_ticks()

    def generate_obstacles(self):
        self.obstacles = []

        if self.level < 3:
            return

        count = min(5 + self.level, 18)
        head = self.snake[0]

        while len(self.obstacles) < count:
            cell = self.random_empty_cell(avoid_head=True)

            near_head = abs(cell[0] - head[0]) + abs(cell[1] - head[1]) <= 2
            if not near_head and cell not in self.obstacles:
                self.obstacles.append(cell)

    def change_direction(self, new_dir):
        opposite = (-self.direction[0], -self.direction[1])
        if new_dir != opposite:
            self.next_direction = new_dir

    def update_power_timer(self):
        now = pygame.time.get_ticks()

        if self.active_power in ("speed", "slow") and now > self.power_end_time:
            self.active_power = None

        if self.powerup and now - self.powerup_spawn_time > self.powerup_lifetime:
            self.powerup = None
            self.powerup_type = None

        if self.food and now - self.food_spawn_time > self.food_lifetime:
            self.spawn_food()

    def current_speed(self):
        base = self.speed + self.level
        if self.active_power == "speed":
            return base + 5
        if self.active_power == "slow":
            return max(4, base - 4)
        return base

    def use_shield_or_die(self):
        if self.shield:
            self.shield = False
            self.active_power = None
            return False

        self.game_over = True
        return True

    def update(self):
        if self.game_over:
            if not self.result_saved:
                save_result(self.username, self.score, self.level)
                self.result_saved = True
            return

        self.update_power_timer()
        self.spawn_powerup()

        self.direction = self.next_direction
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        hit_wall = (
            new_head[0] < 0 or new_head[0] >= GRID_WIDTH
            or new_head[1] < 0 or new_head[1] >= GRID_HEIGHT
        )

        hit_self = new_head in self.snake
        hit_obstacle = new_head in self.obstacles

        if hit_wall or hit_self or hit_obstacle:
            if self.use_shield_or_die():
                return

            new_head = self.snake[0]

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += self.food_value * 10
            self.food_eaten += 1

            if self.food_eaten % 3 == 0:
                self.level += 1
                self.speed += 1
                self.generate_obstacles()

            self.spawn_food()

        elif self.poison and new_head == self.poison:
            for _ in range(2):
                if len(self.snake) > 0:
                    self.snake.pop()

            self.poison = None
            self.spawn_poison()

            if len(self.snake) <= 1:
                self.game_over = True

        elif self.powerup and new_head == self.powerup:
            if self.powerup_type == "speed":
                self.active_power = "speed"
                self.power_end_time = pygame.time.get_ticks() + 5000
            elif self.powerup_type == "slow":
                self.active_power = "slow"
                self.power_end_time = pygame.time.get_ticks() + 5000
            elif self.powerup_type == "shield":
                self.active_power = "shield"
                self.shield = True

            self.powerup = None
            self.powerup_type = None
            self.snake.pop()

        else:
            self.snake.pop()

    def draw_cell(self, screen, cell, color):
        x, y = cell
        rect = pygame.Rect(x * CELL, y * CELL, CELL, CELL)
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, BLACK, rect, 1)

    def draw_grid(self, screen):
        if not self.settings.get("grid", True):
            return

        for x in range(0, WIDTH, CELL):
            pygame.draw.line(screen, (230, 230, 230), (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, CELL):
            pygame.draw.line(screen, (230, 230, 230), (0, y), (WIDTH, y))

    def draw(self, screen, font):
        screen.fill(WHITE)
        self.draw_grid(screen)

        for block in self.obstacles:
            self.draw_cell(screen, block, DARK_GRAY)

        if self.food:
            color = YELLOW if self.food_value == 1 else ORANGE if self.food_value == 2 else BLUE
            self.draw_cell(screen, self.food, color)

        if self.poison:
            self.draw_cell(screen, self.poison, DARK_RED)

        if self.powerup:
            color = PURPLE
            if self.powerup_type == "speed":
                color = BLUE
            elif self.powerup_type == "slow":
                color = ORANGE
            elif self.powerup_type == "shield":
                color = (0, 180, 180)
            self.draw_cell(screen, self.powerup, color)

        for segment in self.snake:
            self.draw_cell(screen, segment, self.snake_color)

        if self.shield:
            head = self.snake[0]
            pygame.draw.circle(screen, (0, 180, 180), (head[0] * CELL + 10, head[1] * CELL + 10), 18, 2)

        hud = f"User: {self.username}   Score: {self.score}   Level: {self.level}   Best: {self.personal_best}"
        text = font.render(hud, True, BLACK)
        screen.blit(text, (10, 10))

        if self.active_power:
            if self.active_power in ("speed", "slow"):
                left = max(0, (self.power_end_time - pygame.time.get_ticks()) // 1000)
                power_text = f"Power: {self.active_power} {left}s"
            else:
                power_text = "Power: shield"
        else:
            power_text = "Power: none"

        text2 = font.render(power_text, True, BLACK)
        screen.blit(text2, (10, 35))
