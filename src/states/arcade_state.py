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

        # --- Zonas Interactivas con tus nuevos valores ---
        self.machines = {
            "PONG": pygame.Rect(390, 280, 125, 300),
            "SF": pygame.Rect(555, 280, 125, 300),
            "CXYS": pygame.Rect(720, 280, 125, 300),
            # --- NUEVO: Hitboxes para créditos y tragamonedas ---
            "CREDITS": pygame.Rect(1000, 300, 200, 150),
            "SLOTS": pygame.Rect(200, 280, 125, 300) 
        }
        
        # --- Lógica de dinero, fichas y avisos ---
        self.dinero_total = 0
        self.fichas = 0
        self.costo_ficha = 100
        
        self.interaction_prompt_text = None
        self.font = pygame.font.Font("assets/fonts/UAV-OSD-Mono.ttf", 50)
        self.prompt_surface = self.font.render("E", True, settings.WHITE)
        self.hud_font = pygame.font.Font(None, 50)

    def startup(self, persistent):
        """Al entrar al estado, cargamos el dinero y las fichas."""
        super().startup(persistent)
        self.dinero_total = self.persistent.get('dinero_total', 0)
        self.fichas = self.persistent.get('fichas', 0)

    def get_event(self, event):
        if event.type == pygame.QUIT:
            self.quit = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Guardamos el estado antes de salir
                self.persistent['dinero_total'] = self.dinero_total
                self.persistent['fichas'] = self.fichas
                self.next_state = "HUB"
                self.done = True
            
            if event.key == pygame.K_e and self.interaction_prompt_text is not None:
                machine = self.interaction_prompt_text
                
                # --- Lógica de Interacción ---
                if machine in ["PONG", "SF", "CXYS"]: # Si es una máquina de arcade
                    if self.fichas > 0:
                        self.fichas -= 1
                        print(f"Gastaste una ficha. Entrando a {machine}...")
                        self.persistent['dinero_total'] = self.dinero_total
                        self.persistent['fichas'] = self.fichas
                        self.next_state = machine # El nombre del estado es el mismo que el de la máquina
                        self.done = True
                    else:
                        print("¡Necesitas fichas para jugar!")

                elif machine == "CREDITS":
                    if self.dinero_total >= self.costo_ficha:
                        self.dinero_total -= self.costo_ficha
                        self.fichas += 1
                        print(f"Cambiaste ${self.costo_ficha} por 1 ficha.")
                    else:
                        print("¡No tenés suficiente dinero!")

                elif machine == "SLOTS":
                    if self.dinero_total >= 50: # Apostar cuesta $50
                        self.dinero_total -= 50
                        resultado = random.choice(['NADA', 'PREMIO_CHICO', 'PREMIO_GRANDE'])
                        if resultado == 'PREMIO_GRANDE':
                            self.fichas += 5
                            print("¡PREMIO GRANDE! ¡Ganaste 5 fichas!")
                        elif resultado == 'PREMIO_CHICO':
                            self.fichas += 1
                            print("¡Premio! Ganaste 1 ficha.")
                        else:
                            print("No ganaste nada...")
                    else:
                        print("¡Necesitas $50 para apostar!")

    def update(self, dt):
        self.all_sprites.update(dt)
        
        self.interaction_prompt_text = None
        for machine_name, machine_rect in self.machines.items():
            if self.player.hitbox.colliderect(machine_rect):
                self.interaction_prompt_text = machine_name
                break

    def draw(self, surface):
        surface.blit(self.background_image, (0, 0))
        self.all_sprites.draw(surface)

        if self.interaction_prompt_text is not None:
            prompt_rect = self.prompt_surface.get_rect(center=self.player.rect.midtop)
            prompt_rect.y -= 20
            surface.blit(self.prompt_surface, prompt_rect)
            
        # HUD de Dinero y Fichas
        dinero_texto = self.hud_font.render(f"Dinero: ${self.dinero_total}", True, settings.WHITE)
        fichas_texto = self.hud_font.render(f"Fichas: {self.fichas}", True, settings.WHITE)
        surface.blit(dinero_texto, (10, 10))
        surface.blit(fichas_texto, (10, 50))

        # Modo Debug
        if settings.DEBUG_MODE:
            for machine_rect in self.machines.values():
                pygame.draw.rect(surface, (255, 0, 255), machine_rect, 3)
            if self.player.hitbox:
                pygame.draw.rect(surface, (0, 255, 0), self.player.hitbox, 2)