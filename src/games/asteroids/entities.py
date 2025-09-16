import pygame
import math
import random

# Colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)

# Físicas
THRUST = 0.12
FRICTION = 0.998
MAX_SPEED = 6.0
ROTATION_SPEED = 3.5
BULLET_SPEED = 10.0
BULLET_LIFETIME = 60  # frames
FIRE_COOLDOWN = 12  # frames
BULLET_GRACE_PERIOD = 5  # frames de gracia para no colisionar con la nave

# Tamaños de asteroides (radio, puntos)
ASTEROID_SIZES = {
    "large": {"radius": 50, "points": 20, "split_count": 3},
    "medium": {"radius": 30, "points": 50, "split_count": 2},
    "small": {"radius": 15, "points": 100, "split_count": 0}
}

# Clase para la nave del jugador
class Ship(pygame.sprite.Sprite):
    def __init__(self, x, y, screen_width, screen_height):
        super().__init__()
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.angle = 0  # en grados
        self.radius = 10
        self.thrusting = False
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.update_image()
        
    def update_image(self):
        # Crear una superficie para la nave
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        
        # Dibujar la nave como un triángulo
        points = [
            (self.radius, 0),  # punta
            (0, self.radius * 2),  # esquina inferior izquierda
            (self.radius * 2, self.radius * 2)  # esquina inferior derecha
        ]
        
        # Rotar los puntos según el ángulo
        rotated_points = []
        for px, py in points:
            # Convertir a coordenadas relativas al centro
            rx = px - self.radius
            ry = py - self.radius
            
            # Rotar
            angle_rad = math.radians(self.angle)
            rrx = rx * math.cos(angle_rad) - ry * math.sin(angle_rad)
            rry = rx * math.sin(angle_rad) + ry * math.cos(angle_rad)
            
            # Convertir de vuelta a coordenadas de superficie
            rotated_points.append((rrx + self.radius, rry + self.radius))
        
        # Dibujar el triángulo
        color = WHITE if not self.invulnerable or self.invulnerable_timer % 10 < 5 else (100, 100, 100)
        pygame.draw.polygon(self.image, color, rotated_points)
        
        # Si está acelerando, dibujar la llama
        if self.thrusting:
            flame_points = [
                (self.radius * 0.8, self.radius * 1.8),
                (self.radius, self.radius * 2.5),
                (self.radius * 1.2, self.radius * 1.8)
            ]
            
            rotated_flame = []
            for px, py in flame_points:
                rx = px - self.radius
                ry = py - self.radius
                
                angle_rad = math.radians(self.angle)
                rrx = rx * math.cos(angle_rad) - ry * math.sin(angle_rad)
                rry = rx * math.sin(angle_rad) + ry * math.cos(angle_rad)
                
                rotated_flame.append((rrx + self.radius, rry + self.radius))
            
            pygame.draw.polygon(self.image, YELLOW, rotated_flame)
        
        self.rect = self.image.get_rect(center=(self.x, self.y))
    
    def rotate(self, direction):
        self.angle += direction * ROTATION_SPEED
        self.angle %= 360
        self.update_image()
    
    def thrust(self):
        # Aplicar aceleración en la dirección de la nave
        angle_rad = math.radians(self.angle)
        self.vx += THRUST * math.sin(angle_rad)
        self.vy -= THRUST * math.cos(angle_rad)
        
        # Limitar velocidad máxima
        speed = math.sqrt(self.vx**2 + self.vy**2)
        if speed > MAX_SPEED:
            self.vx = (self.vx / speed) * MAX_SPEED
            self.vy = (self.vy / speed) * MAX_SPEED
        
        self.thrusting = True
        self.update_image()
    
    def update(self):
        # Aplicar fricción
        self.vx *= FRICTION
        self.vy *= FRICTION
        
        # Actualizar posición
        self.x += self.vx
        self.y += self.vy
        
        # Wrap-around
        if self.x < 0:
            self.x = self.screen_width
        elif self.x > self.screen_width:
            self.x = 0
            
        if self.y < 0:
            self.y = self.screen_height
        elif self.y > self.screen_height:
            self.y = 0
        
        # Actualizar imagen y rectángulo
        self.rect.center = (self.x, self.y)
        
        # Actualizar invulnerabilidad
        if self.invulnerable:
            self.invulnerable_timer -= 1
            if self.invulnerable_timer <= 0:
                self.invulnerable = False
            self.update_image()
        
        # Resetear thrust
        self.thrusting = False
        self.update_image()
    
    def draw(self, surface):
        surface.blit(self.image, self.rect)

# Clase para las balas
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, screen_width, screen_height, owner="player"):
        super().__init__()
        self.x = x
        self.y = y
        self.angle = angle
        self.radius = 3
        self.lifetime = BULLET_LIFETIME
        self.owner = owner
        self.frames_alive = 0  # Para el tiempo de gracia
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Calcular velocidad
        angle_rad = math.radians(angle)
        self.vx = BULLET_SPEED * math.sin(angle_rad)
        self.vy = -BULLET_SPEED * math.cos(angle_rad)
        
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, WHITE, (self.radius, self.radius), self.radius)
        self.rect = self.image.get_rect(center=(self.x, self.y))
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1
        self.frames_alive += 1
        
        # Wrap-around
        if self.x < 0:
            self.x = self.screen_width
        elif self.x > self.screen_width:
            self.x = 0
            
        if self.y < 0:
            self.y = self.screen_height
        elif self.y > self.screen_height:
            self.y = 0
        
        self.rect.center = (self.x, self.y)
        
        # Si la bala ha vivido suficiente tiempo, eliminarla
        if self.lifetime <= 0:
            self.kill()
    
    def draw(self, surface):
        surface.blit(self.image, self.rect)

# Clase para los asteroides
class Asteroid(pygame.sprite.Sprite):
    def __init__(self, x, y, screen_width, screen_height, size="large"):
        super().__init__()
        self.x = x
        self.y = y
        self.size = size
        self.radius = ASTEROID_SIZES[size]["radius"]
        self.points = ASTEROID_SIZES[size]["points"]
        self.split_count = ASTEROID_SIZES[size]["split_count"]
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Velocidad aleatoria
        speed = random.uniform(1.0, 3.0) if size == "large" else random.uniform(1.5, 4.0)
        angle = random.uniform(0, 360)
        angle_rad = math.radians(angle)
        self.vx = speed * math.sin(angle_rad)
        self.vy = -speed * math.cos(angle_rad)
        
        # Rotación aleatoria
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-2, 2)
        
        # Crear una forma irregular para el asteroide
        self.vertices = []
        num_vertices = random.randint(8, 12)
        for i in range(num_vertices):
            angle = (360 / num_vertices) * i
            # Añadir variación al radio para hacer irregular
            r = self.radius * random.uniform(0.8, 1.2)
            angle_rad = math.radians(angle)
            x_vert = r * math.sin(angle_rad)
            y_vert = -r * math.cos(angle_rad)
            self.vertices.append((x_vert, y_vert))
        
        self.update_image()
    
    def update_image(self):
        self.image = pygame.Surface((self.radius * 2.5, self.radius * 2.5), pygame.SRCALPHA)
        
        # Rotar los vértices
        rotated_vertices = []
        angle_rad = math.radians(self.rotation)
        for vx, vy in self.vertices:
            rx = vx * math.cos(angle_rad) - vy * math.sin(angle_rad)
            ry = vx * math.sin(angle_rad) + vy * math.cos(angle_rad)
            rotated_vertices.append((rx + self.radius * 1.25, ry + self.radius * 1.25))
        
        pygame.draw.polygon(self.image, WHITE, rotated_vertices, 1)
        self.rect = self.image.get_rect(center=(self.x, self.y))
    
    def update(self):
        # Actualizar posición
        self.x += self.vx
        self.y += self.vy
        
        # Actualizar rotación
        self.rotation += self.rotation_speed
        self.rotation %= 360
        
        # Wrap-around
        if self.x < 0:
            self.x = self.screen_width
        elif self.x > self.screen_width:
            self.x = 0
            
        if self.y < 0:
            self.y = self.screen_height
        elif self.y > self.screen_height:
            self.y = 0
        
        # Actualizar imagen y rectángulo
        self.update_image()
        self.rect.center = (self.x, self.y)
    
    def draw(self, surface):
        surface.blit(self.image, self.rect)
    
    def split(self):
        # Crear asteroides más pequeños
        new_asteroids = []
        if self.size == "large":
            new_size = "medium"
        elif self.size == "medium":
            new_size = "small"
        else:
            return new_asteroids  # Los asteroides pequeños no se dividen
        
        for _ in range(self.split_count):
            # Crear nuevo asteroide en la posición actual con velocidad aleatoria
            new_asteroid = Asteroid(self.x, self.y, self.screen_width, self.screen_height, new_size)
            new_asteroids.append(new_asteroid)
        
        return new_asteroids

# Clase para los ovnis (UFOs)
class UFO(pygame.sprite.Sprite):
    def __init__(self, screen_width, screen_height):
        super().__init__()
        self.radius = 20
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.x = random.choice([0, self.screen_width])
        self.y = random.randint(50, self.screen_height - 50)
        
        # Dirección de movimiento (horizontal)
        self.vx = 2 if self.x == 0 else -2
        self.vy = 0
        
        # Temporizador de disparo
        self.shoot_timer = random.randint(60, 180)
        
        self.update_image()
    
    def update_image(self):
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        
        # Dibujar un ovni simple (disco con cúpula)
        pygame.draw.ellipse(self.image, GREEN, (0, self.radius, self.radius * 2, self.radius))
        pygame.draw.ellipse(self.image, CYAN, (self.radius * 0.5, 0, self.radius, self.radius))
        
        self.rect = self.image.get_rect(center=(self.x, self.y))
    
    def update(self):
        # Movimiento horizontal
        self.x += self.vx
        
        # Si sale de la pantalla, eliminar
        if self.x < -self.radius or self.x > self.screen_width + self.radius:
            self.kill()
            return
        
        # Temporizador de disparo
        self.shoot_timer -= 1
        if self.shoot_timer <= 0:
            self.shoot_timer = random.randint(60, 180)
            return True  # Indica que debe disparar
        
        self.rect.center = (self.x, self.y)
        return False
    
    def draw(self, surface):
        surface.blit(self.image, self.rect)
    
    def get_shoot_direction(self, target_x, target_y):
        # Calcular dirección hacia el objetivo
        dx = target_x - self.x
        dy = target_y - self.y
        angle = math.degrees(math.atan2(dy, dx)) + 90
        return angle % 360

# Clase para los power-ups
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, power_type):
        super().__init__()
        self.x = x
        self.y = y
        self.radius = 15
        self.power_type = power_type  # "shield", "triple_shot", "extra_life", "slow_time"
        self.lifetime = 300  # frames (5 segundos a 60 FPS)
        self.pulse = 0
        
        self.update_image()
    
    def update_image(self):
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        
        # Dibujar según el tipo de power-up
        if self.power_type == "shield":
            # Escudo
            pygame.draw.circle(self.image, BLUE, (self.radius, self.radius), self.radius, 2)
            pygame.draw.circle(self.image, CYAN, (self.radius, self.radius), self.radius - 5, 1)
        elif self.power_type == "triple_shot":
            # Triple disparo
            pygame.draw.circle(self.image, YELLOW, (self.radius, self.radius), self.radius, 2)
            for angle in [0, 120, 240]:
                angle_rad = math.radians(angle)
                end_x = self.radius + (self.radius - 5) * math.sin(angle_rad)
                end_y = self.radius - (self.radius - 5) * math.cos(angle_rad)
                pygame.draw.line(self.image, YELLOW, (self.radius, self.radius), (end_x, end_y), 2)
        elif self.power_type == "extra_life":
            # Vida extra
            pygame.draw.circle(self.image, GREEN, (self.radius, self.radius), self.radius, 2)
            # Dibujar una pequeña nave
            points = [
                (self.radius, self.radius - 5),
                (self.radius - 5, self.radius + 5),
                (self.radius + 5, self.radius + 5)
            ]
            pygame.draw.polygon(self.image, GREEN, points)
        elif self.power_type == "slow_time":
            # Tiempo lento
            pygame.draw.circle(self.image, MAGENTA, (self.radius, self.radius), self.radius, 2)
            # Dibujar un reloj simple
            pygame.draw.circle(self.image, MAGENTA, (self.radius, self.radius), 5, 1)
            pygame.draw.line(self.image, MAGENTA, (self.radius, self.radius), (self.radius, self.radius - 5), 1)
            pygame.draw.line(self.image, MAGENTA, (self.radius, self.radius), (self.radius + 3, self.radius), 1)
        
        self.rect = self.image.get_rect(center=(self.x, self.y))
    
    def update(self):
        self.lifetime -= 1
        self.pulse = (self.pulse + 1) % 20
        
        # Hacer que parpadee cuando está a punto de desaparecer
        if self.lifetime < 60 and self.lifetime % 10 < 5:
            self.image.set_alpha(128)
        else:
            self.image.set_alpha(255)
        
        # Actualizar tamaño con pulso
        scale = 1.0 + 0.1 * math.sin(self.pulse * math.pi / 10)
        self.radius = 15 * scale
        self.update_image()
        
        # Si ha vivido suficiente tiempo, eliminar
        if self.lifetime <= 0:
            self.kill()
    
    def draw(self, surface):
        surface.blit(self.image, self.rect)

# Clase para efectos de partículas
class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, color, velocity, lifetime):
        super().__init__()
        self.x = x
        self.y = y
        self.color = color
        self.vx, self.vy = velocity
        self.lifetime = lifetime
        self.initial_lifetime = lifetime
        self.radius = random.randint(1, 3)
        
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (self.radius, self.radius), self.radius)
        self.rect = self.image.get_rect(center=(self.x, self.y))
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1
        
        # Desvanecer con el tiempo
        alpha = int(255 * (self.lifetime / self.initial_lifetime))
        self.image.set_alpha(alpha)
        
        self.rect.center = (self.x, self.y)
        
        # Si ha vivido suficiente tiempo, eliminar
        if self.lifetime <= 0:
            self.kill()
    
    def draw(self, surface):
        surface.blit(self.image, self.rect)
