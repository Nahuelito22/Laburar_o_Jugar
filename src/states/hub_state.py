# src/states/hub_state.py
import pygame
from .base_state import BaseState
from .. import settings
from ..entities import PlayerHub
from .. import save_manager

class HubState(BaseState):
    def __init__(self):
        super().__init__()
        self.background_image = pygame.image.load("assets/images/background_hub_Final.jpg").convert()
        
        self.all_sprites = pygame.sprite.Group()
        self.player = PlayerHub(
            x=settings.SCREEN_WIDTH / 2, 
            y=settings.SCREEN_HEIGHT - 80
        )
        self.all_sprites.add(self.player)

        self.work_zone = pygame.Rect(0, 0, 150, settings.SCREEN_HEIGHT)
        self.play_zone = pygame.Rect(settings.SCREEN_WIDTH - 150, 0, 150, settings.SCREEN_HEIGHT)

        try:
            self.arrow_font = pygame.font.Font("assets/fonts/UAV-OSD-Mono.ttf", 120)
        except FileNotFoundError:
            self.arrow_font = pygame.font.Font(None, 150)
            
        self.left_arrow = self.arrow_font.render("<", True, settings.WHITE)
        self.right_arrow = self.arrow_font.render(">", True, settings.WHITE)
        
        self.left_arrow_rect = self.left_arrow.get_rect(centery=settings.SCREEN_HEIGHT / 2, left=40)
        self.right_arrow_rect = self.right_arrow.get_rect(centery=settings.SCREEN_HEIGHT / 2, right=settings.SCREEN_WIDTH - 40)

        self.dinero_total = 0
        self.fichas = 0
        self.hud_font = pygame.font.Font(None, 50)

    def startup(self, persistent):
        super().startup(persistent)
        
        self.dinero_total = self.persistent.get('dinero_total')
        self.fichas = self.persistent.get('fichas')

        if self.dinero_total is None:
            save_data = save_manager.load_data()
            self.dinero_total = save_data.get('dinero_total', 0)
        
        if self.fichas is None:
            save_data = save_manager.load_data()
            self.fichas = save_data.get('fichas', 0)

    def get_event(self, event):
        if event.type == pygame.QUIT:
            self.quit = True
        
    def update(self, dt):
        self.all_sprites.update(dt)
        
        if self.player.hitbox.colliderect(self.work_zone):
            self.persistent['dinero_total'] = self.dinero_total
            self.persistent['fichas'] = self.fichas
            self.done = True
            self.next_state = "PAPERBOY"
            
        if self.player.hitbox.colliderect(self.play_zone):
            self.persistent['dinero_total'] = self.dinero_total
            self.persistent['fichas'] = self.fichas
            self.done = True
            self.next_state = "ARCADE"

    def draw(self, surface):
        surface.blit(self.background_image, (0, 0))
        self.all_sprites.draw(surface)
        
        surface.blit(self.left_arrow, self.left_arrow_rect)
        surface.blit(self.right_arrow, self.right_arrow_rect)
        
        # --- HUD CORREGIDO ---
        # Mantenemos solo el bloque que incluye el nombre de usuario
        nombre = self.persistent.get('nombre_usuario', 'Jugador')
        dinero_texto = self.hud_font.render(f"Dinero de {nombre}: ${self.dinero_total}", True, settings.WHITE)
        fichas_texto = self.hud_font.render(f"Fichas: {self.fichas}", True, settings.WHITE)
        surface.blit(dinero_texto, (10, 10))
        surface.blit(fichas_texto, (10, 50))

        # Opcional: Descomenta para ver las zonas de activación
        # if settings.DEBUG_MODE:
        #     pygame.draw.rect(surface, (255, 0, 0), self.work_zone, 2)
        #     pygame.draw.rect(surface, (0, 0, 255), self.play_zone, 2)