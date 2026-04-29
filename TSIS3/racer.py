import random
import pygame
from persistence import add_score


WIDTH, HEIGHT = 800, 700
ROAD_X = 170
ROAD_WIDTH = 460
LANES = 4
LANE_WIDTH = ROAD_WIDTH // LANES
ROAD_TOP = 0
ROAD_BOTTOM = HEIGHT
FINISH_DISTANCE = 3000

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ROAD = (45, 45, 45)
GRASS = (25, 120, 45)
YELLOW = (230, 210, 40)
RED = (220, 40, 40)
BLUE = (40, 100, 230)
GREEN = (40, 180, 70)
ORANGE = (255, 140, 0)
PURPLE = (150, 60, 180)
CYAN = (0, 200, 220)
GRAY = (120, 120, 120)

CAR_COLORS = {
    "blue": BLUE,
    "red": RED,
    "green": GREEN,
    "purple": PURPLE
}


def lane_center(lane):
    return ROAD_X + lane * LANE_WIDTH + LANE_WIDTH // 2


def rect_safe_from_player(rect, player_rect):
    safe_area = player_rect.inflate(120, 180)
    return not rect.colliderect(safe_area)


class Player:
    def __init__(self, color_name):
        self.w = 45
        self.h = 70
        self.lane = 1
        self.x = lane_center(self.lane) - self.w // 2
        self.y = HEIGHT - 120
        self.speed_x = 8
        self.color = CAR_COLORS.get(color_name, BLUE)
        self.shield = False

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > ROAD_X:
            self.x -= self.speed_x
        if keys[pygame.K_RIGHT] and self.x + self.w < ROAD_X + ROAD_WIDTH:
            self.x += self.speed_x
        if keys[pygame.K_UP] and self.y > 10:
            self.y -= self.speed_x
        if keys[pygame.K_DOWN] and self.y + self.h < HEIGHT:
            self.y += self.speed_x

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)

        if self.shield:
            pygame.draw.circle(screen, CYAN, self.rect.center, 48, 3)


class TrafficCar:
    def __init__(self, speed):
        self.w = 45
        self.h = 70
        self.lane = random.randint(0, LANES - 1)
        self.x = lane_center(self.lane) - self.w // 2
        self.y = -self.h
        self.speed = speed
        self.color = random.choice([RED, ORANGE, PURPLE])

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def update(self):
        self.y += self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)


class Obstacle:
    def __init__(self, kind, speed):
        self.kind = kind
        self.lane = random.randint(0, LANES - 1)
        self.x = lane_center(self.lane) - 25
        self.y = -50
        self.w = 50
        self.h = 35
        self.speed = speed

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def update(self):
        self.y += self.speed

    def draw(self, screen):
        if self.kind == "barrier":
            pygame.draw.rect(screen, RED, self.rect)
            pygame.draw.rect(screen, BLACK, self.rect, 2)

        elif self.kind == "oil":
            pygame.draw.ellipse(screen, BLACK, self.rect)

        elif self.kind == "pothole":
            pygame.draw.ellipse(screen, DARK_BROWN, self.rect)
            pygame.draw.ellipse(screen, BLACK, self.rect, 2)

        elif self.kind == "bump":
            pygame.draw.rect(screen, YELLOW, self.rect)
            pygame.draw.rect(screen, BLACK, self.rect, 2)


DARK_BROWN = (75, 45, 20)


class Coin:
    def __init__(self, speed):
        self.radius = 13
        self.lane = random.randint(0, LANES - 1)
        self.x = lane_center(self.lane)
        self.y = -20
        self.value = random.choice([1, 2, 5])
        self.speed = speed

    @property
    def rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

    def update(self):
        self.y += self.speed

    def draw(self, screen):
        pygame.draw.circle(screen, YELLOW, (self.x, int(self.y)), self.radius)
        pygame.draw.circle(screen, BLACK, (self.x, int(self.y)), self.radius, 2)


class PowerUp:
    def __init__(self, kind, speed):
        self.kind = kind
        self.lane = random.randint(0, LANES - 1)
        self.x = lane_center(self.lane)
        self.y = -30
        self.size = 28
        self.speed = speed
        self.life = 420

    @property
    def rect(self):
        return pygame.Rect(self.x - self.size // 2, self.y - self.size // 2, self.size, self.size)

    def update(self):
        self.y += self.speed
        self.life -= 1

    def draw(self, screen):
        if self.kind == "nitro":
            color = CYAN
            text = "N"
        elif self.kind == "shield":
            color = GREEN
            text = "S"
        else:
            color = ORANGE
            text = "R"

        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)


class MovingBarrier:
    def __init__(self, speed):
        self.w = 80
        self.h = 25
        self.x = ROAD_X + 20
        self.y = -40
        self.speed = speed
        self.dx = 3

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def update(self):
        self.y += self.speed
        self.x += self.dx

        if self.x < ROAD_X or self.x + self.w > ROAD_X + ROAD_WIDTH:
            self.dx *= -1

    def draw(self, screen):
        pygame.draw.rect(screen, RED, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)


class RacerGame:
    def __init__(self, screen, font, big_font, username, settings):
        self.screen = screen
        self.font = font
        self.big_font = big_font
        self.username = username or "Player"
        self.settings = settings

        self.player = Player(settings.get("car_color", "blue"))

        self.traffic = []
        self.obstacles = []
        self.coins = []
        self.powerups = []
        self.events = []

        self.distance = 0
        self.coins_count = 0
        self.score = 0
        self.road_offset = 0

        self.game_over = False
        self.finished = False
        self.saved_score = False

        self.active_power = None
        self.power_timer = 0

        difficulty = settings.get("difficulty", "normal")
        if difficulty == "easy":
            self.base_speed = 4
            self.spawn_multiplier = 0.75
        elif difficulty == "hard":
            self.base_speed = 6
            self.spawn_multiplier = 1.35
        else:
            self.base_speed = 5
            self.spawn_multiplier = 1.0

    def current_speed(self):
        speed = self.base_speed + self.distance // 700
        if self.active_power == "nitro":
            speed += 4
        return speed

    def spawn_chance(self, base):
        scale = 1 + self.distance / 2500
        return base * self.spawn_multiplier * scale

    def safe_spawn(self, obj):
        return rect_safe_from_player(obj.rect, self.player.rect)

    def spawn_objects(self):
        speed = self.current_speed()

        if random.random() < self.spawn_chance(0.018):
            car = TrafficCar(speed + random.randint(1, 3))
            if self.safe_spawn(car):
                self.traffic.append(car)

        if random.random() < self.spawn_chance(0.014):
            kind = random.choice(["barrier", "oil", "pothole", "bump"])
            obs = Obstacle(kind, speed)
            if self.safe_spawn(obs):
                self.obstacles.append(obs)

        if random.random() < 0.025:
            coin = Coin(speed)
            if self.safe_spawn(coin):
                self.coins.append(coin)

        if random.random() < 0.004 and not self.powerups:
            p = PowerUp(random.choice(["nitro", "shield", "repair"]), speed)
            if self.safe_spawn(p):
                self.powerups.append(p)

        if random.random() < self.spawn_chance(0.003):
            event = MovingBarrier(speed)
            if self.safe_spawn(event):
                self.events.append(event)

    def update_power(self):
        if self.active_power == "nitro":
            self.power_timer -= 1
            if self.power_timer <= 0:
                self.active_power = None
                self.power_timer = 0

    def apply_powerup(self, power):
        if self.active_power is not None:
            return

        if power.kind == "nitro":
            self.active_power = "nitro"
            self.power_timer = 240

        elif power.kind == "shield":
            self.active_power = "shield"
            self.player.shield = True

        elif power.kind == "repair":
            if self.obstacles:
                self.obstacles.pop(0)
            self.score += 50

    def handle_collision(self, obj):
        if self.active_power == "shield":
            self.active_power = None
            self.player.shield = False
            return False

        self.game_over = True
        return True

    def update(self):
        if self.game_over:
            return

        keys = pygame.key.get_pressed()
        self.player.move(keys)

        self.distance += self.current_speed() * 0.1
        self.score = self.coins_count * 10 + int(self.distance)

        if self.distance >= FINISH_DISTANCE:
            self.finished = True
            self.game_over = True

        self.road_offset = (self.road_offset + self.current_speed()) % 40

        self.spawn_objects()
        self.update_power()

        for car in self.traffic[:]:
            car.update()
            if car.y > HEIGHT:
                self.traffic.remove(car)
            elif car.rect.colliderect(self.player.rect):
                self.handle_collision(car)

        for obs in self.obstacles[:]:
            obs.update()
            if obs.y > HEIGHT:
                self.obstacles.remove(obs)
            elif obs.rect.colliderect(self.player.rect):
                if obs.kind in ("oil", "bump"):
                    self.player.y += 25
                    self.obstacles.remove(obs)
                else:
                    self.handle_collision(obs)

        for event in self.events[:]:
            event.update()
            if event.y > HEIGHT:
                self.events.remove(event)
            elif event.rect.colliderect(self.player.rect):
                self.handle_collision(event)

        for coin in self.coins[:]:
            coin.update()
            if coin.y > HEIGHT:
                self.coins.remove(coin)
            elif coin.rect.colliderect(self.player.rect):
                self.coins_count += coin.value
                self.score += coin.value * 10
                self.coins.remove(coin)

        for p in self.powerups[:]:
            p.update()
            if p.y > HEIGHT or p.life <= 0:
                self.powerups.remove(p)
            elif p.rect.colliderect(self.player.rect):
                self.apply_powerup(p)
                self.powerups.remove(p)

        if self.game_over and not self.saved_score:
            add_score(self.username, self.score, self.distance, self.coins_count)
            self.saved_score = True

    def draw_road(self):
        self.screen.fill(GRASS)
        pygame.draw.rect(self.screen, ROAD, (ROAD_X, 0, ROAD_WIDTH, HEIGHT))

        pygame.draw.line(self.screen, WHITE, (ROAD_X, 0), (ROAD_X, HEIGHT), 4)
        pygame.draw.line(self.screen, WHITE, (ROAD_X + ROAD_WIDTH, 0), (ROAD_X + ROAD_WIDTH, HEIGHT), 4)

        for lane in range(1, LANES):
            x = ROAD_X + lane * LANE_WIDTH
            for y in range(-40, HEIGHT, 40):
                pygame.draw.line(self.screen, WHITE, (x, y + self.road_offset), (x, y + 20 + self.road_offset), 3)

    def draw_hud(self):
        remaining = max(0, FINISH_DISTANCE - int(self.distance))

        lines = [
            f"Name: {self.username}",
            f"Score: {int(self.score)}",
            f"Coins: {self.coins_count}",
            f"Distance: {int(self.distance)} / {FINISH_DISTANCE}",
            f"Remaining: {remaining}"
        ]

        y = 15
        for line in lines:
            text = self.font.render(line, True, WHITE)
            self.screen.blit(text, (10, y))
            y += 25

        if self.active_power:
            if self.active_power == "nitro":
                seconds = self.power_timer // 60
                power_text = f"Power: Nitro {seconds}s"
            else:
                power_text = "Power: Shield"

            text = self.font.render(power_text, True, YELLOW)
            self.screen.blit(text, (620, 15))
        else:
            text = self.font.render("Power: none", True, WHITE)
            self.screen.blit(text, (620, 15))

    def draw(self):
        self.draw_road()

        for coin in self.coins:
            coin.draw(self.screen)

        for p in self.powerups:
            p.draw(self.screen)

        for obs in self.obstacles:
            obs.draw(self.screen)

        for event in self.events:
            event.draw(self.screen)

        for car in self.traffic:
            car.draw(self.screen)

        self.player.draw(self.screen)
        self.draw_hud()

        if self.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))

            if self.finished:
                title = "FINISH!"
            else:
                title = "GAME OVER"

            label = self.big_font.render(title, True, WHITE)
            rect = label.get_rect(center=(WIDTH // 2, 230))
            self.screen.blit(label, rect)

            summary = f"Score: {int(self.score)}   Distance: {int(self.distance)}   Coins: {self.coins_count}"
            text = self.font.render(summary, True, WHITE)
            text_rect = text.get_rect(center=(WIDTH // 2, 290))
            self.screen.blit(text, text_rect)
