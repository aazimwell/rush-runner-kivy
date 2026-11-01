"""Menu / character / settings / high-score screens for Rush Runner."""
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.image import Image
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.spinner import Spinner
import os

from ui_helpers import gold_button, blue_button, title_label, body_label
from save_manager import CHARACTERS, character_by_id


def _menu_layout(app, title, subtitle=""):
    layout = BoxLayout(orientation="vertical", padding=24, spacing=12)
    layout.add_widget(title_label(title))
    if subtitle:
        layout.add_widget(body_label(subtitle))
    layout.add_widget(Label(size_hint=(1, 1)))  # spacer
    return layout


class MenuScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        app = self.manager.app
        save = app.save
        layout = _menu_layout(app, "RUSH RUNNER", "ENDLESS ADVENTURE")
        layout.add_widget(body_label(
            "Coins: %d   |   Best: %d" % (save.get("coins"),
                                          save.get("high_score"))))
        layout.add_widget(gold_button(
            "▶  PLAY", lambda b: app.start_game()))
        layout.add_widget(blue_button(
            "CHARACTER", lambda b: setattr(self.manager, "current", "character")))
        layout.add_widget(blue_button(
            "SETTINGS", lambda b: setattr(self.manager, "current", "settings")))
        layout.add_widget(blue_button(
            "HIGH SCORE", lambda b: setattr(self.manager, "current", "highscore")))
        layout.add_widget(blue_button(
            "QUIT", lambda b: app.stop()))
        layout.add_widget(Label(size_hint=(1, 1)))
        self.add_widget(layout)


class CharacterScreen(Screen):
    index = 0

    def on_enter(self):
        self.clear_widgets()
        app = self.manager.app
        chars = CHARACTERS
        current = character_by_id(app.save.get("character"))
        self.index = next((i for i, c in enumerate(chars)
                           if c["id"] == current["id"]), 0)
        self._render(app, chars)

    def _render(self, app, chars):
        self.clear_widgets()
        c = chars[self.index]
        layout = BoxLayout(orientation="vertical", padding=24, spacing=10)
        layout.add_widget(title_label("CHARACTER SELECT", 28))
        if os.path.exists(c["image"]):
            layout.add_widget(Image(source=c["image"], size_hint=(1, 0.5)))
        layout.add_widget(Label(text=c["name"], font_size=24, bold=True,
                                color=(1, 1, 1, 1), size_hint=(1, None), height=36))
        layout.add_widget(body_label(c["desc"]))
        layout.add_widget(body_label(
            "Speed: %.2f   Health: %d   Ability: %s"
            % (c["speed"], c["health"], c["ability"])))
        row = BoxLayout(size_hint=(1, None), height=52, spacing=10)
        row.add_widget(blue_button("◀ PREV", lambda b: self._step(app, -1),
                                   size_hint=(0.5, None)))
        row.add_widget(blue_button("NEXT ▶", lambda b: self._step(app, 1),
                                   size_hint=(0.5, None)))
        layout.add_widget(row)
        layout.add_widget(gold_button("✓  SELECT", lambda b: self._select(app, c)))
        layout.add_widget(blue_button(
            "BACK", lambda b: setattr(self.manager, "current", "menu")))
        self.add_widget(layout)

    def _step(self, app, delta):
        self.index = (self.index + len(CHARACTERS) + delta) % len(CHARACTERS)
        self._render(app, CHARACTERS)

    def _select(self, app, char):
        app.save.set("character", char["id"])
        self.manager.current = "menu"


class SettingsScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        app = self.manager.app
        save = app.save
        layout = BoxLayout(orientation="vertical", padding=24, spacing=10)
        layout.add_widget(title_label("SETTINGS", 28))

        def toggle(text, key):
            btn = ToggleButton(text="%s: %s" % (text, "ON" if save.get(key) else "OFF"),
                               state="down" if save.get(key) else "normal",
                               size_hint=(0.9, None), height=48)
            def flip(b):
                save.set(key, b.state == "down")
                b.text = "%s: %s" % (text, "ON" if save.get(key) else "OFF")
            btn.bind(on_press=flip)
            return btn

        layout.add_widget(toggle("Music", "music"))
        layout.add_widget(toggle("Sound Effects", "sound"))

        def spinner(label, key, values):
            row = BoxLayout(size_hint=(1, None), height=48, spacing=8)
            row.add_widget(Label(text=label, size_hint=(0.5, 1)))
            sp = Spinner(text=str(save.get(key)), values=values,
                         size_hint=(0.5, 1))
            sp.bind(text=lambda s, v: save.set(key, v))
            row.add_widget(sp)
            return row

        layout.add_widget(spinner("Graphics Quality", "graphics",
                                  ["Low", "Medium", "High"]))
        layout.add_widget(spinner("Control Style", "control_style",
                                  ["Touch", "Tilt", "Both"]))
        layout.add_widget(spinner("Control Mode", "control_mode",
                                  ["Touch", "Tilt", "Both"]))
        layout.add_widget(spinner("Sensitivity", "sensitivity",
                                  ["Low", "Medium", "High"]))
        layout.add_widget(spinner("Language", "language",
                                  ["English", "Bangla"]))

        def calibrate(b):
            ok = app.tilt.calibrate() if hasattr(app, "tilt") and app.tilt else False
            if ok:
                app.save.set("tilt_offset", app.tilt.tilt_offset)
                b.text = "CALIBRATED ✓"
            else:
                b.text = "SENSOR NOT AVAILABLE"
        layout.add_widget(gold_button("CALIBRATE NOW (TILT)", calibrate))
        layout.add_widget(blue_button(
            "BACK", lambda b: setattr(self.manager, "current", "menu")))
        self.add_widget(layout)


class HighScoreScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        app = self.manager.app
        save = app.save
        layout = BoxLayout(orientation="vertical", padding=24, spacing=12)
        layout.add_widget(title_label("HIGH SCORE", 28))
        layout.add_widget(body_label("Best score: %d" % save.get("high_score")))
        layout.add_widget(body_label("Best distance: %d m" % save.get("best_distance")))
        layout.add_widget(body_label("Total coins: %d" % save.get("coins")))
        layout.add_widget(body_label(
            "Character: %s" % character_by_id(save.get("character"))["name"]))
        layout.add_widget(blue_button(
            "BACK", lambda b: setattr(self.manager, "current", "menu")))
        self.add_widget(layout)
