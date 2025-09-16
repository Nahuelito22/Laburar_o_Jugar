# src/states/pre_game_menu_state.py
import pygame
from .base_state import BaseState
from .. import settings

class PreGameMenuState(BaseState):
    def __init__(self):
        super().__init__()
        self.font_title = pygame.font.Font(settings.resource_path("fonts/UAV-OSD-Mono.ttf"), 80)
        self.font_info = pygame.font.Font(settings.resource_path("fonts/UAV-OSD-Mono.ttf"), 40)
        self.font_scores = pygame.font.Font(settings.resource_path("fonts/UAV-OSD-Mono.ttf"), 30)

        self.game_title = ""
        self.high_scores = []
        self.fichas = 0
        self.game_modes = []
        self.selected_mode_index = 0
        
        self.dim_surface = pygame.Surface(settings.SCREEN_SIZE)
        self.dim_surface.set_alpha(180)
        self.dim_surface.fill(settings.BLACK)

    def startup(self, persistent):
        super().startup(persistent)
        self.game_title = self.persistent.get('game_title', 'NO_TITLE')
        self.high_scores = self.persistent.get('high_scores', [])
        self.fichas = self.persistent.get('fichas', 0)
        self.game_modes = self.persistent.get('game_modes', ['Default'])
        self.selected_mode_index = 0

    def get_event(self, event):
        if event.type == pygame.QUIT:
            self.quit = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.next_state = "ARCADE"
                self.done = True
            elif event.key == pygame.K_RETURN:
                if self.fichas > 0:
                    self.persistent['fichas'] -= 1
                    self.persistent['game_mode'] = self.game_modes[self.selected_mode_index]
                    self.next_state = self.game_title
                    self.done = True
                else:
                    # Opcional: mostrar un mensaje de "no hay fichas" en el menú
                    print("No tienes fichas para jugar!")
            elif event.key == pygame.K_UP:
                self.selected_mode_index = (self.selected_mode_index - 1) % len(self.game_modes)
            elif event.key == pygame.K_DOWN:
                self.selected_mode_index = (self.selected_mode_index + 1) % len(self.game_modes)

    def draw(self, surface):
        # Dibujamos el estado de arcade detrás
        # (Esto requiere una pequeña modificación en el bucle principal de App)
        # Por ahora, solo un fondo negro.
        surface.blit(self.persistent['arcade_surface'], (0, 0))
        surface.blit(self.dim_surface, (0, 0))

        # --- Dibuja el contenido del menú ---
        popup_rect = pygame.Rect(0, 0, 1200, 600)
        popup_rect.center = settings.SCREEN_CENTER
        pygame.draw.rect(surface, (20, 20, 50), popup_rect, border_radius=15)
        pygame.draw.rect(surface, settings.WHITE, popup_rect, 3, border_radius=15)

        # Título del juego
        title_surf = self.font_title.render(self.game_title, True, settings.WHITE)
        surface.blit(title_surf, title_surf.get_rect(centerx=popup_rect.centerx, y=popup_rect.top + 30))

        # High Scores
        scores_title_surf = self.font_info.render("High Scores", True, settings.WHITE)
        surface.blit(scores_title_surf, (popup_rect.left + 50, popup_rect.top + 150))
        for i, score in enumerate(self.high_scores[:5]):
            score_surf = self.font_scores.render(f"{i+1}. {score}", True, settings.YELLOW)
            surface.blit(score_surf, (popup_rect.left + 70, popup_rect.top + 220 + i * 40))

        # Modos de juego
        modes_title_surf = self.font_info.render("Modo de Juego", True, settings.WHITE)
        surface.blit(modes_title_surf, (popup_rect.right - 450, popup_rect.top + 150))
        for i, mode in enumerate(self.game_modes):
            color = settings.CYAN if i == self.selected_mode_index else settings.WHITE
            mode_surf = self.font_scores.render(mode, True, color)
            surface.blit(mode_surf, (popup_rect.right - 430, popup_rect.top + 220 + i * 50))

        # Fichas y Prompt
        fichas_surf = self.font_info.render(f"Fichas: {self.fichas}", True, settings.WHITE)
        surface.blit(fichas_surf, fichas_surf.get_rect(centerx=popup_rect.centerx, y=popup_rect.bottom - 150))

        if self.fichas > 0:
            prompt_text = "Presiona ENTER para Jugar (1 Ficha)"
            prompt_color = (150, 255, 150)
        else:
            prompt_text = "¡Necesitas Fichas!"
            prompt_color = (255, 150, 150)
        
        prompt_surf = self.font_info.render(prompt_text, True, prompt_color)
        surface.blit(prompt_surf, prompt_surf.get_rect(centerx=popup_rect.centerx, y=popup_rect.bottom - 100))

        # Salir
        exit_surf = self.font_scores.render("Presiona ESC para Volver", True, settings.WHITE)
        surface.blit(exit_surf, exit_surf.get_rect(centerx=popup_rect.centerx, y=popup_rect.bottom - 40))
