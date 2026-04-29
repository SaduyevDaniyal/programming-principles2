import pygame
from racer import RacerGame, WIDTH, HEIGHT
from ui import Button, draw_center_text, draw_left_text
from persistence import load_settings, save_settings, load_leaderboard


pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSIS3 Racer Game")

font = pygame.font.SysFont("arial", 24)
small_font = pygame.font.SysFont("arial", 18)
big_font = pygame.font.SysFont("arial", 48)
clock = pygame.time.Clock()

settings = load_settings()

state = "name"
username = ""
game = None


def main_menu():
    buttons = {
        "play": Button(300, 220, 200, 50, "Play"),
        "leaderboard": Button(300, 290, 200, 50, "Leaderboard"),
        "settings": Button(300, 360, 200, 50, "Settings"),
        "quit": Button(300, 430, 200, 50, "Quit")
    }
    return buttons


def settings_buttons():
    return {
        "sound": Button(260, 210, 280, 45, "Toggle Sound"),
        "color": Button(260, 275, 280, 45, "Change Car Color"),
        "difficulty": Button(260, 340, 280, 45, "Change Difficulty"),
        "back": Button(260, 430, 280, 45, "Back")
    }


def game_over_buttons():
    return {
        "retry": Button(260, 360, 280, 45, "Retry"),
        "menu": Button(260, 425, 280, 45, "Main Menu")
    }


def leaderboard_buttons():
    return {
        "back": Button(300, 610, 200, 45, "Back")
    }


def start_game():
    global game, state
    game = RacerGame(screen, small_font, big_font, username, settings)
    state = "game"


def draw_name_screen():
    screen.fill((40, 40, 40))
    draw_center_text(screen, "Enter your name", big_font, 220, (255, 255, 255))
    draw_center_text(screen, username + "|", font, 310, (255, 255, 255))
    draw_center_text(screen, "Press Enter to continue", small_font, 370, (255, 255, 255))


def draw_main_menu(buttons):
    screen.fill((40, 120, 40))
    draw_center_text(screen, "TSIS3 RACER", big_font, 140, (255, 255, 255))

    for button in buttons.values():
        button.draw(screen, font)


def draw_settings(buttons):
    screen.fill((50, 50, 80))
    draw_center_text(screen, "SETTINGS", big_font, 120, (255, 255, 255))

    sound = "ON" if settings["sound"] else "OFF"
    draw_center_text(screen, f"Sound: {sound}", font, 170, (255, 255, 255))
    draw_center_text(screen, f"Car color: {settings['car_color']}", font, 190, (255, 255, 255))
    draw_center_text(screen, f"Difficulty: {settings['difficulty']}", font, 405, (255, 255, 255))

    for button in buttons.values():
        button.draw(screen, font)


def draw_leaderboard(buttons):
    screen.fill((30, 30, 30))
    draw_center_text(screen, "LEADERBOARD TOP 10", big_font, 80, (255, 255, 255))

    entries = load_leaderboard()

    y = 150
    if not entries:
        draw_center_text(screen, "No scores yet", font, 220, (255, 255, 255))
    else:
        for index, entry in enumerate(entries, start=1):
            line = f"{index}. {entry['name']}   Score: {entry['score']}   Distance: {entry['distance']}   Coins: {entry['coins']}"
            draw_left_text(screen, line, small_font, 120, y, (255, 255, 255))
            y += 35

    for button in buttons.values():
        button.draw(screen, font)


def draw_game_over(buttons):
    game.draw()

    for button in buttons.values():
        button.draw(screen, font)


def change_color():
    colors = ["blue", "red", "green", "purple"]
    current = settings["car_color"]
    index = colors.index(current) if current in colors else 0
    settings["car_color"] = colors[(index + 1) % len(colors)]
    save_settings(settings)


def change_difficulty():
    levels = ["easy", "normal", "hard"]
    current = settings["difficulty"]
    index = levels.index(current) if current in levels else 1
    settings["difficulty"] = levels[(index + 1) % len(levels)]
    save_settings(settings)


running = True

menu_buttons = main_menu()
set_buttons = settings_buttons()
over_buttons = game_over_buttons()
lead_buttons = leaderboard_buttons()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if state == "name":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if not username:
                        username = "Player"
                    state = "menu"
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                elif event.key == pygame.K_ESCAPE:
                    running = False
                else:
                    if len(username) < 12:
                        username += event.unicode

        elif state == "menu":
            if menu_buttons["play"].clicked(event):
                start_game()
            elif menu_buttons["leaderboard"].clicked(event):
                state = "leaderboard"
            elif menu_buttons["settings"].clicked(event):
                state = "settings"
            elif menu_buttons["quit"].clicked(event):
                running = False

        elif state == "settings":
            if set_buttons["sound"].clicked(event):
                settings["sound"] = not settings["sound"]
                save_settings(settings)
            elif set_buttons["color"].clicked(event):
                change_color()
            elif set_buttons["difficulty"].clicked(event):
                change_difficulty()
            elif set_buttons["back"].clicked(event):
                state = "menu"

        elif state == "leaderboard":
            if lead_buttons["back"].clicked(event):
                state = "menu"

        elif state == "game":
            if game and game.game_over:
                if over_buttons["retry"].clicked(event):
                    start_game()
                elif over_buttons["menu"].clicked(event):
                    state = "menu"

    if state == "name":
        draw_name_screen()

    elif state == "menu":
        draw_main_menu(menu_buttons)

    elif state == "settings":
        draw_settings(set_buttons)

    elif state == "leaderboard":
        draw_leaderboard(lead_buttons)

    elif state == "game":
        if game:
            if not game.game_over:
                game.update()
                game.draw()
            else:
                draw_game_over(over_buttons)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
