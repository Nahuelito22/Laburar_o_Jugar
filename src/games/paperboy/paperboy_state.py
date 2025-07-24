# src/games/paperboy/paperboy_state.py
import pygame
from ...states.base_state import BaseState
from ... import settings

class PaperboyState(BaseState):
    def __init__(self):
        super().__init__()
        self.next_state = "HUB"

    def get_event(self, event):
        if event.type == pygame.QUIT:
            self.quit = True
        # Si se presiona ESCAPE, volvemos al Hub
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.done = True

    def update(self, dt):
        # No hay nada que actualizar por ahora
        pass

    def draw(self, surface):
        # Simplemente dibujamos un fondo negro y un texto de marcador
        surface.fill(settings.BLACK)
        font = pygame.font.Font(None, 50)
        
        text = font.render("Paperboy (Top-Down) - En Construccion", True, settings.WHITE)
        text_rect = text.get_rect(center=(settings.SCREEN_WIDTH / 2, settings.SCREEN_HEIGHT / 2))
        surface.blit(text, text_rect)
        
        esc_text = font.render("Presiona ESC para volver al Hub", True, settings.WHITE)
        esc_rect = esc_text.get_rect(center=(settings.SCREEN_WIDTH / 2, settings.SCREEN_HEIGHT / 2 + 60))
        surface.blit(esc_text, esc_rect)