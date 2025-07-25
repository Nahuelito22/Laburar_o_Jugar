# src/games/paperboy/entities.py
import pygame
from ...components.spritesheet import SpriteSheet
from ... import settings

FRAME_WIDTH = 256
FRAME_HEIGHT = 256

class PlayerPaperboy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        
        self.animations = {
            'ride': self.cargar_animacion("assets/images/Paperboy_ride.png"),
            'spin_left': self.cargar_animacion("assets/images/Paperboy_spin_left.png"),
            'spin_right': self.cargar_animacion("assets/images/Paperboy_spin_right.png")
        }
        self.estado_animacion = 'ride'
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()
        self.animation_speed = 120

        self.image = self.animations[self.estado_animacion][self.current_frame]
        self.rect = self.image.get_rect(centerx=settings.SCREEN_WIDTH / 2, bottom=settings.SCREEN_HEIGHT - 50)
        self.speed = 350
        
        # ---- NUEVO: Límites de la calle ----
        # Ajustá estos valores para que coincidan con tu calle
        self.limite_izquierdo = 300
        self.limite_derecho = 1000

    def cargar_animacion(self, spritesheet_path):
        spritesheet = SpriteSheet(spritesheet_path)
        frames = []
        num_frames = spritesheet.sheet.get_height() // FRAME_HEIGHT
        for i in range(num_frames):
            frame = spritesheet.get_image(0, i * FRAME_HEIGHT, FRAME_WIDTH, FRAME_HEIGHT)
            frames.append(frame)
        return frames

    def update(self, dt):
        # Lógica de estado y animación (sin cambios)
        keys = pygame.key.get_pressed()
        nuevo_estado = 'ride'
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed * dt
            nuevo_estado = 'spin_left'
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed * dt
            nuevo_estado = 'spin_right'
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= self.speed * dt
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += self.speed * dt

        if nuevo_estado != self.estado_animacion:
            self.estado_animacion = nuevo_estado
            self.current_frame = 0

        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_speed:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.animations[self.estado_animacion])
            self.image = self.animations[self.estado_animacion][self.current_frame]

        # ---- LÍMITES DE LA PANTALLA (ACTUALIZADOS) ----
        # Límites horizontales (ahora usan los límites de la calle)
        if self.rect.left < self.limite_izquierdo:
            self.rect.left = self.limite_izquierdo
        if self.rect.right > self.limite_derecho:
            self.rect.right = self.limite_derecho
            
        # Límites verticales (sin cambios)
        if self.rect.top < 0: self.rect.top = 0
        if self.rect.bottom > settings.SCREEN_HEIGHT: self.rect.bottom = settings.SCREEN_HEIGHT