# src/games/cxys/cxys_state.py
import pygame
from ...states.base_state import BaseState
from ... import settings

class CXYSState(BaseState):
    def __init__(self):
        super().__init__()
        self.next_state = "ARCADE"
        self.font = pygame.font.Font("assets/fonts/UAV-OSD-Mono.ttf", 40)
        
        self.title_text = self.font.render("Juego en Construccion...)", True, settings.WHITE)
        self.title_rect = self.title_text.get_rect(center=(settings.SCREEN_WIDTH / 2, settings.SCREEN_HEIGHT / 2 - 50))

        self.instructions_text = self.font.render("Presiona ESC para volver", True, (180, 180, 180))
        self.instructions_rect = self.instructions_text.get_rect(center=(settings.SCREEN_WIDTH / 2, settings.SCREEN_HEIGHT / 2 + 50))

    def get_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.done = True

    def draw(self, surface):
        surface.fill(settings.BLACK)
        surface.blit(self.title_text, self.title_rect)
        surface.blit(self.instructions_text, self.instructions_rect)