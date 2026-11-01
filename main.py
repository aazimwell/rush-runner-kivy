"""Rush Runner — Kivy version.

Entry point. Builds a ScreenManager with menu, character,
settings, high-score and game screens, wires the save manager
and the tilt sensor, and starts the game on PLAY.

This version replaces the blocked Pygame Buildozer build (see
README.md): same game, same screens, Kivy framework, built with
the user's explicit approval.
"""
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.core.window import Window

from save_manager import SaveManager
from sensors import TiltSensor
from screens import MenuScreen, CharacterScreen, SettingsScreen, HighScoreScreen
from game_screen import GameScreen

Window.size = (400, 700)


class RushRunnerApp(App):
    title = "Rush Runner"

    def build(self):
        self.save = SaveManager()
        self.tilt = TiltSensor(sensitivity=self.save.get("sensitivity"),
                               tilt_offset=self.save.get("tilt_offset", 0.0))
        sm = ScreenManager(transition=FadeTransition())
        sm.app = self
        sm.add_widget(MenuScreen(name="menu"))
        sm.add_widget(CharacterScreen(name="character"))
        sm.add_widget(SettingsScreen(name="settings"))
        sm.add_widget(HighScoreScreen(name="highscore"))
        self.game_screen = GameScreen(name="game")
        sm.add_widget(self.game_screen)
        self.sm = sm
        return sm

    def start_game(self):
        self.game_screen.start(self)
        self.sm.current = "game"

    def on_stop(self):
        if self.tilt:
            self.tilt.stop()
        if hasattr(self, "game_screen"):
            self.game_screen.stop()


if __name__ == "__main__":
    RushRunnerApp().run()
