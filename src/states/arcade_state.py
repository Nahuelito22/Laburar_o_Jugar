# src/states/arcade_state.py
import pygame
import random
from .base_state import BaseState
from .. import settings
from ..entities import PlayerHub

class ArcadeState(BaseState):
    def __init__(self):
        super().__init__()
        self.background_image = pygame.image.load("assets/images/hub_arcade.png").convert()
        self.background_image = pygame.transform.scale(self.background_image, settings.SCREEN_SIZE)

        self.player = PlayerHub(x=settings.SCREEN_WIDTH - 150, y=settings.SCREEN_HEIGHT - 80)
        self.all_sprites = pygame.sprite.Group(self.player)

        # Usamos tus valores de hitbox ya ajustados
        self.machines = {
            "PONG": pygame.Rect(390, 280, 125, 300),
            "SF": pygame.Rect(555, 280, 125, 300),
            "CXYS": pygame.Rect(720, 280, 125, 300),
            "CREDITS": pygame.Rect(1000, 300, 200, 150),
            "SLOTS": pygame.Rect(200, 280, 125, 300) 
        }
        
        # Variables de la tienda y pop-up
        self.dinero_total = 0
        self.fichas = 0
        self.costo_ficha = 100
        self.maquina_activa = None
        
        # Assets para la UI
        self.interaction_font = pygame.font.Font("assets/fonts/UAV-OSD-Mono.ttf", 50)
        self.popup_font = pygame.font.Font("assets/fonts/UAV-OSD-Mono.ttf", 40)
        self.hud_font = pygame.font.Font(None, 50)
        self.prompt_surface = self.interaction_font.render("E", True, settings.WHITE)
        self.slots_result_text = None

        # Superficie para oscurecer el fondo
        self.dim_surface = pygame.Surface(settings.SCREEN_SIZE)
        self.dim_surface.set_alpha(180)
        self.dim_surface.fill(settings.BLACK)

    def startup(self, persistent):
        super().startup(persistent)
        self.dinero_total = self.persistent.get('dinero_total', 0)
        self.fichas = self.persistent.get('fichas', 0)

    def get_event(self, event):
        if event.type == pygame.QUIT:
            self.quit = True
        
        if event.type == pygame.KEYDOWN:
            # --- Lógica si un pop-up está ACTIVO ---
            if self.maquina_activa is not None:
                if event.key == pygame.K_RETURN: # Presionar ENTER para confirmar
                    if self.maquina_activa == "CREDITS":
                        if self.dinero_total >= self.costo_ficha:
                            self.dinero_total -= self.costo_ficha
                            self.fichas += 1
                        self.maquina_activa = None
                    
                    elif self.maquina_activa == "SLOTS":
                        if self.dinero_total >= 50:
                            self.dinero_total -= 50
                            resultado = random.choice(['NADA', 'NADA', 'NADA', 'PREMIO_CHICO', 'PREMIO_GRANDE'])
                            if resultado == 'PREMIO_GRANDE':
                                self.fichas += 5
                                self.slots_result_text = "¡PREMIO GRANDE! (+5 Fichas)"
                            elif resultado == 'PREMIO_CHICO':
                                self.fichas += 1
                                self.slots_result_text = "¡Premio! (+1 Ficha)"
                            else:
                                self.slots_result_text = "Mala suerte... Intenta de nuevo."
                        else:
                            self.slots_result_text = "¡Dinero insuficiente!"

                if event.key == pygame.K_ESCAPE:
                    self.maquina_activa = None
            
            # --- Lógica si el juego está NORMAL ---
            else:
                if event.key == pygame.K_ESCAPE:
                    self.persistent['dinero_total'] = self.dinero_total
                    self.persistent['fichas'] = self.fichas
                    self.next_state = "HUB"
                    self.done = True
                
                if event.key == pygame.K_e and self.interaction_prompt_text is not None:
                    machine = self.interaction_prompt_text
                    
                    if machine == "CREDITS":
                        self.maquina_activa = "CREDITS"
                    
                    elif machine == "SLOTS":
                        self.slots_result_text = None # Reinicia el texto del resultado
                        self.maquina_activa = "SLOTS"

                    elif machine in ["PONG", "SF", "CXYS"]:
                        if self.fichas > 0:
                            self.fichas -= 1
                            self.persistent['dinero_total'] = self.dinero_total
                            self.persistent['fichas'] = self.fichas
                            self.next_state = machine
                            self.done = True
                        else:
                            print("¡Necesitas fichas para jugar!")
    
    def update(self, dt):
        if self.maquina_activa is None:
            self.all_sprites.update(dt)
            self.interaction_prompt_text = None
            for machine_name, machine_rect in self.machines.items():
                if self.player.hitbox.colliderect(machine_rect):
                    self.interaction_prompt_text = machine_name
                    break

    def draw_credits_popup(self, surface):
        popup_rect = pygame.Rect(0, 0, 1000, 350)
        popup_rect.center = (settings.SCREEN_WIDTH / 2, settings.SCREEN_HEIGHT / 2)
        pygame.draw.rect(surface, (20, 20, 50), popup_rect)
        pygame.draw.rect(surface, settings.WHITE, popup_rect, 3)
        title = self.hud_font.render("Cambiar Dinero por Fichas", True, settings.WHITE)
        surface.blit(title, title.get_rect(centerx=popup_rect.centerx, y=popup_rect.top + 20))
        info_text = self.popup_font.render(f"Costo: ${self.costo_ficha} por 1 Ficha", True, settings.WHITE)
        surface.blit(info_text, info_text.get_rect(centerx=popup_rect.centerx, y=popup_rect.top + 100))
        confirm_text = self.popup_font.render("Presiona ENTER para comprar", True, (150, 255, 150))
        surface.blit(confirm_text, confirm_text.get_rect(centerx=popup_rect.centerx, y=popup_rect.top + 200))
        cancel_text = self.popup_font.render("Presiona ESC para cancelar", True, (255, 150, 150))
        surface.blit(cancel_text, cancel_text.get_rect(centerx=popup_rect.centerx, y=popup_rect.top + 250))

    def draw_slots_popup(self, surface):
        popup_rect = pygame.Rect(0, 0, 1000, 400)
        popup_rect.center = (settings.SCREEN_WIDTH / 2, settings.SCREEN_HEIGHT / 2)
        pygame.draw.rect(surface, (50, 20, 20), popup_rect)
        pygame.draw.rect(surface, settings.WHITE, popup_rect, 3)
        title = self.hud_font.render("Tragamonedas", True, settings.WHITE)
        surface.blit(title, title.get_rect(centerx=popup_rect.centerx, y=popup_rect.top + 20))
        info_text = self.popup_font.render("Costo de la tirada: $50", True, settings.WHITE)
        surface.blit(info_text, info_text.get_rect(centerx=popup_rect.centerx, y=popup_rect.top + 100))
        if self.slots_result_text:
            result_surf = self.popup_font.render(self.slots_result_text, True, (255, 255, 100))
            surface.blit(result_surf, result_surf.get_rect(centerx=popup_rect.centerx, y=popup_rect.top + 180))
        confirm_text = self.popup_font.render("Presiona ENTER para apostar", True, (150, 255, 150))
        surface.blit(confirm_text, confirm_text.get_rect(centerx=popup_rect.centerx, y=popup_rect.top + 280))
        cancel_text = self.popup_font.render("Presiona ESC para salir", True, (255, 150, 150))
        surface.blit(cancel_text, cancel_text.get_rect(centerx=popup_rect.centerx, y=popup_rect.top + 330))

    def draw(self, surface):
        surface.blit(self.background_image, (0, 0))
        self.all_sprites.draw(surface)

        if self.interaction_prompt_text is not None and self.maquina_activa is None:
            prompt_rect = self.prompt_surface.get_rect(center=self.player.rect.midtop)
            prompt_rect.y -= 20
            surface.blit(self.prompt_surface, prompt_rect)
            
        dinero_texto = self.hud_font.render(f"Dinero: ${self.dinero_total}", True, settings.WHITE)
        fichas_texto = self.hud_font.render(f"Fichas: {self.fichas}", True, settings.WHITE)
        surface.blit(dinero_texto, (10, 10))
        surface.blit(fichas_texto, (10, 50))

        if self.maquina_activa is not None:
            surface.blit(self.dim_surface, (0, 0))
            if self.maquina_activa == "CREDITS":
                self.draw_credits_popup(surface)
            elif self.maquina_activa == "SLOTS":
                self.draw_slots_popup(surface)

        if settings.DEBUG_MODE:
            for machine_rect in self.machines.values():
                pygame.draw.rect(surface, (255, 0, 255), machine_rect, 3)
            if self.player.hitbox:
                pygame.draw.rect(surface, (0, 255, 0), self.player.hitbox, 2)