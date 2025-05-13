import json
import os

CONFIG_DIR = os.path.join(os.path.dirname(__file__), "config")

def load_json(filename):
    path = os.path.join(CONFIG_DIR, filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def load_all_config():
    cats_config = load_json("cats.json")
    food_config = load_json("food.json")
    medicine_config = load_json("medicine.json")
    return {
        "cats": cats_config.get("cats", []),
        "food": food_config,
        "medicine": medicine_config
    }
