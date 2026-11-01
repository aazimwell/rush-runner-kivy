"""Shared Kivy UI helpers for Rush Runner.

Golden primary buttons, dark-blue secondary buttons, and a
header label — matching the reference UI (dark navy, cyan neon
borders, golden-yellow actions) without copying any image.
"""
from kivy.uix.button import Button
from kivy.uix.label import Label

NAVY = (0.02, 0.05, 0.18, 1)
CYAN = (0.0, 0.85, 1, 1)
GOLD = (1.0, 0.75, 0.1, 1)
DARK_BLUE = (0.05, 0.2, 0.55, 1)
GREEN = (0.1, 0.8, 0.3, 1)
RED = (0.85, 0.15, 0.2, 1)
WHITE = (1, 1, 1, 1)


def gold_button(text, on_press=None, size_hint=(0.8, None), height=56):
    btn = Button(text=text, size_hint=size_hint, height=height,
                 background_color=GOLD, color=(0, 0, 0, 1),
                 font_size=20, bold=True)
    if on_press:
        btn.bind(on_press=on_press)
    return btn


def blue_button(text, on_press=None, size_hint=(0.8, None), height=52):
    btn = Button(text=text, size_hint=size_hint, height=height,
                 background_color=DARK_BLUE, color=WHITE,
                 font_size=18, bold=True)
    if on_press:
        btn.bind(on_press=on_press)
    return btn


def title_label(text, font_size=34):
    return Label(text=text, font_size=font_size, bold=True,
                 color=GOLD, size_hint=(1, None), height=52)


def body_label(text, font_size=16):
    return Label(text=text, font_size=font_size, color=WHITE,
                 size_hint=(1, None), height=30)
