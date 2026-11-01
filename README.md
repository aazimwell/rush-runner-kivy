# RUSH RUNNER — ENDLESS ADVENTURE (Kivy version)

A complete, playable, offline Android endless-runner game, built
with Python + Kivy. Same game as the earlier Pygame version:
neon night-city, main menu, character select, 3-lane gameplay,
pause, level-complete and game-over screens, settings, swipe +
tilt controls, local high scores and coins.

## Why Kivy? (honest compatibility note)

The Pygame version could not be built into an APK with
Buildozer / python-for-android on current GitHub runners, after
8 Actions runs:

- `pygame-ce` has **no python-for-android recipe**, so p4a tried
  a pip install and failed: "No matching distribution found
  for pygame-ce" (no Android wheel exists).
- The old `pygame` recipe then failed compiling against
  Python 3.12+: "longintrepr.h file not found" (that header was
  removed in Python 3.12, and the old recipe predates it).

Kivy is the maintained Python Android framework with a working
p4a recipe, so this version uses Kivy for rendering and input
while keeping the same game design, screens, characters,
controls and offline save system. **The framework change was
made with the user's explicit approval** — it was not done
silently. The game itself is unchanged in scope.

## Project structure

```
main.py            App entry, ScreenManager wiring
screens.py         Menu / Character / Settings / High Score
game_screen.py     Gameplay rendering, swipe/keyboard/tilt input,
                   pause, level-complete, game-over overlays
game_logic.py      Framework-free game rules (testable headless)
save_manager.py    Local JSON save + character definitions
sensors.py         Real plyer accelerometer, touch-only fallback
ui_helpers.py      Golden/blue buttons, titles (reference UI style)
assets/            City, character, coin, icon, presplash, sounds
buildozer.spec     Android packaging (portrait, fullscreen)
.github/workflows/android-apk.yml   GitHub Actions APK build
```

## Controls

- Swipe left / right: change lane. Swipe up: jump. Swipe down: slide.
- Tilt (Android, plyer accelerometer): lean left/right to change
  lane. Settings → CALIBRATE NOW stores the neutral position.
  Control mode: Touch / Tilt / Both. Sensitivity: Low / Medium / High.
- Desktop testing: arrow keys + space, Esc pauses.
- Tilt is never simulated with random values. If no sensor is
  available, the game falls back cleanly to touch controls.

## Gameplay rules

- Barrier: jump over it. Car: change lane. Drone: slide under it.
- A hit costs 1 health (character health differs: Panda 4,
  Robo 3, Female/Shadow 2) with 1 second invulnerability.
- Coins: +10 score each. Score = distance + coins × 10.
- Every 1000 m: LEVEL COMPLETE (trophy, score, coins, distance,
  3 stars, HOME / NEXT). Health 0: GAME OVER.

## Offline

No login, no server, no ads, no downloads. Coins, high score,
best distance, selected character and all settings persist in
a local `save.json`. The game launches and plays in airplane mode.

## Desktop run (testing only)

```
pip install kivy plyer
python main.py
```

## Android build (GitHub Actions, phone-friendly)

1. Create a GitHub repository and upload this whole project,
   keeping `.github/workflows/android-apk.yml` intact.
2. Open the Actions tab — the workflow "Build Android APK"
   runs on push to `main` (or run it manually via
   workflow_dispatch).
3. On success, download artifact **RUSH-RUNNER-ANDROID-APK**
   and install the APK on your phone.

Workflow: Ubuntu 22.04, Python 3.11, JDK 17, Cython < 3.0,
`yes | buildozer android debug` (accepts Android SDK licences
on a non-interactive runner), artifact upload on success.

## Testing checklist

- [ ] Home screen opens; PLAY / CHARACTER / SETTINGS /
      HIGH SCORE / QUIT all work
- [ ] Character selection changes the gameplay character
- [ ] Swipe left/right/up/down work; keyboard works on desktop
- [ ] Coins collect; obstacles hit correctly by type
- [ ] Score/distance/speed increase; pause/resume/restart work
- [ ] Level complete at 1000 m; game over at health 0
- [ ] High score and settings persist after reopening
- [ ] Offline (airplane mode) play works

## Explicitly unverified (do not treat as done)

- **Android APK build:** only proven when the GitHub Actions
  run succeeds and the artifact downloads.
- **Tilt on a real device:** plyer sensor path is fallback-only
  on desktop; sign convention is device-dependent.
- **Full interactive playthrough on a phone:** only headless /
  logic tests were run during development (see below).

## Troubleshooting

- Build fails at SDK licences: the workflow pipes `yes` into
  Buildozer for this reason; do not remove that pipe.
- Build fails with a pygame error: you are looking at the old
  Pygame project — this Kivy project has no pygame dependency.
- Tilt does nothing on desktop: expected — no accelerometer
  exists there; use swipe/keyboard, or test tilt on a phone.
