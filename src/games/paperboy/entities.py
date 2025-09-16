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

class PlayerPaperboy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.animations = {
            'ride': self.cargar_animacion(settings.resource_path("images/Paperboy_ride.png")),
            'spin_left': self.cargar_animacion(settings.resource_path("images/Paperboy_spin_left.png")),
            'spin_right': self.cargar_animacion(settings.resource_path("images/Paperboy_spin_right.png")),
            'throw_left': self.cargar_animacion(settings.resource_path("images/Paperboy_throw_left.png"), False),
            'throw_right': self.cargar_animacion(settings.resource_path("images/Paperboy_throw_right.png"), False)
        }
        self.estado_animacion = 'ride'
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()
        self.animation_speed = 120
        self.image = self.animations[self.estado_animacion]['frames'][self.current_frame]
        self.rect = self.image.get_rect(centerx=settings.SCREEN_WIDTH / 2, bottom=settings.SCREEN_HEIGHT - 50)
        
        # --- LÓGICA DE VELOCIDAD MEJORADA ---
        self.original_speed = 350
        self.speed = self.original_speed
        
        self.limite_izquierdo = 450
        self.limite_derecho = 860
        self.hitbox = self.rect.inflate(-self.rect.width * 0.75, -self.rect.height * 0.40)
        
        # Variables para el efecto de ralentización
        self.is_slowed = False
        self.slow_timer = 0
        self.slow_duration = 2000 # 2 segundos

    def cargar_animacion(self, spritesheet_path, loop=True):
        spritesheet = SpriteSheet(spritesheet_path)
        frames = []
        num_frames = spritesheet.sheet.get_height() // PLAYER_FRAME_HEIGHT
        for i in range(num_frames):
            frame = spritesheet.get_image(0, i * PLAYER_FRAME_HEIGHT, PLAYER_FRAME_WIDTH, PLAYER_FRAME_HEIGHT)
            frames.append(frame)
        return {'frames': frames, 'loop': loop}

    def update(self, dt):
        # Manejo del efecto de ralentización
        if self.is_slowed:
            self.speed = self.original_speed * 0.5 # 50% de la velocidad normal
            self.slow_timer -= dt * 1000
            if self.slow_timer <= 0:
                self.is_slowed = False
        else:
            self.speed = self.original_speed

        # Lógica de animación
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

        # Lógica de movimiento
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

    def ralentizar(self):
        """Activa el efecto de ralentización."""
        if not self.is_slowed:
            self.is_slowed = True
            self.slow_timer = self.slow_duration


class Buzon(pygame.sprite.Sprite):
    def __init__(self, x, y, scroll_speed, lado):
        super().__init__()
        colores = ["blue", "green", "red", "yellow"]
        img_path = f"images/mailbox_{random.choice(colores)}.png"
        self.image = pygame.image.load(settings.resource_path(img_path)).convert_alpha()
        self.image = pygame.transform.scale(self.image, (BUZON_WIDTH, BUZON_HEIGHT))
        if lado == "izquierda":
            self.image = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect(center=(x, y))
        self.scroll_speed = scroll_speed

    def update(self, dt):
        self.rect.y += self.scroll_speed * dt
        # El state se encarga de matarlo si sale de pantalla

class Casa(pygame.sprite.Sprite):
    def __init__(self, scroll_speed, limite_cesped_izq, limite_cesped_der):
        super().__init__()
        
        # --- LÓGICA DE DIBUJO PROCEDURAL MEJORADA ---
        ancho_casa = random.randint(150, 250)
        alto_casa = random.randint(150, 250)
        self.image = pygame.Surface((ancho_casa, alto_casa), pygame.SRCALPHA)
        
        # Paletas de colores
        colores_pared = [(139, 69, 19), (112, 128, 144), (188, 143, 143)]
        colores_techo_base = [(128, 0, 0), (47, 79, 79), (85, 107, 47)]
        color_pared = random.choice(colores_pared)
        color_techo = random.choice(colores_techo_base)
        
        # --- LÍNEA CORREGIDA AQUÍ ---
        # Usamos max(0, ...) para asegurarnos de que el valor no sea negativo
        color_ladrillo = (
            max(0, color_techo[0] - 20), 
            max(0, color_techo[1] - 20), 
            max(0, color_techo[2] - 20)
        )
        color_camino = (180, 180, 180)

        # Cuerpo de la casa
        pygame.draw.rect(self.image, color_pared, (0, 20, ancho_casa, alto_casa - 20))
        # Techo de ladrillos
        alto_techo = int(alto_casa * 0.8)
        pygame.draw.rect(self.image, color_techo, (0, 0, ancho_casa, alto_techo))
        tam_ladrillo = 20
        for y in range(0, alto_techo, tam_ladrillo):
            for x in range(0, ancho_casa, tam_ladrillo):
                offset = tam_ladrillo // 2 if (y // tam_ladrillo) % 2 == 0 else 0
                pygame.draw.rect(self.image, color_ladrillo, (x + offset, y, tam_ladrillo, tam_ladrillo), 1)

        # Posicionamiento y creación del buzón
        self.rect = self.image.get_rect()
        lado = random.choice(["izquierda", "derecha"])
        if lado == "izquierda":
            self.rect.right = random.randint(20, limite_cesped_izq - 20)
            camino_rect = pygame.Rect(ancho_casa - 30, alto_casa - 60, 30, 40)
            pygame.draw.rect(self.image, color_camino, camino_rect)
            buzon_x = self.rect.right + BUZON_WIDTH / 2
        else:
            self.rect.left = random.randint(limite_cesped_der + 20, settings.SCREEN_WIDTH - 20)
            camino_rect = pygame.Rect(0, alto_casa - 60, 30, 40)
            pygame.draw.rect(self.image, color_camino, camino_rect)
            buzon_x = self.rect.left - BUZON_WIDTH / 2

        self.rect.bottom = random.randint(-50, 0)
        self.scroll_speed = scroll_speed
        
        self.buzon = Buzon(buzon_x, self.rect.bottom - 40, scroll_speed, lado)

    def update(self, dt):
        self.rect.y += self.scroll_speed * dt
        if self.rect.top > settings.SCREEN_HEIGHT:
            self.kill()
            self.buzon.kill()

class Auto(pygame.sprite.Sprite):
    def __init__(self, scroll_speed, limite_izq_calle, limite_der_calle):
        super().__init__()
        tipos_de_vehiculos = [
            {'nombre': 'car_blue', 'height': 400, 'num_frames': 2},
            {'nombre': 'car_red', 'height': 400, 'num_frames': 2},
            {'nombre': 'car_white', 'height': 400, 'num_frames': 2},
            {'nombre': 'bus', 'height': 550, 'num_frames': 2},
            {'nombre': 'police_car', 'height': 420, 'num_frames': 2}
        ]
        vehiculo_elegido = random.choice(tipos_de_vehiculos)
        
        # --- NUEVO: Identificamos si es un auto de policía ---
        self.es_policia = vehiculo_elegido['nombre'] == 'police_car'
        
        path = f"images/{vehiculo_elegido['nombre']}_move.png"
        spritesheet = SpriteSheet(settings.resource_path(path))
        
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
        
        x = random.randint(limite_izq_calle + self.rect.width // 2, limite_der_calle - self.rect.width // 2)
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
        self.image = pygame.image.load(settings.resource_path("images/periodico.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (32, 32))
        self.rect = self.image.get_rect(center=start_pos)
        
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


class ManchaAceite(pygame.sprite.Sprite):
    def __init__(self, scroll_speed, limite_izq, limite_der):
        super().__init__()
        self.image = pygame.Surface((100, 80), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, (20, 20, 20), self.image.get_rect())
        self.rect = self.image.get_rect(
            centerx=random.randint(limite_izq, limite_der),
            bottom=random.randint(-200, -50)
        )
        self.scroll_speed = scroll_speed

    def update(self, dt):
        self.rect.y += self.scroll_speed * dt
        if self.rect.top > settings.SCREEN_HEIGHT:
            self.kill()

class PeriodicoDevuelto(pygame.sprite.Sprite):
    def __init__(self, start_pos, player_pos, scroll_speed):
        super().__init__()
        self.image = pygame.image.load(settings.resource_path("images/periodico.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (32, 32))
        self.rect = self.image.get_rect(center=start_pos)
        self.speed = 500
        
        dx = player_pos[0] - start_pos[0]
        dy = player_pos[1] - start_pos[1]
        distancia = math.hypot(dx, dy)
        if distancia > 0:
            self.vel_x = (dx / distancia) * self.speed
            self.vel_y = (dy / distancia) * self.speed
        else:
            self.vel_x, self.vel_y = 0, self.speed

    def update(self, dt):
        self.rect.x += self.vel_x * dt
        self.rect.y += self.vel_y * dt
        screen_rect = pygame.Rect(0, 0, settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
        
        if not screen_rect.colliderect(self.rect):
            self.kill()