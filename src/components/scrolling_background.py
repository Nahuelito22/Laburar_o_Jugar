# src/components/scrolling_background.py
import pygame
import random
from .. import settings

class ScrollingBackground:
    def __init__(self, image_paths, speed): # Acepta 'image_paths' (plural)
        self.images = [pygame.image.load(path).convert() for path in image_paths]

        self.bg1_img = random.choice(self.images)
        self.bg2_img = random.choice(self.images)

        self.bg1_rect = self.bg1_img.get_rect(topleft=(0, 0))
        self.bg2_rect = self.bg2_img.get_rect(topleft=(0, -settings.SCREEN_HEIGHT))

        self.speed = speed

    def update(self, dt):
        self.bg1_rect.y += self.speed * dt
        self.bg2_rect.y += self.speed * dt

        if self.bg1_rect.top >= settings.SCREEN_HEIGHT:
            self.bg1_rect.top = self.bg2_rect.top - settings.SCREEN_HEIGHT
            self.bg1_img = random.choice(self.images)

        if self.bg2_rect.top >= settings.SCREEN_HEIGHT:
            self.bg2_rect.top = self.bg1_rect.top - settings.SCREEN_HEIGHT
            self.bg2_img = random.choice(self.images)

    def draw(self, surface):
        surface.blit(self.bg1_img, self.bg2_rect)
        surface.blit(self.bg2_img, self.bg1_rect)