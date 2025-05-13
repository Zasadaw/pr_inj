import pygame

def draw_button(screen, text, rect_tuple, color=(150, 150, 150)):
    rect = pygame.Rect(rect_tuple)
    pygame.draw.rect(screen, color, rect)
    draw_text(screen, text, (rect.x + 10, rect.y + 10), 20)
    return rect

def draw_text(screen, text, pos, size=24, color=(0, 0, 0)):
    font = pygame.font.SysFont(None, size)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, pos)

def is_button_clicked(button_rect, pos):
    return button_rect.collidepoint(pos)

# def is_button_pressed(button_rect, pos):
#     return button_rect.collidepoint(pos)