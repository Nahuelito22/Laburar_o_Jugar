# src/entities.py
import pygame
from .components.spritesheet import SpriteSheet
from . import settings

# Dimensiones del fotograma de sprites 
PLAYER_FRAME_WIDTH = 256
PLAYER_FRAME_HEIGHT = 256

class PlayerHub(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        # --- LÍNEAS MODIFICADAS ---
        self.animations = {
            'idle': self.cargar_idle(settings.resource_path("images/player_idle.png")),
            'walk_left': self.cargar_animacion(settings.resource_path("images/player_walk_left.png")),
            'walk_right': self.cargar_animacion(settings.resource_path("images/player_walk_right.png"))
        }
        
        self.estado = 'idle'
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()
        self.animation_speed = 150

        self.image = self.animations[self.estado][self.current_frame]
        self.rect = self.image.get_rect(centerx=x, bottom=y)
        
        self.hitbox = self.rect.inflate(-self.rect.width * 0.7, -self.rect.height * 0.2)
        
        self.speed = 300
        self.moving = False

    def cargar_idle(self, image_path):
        # Esta función ya recibe la ruta correcta, no necesita cambios
        img = pygame.image.load(image_path).convert_alpha()
        scaled_img = pygame.transform.scale(img, (PLAYER_FRAME_WIDTH, PLAYER_FRAME_HEIGHT))
        return [scaled_img]

    def cargar_animacion(self, spritesheet_path):
        # Esta función ya recibe la ruta correcta, no necesita cambios
        spritesheet = SpriteSheet(spritesheet_path)
        frames = []
        num_frames = spritesheet.sheet.get_height() // PLAYER_FRAME_HEIGHT
        for i in range(num_frames):
            frame = spritesheet.get_image(0, i * PLAYER_FRAME_HEIGHT, PLAYER_FRAME_WIDTH, PLAYER_FRAME_HEIGHT)
            frames.append(frame)
        return frames

    def update(self, dt):
        self.moving = False
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed * dt
            self.estado = 'walk_left'
            self.moving = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed * dt
            self.estado = 'walk_right'
            self.moving = True
        
        if not self.moving:
            self.estado = 'idle'

        # Límites de la pantalla
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > settings.SCREEN_WIDTH:
            self.rect.right = settings.SCREEN_WIDTH
        
        # Animación
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_speed:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.animations[self.estado])
            self.image = self.animations[self.estado][self.current_frame]
            
        # Mantenemos el hitbox centrado
        self.hitbox.center = self.rect.center