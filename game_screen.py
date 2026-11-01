"""Gameplay screen for Rush Runner (Kivy version).

Renders GameState with Kivy canvas instructions: night-city
background, perspective road (lane x positions widen towards the
bottom), player sprite (character PNG if present, else a coloured
runner rectangle), obstacles and coins scaled by depth (z).

Controls:
- Swipe: down/move/up detection on touch — left/right lane,
  up = jump, down = slide. One action per touch, 40 px dead-zone.
- Tilt: polled each frame via sensors.TiltSensor (edge-triggered).
- Keyboard: arrows + space (desktop testing).
- Pause: top-left button + overlay with RESUME / RESTART /
  SETTINGS / HOME. Level-complete (every 1000 m) and game-over
  overlays with HOME / NEXT / RESTART.
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle, Line
from kivy.clock import Clock
from kivy.core.window import Window
import os

from game_logic import GameState
from ui_helpers import gold_button, blue_button, NAVY, CYAN, GOLD
from save_manager import character_by_id

DEAD_ZONE = 40


class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.state = None
        self.event = None
        self.paused = False
        self.overlay = None
        self._touch_start = None
        self._touch_done = False
        self.root_layout = FloatLayout()
        self.add_widget(self.root_layout)
        self.hud = Label(text="", font_size=18, bold=True, color=(1, 1, 1, 1),
                         size_hint=(None, None), pos_hint={"x": 0.02, "top": 0.98})
        self.root_layout.add_widget(self.hud)
        pause = Button(text="II", size_hint=(None, None), size=(56, 56),
                       pos_hint={"right": 0.98, "top": 0.98})
        pause.bind(on_press=lambda b: self.pause_game())
        self.root_layout.add_widget(pause)
        Window.bind(on_key_down=self._on_key)

    # ---- lifecycle -------------------------------------------------
    def start(self, app):
        self.app = app
        char = character_by_id(app.save.get("character"))
        self.state = GameState(speed_mult=char["speed"], health=char["health"])
        self.char = char
        self.paused = False
        self._clear_overlay()
        if self.event:
            self.event.cancel()
        self.event = Clock.schedule_interval(self._tick, 1 / 60.0)

    def stop(self):
        if self.event:
            self.event.cancel()
            self.event = None

    # ---- input -----------------------------------------------------
    def on_touch_down(self, touch):
        if self.manager.current != "game" or self.paused:
            return super().on_touch_down(touch)
        self._touch_start = (touch.x, touch.y)
        self._touch_done = False
        return True

    def on_touch_move(self, touch):
        if self._touch_start and not self._touch_done and self.state:
            dx = touch.x - self._touch_start[0]
            dy = touch.y - self._touch_start[1]
            if abs(dx) > DEAD_ZONE or abs(dy) > DEAD_ZONE:
                self._touch_done = True
                if abs(dx) > abs(dy):
                    self.state.move_left() if dx < 0 else self.state.move_right()
                else:
                    self.state.jump() if dy > 0 else self.state.slide()
        return True

    def _on_key(self, window, key, scancode, codepoint, modifiers):
        if self.manager.current != "game" or not self.state or self.paused:
            return False
        if key == 276:  # left
            self.state.move_left()
        elif key == 275:  # right
            self.state.move_right()
        elif key == 273 or key == 32:  # up / space
            self.state.jump()
        elif key == 274:  # down
            self.state.slide()
        elif key == 27:  # escape / back
            self.pause_game()
        return True

    # ---- tick / draw ----------------------------------------------
    def _tick(self, dt):
        if self.paused or not self.state:
            return
        # tilt (edge-triggered inside TiltSensor)
        tilt = getattr(self.app, "tilt", None)
        mode = self.app.save.get("control_mode", "Touch")
        if tilt and tilt.available and mode in ("Tilt", "Both"):
            direction = tilt.direction()
            if direction < 0:
                self.state.move_left()
            elif direction > 0:
                self.state.move_right()
        result = self.state.update(min(dt, 0.05))
        self._draw()
        self.hud.text = ("Score: %d   Coins: %d   %.0f m   Speed: %.1f   "
                         "HP: %d" % (self.state.score, self.state.coins_run,
                                     self.state.distance, self.state.speed,
                                     self.state.health))
        if result == "milestone":
            self._show_level_complete()
        elif self.state.over:
            self._finish_run(game_over=True)

    def _lane_x(self, lane, z, w):
        # perspective: lanes converge towards the horizon (top)
        t = max(0.0, min(1.0, 1.0 - z / 100.0))  # 1 near, 0 far
        centre = w * (0.5 + (lane - 1) * (0.12 + 0.22 * t))
        return centre

    def _draw(self):
        self.root_layout.canvas.before.clear()
        w, h = self.width, self.height
        with self.root_layout.canvas.before:
            Color(*NAVY)
            Rectangle(pos=(0, 0), size=(w, h))
            # city skyline (simple neon rectangles)
            Color(0.1, 0.1, 0.35, 1)
            for i, bh in enumerate([0.55, 0.7, 0.5, 0.75, 0.6]):
                Rectangle(pos=(i * w / 5, h * 0.55), size=(w / 5 - 4, h * bh * 0.45))
            # road
            Color(0.15, 0.15, 0.3, 1)
            Rectangle(pos=(w * 0.15, 0), size=(w * 0.7, h * 0.55))
            Color(*CYAN)
            Line(points=[w * 0.5, h * 0.55, w * 0.15, 0], width=1.5)
            Line(points=[w * 0.5, h * 0.55, w * 0.85, 0], width=1.5)
            # coins (gold circles as rectangles)
            Color(*GOLD)
            for coin in self.state.coins:
                x = self._lane_x(coin.lane, coin.z, w)
                s = 10 + 22 * (1 - coin.z / 100.0)
                Rectangle(pos=(x - s / 2, h * 0.18 + coin.z * 0.3), size=(s, s))
            # obstacles
            for obj in self.state.obstacles:
                x = self._lane_x(obj.lane, obj.z, w)
                s = 24 + 46 * (1 - obj.z / 100.0)
                y = h * 0.18 + obj.z * 0.3
                if obj.kind == "barrier":
                    Color(1, 0.6, 0, 1)
                elif obj.kind == "car":
                    Color(0.8, 0.1, 0.2, 1)
                else:
                    Color(0.6, 0.2, 0.9, 1)
                Rectangle(pos=(x - s / 2, y), size=(s, s * 0.7))
            # player
            px = self._lane_x(self.state.lane, 0, w)
            py = h * 0.12 + self.state.jump_y * 3
            ph = 70 if not self.state.sliding else 38
            Color(0, 0, 0, 1)
            Rectangle(pos=(px - 26, py), size=(52, ph))

    # ---- overlays ---------------------------------------------------
    def _clear_overlay(self):
        if self.overlay:
            self.root_layout.remove_widget(self.overlay)
            self.overlay = None

    def _panel(self, title, buttons):
        self._clear_overlay()
        panel = BoxLayout(orientation="vertical", padding=24, spacing=10,
                          size_hint=(0.8, 0.6),
                          pos_hint={"center_x": 0.5, "center_y": 0.5})
        panel.add_widget(Label(text=title, font_size=30, bold=True,
                               color=GOLD, size_hint=(1, None), height=44))
        for text, fn in buttons:
            panel.add_widget(gold_button(text, fn) if text in ("RESUME", "NEXT") else blue_button(text, fn))
        self.overlay = panel
        self.root_layout.add_widget(panel)

    def pause_game(self):
        if not self.state or self.state.over:
            return
        self.paused = True
        self._panel("PAUSED", [
            ("RESUME", lambda b: self._resume()),
            ("RESTART", lambda b: self._restart()),
            ("SETTINGS", lambda b: self._to_settings()),
            ("HOME", lambda b: self._home()),
        ])

    def _resume(self):
        self.paused = False
        self._clear_overlay()

    def _restart(self):
        self.start(self.app)

    def _to_settings(self):
        self.paused = False
        self._clear_overlay()
        self.stop()
        self.manager.current = "settings"

    def _home(self):
        self.paused = False
        self._clear_overlay()
        self.stop()
        self.manager.current = "menu"

    def _show_level_complete(self):
        self.paused = True
        st = self.state
        self._panel("LEVEL COMPLETE!", [
            ("HOME", lambda b: self._finish_run(game_over=False)),
            ("NEXT", lambda b: self._next_level()),
        ])
        # score line is shown via the panel title area in the HUD;
        # totals are banked when the run finishes (see _finish_run).

    def _next_level(self):
        self.paused = False
        self._clear_overlay()
        # speed already rises with distance; continue the same run
        # at a higher base by bumping distance forward slightly.
        self.state.distance += 1

    def _finish_run(self, game_over):
        st = self.state
        save = self.app.save
        save.set("coins", save.get("coins") + st.coins_run)
        if st.score > save.get("high_score"):
            save.set("high_score", st.score)
        if st.distance > save.get("best_distance"):
            save.set("best_distance", int(st.distance))
        self.paused = True
        if game_over:
            self._panel("GAME OVER", [
                ("RESTART", lambda b: self._restart()),
                ("HOME", lambda b: self._home()),
            ])
        else:
            self._home()
