# src/states/game_over_state.py
import pygame
from .base_state import BaseState
from .. import settings
from .. import save_manager # Importamos el gestor de guardado

class GameOverState(BaseState):
    def __init__(self):
        super().__init__()
        self.next_state = "HUB"
        self.font_grande = pygame.font.Font(None, 80)
        self.font_normal = pygame.font.Font(None, 50)
        
        # Textos fijos
        self.game_over_text = self.font_grande.render("¡Perdiste!", True, settings.WHITE)
        self.game_over_rect = self.game_over_text.get_rect(center=(settings.SCREEN_WIDTH / 2, 200))
        
        self.instructions_text = self.font_normal.render("Presiona Enter para reintentar", True, settings.WHITE)
        self.instructions_rect = self.instructions_text.get_rect(center=(settings.SCREEN_WIDTH / 2, 550))
        
        # Textos de puntaje (se crearán en startup)
        self.score_text = None
        self.highscore_text = None

    def startup(self, persistent):
        """Se ejecuta al entrar en este estado."""
        super().startup(persistent)
        last_score = self.persistent.get('last_score', 0)
        high_score = save_manager.load_data().get('high_score', 0)

        # Creamos los textos de puntaje con los datos actualizados
        self.score_text = self.font_normal.render(f"Tu Puntaje: {last_score}", True, settings.WHITE)
        self.score_rect = self.score_text.get_rect(center=(settings.SCREEN_WIDTH / 2, 350))

        self.highscore_text = self.font_normal.render(f"Record: {high_score}", True, settings.WHITE)
        self.highscore_rect = self.highscore_text.get_rect(center=(settings.SCREEN_WIDTH / 2, 420))

    def get_event(self, event):
        if event.type == pygame.QUIT:
            self.quit = True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.done = True

    def draw(self, surface):
        surface.fill(settings.BLACK)
        surface.blit(self.game_over_text, self.game_over_rect)
        surface.blit(self.instructions_text, self.instructions_rect)
        if self.score_text:
            surface.blit(self.score_text, self.score_rect)
            surface.blit(self.highscore_text, self.highscore_rect)