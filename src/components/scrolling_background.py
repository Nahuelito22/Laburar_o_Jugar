# src/components/scrolling_background.py
import pygame
from .. import settings

class ScrollingBackground:
    def __init__(self, image_path, speed):
        # Cargamos UNA SOLA imagen, la tira larga
        self.image = pygame.image.load(image_path).convert()
        
        # Obtenemos la altura real de nuestra imagen larga
        self.image_height = self.image.get_height()

        # Creamos dos rectángulos para esta misma imagen
        self.rect1 = self.image.get_rect(topleft=(0, 0))
        # El segundo rectángulo se posiciona justo arriba del primero
        self.rect2 = self.image.get_rect(topleft=(0, -self.image_height))
        
        # Solo necesitamos velocidad vertical ahora
        self.speed_y = -speed

    def update(self, dt):
        # Movemos ambos rectángulos hacia abajo
        self.rect1.y += self.speed_y * dt
        self.rect2.y += self.speed_y * dt
        
        # Si el primer rectángulo salió por completo de la pantalla...
        if self.rect1.top >= settings.SCREEN_HEIGHT:
            # Lo teletransportamos arriba del segundo
            self.rect1.y = self.rect2.y - self.image_height

        # Si el segundo rectángulo salió por completo de la pantalla...
        if self.rect2.top >= settings.SCREEN_HEIGHT:
            # Lo teletransportamos arriba del primero
            self.rect2.y = self.rect1.y - self.image_height

    def draw(self, surface):
        # Dibujamos la misma imagen en las dos posiciones
        surface.blit(self.image, self.rect1)
        surface.blit(self.image, self.rect2)