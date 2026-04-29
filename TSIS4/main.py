import json
import pygame
from pathlib import Path

from db import create_tables, get_top_scores
from game import SnakeGame, WIDTH, HEIGHT


pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSIS4 Snake Game")

clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 22)
small_font = pygame.font.SysFont("arial", 18)
big_font = pygame.font.SysFont("arial", 46)

SETTINGS_FILE = Path("settings.json")

DEFAULT_SETTINGS = {
    "snake_color": [0, 200, 0],
    "grid": True,
    "sound": False
}


def load_settings():
    if not SETTINGS_FILE.exists():
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()

    with open(SETTINGS_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    settings = DEFAULT_SETTINGS.copy()
    settings.update(data)
    return settings


def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
        json.dump(settings, file, indent=4)


class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text

    def draw(self, screen):
        mouse = pygame.mouse.get_pos()
        color = (220, 220, 220) if self.rect.collidepoint(mouse) else (180, 180, 180)

        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)

        label = font.render(self.text, True, (0, 0, 0))
        label_rect = label.get_rect(center=self.rect.center)
        screen.blit(label, label_rect)

    def clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)


def center_text(text, y, fnt=font, color=(0, 0, 0)):
    label = fnt.render(text, True, color)
    rect = label.get_rect(center=(WIDTH // 2, y))
    screen.blit(label, rect)


def left_text(text, x, y, fnt=small_font, color=(0, 0, 0)):
    label = fnt.render(text, True, color)
    screen.blit(label, (x, y))


settings = load_settings()

try:
    create_tables()
    db_ok = True
except Exception as error:
    print("Database error:", error)
    db_ok = False

state = "menu"
username = ""
typing_name = True
game = None

menu_buttons = {
    "play": Button(300, 210, 200, 45, "Play"),
    "leaderboard": Button(300, 270, 200, 45, "Leaderboard"),
    "settings": Button(300, 330, 200, 45, "Settings"),
    "quit": Button(300, 390, 200, 45, "Quit")
}

settings_buttons = {
    "grid": Button(270, 210, 260, 45, "Toggle Grid"),
    "sound": Button(270, 270, 260, 45, "Toggle Sound"),
    "color": Button(270, 330, 260, 45, "Change Color"),
    "save": Button(270, 430, 260, 45, "Save & Back")
}

leaderboard_back = Button(300, 530, 200, 45, "Back")

gameover_buttons = {
    "retry": Button(270, 390, 260, 45, "Retry"),
    "menu": Button(270, 450, 260, 45, "Main Menu")
}


def draw_menu():
    screen.fill((235, 235, 235))
    center_text("TSIS4 SNAKE", 90, big_font)

    center_text("Username:", 145)
    pygame.draw.rect(screen, (255, 255, 255), (270, 165, 260, 35))
    pygame.draw.rect(screen, (0, 0, 0), (270, 165, 260, 35), 2)
    left_text(username + "|", 280, 173, font)

    if not db_ok:
        center_text("DB not connected. Check database.ini", 505, small_font, (200, 0, 0))

    for button in menu_buttons.values():
        button.draw(screen)


def draw_settings():
    screen.fill((230, 230, 250))
    center_text("SETTINGS", 90, big_font)

    center_text(f"Grid: {settings['grid']}", 160)
    center_text(f"Sound: {settings['sound']}", 185)
    center_text(f"Snake color: {settings['snake_color']}", 395)

    for button in settings_buttons.values():
        button.draw(screen)


def draw_leaderboard():
    screen.fill((245, 245, 245))
    center_text("LEADERBOARD TOP 10", 70, big_font)

    entries = get_top_scores() if db_ok else []

    if not entries:
        center_text("No scores yet or database not connected", 160)
    else:
        y = 130
        left_text("Rank   Name        Score   Level   Date", 130, 105, font)
        for index, row in enumerate(entries, start=1):
            name, score, level, date = row
            line = f"{index:<5} {name:<10} {score:<7} {level:<7} {date}"
            left_text(line, 130, y, small_font)
            y += 35

    leaderboard_back.draw(screen)


def draw_game_over():
    if game:
        game.draw(screen, small_font)

    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(190)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    center_text("GAME OVER", 170, big_font, (255, 255, 255))

    if game:
        center_text(f"Score: {game.score}", 240, font, (255, 255, 255))
        center_text(f"Level reached: {game.level}", 275, font, (255, 255, 255))
        center_text(f"Personal best: {game.personal_best}", 310, font, (255, 255, 255))

    for button in gameover_buttons.values():
        button.draw(screen)


def start_game():
    global game, state
    name = username.strip() or "Player"
    game = SnakeGame(name, settings)
    state = "game"


def change_color():
    colors = [
        [0, 200, 0],
        [0, 100, 255],
        [220, 0, 0],
        [160, 0, 200],
        [255, 140, 0]
    ]

    current = settings["snake_color"]

    try:
        index = colors.index(current)
    except ValueError:
        index = 0

    settings["snake_color"] = colors[(index + 1) % len(colors)]


running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if state == "menu":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                elif event.key == pygame.K_RETURN:
                    start_game()
                else:
                    if len(username) < 12:
                        username += event.unicode

            if menu_buttons["play"].clicked(event):
                start_game()
            elif menu_buttons["leaderboard"].clicked(event):
                state = "leaderboard"
            elif menu_buttons["settings"].clicked(event):
                state = "settings"
            elif menu_buttons["quit"].clicked(event):
                running = False

        elif state == "settings":
            if settings_buttons["grid"].clicked(event):
                settings["grid"] = not settings["grid"]
            elif settings_buttons["sound"].clicked(event):
                settings["sound"] = not settings["sound"]
            elif settings_buttons["color"].clicked(event):
                change_color()
            elif settings_buttons["save"].clicked(event):
                save_settings(settings)
                state = "menu"

        elif state == "leaderboard":
            if leaderboard_back.clicked(event):
                state = "menu"

        elif state == "game":
            if event.type == pygame.KEYDOWN and game and not game.game_over:
                if event.key == pygame.K_UP:
                    game.change_direction((0, -1))
                elif event.key == pygame.K_DOWN:
                    game.change_direction((0, 1))
                elif event.key == pygame.K_LEFT:
                    game.change_direction((-1, 0))
                elif event.key == pygame.K_RIGHT:
                    game.change_direction((1, 0))

            if game and game.game_over:
                if gameover_buttons["retry"].clicked(event):
                    start_game()
                elif gameover_buttons["menu"].clicked(event):
                    state = "menu"

    if state == "menu":
        draw_menu()

    elif state == "settings":
        draw_settings()

    elif state == "leaderboard":
        draw_leaderboard()

    elif state == "game":
        if game:
            game.update()

            if game.game_over:
                draw_game_over()
            else:
                game.draw(screen, small_font)

    pygame.display.flip()

    if state == "game" and game and not game.game_over:
        clock.tick(game.current_speed())
    else:
        clock.tick(60)

pygame.quit()
