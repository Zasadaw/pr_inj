import pygame
import random
import math
import os
import json
from time import time

pygame.init()

# ========================
# Настройки окна и цветов
# ========================
WIDTH, HEIGHT = 1500, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Котоферма")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (100, 200, 100)
RED = (255, 0, 0)

# ========================
# Шрифт и текст
# ========================
font = pygame.font.SysFont("Arial", 14)

def draw_text(text, x, y, color=BLACK):
    rendered = font.render(text, True, color)
    screen.blit(rendered, (x, y))
    return rendered.get_width(), rendered.get_height()

# ========================
# Загрузка изображений
# ========================
background_img = pygame.image.load("assets/background/farm_map.png")
food_icon = pygame.image.load("assets/icons/food.png")
toy_icon = pygame.image.load("assets/icons/toy.png")
medicine_icon = pygame.image.load("assets/icons/medicine.png")
cap_icon = pygame.image.load("assets/icons/cap.png")
pillow_icon = pygame.image.load("assets/icons/pillow.png")

ACTION_ICON_SIZE = (64, 64)  # Размер иконок действий
food_icon = pygame.transform.scale(food_icon, ACTION_ICON_SIZE)
toy_icon = pygame.transform.scale(toy_icon, ACTION_ICON_SIZE)
medicine_icon = pygame.transform.scale(medicine_icon, ACTION_ICON_SIZE)
cap_icon = pygame.transform.scale(cap_icon, ACTION_ICON_SIZE)
pillow_icon = pygame.transform.scale(pillow_icon, ACTION_ICON_SIZE)

# Прямоугольники для кликов по иконкам действий (внизу экрана)
action_icons = {
    "еда": {"rect": pygame.Rect(50, 600, *ACTION_ICON_SIZE), "icon": food_icon, "offset": 0, "speed": 0.05},
    "игрушка": {"rect": pygame.Rect(120, 600, *ACTION_ICON_SIZE), "icon": toy_icon, "offset": 0.5, "speed": 0.07},
    "лекарство": {"rect": pygame.Rect(190, 600, *ACTION_ICON_SIZE), "icon": medicine_icon, "offset": 1.0, "speed": 0.06},
    "шапочка": {"rect": pygame.Rect(260, 600, *ACTION_ICON_SIZE), "icon": cap_icon, "offset": 1.5, "speed": 0.04},
    "подушка": {"rect": pygame.Rect(330, 600, *ACTION_ICON_SIZE), "icon": pillow_icon, "offset": 2.0, "speed": 0.04}
}

# --- Кнопки покупки и продажи ---
BUTTON_WIDTH = 100
BUTTON_HEIGHT = 30
button_y_start = 10
button_spacing = 40

action_buttons_rects = {
    "купить_еда": pygame.Rect(10, button_y_start + i * button_spacing, BUTTON_WIDTH, BUTTON_HEIGHT) for i, key in enumerate(["купить_еда", "купить_лекарство", "купить_шапочка", "купить_подушка", "купить_кота", "продать_кота", "сохранить", "загрузить"])
}

# То же через ручное создание:
action_buttons_rects = {
    "купить_еда": pygame.Rect(10, 170, BUTTON_WIDTH, BUTTON_HEIGHT),
    "купить_лекарство": pygame.Rect(10, 210, BUTTON_WIDTH, BUTTON_HEIGHT),
    "купить_шапочка": pygame.Rect(10, 250, BUTTON_WIDTH, BUTTON_HEIGHT),
    "купить_подушка": pygame.Rect(10, 290, BUTTON_WIDTH, BUTTON_HEIGHT),
    "купить_кота": pygame.Rect(10, 330, BUTTON_WIDTH, BUTTON_HEIGHT),
    "продать_кота": pygame.Rect(10, 370, BUTTON_WIDTH, BUTTON_HEIGHT),
    "сохранить": pygame.Rect(10, 410, BUTTON_WIDTH, BUTTON_HEIGHT),
    "загрузить": pygame.Rect(10, 450, BUTTON_WIDTH, BUTTON_HEIGHT),
}

# --- Кнопки громкости ---
VOLUME_X = 1300
VOLUME_Y = 540

volume_label_rect = pygame.Rect(VOLUME_X, VOLUME_Y - 20, 150, 20)
volume_up_rect = pygame.Rect(VOLUME_X + 50, VOLUME_Y, 30, 30)
volume_down_rect = pygame.Rect(VOLUME_X + 90, VOLUME_Y, 30, 30)

# ========================
# Таймер суток
# ========================
DAY_DURATION_MS = 3 * 60 * 1000  # 3 минуты
day_started_at = pygame.time.get_ticks()
show_day_message = False
message_timer = 0

# ========================
# Воспроизведение звука
# ========================
last_sound_time = {}

def play_sound(sound_file, cooldown=4):
    current_time = time()
    sound_path = f"assets/sounds/{sound_file}"
    if os.path.exists(sound_path):
        if sound_file not in last_sound_time or current_time - last_sound_time[sound_file] >= cooldown:
            sound = pygame.mixer.Sound(sound_path)
            sound.play()
            last_sound_time[sound_file] = current_time

# ========================
# Фоновая музыка
# ========================
try:
    pygame.mixer.init()
    pygame.mixer.music.load("assets/sounds/background_music.mp3")
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)
except Exception as e:
    print(f"Ошибка загрузки музыки: {e}")

# ========================
# Класс Cat — кот в игре
# ========================
class Cat:
    def __init__(self, name, cat_type="обычный"):
        self.name = name
        self.type = cat_type
        self.level = 1
        self.exp = 0
        self.happiness = 100
        self.health = 100
        self.hunger = 100
        self.x = random.randint(100, 400)
        self.y = random.randint(100, 400)
        self.dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.frames = self.load_animation_frames()
        self.frame_index = 0
        self.animation_timer = 0
        self.skills = {
            "игривость": 1,
            "чистоплотность": 1,
            "ум": 1
        }
        self.accessories = []

    def load_animation_frames(self):
        if self.type == "обычный":
            return [pygame.image.load("assets/cats/ordinary_idle.png")]
        elif self.type == "редкий":
            return [pygame.image.load("assets/cats/rare_sleeping.png")]
        elif self.type == "легендарный":
            return [pygame.image.load("assets/cats/legendary_eating.png")]
        elif self.name in ["Генрий", "Борис", "Люся", "Мурзик"]:
            return [pygame.image.load(f"assets/cats/unique/{self.name.lower()}.png")]

    def animate(self):
        self.animation_timer += 1
        if self.animation_timer % 10 == 0:
            self.frame_index = (self.frame_index + 1) % len(self.frames)

    def feed(self):
        if game.inventory["еда"] > 0:
            self.hunger = min(100, self.hunger + 20)
            game.inventory["еда"] -= 1
            play_sound("eat.mp3")
            game.add_log(f"{self.name} поел.")

    def play(self):
        if self.hunger > 10:
            self.happiness = min(100, self.happiness + 15)
            self.hunger = max(0, self.hunger - 10)
            self.health = max(0, self.health - 10)
            play_sound("meow.mp3")
            self.add_exp(15)
            game.add_log(f"{self.name} поиграл.")

    def heal(self):
        if game.inventory["лекарство"] > 0:
            self.health = min(100, self.health + 20)
            game.inventory["лекарство"] -= 1
            play_sound("heal.mp3")
            game.add_log(f"{self.name} пролечился.")

    def add_exp(self, amount):
        self.exp += amount
        while self.exp >= self.level * 100:
            self.level_up()

    def level_up(self):
        self.exp -= self.level * 100
        self.level += 1
        self.skills[random.choice(list(self.skills.keys()))] += 1
        game.add_log(f"{self.name} достиг уровня {self.level}!")

    def get_price(self):
        base_price = CAT_TYPES_PRICE[self.type]
        price = int(base_price * (1 + 0.5 * (self.level - 1)))
        return price

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "happiness": self.happiness,
            "health": self.health,
            "hunger": self.hunger,
            "level": self.level,
            "exp": self.exp,
            "x": self.x,
            "y": self.y,
            "skills": self.skills,
            "accessories": self.accessories
        }

    @classmethod
    def from_dict(cls, data):
        cat = cls(data["name"], data["type"])
        cat.happiness = data["happiness"]
        cat.health = data["health"]
        cat.hunger = data["hunger"]
        cat.level = data["level"]
        cat.exp = data["exp"]
        cat.x = data["x"]
        cat.y = data["y"]
        cat.skills = data["skills"]
        cat.accessories = data.get("accessories", [])
        return cat


# ========================
# Параметры котов
# ========================
CAT_TYPES_PRICE = {
    "обычный": 50,
    "редкий": 100,
    "легендарный": 200
}

UNIQUE_CATS = ["Генрий", "Борис", "Люся", "Мурзик"]

CAT_PRICE_INCREMENT = {
    "обычный": 10,
    "редкий": 20,
    "легендарный": 30
}

ACCESSORY_DATA = {
    "шапочка": {"price": 20, "effect": {"happiness": 10}},
    "подушка": {"price": 30, "effect": {"health": 10}}
}

# ========================
# Игровая логика
# ========================
class Game:
    SAVES_DIR = "saves"

    def __init__(self):
        self.cats = [
            Cat("Рыжик", "обычный"),
        ]
        self.day = 1
        self.money = 1000
        self.log_messages = []
        self.inventory = {
            "еда": 5,
            "лекарство": 2,
            "аксессуары": {
                "шапочка": 1,
                "подушка": 1
            }
        }

    def next_day(self):
        global day_started_at
        for cat in self.cats:
            cat.happiness = max(0, cat.happiness - 20)
            cat.health = max(0, cat.health - 20)
            cat.hunger = max(0, cat.hunger - 20)
        self.day += 1
        self.add_log("Прошли сутки.")
        day_started_at = pygame.time.get_ticks()  # Перезапуск таймера

    def buy_cat(self):
        cat_type = random.choices(
            ["обычный", "редкий", "легендарный"],
            weights=[6, 3, 1],
            k=1
        )[0]

        avg_level = sum(cat.level for cat in self.cats) / len(self.cats) if self.cats else 1
        price = int(CAT_TYPES_PRICE[cat_type] * (1 + 0.5 * (avg_level - 1)))

        if self.money >= price:
            self.money -= price
            unique_name = random.choice(UNIQUE_CATS) if random.random() < 0.2 else f"Котик {len(game.cats)+1}"
            self.cats.append(Cat(unique_name, cat_type))
            self.add_log(f"Вы купили нового котика: {unique_name}")
            return f"Вы купили {cat_type} котика по имени {unique_name}."
        else:
            return "Недостаточно денег."

    def sell_cat(self, index):
        if 0 <= index < len(self.cats):
            price = int(30 * (1 + 0.5 * self.cats[index].level))
            self.money += price
            removed = self.cats.pop(index)
            self.add_log(f"Вы продали {removed.name} за {price} монет.")
            return f"Вы продали {removed.name} за {price} монет."
        else:
            return "Неверный номер котика."

    def save_game(self, slot=1):
        os.makedirs(self.SAVES_DIR, exist_ok=True)
        data = {
            "day": self.day,
            "money": self.money,
            "cats": [cat.to_dict() for cat in self.cats],
            "inventory": self.inventory
        }
        with open(f"{self.SAVES_DIR}/slot_{slot}.json", "w") as f:
            json.dump(data, f, indent=4)
        self.add_log(f"Игра сохранена в слот {slot}.")
        return f"Сохранение {slot} создано!"

    def load_game(self, slot=1):
        try:
            with open(f"{self.SAVES_DIR}/slot_{slot}.json", "r") as f:
                data = json.load(f)
            self.day = data["day"]
            self.money = data["money"]
            self.cats = [Cat.from_dict(cat_data) for cat_data in data["cats"]]
            self.inventory = data["inventory"]
            self.add_log(f"Загружено сохранение {slot}.")
            return f"Слот {slot} загружен."
        except Exception as e:
            return f"Ошибка загрузки: {e}"

    def add_log(self, msg):
        self.log_messages.insert(0, f"[День {self.day}] {msg}")
        if len(self.log_messages) > 5:
            self.log_messages.pop()


game = Game()
selected_cat = game.cats[0] if game.cats else None
running = True
clock = pygame.time.Clock()
show_day_message = False
message_timer = 0
stat_window_pos = [WIDTH - 260, 10]  # Статистика справа сверху
dragging_stat_window = False
drag_offset_x = drag_offset_y = 0

# ========================
# Основной игровой цикл
# ========================
while running:
    current_time = pygame.time.get_ticks()
    time_passed = current_time - day_started_at
    screen_width, screen_height = pygame.display.get_surface().get_size()

    screen.fill(WHITE)
    scaled_background = pygame.transform.scale(background_img, (screen_width, screen_height))
    screen.blit(scaled_background, (0, 0))

    # --- Обработка дней ---
    time_left = max(0, DAY_DURATION_MS - time_passed)
    minutes = time_left // 60000
    seconds = (time_left // 1000) % 60
    draw_text(f"Время до конца суток: {minutes:02d}:{seconds:02d}", 10, 20)

    if time_passed >= DAY_DURATION_MS and not show_day_message:
        game.next_day()
        show_day_message = True
        message_timer = current_time

    if show_day_message:
        draw_text("❗ Прошли сутки!", 10, 40, RED)
        if current_time - message_timer > 3000:
            show_day_message = False

    # --- Лог действий ---
    LOG_LINES = 5
    log_x = WIDTH - 260
    log_y = HEIGHT - 150
    log_width = 250
    log_height = 200

    pygame.draw.rect(screen, BLACK, (log_x, log_y, log_width, log_height))  # Чёрный фон под логом
    pygame.draw.rect(screen, GREEN, (log_x, log_y, log_width, log_height), 3)

    line_y = log_y + 10
    for msg in game.log_messages[:LOG_LINES]:
        draw_text(msg, log_x + 10, line_y, RED)
        line_y += 20

    # --- Кнопки действий ---
    for key, rect in action_buttons_rects.items():
        pygame.draw.rect(screen, RED, rect)
        text = key.replace("_", " ").capitalize()
        text_w, text_h = draw_text(text, 0, 0)
        text_x = rect.x + (rect.width - text_w) // 2
        text_y = rect.y + (rect.height - text_h) // 2
        draw_text(text, text_x, text_y)

    # --- Кнопки Volume ---
    draw_text("Volume", volume_label_rect.x + 5, volume_label_rect.y, BLACK)
    pygame.draw.rect(screen, GREEN, volume_up_rect)
    pygame.draw.rect(screen, GREEN, volume_down_rect)
    draw_text("+", volume_up_rect.x + 10, volume_up_rect.y + 5)
    draw_text("-", volume_down_rect.x + 10, volume_down_rect.y + 5)

    # --- Статистика выбранного кота ---
    if selected_cat is None and game.cats:
        selected_cat = game.cats[0]

    if selected_cat:
        stat_window_rect = pygame.Rect(stat_window_pos[0], stat_window_pos[1], 250, 200)
        pygame.draw.rect(screen, WHITE, stat_window_rect)
        pygame.draw.rect(screen, GREEN, stat_window_rect, 2)

        lines = [
            f"Имя: {selected_cat.name}",
            f"Тип: {selected_cat.type}",
            f"Уровень: {selected_cat.level}",
            f"Здоровье: {selected_cat.health}",
            f"Настроение: {selected_cat.happiness}",
            f"Голод: {selected_cat.hunger}",
            f"Опыт: {selected_cat.exp} / {selected_cat.level * 100}",
            f"Цена: {selected_cat.get_price()} монет",
            f"Надето: {', '.join(selected_cat.accessories) or 'ничего'}"
        ]

        skill_y = stat_window_pos[1] + 10
        for line in lines:
            draw_text(line, stat_window_pos[0] + 10, skill_y)
            skill_y += 20

    # --- Отрисовка иконок действий с анимацией ---
    for key, data in action_icons.items():
        rect = data["rect"]
        icon = data["icon"]
        offset = data["offset"]
        speed = data["speed"]

        y_offset = int(math.sin(offset) * 10)
        data["offset"] += speed
        screen.blit(icon, (rect.x, rect.y + y_offset))
        pygame.draw.rect(screen, GREEN, rect, 2)

        text = key.capitalize()
        text_w, text_h = draw_text(text, 0, 0)
        text_x = rect.x + (rect.width - text_w) // 2
        text_y = rect.bottom + 5
        draw_text(text, text_x, text_y)

    # --- Инвентарь ---
    draw_text(f"Еды: {game.inventory['еда']}", 10, 60)
    draw_text(f"Лекарств: {game.inventory['лекарство']}", 10, 80)
    draw_text(f"Шапочек: {game.inventory['аксессуары']['шапочка']}", 10, 100)
    draw_text(f"Подушек: {game.inventory['аксессуары']['подушка']}", 10, 120)

    # --- Отображение котов ---
    for cat in game.cats:
        cat.animate()
        original = cat.frames[cat.frame_index]
        width = int(original.get_width() / 3 * 0.65)
        height = int(original.get_height() / 3 * 0.65)
        scaled_image = pygame.transform.scale(original, (width, height))
        screen.blit(scaled_image, (cat.x, cat.y))

    # --- GAME OVER ---
    if not game.cats:
        game_over_font = pygame.font.SysFont("Arial", 48)
        game_over_text = game_over_font.render("GAME OVER", True, RED)
        screen.blit(game_over_text, (WIDTH // 2 - 100, HEIGHT // 2 - 30))
        pygame.display.flip()
        pygame.time.wait(5000)  # Ждём 5 секунд перед выходом
        running = False

    # --- Обработка событий ---
    event_list = pygame.event.get()
    for event in event_list:
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos

            # Нажатие на кнопки действий
            for key, rect in action_buttons_rects.items():
                if rect.collidepoint(x, y):
                    if key == "купить_еда":
                        if game.money >= 10:
                            game.money -= 10
                            game.inventory["еда"] += 1
                            game.add_log("Купили еду.")
                    elif key == "купить_лекарство":
                        if game.money >= 20:
                            game.money -= 20
                            game.inventory["лекарство"] += 1
                            game.add_log("Купили лекарство.")
                    elif key == "купить_шапочка":
                        if game.money >= 20:
                            game.money -= 20
                            game.inventory["аксессуары"]["шапочка"] += 1
                            game.add_log("Купили шапочку.")
                    elif key == "купить_подушка":
                        if game.money >= 30:
                            game.money -= 30
                            game.inventory["аксессуары"]["подушка"] += 1
                            game.add_log("Купили подушку.")
                    elif key == "купить_кота":
                        msg = game.buy_cat()
                        game.add_log(msg)
                    elif key == "продать_кота":
                        if selected_cat and len(game.cats) > 1:
                            index = game.cats.index(selected_cat)
                            msg = game.sell_cat(index)
                            game.add_log(msg)
                            selected_cat = game.cats[0] if game.cats else None
                    elif key == "сохранить":
                        game.save_game(1)
                    elif key == "загрузить":
                        game.load_game(1)

            # Нажатие на иконки действий
            for key, data in action_icons.items():
                rect = data["rect"]
                if rect.collidepoint(x, y):
                    if key == "еда" and selected_cat:
                        selected_cat.feed()
                    elif key == "игрушка" and selected_cat:
                        selected_cat.play()
                    elif key == "лекарство" and selected_cat:
                        selected_cat.heal()
                    elif key == "шапочка" and selected_cat:
                        if game.inventory["аксессуары"]["шапочка"] > 0:
                            selected_cat.accessories.append("шапочка")
                            game.inventory["аксессуары"]["шапочка"] -= 1
                            game.add_log(f"{selected_cat.name} надел шапочку.")
                    elif key == "подушка" and selected_cat:
                        if game.inventory["аксессуары"]["подушка"] > 0:
                            selected_cat.accessories.append("подушка")
                            game.inventory["аксессуары"]["подушка"] -= 1
                            game.add_log(f"{selected_cat.name} получил подушку.")

            # Выбор кота мышкой
            if event.button == 1:
                for cat in reversed(game.cats):
                    original = cat.frames[cat.frame_index]
                    width = int(original.get_width() / 3 * 0.65)
                    height = int(original.get_height() / 3 * 0.65)
                    cat_rect = pygame.Rect(cat.x, cat.y, width, height)
                    if cat_rect.collidepoint(x, y):
                        selected_cat = cat
                        cat.dragging = True
                        cat.drag_offset_x = x - cat.x
                        cat.drag_offset_y = y - cat.y
                        break

        elif event.type == pygame.MOUSEBUTTONUP:
            for cat in game.cats:
                cat.dragging = False
            dragging_stat_window = False

        elif event.type == pygame.MOUSEMOTION:
            for cat in game.cats:
                if cat.dragging:
                    cat.x = event.pos[0] - cat.drag_offset_x
                    cat.y = event.pos[1] - cat.drag_offset_y

    # --- Перетаскивание окна статистики ---
    stat_window_rect = pygame.Rect(stat_window_pos[0], stat_window_pos[1], 250, 200)
    for event in event_list:
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if stat_window_rect.collidepoint(x, y):
                dragging_stat_window = True
                drag_offset_x = x - stat_window_pos[0]
                drag_offset_y = y - stat_window_pos[1]
        elif event.type == pygame.MOUSEBUTTONUP:
            dragging_stat_window = False
        elif event.type == pygame.MOUSEMOTION:
            if dragging_stat_window:
                stat_window_pos[0] = event.pos[0] - drag_offset_x
                stat_window_pos[1] = event.pos[1] - drag_offset_y

    # --- Обработка громкости ---
    for event in event_list:
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if volume_up_rect.collidepoint(x, y):
                current_vol = pygame.mixer.music.get_volume()
                pygame.mixer.music.set_volume(min(current_vol + 0.1, 1.0))
                game.add_log("Громкость увеличена.")
            elif volume_down_rect.collidepoint(x, y):
                current_vol = pygame.mixer.music.get_volume()
                pygame.mixer.music.set_volume(max(current_vol - 0.1, 0.0))
                game.add_log("Громкость уменьшена.")

    # --- Обновление экрана ---
    pygame.display.flip()
    clock.tick(60)

pygame.quit()