# src/states/menu_state.py
import pygame
import os
from .base_state import BaseState
from .. import settings
from .. import save_manager

class MenuState(BaseState):
    def __init__(self):
        super().__init__()
        self.next_state = "INTRO"
        
        # --- Fuentes ---
        self.title_font = pygame.font.Font(settings.resource_path("fonts/UAV-OSD-Mono.ttf"), 80)
        self.button_font = pygame.font.Font(settings.resource_path("fonts/UAV-OSD-Mono.ttf"), 60)
        self.help_font = pygame.font.Font(None, 32)

        # --- TÍTULO ---
        self.title_text = self.title_font.render("¿Laburar o Jugar?", True, settings.WHITE)
        self.title_rect = self.title_text.get_rect(center=(settings.SCREEN_WIDTH / 2, 150))
        
        # --- LÓGICA DE AYUDA (POP-UP) ---
        self.ayuda_activa = False
        self.help_icon = self.title_font.render("?", True, settings.WHITE)
        self.help_rect = self.help_icon.get_rect(center=(settings.SCREEN_WIDTH - 50, settings.SCREEN_HEIGHT - 50))
        self.dim_surface = pygame.Surface(settings.SCREEN_SIZE)
        self.dim_surface.set_alpha(180)
        self.dim_surface.fill(settings.BLACK)

        # --- BOTONES DINÁMICOS ---
        self.new_game_text = self.button_font.render("Nueva Partida", True, settings.WHITE)
        self.new_game_rect = self.new_game_text.get_rect(center=(settings.SCREEN_WIDTH / 2, 350))
        
        if os.path.exists(save_manager.SAVE_FILE):
            save_data = save_manager.load_data()
            nombre_guardado = save_data.get('nombre_usuario', 'Jugador')
            self.continue_text = self.button_font.render(f"Continuar: {nombre_guardado}", True, settings.WHITE)
        else:
            self.continue_text = self.button_font.render("Continuar", True, (100, 100, 100))
        
        self.continue_rect = self.continue_text.get_rect(center=(settings.SCREEN_WIDTH / 2, 500))

        # Lógica de ingreso de nombre
        self.ingresando_nombre = False
        self.nombre_usuario = ""
        self.input_box = pygame.Rect(0, 0, 400, 70)
        self.input_box.center = (settings.SCREEN_WIDTH / 2, 450)

    def get_event(self, event):
        if event.type == pygame.QUIT:
            self.quit = True

        if self.ayuda_activa:
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                self.ayuda_activa = False
            return

        if self.ingresando_nombre:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if self.nombre_usuario:
                        self.persistent = {'nombre_usuario': self.nombre_usuario, 'high_score': 0, 'dinero_total': 0, 'fichas': 0}
                        save_manager.save_data(self.persistent)
                        self.done = True
                elif event.key == pygame.K_BACKSPACE:
                    self.nombre_usuario = self.nombre_usuario[:-1]
                else:
                    self.nombre_usuario += event.unicode
        
        else:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.new_game_rect.collidepoint(event.pos):
                    self.ingresando_nombre = True
                    self.nombre_usuario = ""

                if self.continue_rect.collidepoint(event.pos):
                    if os.path.exists(save_manager.SAVE_FILE):
                        self.persistent = save_manager.load_data()
                        self.done = True
                
                if self.help_rect.collidepoint(event.pos):
                    self.ayuda_activa = True

    def draw_help_popup(self, surface):
        popup_rect = pygame.Rect(0, 0, 800, 400)
        popup_rect.center = (settings.SCREEN_WIDTH / 2, settings.SCREEN_HEIGHT / 2)
        pygame.draw.rect(surface, (20, 20, 50), popup_rect)
        pygame.draw.rect(surface, settings.WHITE, popup_rect, 3)

        title = self.button_font.render("Como Jugar", True, settings.WHITE)
        line1 = self.help_font.render("Elige 'Laburar' para jugar al Paperboy y ganar dinero.", True, settings.WHITE)
        line2 = self.help_font.render("Elige 'Jugar' para ir al Salón Arcade.", True, settings.WHITE)
        line3 = self.help_font.render("En el Arcade, cambia tu dinero por fichas para jugar.", True, settings.WHITE)
        line4 = self.help_font.render("¡Consigue el mayor puntaje!", True, (255, 255, 100))
        close_text = self.help_font.render("Presiona cualquier tecla para cerrar", True, (180, 180, 180))
        
        surface.blit(title, title.get_rect(centerx=popup_rect.centerx, y=popup_rect.top + 30))
        surface.blit(line1, (popup_rect.left + 40, popup_rect.top + 120))
        surface.blit(line2, (popup_rect.left + 40, popup_rect.top + 160))
        surface.blit(line3, (popup_rect.left + 40, popup_rect.top + 200))
        surface.blit(line4, line4.get_rect(centerx=popup_rect.centerx, y=popup_rect.top + 260))
        surface.blit(close_text, close_text.get_rect(centerx=popup_rect.centerx, y=popup_rect.top + 340))

    def draw(self, surface):
        surface.fill((20, 20, 40))
        surface.blit(self.title_text, self.title_rect)
        
        if not self.ingresando_nombre:
            mouse_pos = pygame.mouse.get_pos()
            if self.new_game_rect.collidepoint(mouse_pos): pygame.draw.rect(surface, (70, 70, 100), self.new_game_rect.inflate(20, 20))
            else: pygame.draw.rect(surface, (40, 40, 70), self.new_game_rect.inflate(20, 20))
            if self.continue_rect.collidepoint(mouse_pos): pygame.draw.rect(surface, (70, 70, 100), self.continue_rect.inflate(20, 20))
            else: pygame.draw.rect(surface, (40, 40, 70), self.continue_rect.inflate(20, 20))
            
            surface.blit(self.new_game_text, self.new_game_rect)
            surface.blit(self.continue_text, self.continue_rect)
            surface.blit(self.help_icon, self.help_rect)
        else:
            prompt_text = self.button_font.render("Ingresa tu nombre:", True, settings.WHITE)
            prompt_rect = prompt_text.get_rect(center=(settings.SCREEN_WIDTH / 2, 300))
            surface.blit(prompt_text, prompt_rect)
            pygame.draw.rect(surface, (70, 70, 100), self.input_box)
            pygame.draw.rect(surface, settings.WHITE, self.input_box, 2)
            input_surface = self.button_font.render(self.nombre_usuario, True, settings.WHITE)
            surface.blit(input_surface, (self.input_box.x + 15, self.input_box.y + 10))

        if self.ayuda_activa:
            surface.blit(self.dim_surface, (0, 0))
            self.draw_help_popup(surface)