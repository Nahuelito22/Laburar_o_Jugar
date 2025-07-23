# src/states/intro_state.py
import pygame
from .base_state import BaseState
from .. import settings

class IntroState(BaseState):
    def __init__(self):
        super().__init__()
        self.intro_image = pygame.image.load("assets/images/intro_scene.png").convert()
        self.alarm_sound = pygame.mixer.Sound("assets/sounds/alarm_clock.wav")
        self.blink_surface = pygame.Surface(settings.SCREEN_SIZE)
        self.blink_surface.fill(settings.BLACK)
        self.alpha = 255
        self.blink_speed = -5
        self.blink_count = 0
        self.total_blinks = 2
        self.scene_timer = 0
        self.scene_duration = 6000
        self.next_state = "HUB"

    def startup(self, persistent):
        super().startup(persistent)
        self.alarm_sound.play()

    def update(self, dt):
        self.scene_timer += dt * 1000
        self.alpha += self.blink_speed
        if self.alpha <= 0 or self.alpha >= 255:
            self.blink_speed *= -1
            self.alpha = max(0, min(255, self.alpha))
            if self.blink_speed < 0:
                self.blink_count += 1
        self.blink_surface.set_alpha(self.alpha)
        if self.scene_timer >= self.scene_duration or self.blink_count >= self.total_blinks:
            self.alarm_sound.stop()
            self.done = True

    def draw(self, surface):
        surface.blit(self.intro_image, (0, 0))
        surface.blit(self.blink_surface, (0, 0))