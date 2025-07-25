# src/games/paperboy/entities.py
import pygame
from ...components.spritesheet import SpriteSheet
from ... import settings

# --- Dimensiones del fotograma del jugador (ajusta si es necesario) ---
FRAME_WIDTH = 256
FRAME_HEIGHT = 256

class PlayerPaperboy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        
        # Por ahora, solo cargamos la animación de pedalear
        self.animacion_pedal = self.cargar_animacion("assets/images/Paperboy_ride.png")
        
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()
        self.animation_speed = 120

        self.image = self.animacion_pedal[self.current_frame]
        self.rect = self.image.get_rect(centerx=settings.SCREEN_WIDTH / 2, bottom=settings.SCREEN_HEIGHT - 50)
        self.speed = 350

    def cargar_animacion(self, spritesheet_path):
        """Carga una animación desde una hoja de sprites vertical."""
        spritesheet = SpriteSheet(spritesheet_path)
        frames = []
        num_frames = spritesheet.sheet.get_height() // FRAME_HEIGHT
        for i in range(num_frames):
            frame = spritesheet.get_image(0, i * FRAME_HEIGHT, FRAME_WIDTH, FRAME_HEIGHT)
            frames.append(frame)
        return frames

    def update(self, dt):
        # 1. Animación de pedaleo
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_speed:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.animacion_pedal)
            self.image = self.animacion_pedal[self.current_frame]

        # 2. Movimiento (arriba, abajo, izquierda, derecha)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed * dt
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed * dt
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= self.speed * dt
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += self.speed * dt

        # 3. Límites para que no se salga de la pantalla
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > settings.SCREEN_WIDTH: self.rect.right = settings.SCREEN_WIDTH
        if self.rect.top < 0: self.rect.top = 0
        if self.rect.bottom > settings.SCREEN_HEIGHT: self.rect.bottom = settings.SCREEN_HEIGHT