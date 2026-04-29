import pygame


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (190, 190, 190)
DARK_GRAY = (80, 80, 80)


class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text

    def draw(self, screen, font):
        mouse = pygame.mouse.get_pos()
        color = (220, 220, 220) if self.rect.collidepoint(mouse) else (180, 180, 180)

        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)

        label = font.render(self.text, True, BLACK)
        label_rect = label.get_rect(center=self.rect.center)
        screen.blit(label, label_rect)

    def clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)


def draw_center_text(screen, text, font, y, color=BLACK):
    label = font.render(text, True, color)
    rect = label.get_rect(center=(screen.get_width() // 2, y))
    screen.blit(label, rect)


def draw_left_text(screen, text, font, x, y, color=BLACK):
    label = font.render(text, True, color)
    screen.blit(label, (x, y))
