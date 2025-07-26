# src/states/arcade_state.py
import pygame
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

        # --- ZONAS INTERACTIVAS (HITBOXES) DE LAS MÁQUINAS ---
        # pygame.Rect(posicion_x, posicion_y, ancho, alto)
        # ¡Estos son los valores que tenés que modificar para ajustar los rectángulos!
        self.machines = {
            "PONG": pygame.Rect(390, 280, 125, 300),
            "SF": pygame.Rect(555, 280, 125, 300), # Ejemplo para la 2da máquina
            "CXYS": pygame.Rect(720, 280, 125, 300) # Ejemplo para la 3ra máquina
        }
        
        # --- NUEVO: Lógica para el aviso de interacción ---
        self.interaction_prompt_text = None
        self.font = pygame.font.Font("assets/fonts/UAV-OSD-Mono.ttf", 50)
        self.prompt_surface = self.font.render("E", True, settings.WHITE)

    def get_event(self, event):
        if event.type == pygame.QUIT:
            self.quit = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.next_state = "HUB"
                self.done = True
            
            # --- NUEVO: Transición al presionar "E" ---
            if event.key == pygame.K_e:
                # Si estamos cerca de una máquina para interactuar...
                if self.interaction_prompt_text is not None:
                    print(f"Entrando a {self.interaction_prompt_text}...")
                    self.next_state = self.interaction_prompt_text # El texto nos dice a qué estado ir
                    self.done = True

    def update(self, dt):
        self.all_sprites.update(dt)
        
        # --- NUEVO: Comprobamos si el jugador está cerca de alguna máquina ---
        self.interaction_prompt_text = None # Reiniciamos el aviso
        for machine_name, machine_rect in self.machines.items():
            if self.player.hitbox.colliderect(machine_rect):
                self.interaction_prompt_text = machine_name.upper() # Guardamos el nombre de la máquina
                break # Solo podemos interactuar con una a la vez

    def draw(self, surface):
        surface.blit(self.background_image, (0, 0))
        self.all_sprites.draw(surface)

        # --- NUEVO: Dibujamos el aviso "E" si corresponde ---
        if self.interaction_prompt_text is not None:
            # Posicionamos la "E" encima de la cabeza del jugador
            prompt_rect = self.prompt_surface.get_rect(center=self.player.rect.midtop)
            prompt_rect.y -= 20 # Un pequeño margen hacia arriba
            surface.blit(self.prompt_surface, prompt_rect)

        # Modo Debug para ver las cajas de las máquinas
        if settings.DEBUG_MODE:
            for machine_rect in self.machines.values():
                pygame.draw.rect(surface, (255, 0, 255), machine_rect, 3) # Fucsia para las máquinas
            if self.player.hitbox:
                pygame.draw.rect(surface, (0, 255, 0), self.player.hitbox, 2) # Verde para el jugador