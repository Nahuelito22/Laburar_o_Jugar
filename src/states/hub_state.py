# src/states/hub_state.py
import pygame
from .base_state import BaseState
from .. import settings
from ..entities import PlayerHub # <-- Importamos nuestra nueva clase de jugador

class HubState(BaseState):
    def __init__(self):
        super().__init__()
        self.background_image = pygame.image.load("assets/images/background_hub_Final.jpg").convert()
        
        # --- Creamos al jugador usando la nueva clase y lo añadimos a un grupo ---
        self.all_sprites = pygame.sprite.Group()
        self.player = PlayerHub(
            x=settings.SCREEN_WIDTH / 2, 
            y=settings.SCREEN_HEIGHT - 80
        )
        self.all_sprites.add(self.player)

        # --- Zonas de activación (se mantienen igual) ---
        self.work_zone = pygame.Rect(0, 0, 150, settings.SCREEN_HEIGHT)
        self.play_zone = pygame.Rect(settings.SCREEN_WIDTH - 150, 0, 150, settings.SCREEN_HEIGHT)

        # --- Lógica para las flechas visuales (se mantienen igual) ---
        try:
            self.arrow_font = pygame.font.Font("assets/fonts/UAV-OSD-Mono.ttf", 120)
        except FileNotFoundError:
            self.arrow_font = pygame.font.Font(None, 150)
            
        self.left_arrow = self.arrow_font.render("<", True, settings.WHITE)
        self.right_arrow = self.arrow_font.render(">", True, settings.WHITE)
        
        self.left_arrow_rect = self.left_arrow.get_rect(centery=settings.SCREEN_HEIGHT / 2, left=40)
        self.right_arrow_rect = self.right_arrow.get_rect(centery=settings.SCREEN_HEIGHT / 2, right=settings.SCREEN_WIDTH - 40)

    def get_event(self, event):
        if event.type == pygame.QUIT:
            self.quit = True
        
    def update(self, dt):
        # El grupo de sprites se encarga de llamar al update() del jugador
        self.all_sprites.update(dt)
        
        # Comprobamos colisiones con las zonas
        if self.player.rect.colliderect(self.work_zone):
            print("TRANSICIÓN: Paperboy")
            self.next_state = "PAPERBOY"
            self.done = True
            
        if self.player.rect.colliderect(self.play_zone):
                print("TRANSICIÓN: Arcade")
                self.next_state = "ARCADE" # <-- CAMBIADO
                self.done = True

    def draw(self, surface):
        # 1. SIEMPRE dibujamos el fondo primero. Esto borra la pantalla.
        surface.blit(self.background_image, (0, 0))
        
        # 2. El grupo de sprites se encarga de dibujar al jugador encima del fondo.
        self.all_sprites.draw(surface)
        
        # 3. Finalmente, dibujamos las flechas por encima de todo.
        surface.blit(self.left_arrow, self.left_arrow_rect)
        surface.blit(self.right_arrow, self.right_arrow_rect)
        
        # Opcional: Descomenta para ver las zonas de activación
        # pygame.draw.rect(surface, (255, 0, 0, 100), self.work_zone)
        # pygame.draw.rect(surface, (0, 0, 255, 100), self.play_zone)