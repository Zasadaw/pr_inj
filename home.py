import pygame
import ui_helpers as ui

def run(screen, cat_manager):
    clock = pygame.time.Clock()
    running = True
    selected_cats = []

    while running:
        screen.fill((200, 230, 255))
        ui.draw_text(screen, "Дом – объединение котов", (250, 10), 30)

        y = 100
        cat_buttons = []
        for cat in cat_manager.cats:
            btn = ui.draw_button(screen, f"{cat.name} (Lv.{cat.level})", (100, y, 400, 50))
            cat_buttons.append((cat, btn))
            screen.blit(cat.image, (550, y))
            y += 60

        merge_btn = ui.draw_button(screen, "Объединить", (100, y + 20, 200, 50))
        back_btn = ui.draw_button(screen, "Назад", (320, y + 20, 200, 50))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for cat, btn in cat_buttons:
                    if ui.is_button_clicked(btn, pos):
                        if cat in selected_cats:
                            selected_cats.remove(cat)
                        elif len(selected_cats) < 2:
                            selected_cats.append(cat)
                if ui.is_button_clicked(merge_btn, pos) and len(selected_cats) == 2:
                    cat_manager.merge_cats(selected_cats[0], selected_cats[1])
                    selected_cats.clear()
                if ui.is_button_clicked(back_btn, pos):
                    running = False

        pygame.display.flip()
        clock.tick(30)
