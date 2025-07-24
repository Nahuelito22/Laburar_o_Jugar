import pygame
from ...components.spritesheet import SpriteSheet
from ... import settings

# --- Dimensiones del fotograma del sprite (ajusta según tu archivo) ---
FRAME_WIDTH = 80 
FRAME_HEIGHT = 80

class PlayerBike(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        
        # --- NUEVO: Cargamos todas las animaciones ---
        self.animations = {
            'pedal': self.cargar_animacion("assets/images/player_pedal.png"),
            'throw_left': self.cargar_animacion("assets/images/player_throw_left.png"),
            'throw_right': self.cargar_animacion("assets/images/player_throw_right.png")
        }
        self.estado_animacion = 'pedal' # El estado inicial
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()
        self.animation_speed = 100

        self.image = self.animations[self.estado_animacion][self.current_frame]
        self.rect = self.image.get_rect(centerx=settings.SCREEN_WIDTH / 2, bottom=settings.SCREEN_HEIGHT - 50)
        self.speed = 400

    def cargar_animacion(self, spritesheet_path):
        """Función de ayuda para cargar una animación desde una hoja de sprites."""
        spritesheet = SpriteSheet(spritesheet_path)
        frames = []
        # Asumiendo que cada hoja tiene 7 fotogramas
        for i in range(7):
            frame = spritesheet.get_image(0, i * FRAME_HEIGHT, FRAME_WIDTH, FRAME_HEIGHT)
            frames.append(frame)
        return frames

    def update(self, dt):
        # 1. Animación
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_speed:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.animations[self.estado_animacion])
            
            # Si la animación de lanzar termina, volvemos a pedalear
            if self.estado_animacion in ['throw_left', 'throw_right'] and self.current_frame == 0:
                self.estado_animacion = 'pedal'

            self.image = self.animations[self.estado_animacion][self.current_frame]

        # 2. Movimiento
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed * dt
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed * dt

        # Límites
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > settings.SCREEN_WIDTH: self.rect.right = settings.SCREEN_WIDTH

    def lanzar(self, direccion):
        """Cambia el estado para iniciar la animación de lanzamiento."""
        if direccion == "izquierda":
            self.estado_animacion = 'throw_left'
        else:
            self.estado_animacion = 'throw_right'
        self.current_frame = 0 # Reiniciamos la animación de lanzamiento

# --- NUEVA CLASE: BUZON ---
class Buzon(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # El buzón es un rectángulo invisible para detectar colisiones
        self.image = pygame.Surface((50, 50)) # Tamaño del área de colisión
        self.image.set_colorkey((0,0,0)) # Hacemos la superficie invisible
        self.rect = self.image.get_rect(topleft=(x, y))