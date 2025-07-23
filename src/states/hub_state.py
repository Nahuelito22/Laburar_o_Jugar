# src/states/hub_state.py
import pygame
from .base_state import BaseState
from .. import settings

class HubState(BaseState):
    def __init__(self):
        super().__init__()
        self.background_image = pygame.image.load("assets/images/background_hub_Final.jpg").convert()
        
        # --- Lógica del Personaje ---
        original_player_image = pygame.image.load("assets/images/player_idle.png").convert_alpha()
        nuevo_ancho = 256
        nuevo_alto = 256
        self.player_image = pygame.transform.scale(original_player_image, (nuevo_ancho, nuevo_alto))
        
        self.player_rect = self.player_image.get_rect(centerx=settings.SCREEN_WIDTH / 2)
        self.player_rect.bottom = settings.SCREEN_HEIGHT - 80
        self.player_speed = 300

        # --- Zonas de activación ---
        self.work_zone = pygame.Rect(0, 0, 150, settings.SCREEN_HEIGHT)
        self.play_zone = pygame.Rect(settings.SCREEN_WIDTH - 150, 0, 150, settings.SCREEN_HEIGHT)

        # --- NUEVO: Lógica para las flechas visuales ---
        try:
            self.arrow_font = pygame.font.Font("assets/fonts/UAV-OSD-Mono.ttf", 120)
        except FileNotFoundError:
            self.arrow_font = pygame.font.Font(None, 150)
            
        # Creamos las superficies de texto para las flechas
        self.left_arrow = self.arrow_font.render("<", True, settings.WHITE)
        self.right_arrow = self.arrow_font.render(">", True, settings.WHITE)
        
        # Posicionamos las flechas cerca de los bordes de la pantalla
        self.left_arrow_rect = self.left_arrow.get_rect(centery=settings.SCREEN_HEIGHT / 2)
        self.left_arrow_rect.left = 40 # 40 píxeles desde el borde izquierdo
        
        self.right_arrow_rect = self.right_arrow.get_rect(centery=settings.SCREEN_HEIGHT / 2)
        self.right_arrow_rect.right = settings.SCREEN_WIDTH - 40 # 40 píxeles desde el borde derecho


    def get_event(self, event):
        if event.type == pygame.QUIT:
            self.quit = True
        
    def update(self, dt):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player_rect.x -= self.player_speed * dt
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player_rect.x += self.player_speed * dt
            
        # Comprobamos colisiones con las zonas
        if self.player_rect.colliderect(self.work_zone):
            print("TRANSICIÓN: Paperboy")
            # self.next_state = "PAPERBOY"
            #self.done = True
            
        if self.player_rect.colliderect(self.play_zone):
            print("TRANSICIÓN: Arcade")
            # self.next_state = "ARCADE_HUB"
            # self.done = True

    def draw(self, surface):
        # Dibujamos el fondo y el personaje
        surface.blit(self.background_image, (0, 0))
        surface.blit(self.player_image, self.player_rect)
        
        # --- NUEVO: Dibujamos las flechas en la pantalla ---
        surface.blit(self.left_arrow, self.left_arrow_rect)
        surface.blit(self.right_arrow, self.right_arrow_rect)
        
        # Opcional: Descomenta para ver las zonas de activación
        # pygame.draw.rect(surface, (255, 0, 0, 100), self.work_zone)
        # pygame.draw.rect(surface, (0, 0, 255, 100), self.play_zone)