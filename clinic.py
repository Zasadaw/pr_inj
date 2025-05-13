import pygame
import ui_helpers as ui

def run(screen, cat_manager):
    clock = pygame.time.Clock()
    running = True
    while running:
        screen.fill((200, 255, 255))
        ui.draw_text(screen, "Клиника – лечение котов", (300, 10), 30)
        # Отрисовываем список котов с информацией об их HP
        y = 100
        cat_buttons = []
        for cat in cat_manager.cats:
            btn = ui.draw_button(screen, f"{cat.name}  HP: {cat.current_hp}/{cat.max_hp}", (100, y, 400, 40))
            cat_buttons.append((cat, btn))
            y += 50
        back_btn = ui.draw_button(screen, "Назад", (100, y + 20, 200, 50))
        ui.draw_text(screen, f"Ваши лекарства: {cat_manager.medicine_inventory}", (10, 10), 24)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                # При нажатии на кота пытаемся применить лекарство (если оно есть)
                for cat, btn in cat_buttons:
                    if ui.is_button_clicked(btn, pos):
                        if cat_manager.use_medicine(cat):
                            print(f"{cat.name} вылечен!")
                        else:
                            print("Нет лекарства в инвентаре!")
                if ui.is_button_clicked(back_btn, pos):
                    running = False
        pygame.display.flip()
        clock.tick(30)
