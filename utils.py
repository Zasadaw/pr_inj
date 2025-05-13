# utils.py
import pygame
import json
import os

# Путь к папке с конфигурациями
CONFIG_DIR = os.path.join(os.getcwd(), "config")
IMAGE_DIR = os.path.join(os.getcwd(), "images")

def load_json(filename):
    path = os.path.join(CONFIG_DIR, filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_json(data, filename):
    path = os.path.join(CONFIG_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Загрузка основных конфигураций
hp_config = load_json("hp_config.json")
price_config = load_json("Price.json")
medicine_config = load_json("MedicinePrice.json")
progress_file = os.path.join(CONFIG_DIR, "progress.json")

RARITIES = ["обычные", "редкие", "эпические", "легендарные"]
RARITY_TO_IMG = {
    "обычные": "common",
    "редкие": "rare",
    "эпические": "epic",
    "легендарные": "legendary"
}

def load_cat_image(level, rarity):
    rarity_str = RARITY_TO_IMG.get(rarity, "common")
    filename = f"{level}_{rarity_str}.png"
    path = os.path.join(IMAGE_DIR, filename)
    if os.path.exists(path):
        return pygame.image.load(path)
    return None

class Cat:
    def __init__(self, data, position):
        self.level = data.get("level", 1)
        self.name = data.get("name", "Кот")
        self.rarity = data.get("rarity", "обычные")
        self.coin_interval = data.get("coin_interval", 5)
        self.coin_amount = data.get("coin_amount", 1)
        self.position = position  # (x, y)
        self.rect = pygame.Rect(position[0], position[1], 50, 50)
        self.image = load_cat_image(self.level, self.rarity)
        # Максимальное здоровье (на основе конфигурации)
        base_hp = hp_config.get(self.rarity, {}).get("max_hp", 100)
        self.max_hp = base_hp + (self.level - 1) * 10
        self.current_hp = self.max_hp
        now = pygame.time.get_ticks()
        self.last_coin_time = now
        self.last_feed_time = now
        self.last_wash_time = now
        self.last_feed_hurt_time = now
        self.last_wash_hurt_time = now
        self.dragging = False

    def update(self, current_time):
        earned = 0
        if (current_time - self.last_coin_time) >= self.coin_interval * 1000:
            self.last_coin_time = current_time
            earned = self.coin_amount
        # (Здесь можно добавить логику снижения HP, если не кормить/не мыть)
        return earned

    def update_image(self):
        self.image = load_cat_image(self.level, self.rarity)

    def draw(self, screen, sleeping=False):
        if self.image:
            img = self.image.copy()
            if sleeping:
                dark = pygame.Surface(img.get_size()).convert_alpha()
                dark.fill((0, 0, 0, 150))
                img.blit(dark, (0, 0))
            screen.blit(img, self.rect.topleft)
        else:
            color = {
                "обычные": (200, 200, 200),
                "редкие": (150, 200, 250),
                "эпические": (250, 200, 150),
                "легендарные": (250, 150, 150)
            }.get(self.rarity, (200, 200, 200))
            pygame.draw.rect(screen, color, self.rect)
        # Отображение имени при наведении мышью
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            font = pygame.font.SysFont(None, 20)
            text = font.render(self.name, True, (0, 0, 0))
            screen.blit(text, (self.rect.x, self.rect.y - 20))
        # Отображение HP
        hp_text = pygame.font.SysFont(None, 16).render(f"{self.current_hp}/{self.max_hp}", True, (255,0,0))
        screen.blit(hp_text, (self.rect.x, self.rect.y + self.rect.height))

def merge_cats(cat1, cat2):
    if cat1.level == cat2.level and cat1.rarity == cat2.rarity:
        idx = RARITIES.index(cat1.rarity)
        if idx < len(RARITIES) - 1:
            new_rarity = "редкие" if cat1.rarity == "обычные" else RARITIES[idx + 1]
        else:
            new_rarity = RARITIES[-1]
        cat2.rarity = new_rarity
        cat2.update_image()
        return True
    return False

def load_progress():
    if os.path.exists(progress_file):
        with open(progress_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        money = data.get("money", 0)
        cats_data = data.get("cats", [])
        cats = []
        for cdata in cats_data:
            pos = tuple(cdata.get("position", (50, 150)))
            cat = Cat(cdata, pos)
            cat.current_hp = cdata.get("current_hp", cat.max_hp)
            now = pygame.time.get_ticks()
            cat.last_coin_time = now
            cat.last_feed_time = now
            cat.last_wash_time = now
            cat.last_feed_hurt_time = now
            cat.last_wash_hurt_time = now
            cats.append(cat)
        food_inventory = data.get("food_inventory", 0)
        medicine_inventory = data.get("medicine_inventory", {})
        return money, cats, food_inventory, medicine_inventory
    else:
        cat = Cat({
            "level": 1,
            "name": "Котик",
            "rarity": "обычные",
            "coin_interval": 5,
            "coin_amount": 1
        }, (50, 150))
        now = pygame.time.get_ticks()
        cat.last_feed_time = now
        cat.last_wash_time = now
        cat.last_feed_hurt_time = now
        cat.last_wash_hurt_time = now
        return 0, [cat], 0, {}

def save_progress(money, cats, food_inventory, medicine_inventory):
    data = {
        "money": money,
        "cats": [{
            "level": cat.level,
            "name": cat.name,
            "rarity": cat.rarity,
            "coin_interval": cat.coin_interval,
            "coin_amount": cat.coin_amount,
            "position": cat.position,
            "current_hp": cat.current_hp
        } for cat in cats],
        "food_inventory": food_inventory,
        "medicine_inventory": medicine_inventory
    }
    with open(progress_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
