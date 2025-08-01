# src/games/space_invaders/entities.py
import pygame
from ... import settings

# Clases de Sprites 
class Nave(pygame.sprite.Sprite):
    def __init__(self, cenital_img, izq_img, der_img):
        super().__init__()
        self.imagenes = {'cenital': cenital_img, 'izquierda': izq_img, 'derecha': der_img}
        self.image = self.imagenes['cenital']
        self.rect = self.image.get_rect(centerx=settings.SCREEN_WIDTH / 2, bottom=settings.SCREEN_HEIGHT - 20)
        self.speed = 0

    def update(self, dt):
        self.rect.x += self.speed * dt
        # Límites
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > settings.SCREEN_WIDTH: self.rect.right = settings.SCREEN_WIDTH
        
        # Cambiar imagen según la velocidad
        if self.speed < 0: self.image = self.imagenes['izquierda']
        elif self.speed > 0: self.image = self.imagenes['derecha']
        else: self.image = self.imagenes['cenital']

class Disparo(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 15))
        self.image.fill((255, 255, 0)) # Amarillo
        self.rect = self.image.get_rect(center=(x, y))
    
    def update(self, dt):
        self.rect.y -= 800 * dt
        if self.rect.bottom < 0:
            self.kill()

class Enemigo(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("assets/images/red.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (40, 40))
        self.rect = self.image.get_rect(topleft=(x, y))
    
    def update(self, dt, speed_x, speed_y):
        self.rect.x += speed_x * dt
        self.rect.y += speed_y

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, imagenes):
        super().__init__()
        self.imagenes = imagenes
        self.image = self.imagenes[0]
        self.rect = self.image.get_rect(center=center)
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 100 

    def update(self, dt):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(self.imagenes):
                self.kill()
            else:
                self.image = self.imagenes[self.frame]