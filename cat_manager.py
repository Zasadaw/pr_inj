import pygame
import json
import os

class Cat:
    def __init__(self, data):
        self.level = data.get("level", 1)
        self.name = data.get("name", "Котик")
        self.rarity = data.get("rarity", "обычные")
        self.max_hp = data.get("max_hp", 100)
        self.current_hp = self.max_hp
        self.image = pygame.image.load(f"images/{data.get('image', 'common_cat.png')}")
        self.image = pygame.transform.scale(self.image, (50, 50))
    
    def upgrade(self):
        self.level += 1
        self.max_hp += 20
        self.current_hp = self.max_hp

class CatManager:
    def __init__(self, game_config):
        self.config = game_config
        self.cats = []
        self.money = 100
        self.food_inventory = 0
        self.medicine_inventory = {}
        if self.config.get("cats"):
            self.cats.append(Cat(self.config["cats"][0]))
        else:
            self.cats.append(Cat({"level": 1, "name": "Котик", "rarity": "обычные", "max_hp": 100, "image": "common_cat.png"}))

    def merge_cats(self, cat1, cat2):
        if cat1.level == cat2.level:
            self.cats.remove(cat1)
            self.cats.remove(cat2)
            new_cat_data = {
                "level": cat1.level + 1,
                "name": f"Котик Lv.{cat1.level + 1}",
                "rarity": "эпические" if cat1.level + 1 >= 3 else "редкие",
                "max_hp": cat1.max_hp + 20,
                "image": "epic_cat.png" if cat1.level + 1 >= 3 else "rare_cat.png"
            }
            self.cats.append(Cat(new_cat_data))
            print(f"Создан новый кот {new_cat_data['name']}!")
