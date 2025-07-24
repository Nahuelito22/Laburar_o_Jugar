# src/games/paperboy/entities.py
import pygame
from ...components.spritesheet import SpriteSheet
from ... import settings

# --- Dimensiones del fotograma del sprite (ajusta según tu archivo) ---
FRAME_WIDTH = 80 
FRAME_HEIGHT = 80
# ------------------------------------

class PlayerBike(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        spritesheet = SpriteSheet("assets/images/Paperboy_Bicicleta.png")
        self.animation_frames = []
        
        # Asumiendo 7 fotogramas en la hoja vertical
        for i in range(7): 
            frame = spritesheet.get_image(0, i * FRAME_HEIGHT, FRAME_WIDTH, FRAME_HEIGHT)
            self.animation_frames.append(frame)
            
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()
        self.animation_speed = 120

        self.image = self.animation_frames[0]
        self.rect = self.image.get_rect()
        # Posición inicial del jugador en la pantalla de Paperboy
        self.rect.centerx = settings.SCREEN_WIDTH / 2
        self.rect.bottom = settings.SCREEN_HEIGHT - 50

        # ---- NUEVO: Variables de movimiento ----
        self.speed = 400 # Píxeles por segundo para el movimiento lateral

    def update(self, dt):
        # 1. Lógica de animación (ya la teníamos)
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_speed:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
            self.image = self.animation_frames[self.current_frame]

        # 2. NUEVO: Lógica de movimiento lateral
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed * dt
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed * dt

        # 3. Límites de la pantalla para que no se salga
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > settings.SCREEN_WIDTH:
            self.rect.right = settings.SCREEN_WIDTH