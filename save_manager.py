"""Local persistence for Rush Runner (Kivy version).

Everything is one JSON file: coins, high score, best distance,
selected character, settings and control preferences. No network,
no account, no cloud. On Android the file lives in the app's
user_data_dir; on desktop it falls back to the working directory.
"""
import json
import os

DEFAULTS = {
    "coins": 0,
    "high_score": 0,
    "best_distance": 0,
    "character": "robo",
    "music": True,
    "sound": True,
    "graphics": "High",
    "control_style": "Touch",
    "language": "English",
    "control_mode": "Touch",
    "sensitivity": "Medium",
    "tilt_offset": 0.0,
}


class SaveManager:
    def __init__(self, path=None):
        if path is None:
            try:
                from kivy.app import App
                app = App.get_running_app()
                base = app.user_data_dir if app else "."
            except Exception:
                base = "."
            path = os.path.join(base, "save.json")
        self.path = path
        self.data = dict(DEFAULTS)
        self.load()

    def load(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            if isinstance(loaded, dict):
                self.data.update(loaded)
        except Exception:
            pass
        return self.data

    def save(self):
        try:
            os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
        except Exception:
            pass

    def get(self, key, default=None):
        return self.data.get(key, DEFAULTS.get(key, default))

    def set(self, key, value):
        self.data[key] = value
        self.save()


CHARACTERS = [
    {"id": "robo", "name": "Robo Runner",
     "desc": "A young hero with unlimited energy!",
     "speed": 1.0, "health": 3, "ability": "Balanced",
     "image": "assets/characters/robo.png"},
    {"id": "female", "name": "Female Runner",
     "desc": "Fast, agile, and fearless on the streets.",
     "speed": 1.1, "health": 2, "ability": "Extra speed",
     "image": "assets/characters/female.png"},
    {"id": "shadow", "name": "Shadow Runner",
     "desc": "Silent, swift, and hard to catch.",
     "speed": 1.05, "health": 2, "ability": "Quick slide",
     "image": "assets/characters/shadow.png"},
    {"id": "panda", "name": "Panda Runner",
     "desc": "Slow but tough — takes an extra hit.",
     "speed": 0.9, "health": 4, "ability": "Extra health",
     "image": "assets/characters/panda.png"},
]


def character_by_id(char_id):
    for c in CHARACTERS:
        if c["id"] == char_id:
            return c
    return CHARACTERS[0]
