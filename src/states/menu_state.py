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
        
        # --- NUEVO: Lógica para el ingreso de nombre ---
        self.ingresando_nombre = False
        self.nombre_usuario = ""
        self.input_box = pygame.Rect(0, 0, 400, 70)
        self.input_box.center = (settings.SCREEN_WIDTH / 2, 450)
        
        # --- Botones ---
        self.new_game_text = self.font.render("Nueva Partida", True, settings.WHITE)
        self.new_game_rect = self.new_game_text.get_rect(center=(settings.SCREEN_WIDTH / 2, 300))
        self.continue_text = self.font.render("Continuar", True, settings.WHITE)
        self.continue_rect = self.continue_text.get_rect(center=(settings.SCREEN_WIDTH / 2, 450))

        self.next_state = "INTRO"

    def get_event(self, event):
        if event.type == pygame.QUIT:
            self.quit = True
        
        # --- Lógica de Eventos para Ingreso de Nombre ---
        if self.ingresando_nombre:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN: # Presionar ENTER para confirmar nombre
                    if self.nombre_usuario: # Si el nombre no está vacío
                        # Creamos los datos para la nueva partida
                        self.persistent = {
                            'nombre_usuario': self.nombre_usuario,
                            'high_score': 0,
                            'dinero_total': 0,
                            'fichas': 0
                        }
                        save_manager.save_data(self.persistent) # Guardamos la nueva partida
                        self.done = True
                elif event.key == pygame.K_BACKSPACE: # Borrar
                    self.nombre_usuario = self.nombre_usuario[:-1]
                else: # Escribir
                    self.nombre_usuario += event.unicode
        
        # --- Lógica de Eventos para el Menú Principal ---
        else:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.new_game_rect.collidepoint(event.pos):
                    # Activamos el modo de ingreso de nombre
                    self.ingresando_nombre = True
                    self.nombre_usuario = "" # Reseteamos el nombre

                if self.continue_rect.collidepoint(event.pos):
                    if os.path.exists(save_manager.SAVE_FILE):
                        self.persistent = save_manager.load_data()
                        self.done = True
                    else:
                        # Si no hay partida, le pedimos que cree una nueva
                        print("No hay partida guardada. Crea una nueva.")
                        self.ingresando_nombre = True
                        self.nombre_usuario = ""

    def draw(self, surface):
        surface.fill((20, 20, 40))
        
        # --- Dibujado del Menú Principal ---
        if not self.ingresando_nombre:
            mouse_pos = pygame.mouse.get_pos()
            # ... (código para dibujar y resaltar botones, sin cambios) ...
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

        # --- Dibujado de la Pantalla de Ingreso de Nombre ---
        else:
            prompt_text = self.font.render("Ingresa tu nombre:", True, settings.WHITE)
            prompt_rect = prompt_text.get_rect(center=(settings.SCREEN_WIDTH / 2, 300))
            surface.blit(prompt_text, prompt_rect)

            pygame.draw.rect(surface, (70, 70, 100), self.input_box)
            pygame.draw.rect(surface, settings.WHITE, self.input_box, 2)
            
            input_surface = self.font.render(self.nombre_usuario, True, settings.WHITE)
            surface.blit(input_surface, (self.input_box.x + 15, self.input_box.y + 10))