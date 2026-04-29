import pygame
from datetime import datetime
from collections import deque
from tools import Tool


pygame.init()

WIDTH, HEIGHT = 1000, 700
TOOLBAR_HEIGHT = 80

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSIS2 Paint Application")

clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 18)
text_font = pygame.font.SysFont("arial", 28)

canvas = pygame.Surface((WIDTH, HEIGHT - TOOLBAR_HEIGHT))
canvas.fill((255, 255, 255))

current_tool = Tool.PENCIL
current_color = (0, 0, 0)
brush_size = 5

drawing = False
start_pos = None
last_pos = None

text_mode = False
text_pos = None
text_value = ""

colors = [
    (0, 0, 0),
    (255, 0, 0),
    (0, 150, 0),
    (0, 0, 255),
    (255, 165, 0),
    (128, 0, 128),
    (255, 255, 255)
]

tool_buttons = [
    ("Pencil", Tool.PENCIL),
    ("Line", Tool.LINE),
    ("Rect", Tool.RECTANGLE),
    ("Circle", Tool.CIRCLE),
    ("Eraser", Tool.ERASER),
    ("Fill", Tool.FILL),
    ("Text", Tool.TEXT),
    ("Square", Tool.SQUARE),
    ("R.Tri", Tool.RIGHT_TRIANGLE),
    ("Eq.Tri", Tool.EQUILATERAL_TRIANGLE),
    ("Rhombus", Tool.RHOMBUS),
]


def to_canvas_pos(pos):
    x, y = pos
    return x, y - TOOLBAR_HEIGHT


def inside_canvas(pos):
    x, y = pos
    return 0 <= x < WIDTH and TOOLBAR_HEIGHT <= y < HEIGHT


def draw_button(rect, text, selected=False):
    color = (190, 190, 190) if selected else (225, 225, 225)
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, (0, 0, 0), rect, 1)

    label = font.render(text, True, (0, 0, 0))
    label_rect = label.get_rect(center=rect.center)
    screen.blit(label, label_rect)


def draw_toolbar():
    pygame.draw.rect(screen, (235, 235, 235), (0, 0, WIDTH, TOOLBAR_HEIGHT))

    x = 10
    y = 10
    for name, tool in tool_buttons:
        rect = pygame.Rect(x, y, 75, 25)
        draw_button(rect, name, current_tool == tool)
        x += 80

    x = 10
    y = 45
    for color in colors:
        rect = pygame.Rect(x, y, 30, 25)
        pygame.draw.rect(screen, color, rect)
        border = 3 if color == current_color else 1
        pygame.draw.rect(screen, (0, 0, 0), rect, border)
        x += 38

    info = "Brush: " + str(brush_size) + " px   1=small  2=medium  3=large   Ctrl+S=save"
    size_text = font.render(info, True, (0, 0, 0))
    screen.blit(size_text, (300, 48))


def handle_toolbar_click(pos):
    global current_tool, current_color

    x = 10
    y = 10
    for name, tool in tool_buttons:
        rect = pygame.Rect(x, y, 75, 25)
        if rect.collidepoint(pos):
            current_tool = tool
            return True
        x += 80

    x = 10
    y = 45
    for color in colors:
        rect = pygame.Rect(x, y, 30, 25)
        if rect.collidepoint(pos):
            current_color = color
            return True
        x += 38

    return False


def draw_shape(surface, tool, start, end, color, width):
    x1, y1 = start
    x2, y2 = end

    if tool == Tool.LINE:
        pygame.draw.line(surface, color, start, end, width)

    elif tool == Tool.RECTANGLE:
        rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
        pygame.draw.rect(surface, color, rect, width)

    elif tool == Tool.CIRCLE:
        radius = int(((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5)
        pygame.draw.circle(surface, color, start, radius, width)

    elif tool == Tool.SQUARE:
        side = min(abs(x2 - x1), abs(y2 - y1))
        sx = 1 if x2 >= x1 else -1
        sy = 1 if y2 >= y1 else -1
        rect = pygame.Rect(x1, y1, side * sx, side * sy)
        rect.normalize()
        pygame.draw.rect(surface, color, rect, width)

    elif tool == Tool.RIGHT_TRIANGLE:
        points = [(x1, y1), (x1, y2), (x2, y2)]
        pygame.draw.polygon(surface, color, points, width)

    elif tool == Tool.EQUILATERAL_TRIANGLE:
        base_mid_x = (x1 + x2) // 2
        points = [(base_mid_x, y1), (x1, y2), (x2, y2)]
        pygame.draw.polygon(surface, color, points, width)

    elif tool == Tool.RHOMBUS:
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        points = [
            (center_x, y1),
            (x2, center_y),
            (center_x, y2),
            (x1, center_y)
        ]
        pygame.draw.polygon(surface, color, points, width)


def flood_fill(surface, start, fill_color):
    width, height = surface.get_size()
    x, y = start

    if not (0 <= x < width and 0 <= y < height):
        return

    target_color = surface.get_at((x, y))
    new_color = pygame.Color(*fill_color)

    if target_color == new_color:
        return

    queue = deque()
    queue.append((x, y))

    while queue:
        px, py = queue.popleft()

        if not (0 <= px < width and 0 <= py < height):
            continue

        if surface.get_at((px, py)) != target_color:
            continue

        surface.set_at((px, py), new_color)

        queue.append((px + 1, py))
        queue.append((px - 1, py))
        queue.append((px, py + 1))
        queue.append((px, py - 1))


def save_canvas():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = "paint_" + timestamp + ".png"
    pygame.image.save(canvas, filename)
    print("Saved:", filename)


def start_text(pos):
    global text_mode, text_pos, text_value
    text_mode = True
    text_pos = pos
    text_value = ""


def confirm_text():
    global text_mode, text_pos, text_value
    if text_mode and text_value:
        rendered = text_font.render(text_value, True, current_color)
        canvas.blit(rendered, text_pos)
    text_mode = False
    text_pos = None
    text_value = ""


def cancel_text():
    global text_mode, text_pos, text_value
    text_mode = False
    text_pos = None
    text_value = ""


running = True

while running:
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                save_canvas()

            elif event.key == pygame.K_1:
                brush_size = 2
            elif event.key == pygame.K_2:
                brush_size = 5
            elif event.key == pygame.K_3:
                brush_size = 10

            elif text_mode:
                if event.key == pygame.K_RETURN:
                    confirm_text()
                elif event.key == pygame.K_ESCAPE:
                    cancel_text()
                elif event.key == pygame.K_BACKSPACE:
                    text_value = text_value[:-1]
                else:
                    text_value += event.unicode

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if event.pos[1] < TOOLBAR_HEIGHT:
                handle_toolbar_click(event.pos)
                continue

            if inside_canvas(event.pos):
                canvas_pos = to_canvas_pos(event.pos)

                if current_tool == Tool.FILL:
                    flood_fill(canvas, canvas_pos, current_color)

                elif current_tool == Tool.TEXT:
                    start_text(canvas_pos)

                else:
                    drawing = True
                    start_pos = canvas_pos
                    last_pos = canvas_pos

        elif event.type == pygame.MOUSEMOTION:
            if drawing and inside_canvas(event.pos):
                canvas_pos = to_canvas_pos(event.pos)

                if current_tool == Tool.PENCIL:
                    pygame.draw.line(canvas, current_color, last_pos, canvas_pos, brush_size)
                    last_pos = canvas_pos

                elif current_tool == Tool.ERASER:
                    pygame.draw.line(canvas, (255, 255, 255), last_pos, canvas_pos, brush_size)
                    last_pos = canvas_pos

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if drawing and inside_canvas(event.pos):
                end_pos = to_canvas_pos(event.pos)

                if current_tool not in (Tool.PENCIL, Tool.ERASER):
                    draw_shape(canvas, current_tool, start_pos, end_pos, current_color, brush_size)

            drawing = False
            start_pos = None
            last_pos = None

    screen.fill((255, 255, 255))
    draw_toolbar()
    screen.blit(canvas, (0, TOOLBAR_HEIGHT))

    if drawing and start_pos and inside_canvas(mouse_pos):
        preview = canvas.copy()
        end_pos = to_canvas_pos(mouse_pos)

        if current_tool not in (Tool.PENCIL, Tool.ERASER):
            draw_shape(preview, current_tool, start_pos, end_pos, current_color, brush_size)

        screen.blit(preview, (0, TOOLBAR_HEIGHT))

    if text_mode and text_pos:
        rendered = text_font.render(text_value + "|", True, current_color)
        screen.blit(rendered, (text_pos[0], text_pos[1] + TOOLBAR_HEIGHT))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
