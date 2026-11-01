"""Rush Runner (Kivy version) — pure game logic, no Kivy dependency.

This module is deliberately framework-free so it can be unit-tested
headlessly. The Kivy screens in game_screen.py render this state.

Rules:
- 3 lanes (0 left, 1 centre, 2 right), player starts centre.
- Jump: vertical physics; slide: timed crouch.
- Obstacles: 'barrier' (jump over it), 'car' (must change lane),
  'drone' (slide under it). Any other obstacle in the same lane
  when it reaches the player is a hit unless the matching action
  is active.
- A hit costs 1 health (from the selected character) and grants
  1 second of invulnerability. Health 0 = game over.
- Coins in a lane add 10 score each plus the distance score.
- Every 1000 m is a milestone (level complete screen in the UI).
- Speed rises slowly with distance.
"""
import random

LANES = 3
SPAWN_Z = 100.0          # spawn distance ahead of the player
HIT_Z = 6.0              # object reaches the player at this z
GRAVITY = -60.0
JUMP_VELOCITY = 26.0
SLIDE_TIME = 0.7


class Obstacle:
    def __init__(self, lane, kind, z):
        self.lane = lane
        self.kind = kind  # 'barrier' | 'car' | 'drone'
        self.z = z


class Coin:
    def __init__(self, lane, z):
        self.lane = lane
        self.z = z


class GameState:
    def __init__(self, speed_mult=1.0, health=3, seed=None):
        self.rng = random.Random(seed)
        self.speed_mult = speed_mult
        self.max_health = health
        self.reset()

    def reset(self):
        self.lane = 1
        self.jump_y = 0.0
        self.jump_v = 0.0
        self.jumping = False
        self.slide_timer = 0.0
        self.distance = 0.0
        self.score = 0
        self.coins_run = 0
        self.health = self.max_health
        self.invuln = 0.0
        self.obstacles = []
        self.coins = []
        self.over = False
        self.milestone = 0        # completed 1000 m milestones
        self._spawn_timer = 0.0
        self._coin_timer = 0.0

    @property
    def sliding(self):
        return self.slide_timer > 0.0

    @property
    def speed(self):
        # base speed in z-units/second, rising with distance
        return (18.0 + min(self.distance * 0.012, 22.0)) * self.speed_mult

    def move_left(self):
        if self.lane > 0:
            self.lane -= 1
            return True
        return False

    def move_right(self):
        if self.lane < LANES - 1:
            self.lane += 1
            return True
        return False

    def jump(self):
        if not self.jumping:
            self.jumping = True
            self.jump_v = JUMP_VELOCITY
            self.slide_timer = 0.0
            return True
        return False

    def slide(self):
        if not self.jumping:
            self.slide_timer = SLIDE_TIME
            return True
        return False

    def _spawn(self):
        lane = self.rng.randrange(LANES)
        kind = self.rng.choice(['barrier', 'car', 'drone'])
        self.obstacles.append(Obstacle(lane, kind, SPAWN_Z))
        if self.rng.random() < 0.7:
            clane = self.rng.randrange(LANES)
            for i in range(3):
                self.coins.append(Coin(clane, SPAWN_Z + i * 8.0))

    def update(self, dt):
        """Advance the world. Returns 'hit' | 'coin' | 'milestone' | None."""
        if self.over:
            return None
        result = None
        self.distance += self.speed * dt
        self.score = int(self.distance) + self.coins_run * 10
        if self.invuln > 0:
            self.invuln -= dt
        # jump physics
        if self.jumping:
            self.jump_v += GRAVITY * dt
            self.jump_y += self.jump_v * dt
            if self.jump_y <= 0:
                self.jump_y = 0.0
                self.jumping = False
        if self.slide_timer > 0:
            self.slide_timer -= dt
        # spawn
        self._spawn_timer -= dt
        if self._spawn_timer <= 0:
            self._spawn()
            self._spawn_timer = self.rng.uniform(0.9, 1.6)
        # move objects towards the player
        dz = self.speed * dt
        for obj in list(self.obstacles):
            obj.z -= dz
            if obj.z <= HIT_Z and obj.z > -HIT_Z:
                if obj.lane == self.lane and self.invuln <= 0:
                    blocked = ((obj.kind == 'barrier' and self.jumping)
                               or (obj.kind == 'drone' and self.sliding))
                    if not blocked:
                        self.health -= 1
                        self.invuln = 1.0
                        result = 'hit'
                        if self.health <= 0:
                            self.over = True
                self.obstacles.remove(obj)
            elif obj.z <= -HIT_Z:
                self.obstacles.remove(obj)
        for coin in list(self.coins):
            coin.z -= dz
            if coin.z <= HIT_Z and coin.z > -HIT_Z:
                if coin.lane == self.lane:
                    self.coins_run += 1
                    result = 'coin'
                self.coins.remove(coin)
            elif coin.z <= -HIT_Z:
                self.coins.remove(coin)
        new_milestone = int(self.distance // 1000)
        if new_milestone > self.milestone:
            self.milestone = new_milestone
            result = 'milestone'
        self.score = int(self.distance) + self.coins_run * 10
        return result
