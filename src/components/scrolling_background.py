# src/components/scrolling_background.py
import pygame
from .. import settings

class ScrollingBackground:
    def __init__(self, image_path, speed):
        self.image = pygame.image.load(image_path).convert()
        self.image_height = self.image.get_height()
        self.rect1 = self.image.get_rect(topleft=(0, 0))
        self.rect2 = self.image.get_rect(topleft=(0, -self.image_height))
        self.speed_y = speed

    def update(self, dt):
        self.rect1.y += self.speed_y * dt
        self.rect2.y += self.speed_y * dt
        if self.rect1.top >= settings.SCREEN_HEIGHT:
            self.rect1.y = self.rect2.y - self.image_height
        if self.rect2.top >= settings.SCREEN_HEIGHT:
            self.rect2.y = self.rect1.y - self.image_height

    def draw(self, surface):
        surface.blit(self.image, self.rect1)
        surface.blit(self.image, self.rect2)