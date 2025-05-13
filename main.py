import pygame
import sys
import json
import os


# Функции сохранения и загрузки прогресса
def load_progress():
    if os.path.exists("Progress.json"):
        with open("Progress.json", "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {}


def save_progress(progress):
    with open("Progress.json", "w", encoding="utf-8") as f:
        json.dump(progress, f, indent=4, ensure_ascii=False)


# Загрузка изображений котов (40 изображений: 10 уровней * 4 редкости)
def load_cat_images(screen_width, screen_height):
    cat_images = {}
    rarities = ['common', 'rare', 'epic', 'legendary']
    # Пример: размер изображения равен 15% ширины и 15% высоты окна (можно менять коэффициенты)
    img_width = int(screen_width * 0.15)
    img_height = int(screen_height * 0.15)
    size = (img_width, img_height)
    
    for level in range(1, 11):
        for rarity in rarities:
            path = f"images/cats/cat_{level}_{rarity}.png"
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.scale(img, size)
                cat_images[(level, rarity)] = img
            else:
                print(f"Изображение не найдено: {path}")
    return cat_images


# Класс кнопки с фоном и полупрозрачным интерфейсом
class Button:
    def __init__(self, x, y, w, h, text, button_bg_img):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.button_bg_img = button_bg_img  # Фоновое изображение кнопки
        self.surface = pygame.Surface((w, h), pygame.SRCALPHA)
        self.surface.fill((0, 0, 0, 150))  # Полупрозрачный чёрный (альфа = 150)
    
    def draw(self, screen, font):
        if self.button_bg_img:
            screen.blit(self.button_bg_img, self.rect)
        screen.blit(self.surface, self.rect.topleft)
        text_surf = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)


def main_menu(screen, clock, screen_width, screen_height):
    background = pygame.image.load("images/background.jpg").convert()
    background = pygame.transform.scale(background, (screen_width, screen_height))
    
    button_bg_img = pygame.image.load("images/button_bg.jpg").convert()
    button_width, button_height = int(screen_width * 0.25), int(screen_height * 0.1)
    button_bg_img = pygame.transform.scale(button_bg_img, (button_width, button_height))
    
    font = pygame.font.SysFont("Arial", int(screen_height * 0.04))
    
    continue_button = Button(screen_width // 2 - button_width // 2, screen_height // 2 - button_height - 10,
                             button_width, button_height, "Продолжить игру", button_bg_img)
    new_game_button = Button(screen_width // 2 - button_width // 2, screen_height // 2 + 10,
                             button_width, button_height, "Начать заново", button_bg_img)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                if continue_button.rect.collidepoint(mouse_pos):
                    progress = load_progress()
                    print("Продолжаем игру с прогрессом:", progress)
                    return "continue"
                elif new_game_button.rect.collidepoint(mouse_pos):
                    progress = {}  # Начальное состояние
                    save_progress(progress)
                    print("Начинаем новую игру.")
                    return "new"
        
        screen.blit(background, (0, 0))
        continue_button.draw(screen, font)
        new_game_button.draw(screen, font)
        
        pygame.display.flip()
        clock.tick(60)


# Пример игрового цикла, где отображается один из котов (для демонстрации работы загрузки изображений)
def game_loop(mode, screen, clock, cat_images, screen_width, screen_height):
    # Для примера выберем уровень 3 и редкость "epic"
    current_cat = cat_images.get((3, "epic"))
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        screen.fill((50, 50, 50))
        if current_cat:
            # Центрируем изображение на экране
            img_rect = current_cat.get_rect(center=(screen_width // 2, screen_height // 2))
            screen.blit(current_cat, img_rect)
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()


def main():
    pygame.init()
    
    # Определяем размеры окна адаптивно относительно экрана пользователя (80% от текущего разрешения)
    display_info = pygame.display.Info()
    screen_width = int(display_info.current_w * 0.8)
    screen_height = int(display_info.current_h * 0.8)
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
    pygame.display.set_caption("Моя игра")
    
    clock = pygame.time.Clock()
    
    # Загружаем изображения котов
    cat_images = load_cat_images(screen_width, screen_height)
    
    mode = main_menu(screen, clock, screen_width, screen_height)
    game_loop(mode, screen, clock, cat_images, screen_width, screen_height)


if __name__ == "__main__":
    main()
