import pygame
import ui_helpers as ui


def run(screen, cat_manager):
    clock = pygame.time.Clock()
    running = True
    while running:
        screen.fill((220, 220, 220))
        ui.draw_text(screen, "Магазин", (350, 10), 30)
        buy_cat_btn = ui.draw_button(screen, f"Купить кота (цена {cat_manager.prices['cat']})", (100, 100, 300, 50))
        buy_food_btn = ui.draw_button(screen, f"Купить еду (цена {cat_manager.prices['food']})", (100, 170, 300, 50))
        buy_med_btn = ui.draw_button(screen, "Купить лекарство", (100, 240, 300, 50))
        back_btn = ui.draw_button(screen, "Назад", (100, 310, 300, 50))
        
        ui.draw_text(screen, f"Деньги: {cat_manager.money}", (10, 10), 24)
        ui.draw_text(screen, f"Еда: {cat_manager.food_inventory}", (10, 40), 24)
        ui.draw_text(screen, f"Лекарства: {cat_manager.medicine_inventory}", (10, 70), 24)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if ui.is_button_clicked(buy_cat_btn, pos):
                    if cat_manager.money >= cat_manager.prices['cat']:
                        cat_manager.money -= cat_manager.prices['cat']
                        cat_manager.add_cat()
                        print("Кот куплен!")
                    else:
                        print("Недостаточно денег для покупки кота!")
                elif ui.is_button_clicked(buy_food_btn, pos):
                    if cat_manager.money >= cat_manager.prices['food']:
                        cat_manager.money -= cat_manager.prices['food']
                        cat_manager.food_inventory += 1
                        print("Куплена еда!")
                    else:
                        print("Недостаточно денег для покупки еды!")
                elif ui.is_button_clicked(buy_med_btn, pos):
                    med = cat_manager.medicine_config.get("medicines", [])[0]
                    if cat_manager.money >= med["price"]:
                        cat_manager.money -= med["price"]
                        name = med["name"]
                        cat_manager.medicine_inventory[name] = cat_manager.medicine_inventory.get(name, 0) + 1
                        print(f"Куплено лекарство: {name}!")
                    else:
                        print("Недостаточно денег для покупки лекарства!")
                elif ui.is_button_clicked(back_btn, pos):
                    running = False
        pygame.display.flip()
        clock.tick(30)