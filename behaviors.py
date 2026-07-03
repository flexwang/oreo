"""Behavior engine for Oreo — walks left and right across the screen."""

import random
from enum import Enum


class State(Enum):
    IDLE = "idle"
    WALK = "walk"
    SIT = "sit"
    HAPPY = "happy"


class FloatingBehavior:
    def __init__(self, screen_width, screen_height, pet_size=150):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.pet_size = pet_size

        self.state = State.WALK
        self.state_timer = 0
        self.state_duration = self._random_duration()

        # Horizontal movement: 1 = right, -1 = left
        self.direction = random.choice([-1, 1])
        self.speed = random.uniform(1.0, 2.0)
        self.angle = 0.0 if self.direction > 0 else 3.14159

    def _random_duration(self):
        durations = {
            State.IDLE: (40, 100),
            State.WALK: (80, 200),
            State.SIT: (60, 150),
            State.HAPPY: (25, 25),
        }
        lo, hi = durations.get(self.state, (50, 100))
        return random.randint(lo, hi)

    def transition(self):
        if self.state == State.HAPPY:
            self.state = State.WALK
        elif self.state == State.WALK:
            r = random.random()
            if r < 0.4:
                self.state = State.IDLE
            elif r < 0.6:
                self.state = State.SIT
            else:
                # Change direction
                self.direction *= -1
                self.angle = 0.0 if self.direction > 0 else 3.14159
                self.speed = random.uniform(1.0, 2.0)
        elif self.state == State.IDLE or self.state == State.SIT:
            self.state = State.WALK
            if random.random() < 0.3:
                self.direction *= -1
                self.angle = 0.0 if self.direction > 0 else 3.14159
            self.speed = random.uniform(1.0, 2.0)

        self.state_timer = 0
        self.state_duration = self._random_duration()

    def update(self, current_x, current_y):
        """Returns (dx, dy) for this tick."""
        self.state_timer += 1

        if self.state_timer >= self.state_duration:
            self.transition()

        if self.state == State.WALK:
            dx = self.direction * self.speed
        else:
            dx = 0

        dy = 0

        # Bounce off left/right edges
        new_x = current_x + dx
        if new_x < 0 or new_x > self.screen_width - self.pet_size:
            self.direction *= -1
            self.angle = 0.0 if self.direction > 0 else 3.14159
            dx = -dx

        return dx, dy

    def trigger_happy(self):
        self.state = State.HAPPY
        self.state_timer = 0
        self.state_duration = 25
