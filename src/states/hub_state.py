# src/states/hub_state.py
import pygame
from .base_state import BaseState
from .. import settings

class HubState(BaseState):
    def __init__(self):
        super().__init__()
        self.background_image = pygame.image.load("assets/images/background_hub.png").convert()
        # Suponiendo que tu player_idle.png es para esta escena
        self.player_image = pygame.image.load("assets/images/player_idle.png").convert_alpha()
        self.player_rect = self.player_image.get_rect(center=(settings.SCREEN_WIDTH / 2, settings.SCREEN_HEIGHT - 150))

    def get_event(self, event):
        if event.type == pygame.QUIT:
            self.quit = True

    def draw(self, surface):
        surface.blit(self.background_image, (0, 0))
        surface.blit(self.player_image, self.player_rect)