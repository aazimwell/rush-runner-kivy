"""Sensor layer for Rush Runner (Kivy version).

Real accelerometer only, via plyer, when it is available (Android).
On desktop plyer is absent, so this reports available=False and
direction 0 — a clean touch-only fallback. Values are NEVER
simulated with random numbers.

Tilt convention (documented, device-dependent in sign):
  tilt value > dead-zone  -> lean right -> move right
  tilt value < -dead-zone -> lean left  -> move left
Calibration stores the neutral reading as tilt_offset; the caller
subtracts it before applying the dead-zone. Edge-triggered: the
caller only moves when the direction changes, so holding a tilt
does not spam lane changes.
"""
try:
    from plyer import accelerometer
    _HAS_PLYER = True
except Exception:
    accelerometer = None
    _HAS_PLYER = False


class TiltSensor:
    def __init__(self, sensitivity="Medium", tilt_offset=0.0):
        self.sensitivity = sensitivity
        self.tilt_offset = tilt_offset
        self.available = False
        self.enabled = False
        self._last_direction = 0
        if _HAS_PLYER:
            try:
                accelerometer.enable()
                self.available = True
                self.enabled = True
            except Exception:
                self.available = False

    @property
    def dead_zone(self):
        return {"Low": 0.45, "Medium": 0.3, "High": 0.18}.get(
            self.sensitivity, 0.3)

    def calibrate(self):
        """Store the current reading as neutral. Returns True on success."""
        if not self.available:
            return False
        try:
            values = accelerometer.acceleration[:3]
        except Exception:
            return False
        if not values or values[0] is None:
            return False
        self.tilt_offset = float(values[0])
        return True

    def direction(self):
        """Return -1 (left), 0 (neutral), 1 (right) — edge-triggered."""
        if not self.available or not self.enabled:
            return 0
        try:
            values = accelerometer.acceleration[:3]
        except Exception:
            return 0
        if not values or values[0] is None:
            return 0
        tilt = float(values[0]) - self.tilt_offset
        dz = self.dead_zone
        direction = 1 if tilt > dz else (-1 if tilt < -dz else 0)
        if direction != self._last_direction:
            self._last_direction = direction
            return direction
        return 0

    def stop(self):
        if self.available:
            try:
                accelerometer.disable()
            except Exception:
                pass
            self.enabled = False
