# src/games/pong/pong_state.py
import pygame
from ...states.base_state import BaseState
from ... import settings

class PongState(BaseState):
    def __init__(self):
        super().__init__()
        self.next_state = "ARCADE"
    def get_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.done = True
    def draw(self, surface):
        surface.fill(settings.BLACK)
        font = pygame.font.Font(None, 50)
        text = font.render("Juego de PONG (Presiona ESC para volver)", True, settings.WHITE)
        text_rect = text.get_rect(center=(settings.SCREEN_WIDTH/2, settings.SCREEN_HEIGHT/2))
        surface.blit(text, text_rect)