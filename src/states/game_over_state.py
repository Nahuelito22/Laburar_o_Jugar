# src/states/game_over_state.py
import pygame
from .base_state import BaseState
from .. import settings
from .. import save_manager

class GameOverState(BaseState):
    def __init__(self):
        super().__init__()
        self.next_state = "HUB" # Al terminar, volvemos al Hub
        self.font = pygame.font.Font(None, 80)
        
        self.game_over_text = self.font.render("¡Perdiste!", True, settings.WHITE)
        self.game_over_rect = self.game_over_text.get_rect(center=(settings.SCREEN_WIDTH / 2, settings.SCREEN_HEIGHT / 2 - 50))
        
        self.instructions_text = self.font.render("Presiona Enter para reintentar", True, settings.WHITE)
        self.instructions_rect = self.instructions_text.get_rect(center=(settings.SCREEN_WIDTH / 2, settings.SCREEN_HEIGHT / 2 + 50))

    def get_event(self, event):
        if event.type == pygame.QUIT:
            self.quit = True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            # --- CAMBIO CLAVE AQUÍ ---
            # Antes de salir, cargamos TODOS los datos actualizados del archivo
            save_data = save_manager.load_data()
            # Y los ponemos en 'persistent' para pasárselos al siguiente estado (Hub)
            self.persistent = save_data
            
            self.done = True

    def draw(self, surface):
        surface.fill(settings.BLACK)
        surface.blit(self.game_over_text, self.game_over_rect)
        surface.blit(self.instructions_text, self.instructions_rect)