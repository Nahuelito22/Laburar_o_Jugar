# src/games/paperboy/entities.py
import pygame
import random
import math
from ...components.spritesheet import SpriteSheet
from ... import settings

# --- Constantes de Tamaño ---
PLAYER_FRAME_WIDTH = 256
PLAYER_FRAME_HEIGHT = 256
BUZON_WIDTH = 64
BUZON_HEIGHT = 64
# (Añade aquí las de los autos si es necesario)

class PlayerPaperboy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.animations = {
            'ride': self.cargar_animacion("assets/images/Paperboy_ride.png"),
            'spin_left': self.cargar_animacion("assets/images/Paperboy_spin_left.png"),
            'spin_right': self.cargar_animacion("assets/images/Paperboy_spin_right.png"),
            'throw_left': self.cargar_animacion("assets/images/Paperboy_throw_left.png", False),
            'throw_right': self.cargar_animacion("assets/images/Paperboy_throw_right.png", False)
        }
        self.estado_animacion = 'ride'
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()
        self.animation_speed = 120
        self.image = self.animations[self.estado_animacion]['frames'][self.current_frame]
        self.rect = self.image.get_rect(centerx=settings.SCREEN_WIDTH / 2, bottom=settings.SCREEN_HEIGHT - 50)
        self.speed = 350
        self.limite_izquierdo = 450
        self.limite_derecho = 860
        
        self.hitbox = self.rect.inflate(-self.rect.width * 0.75, -self.rect.height * 0.40)

    def cargar_animacion(self, spritesheet_path, loop=True):
        spritesheet = SpriteSheet(spritesheet_path)
        frames = []
        num_frames = spritesheet.sheet.get_height() // PLAYER_FRAME_HEIGHT
        for i in range(num_frames):
            frame = spritesheet.get_image(0, i * PLAYER_FRAME_HEIGHT, PLAYER_FRAME_WIDTH, PLAYER_FRAME_HEIGHT)
            frames.append(frame)
        return {'frames': frames, 'loop': loop}

    def update(self, dt):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_speed:
            self.last_update = now
            self.current_frame += 1
            anim_info = self.animations[self.estado_animacion]
            if self.current_frame >= len(anim_info['frames']):
                if anim_info['loop']:
                    self.current_frame = 0
                else:
                    self.estado_animacion = 'ride'
                    self.current_frame = 0
            self.image = self.animations[self.estado_animacion]['frames'][self.current_frame]

        is_throwing = 'throw' in self.estado_animacion
        if not is_throwing:
            keys = pygame.key.get_pressed()
            nuevo_estado = 'ride'
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.rect.x -= self.speed * dt
                nuevo_estado = 'spin_left'
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.rect.x += self.speed * dt
                nuevo_estado = 'spin_right'
            if nuevo_estado != self.estado_animacion:
                self.estado_animacion = nuevo_estado
                self.current_frame = 0
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= self.speed * dt
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += self.speed * dt
        
        self.hitbox.center = self.rect.center

        if self.hitbox.left < self.limite_izquierdo:
            self.hitbox.left = self.limite_izquierdo
            self.rect.centerx = self.hitbox.centerx
        if self.hitbox.right > self.limite_derecho:
            self.hitbox.right = self.limite_derecho
            self.rect.centerx = self.hitbox.centerx

        if self.rect.top < 0: self.rect.top = 0
        if self.rect.bottom > settings.SCREEN_HEIGHT: self.rect.bottom = settings.SCREEN_HEIGHT
        
        self.hitbox.center = self.rect.center

    def lanzar(self, estado):
        is_throwing = 'throw' in self.estado_animacion
        if not is_throwing:
            self.estado_animacion = estado
            self.current_frame = 0

class Buzon(pygame.sprite.Sprite):
    def __init__(self, scroll_speed, limite_izq_buzon, limite_der_buzon):
        super().__init__()
        colores = ["blue", "green", "red", "yellow"]
        lado = random.choice(["izquierda", "derecha"])
        
        img_path = f"assets/images/mailbox_{random.choice(colores)}.png"
        self.image = pygame.image.load(img_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (BUZON_WIDTH, BUZON_HEIGHT))
        
        if lado == "izquierda":
            self.image = pygame.transform.flip(self.image, True, False)
            x = random.randint(limite_izq_buzon - 80, limite_izq_buzon - 20)
        else:
            x = random.randint(limite_der_buzon + 20, limite_der_buzon + 80)
            
        y = random.randint(-200, -100)
        self.rect = self.image.get_rect(center=(x, y))
        self.scroll_speed = scroll_speed

    def update(self, dt):
        self.rect.y += self.scroll_speed * dt
        # La eliminación ahora la maneja el state para la penalización

class Auto(pygame.sprite.Sprite):
    def __init__(self, scroll_speed):
        super().__init__()
        tipos_de_vehiculos = [
            {'nombre': 'car_blue', 'height': 400, 'num_frames': 2},
            {'nombre': 'car_red', 'height': 400, 'num_frames': 2},
            {'nombre': 'car_white', 'height': 400, 'num_frames': 2},
            {'nombre': 'bus', 'height': 550, 'num_frames': 2},
            {'nombre': 'police_car', 'height': 420, 'num_frames': 2}
        ]
        vehiculo_elegido = random.choice(tipos_de_vehiculos)
        path = f"assets/images/{vehiculo_elegido['nombre']}_move.png"
        spritesheet = SpriteSheet(path)
        
        self.animation_frames = []
        frame_height = vehiculo_elegido['height']
        frame_width = spritesheet.sheet.get_width() 
        for i in range(vehiculo_elegido['num_frames']):
            frame = spritesheet.get_image(0, i * frame_height, frame_width, frame_height)
            self.animation_frames.append(frame)

        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()
        self.animation_speed = 180
        self.image = self.animation_frames[self.current_frame]
        
        self.rect = self.image.get_rect()
        self.hitbox = self.rect.inflate(-self.rect.width * 0.7, -self.rect.height * 0.3)
        
        x = random.randint(350, 900)
        y = random.randint(-600, -300)
        self.rect.center = (x, y)
        self.hitbox.center = self.rect.center
        
        self.speed_propia = random.randint(50, 150)
        self.scroll_speed = scroll_speed
        self.is_active = False

    def update(self, dt):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_speed:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
            self.image = self.animation_frames[self.current_frame]

        self.rect.y += (self.scroll_speed + self.speed_propia) * dt
        self.hitbox.center = self.rect.center

        if not self.is_active and self.rect.top > 0:
            self.is_active = True
        if self.rect.top > settings.SCREEN_HEIGHT:
            self.kill()

class Periodico(pygame.sprite.Sprite):
    def __init__(self, start_pos, target_pos, scroll_speed):
        super().__init__()
        self.image = pygame.image.load("assets/images/periodico.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (32, 32))
        self.rect = self.image.get_rect(center=start_pos)
        
        # --- NUEVO: Bandera para saber si acertó ---
        self.acerto = False
        
        self.scroll_speed = scroll_speed
        self.speed = 600
        
        distancia = math.hypot(target_pos[0] - start_pos[0], target_pos[1] - start_pos[1])
        if distancia == 0:
            self.vel_x, self.vel_y = 0, -self.speed
        else:
            self.vel_x = (target_pos[0] - start_pos[0]) / distancia * self.speed
            self.vel_y = (target_pos[1] - start_pos[1]) / distancia * self.speed

    def update(self, dt):
        self.rect.x += self.vel_x * dt
        self.rect.y += self.vel_y * dt + self.scroll_speed * dt
        # La eliminación ahora la maneja el state para la penalización