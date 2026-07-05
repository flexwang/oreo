"""Behavior engine for Oreo — walks left and right, stretches on click."""

import random
from enum import Enum


class State(Enum):
    WALK = "walk"
    STRETCH = "stretch"
    WALK_TAIL_UP = "walk_tail_up"


class FloatingBehavior:
    def __init__(self, screen_width, screen_height, pet_size=150):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.pet_size = pet_size

        self.state = State.WALK
        self.direction = random.choice([-1, 1])
        self.speed = random.uniform(1.0, 2.0)

        self.walk_timer = 0
        self.walk_duration = self._random_walk_duration()

        self.tail_up_timer = 0
        self.tail_up_duration = 0

    def _random_walk_duration(self):
        return random.randint(80, 200)

    def _random_tail_up_duration(self):
        return random.randint(60, 120)

    def update(self, current_x, current_y):
        """Returns (dx, dy) for this tick."""
        if self.state == State.WALK:
            self.walk_timer += 1
            if self.walk_timer >= self.walk_duration:
                self.walk_timer = 0
                self.walk_duration = self._random_walk_duration()
                self.direction *= -1
                self.speed = random.uniform(1.0, 2.0)

            dx = self.direction * self.speed
        elif self.state == State.WALK_TAIL_UP:
            self.tail_up_timer += 1
            if self.tail_up_timer >= self.tail_up_duration:
                self.state = State.WALK
                self.walk_timer = 0
                self.walk_duration = self._random_walk_duration()

            dx = self.direction * self.speed
        else:
            dx = 0

        dy = 0

        new_x = current_x + dx
        if new_x < 0 or new_x > self.screen_width - self.pet_size:
            self.direction *= -1
            dx = -dx

        return dx, dy

    def trigger_stretch(self):
        self.state = State.STRETCH

    def end_stretch(self):
        self.state = State.WALK_TAIL_UP
        self.tail_up_timer = 0
        self.tail_up_duration = self._random_tail_up_duration()
        self.speed = random.uniform(1.0, 2.0)
