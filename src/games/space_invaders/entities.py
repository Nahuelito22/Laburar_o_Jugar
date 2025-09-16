# src/games/space_invaders/entities.py
import pygame
import random
import math
from ... import settings

class Nave(pygame.sprite.Sprite):
    def __init__(self, cenital_img, izq_img, der_img):
        super().__init__()
        self.imagenes = {'cenital': cenital_img, 'izquierda': izq_img, 'derecha': der_img}
        self.image = self.imagenes['cenital']
        self.rect = self.image.get_rect(centerx=settings.SCREEN_WIDTH / 2, bottom=settings.SCREEN_HEIGHT - 20)
        self.speed = 0

    def update(self, dt):
        self.rect.x += self.speed * dt 
        
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > settings.SCREEN_WIDTH: self.rect.right = settings.SCREEN_WIDTH
        
        if self.speed < 0: self.image = self.imagenes['izquierda']
        elif self.speed > 0: self.image = self.imagenes['derecha']
        else: self.image = self.imagenes['cenital']

class Disparo(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 15)); self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(centerx=x, bottom=y)
        self.speed = -500
    
    def update(self, dt):
        self.rect.y += self.speed * dt
        if self.rect.bottom < 0:
            self.kill()

class Enemigo(pygame.sprite.Sprite):
    def __init__(self, x, y, imagen):
        super().__init__()
        self.image = pygame.transform.scale(imagen, (40, 40))
        self.rect = self.image.get_rect(topleft=(x, y))
    
    def update(self, dt, speed_x, speed_y):
        self.rect.x += speed_x * dt
        self.rect.y += speed_y

        # --- NUEVO: Lógica de disparo ---
        # Damos una pequeña probabilidad en cada fotograma de que el enemigo dispare
        if random.randrange(0, 1500) == 1:
            return EnemigoDisparo(self.rect.centerx, self.rect.bottom)
        return None

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
                center = self.rect.center
                self.image = self.imagenes[self.frame]
                self.rect = self.image.get_rect(center=center)

# --- NUEVAS ENTIDADES PARA EL FONDO DINÁMICO ---
class Estrella:
    def __init__(self, speed):
        self.x = random.randrange(0, settings.SCREEN_WIDTH)
        self.y = random.randrange(0, settings.SCREEN_HEIGHT)
        self.size = random.randrange(1, 4)
        self.speed = speed

    def update(self, dt):
        self.y += self.speed * dt
        if self.y > settings.SCREEN_HEIGHT:
            self.y = random.randrange(-20, -5)
            self.x = random.randrange(0, settings.SCREEN_WIDTH)

    def draw(self, surface):
        pygame.draw.circle(surface, settings.WHITE, (int(self.x), int(self.y)), self.size)

class Asteroide(pygame.sprite.Sprite):
    def __init__(self): # Ya no necesita la imagen como parámetro
        super().__init__()
        
        # --- NUEVO: Creamos el asteroide con polígonos ---
        self.size = random.randrange(20, 60)
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        
        # Puntos para dibujar una forma irregular de asteroide
        points = []
        for _ in range(random.randint(6, 9)): # Entre 6 y 9 vértices
            angle = random.uniform(0, 2 * 3.14159)
            distance = random.uniform(self.size * 0.3, self.size * 0.5)
            points.append(
                (self.size / 2 + distance * math.cos(angle),
                 self.size / 2 + distance * math.sin(angle))
            )
        
        pygame.draw.polygon(self.image, (100, 100, 100), points) # Color gris
        self.original_image = self.image # Guardamos la imagen original para rotar
        
        # El resto de la lógica no cambia
        self.rect = self.image.get_rect(center=(random.randrange(0, settings.SCREEN_WIDTH), random.randrange(-100, -20)))
        self.speed_y = random.randrange(50, 150)
        self.speed_x = random.randrange(-30, 30)
        self.rotation = 0
        self.rotation_speed = random.randrange(-90, 90) # Grados por segundo

    def update(self, dt):
        self.rect.y += self.speed_y * dt
        self.rect.x += self.speed_x * dt
        self.rotation = (self.rotation + self.rotation_speed * dt) % 360
        
        # Rotamos la imagen original para no perder calidad
        self.image = pygame.transform.rotate(self.original_image, self.rotation)
        self.rect = self.image.get_rect(center=self.rect.center)
        
        if self.rect.top > settings.SCREEN_HEIGHT:
            self.kill()

class EnemigoDisparo(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 15))
        
        # --- NUEVO: Lista de colores vibrantes ---
        colores_posibles = [
            (0, 255, 255),   # Cian
            (255, 0, 255),   # Magenta
            (0, 255, 0),     # Verde Lima
            (255, 165, 0),   # Naranja
            (255, 255, 100)  # Amarillo claro
        ]
        
        # Elegimos un color al azar de la lista y rellenamos el disparo
        color_elegido = random.choice(colores_posibles)
        self.image.fill(color_elegido)
        
        self.rect = self.image.get_rect(centerx=x, top=y)
        self.speed = 300
    
    def update(self, dt):
        self.rect.y += self.speed * dt
        # Si el disparo sale de la pantalla por abajo, se elimina
        if self.rect.top > settings.SCREEN_HEIGHT:
            self.kill()