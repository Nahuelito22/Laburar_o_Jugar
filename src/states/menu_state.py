# src/states/menu_state.py
import pygame
import os
from .base_state import BaseState
from .. import settings
from .. import save_manager

class MenuState(BaseState):
    def __init__(self):
        super().__init__()
        self.font = pygame.font.Font("assets/fonts/UAV-OSD-Mono.ttf", 60)
        
        # --- Botón de Nueva Partida ---
        self.new_game_text = self.font.render("Nueva Partida", True, settings.WHITE)
        self.new_game_rect = self.new_game_text.get_rect(center=(settings.SCREEN_WIDTH / 2, 300))
        
        # --- Botón de Continuar ---
        self.continue_text = self.font.render("Continuar", True, settings.WHITE)
        self.continue_rect = self.continue_text.get_rect(center=(settings.SCREEN_WIDTH / 2, 450))

        # El estado al que iremos después de la intro
        self.next_state = "INTRO"

    def get_event(self, event):
        if event.type == pygame.QUIT:
            self.quit = True
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Si se hace clic en "Nueva Partida"
            if self.new_game_rect.collidepoint(event.pos):
                # Borramos el archivo de guardado si existe
                if os.path.exists(save_manager.SAVE_FILE):
                    os.remove(save_manager.SAVE_FILE)
                # Iniciamos con datos vacíos
                self.persistent = {'dinero_total': 0, 'fichas': 0}
                self.done = True

            # Si se hace clic en "Continuar"
            if self.continue_rect.collidepoint(event.pos):
                # Cargamos los datos del archivo
                self.persistent = save_manager.load_data()
                self.done = True

    def draw(self, surface):
        surface.fill((20, 20, 40)) # Fondo azul oscuro
        
        # --- Resaltar botones al pasar el mouse ---
        mouse_pos = pygame.mouse.get_pos()
        
        if self.new_game_rect.collidepoint(mouse_pos):
            pygame.draw.rect(surface, (70, 70, 100), self.new_game_rect.inflate(20, 20))
        else:
            pygame.draw.rect(surface, (40, 40, 70), self.new_game_rect.inflate(20, 20))

        if self.continue_rect.collidepoint(mouse_pos):
            pygame.draw.rect(surface, (70, 70, 100), self.continue_rect.inflate(20, 20))
        else:
            pygame.draw.rect(surface, (40, 40, 70), self.continue_rect.inflate(20, 20))
            
        surface.blit(self.new_game_text, self.new_game_rect)
        surface.blit(self.continue_text, self.continue_rect)