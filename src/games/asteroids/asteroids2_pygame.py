import pygame
import math
import random
import os
from enum import Enum

# Inicializar Pygame
pygame.init()

# Constantes
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

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

# Tamaños de asteroides (radio, puntos)
ASTEROID_SIZES = {
    "large": {"radius": 50, "points": 20, "split_count": 3},
    "medium": {"radius": 30, "points": 50, "split_count": 2},
    "small": {"radius": 15, "points": 100, "split_count": 0}
}

# Estados del juego
class GameState(Enum):
    MENU = 1
    PLAYING = 2
    PAUSED = 3
    GAME_OVER = 4
    HIGH_SCORES = 5

# Clase para la nave del jugador
class Ship(pygame.sprite.Sprite):
    def __init__(self, x, y):
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
            self.x = SCREEN_WIDTH
        elif self.x > SCREEN_WIDTH:
            self.x = 0
            
        if self.y < 0:
            self.y = SCREEN_HEIGHT
        elif self.y > SCREEN_HEIGHT:
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
    def __init__(self, x, y, angle):
        super().__init__()
        self.x = x
        self.y = y
        self.angle = angle
        self.radius = 3
        self.lifetime = BULLET_LIFETIME
        
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
        
        # Wrap-around
        if self.x < 0:
            self.x = SCREEN_WIDTH
        elif self.x > SCREEN_WIDTH:
            self.x = 0
            
        if self.y < 0:
            self.y = SCREEN_HEIGHT
        elif self.y > SCREEN_HEIGHT:
            self.y = 0
        
        self.rect.center = (self.x, self.y)
        
        # Si la bala ha vivido suficiente tiempo, eliminarla
        if self.lifetime <= 0:
            self.kill()
    
    def draw(self, surface):
        surface.blit(self.image, self.rect)

# Clase para los asteroides
class Asteroid(pygame.sprite.Sprite):
    def __init__(self, x, y, size="large"):
        super().__init__()
        self.x = x
        self.y = y
        self.size = size
        self.radius = ASTEROID_SIZES[size]["radius"]
        self.points = ASTEROID_SIZES[size]["points"]
        self.split_count = ASTEROID_SIZES[size]["split_count"]
        
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
            x = r * math.sin(angle_rad)
            y = -r * math.cos(angle_rad)
            self.vertices.append((x, y))
        
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
            self.x = SCREEN_WIDTH
        elif self.x > SCREEN_WIDTH:
            self.x = 0
            
        if self.y < 0:
            self.y = SCREEN_HEIGHT
        elif self.y > SCREEN_HEIGHT:
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
            new_asteroid = Asteroid(self.x, self.y, new_size)
            new_asteroids.append(new_asteroid)
        
        return new_asteroids

# Clase para los ovnis (UFOs)
class UFO(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.radius = 20
        self.x = random.choice([0, SCREEN_WIDTH])
        self.y = random.randint(50, SCREEN_HEIGHT - 50)
        
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
        if self.x < -self.radius or self.x > SCREEN_WIDTH + self.radius:
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

# Clase principal del juego
class AsteroidsGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Asteroids")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 24)
        self.big_font = pygame.font.SysFont('Arial', 48)
        
        # Estado del juego
        self.state = GameState.MENU
        self.running = True
        
        # Grupos de sprites
        self.all_sprites = pygame.sprite.Group()
        self.asteroids = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.ufos = pygame.sprite.Group()
        self.power_ups = pygame.sprite.Group()
        self.particles = pygame.sprite.Group()
        
        # Variables del juego
        self.score = 0
        self.lives = 3
        self.level = 1
        self.high_scores = self.load_high_scores()
        
        # Power-ups activos
        self.active_power_ups = {
            "shield": 0,
            "triple_shot": 0,
            "slow_time": 0
        }
        
        # Temporizadores
        self.ufo_spawn_timer = random.randint(600, 1200)  # 10-20 segundos a 60 FPS
        self.power_up_spawn_timer = random.randint(900, 1800)  # 15-30 segundos
        
        # Control de disparo
        self.can_fire = True
        self.fire_cooldown_timer = 0
    
    def load_high_scores(self):
        # Cargar high scores desde un archivo
        try:
            if os.path.exists("highscores.txt"):
                with open("highscores.txt", "r") as f:
                    scores = [int(line.strip()) for line in f.readlines()]
                    return sorted(scores, reverse=True)[:10]  # Top 10
        except:
            pass
        return []
    
    def save_high_scores(self):
        # Guardar high scores en un archivo
        try:
            with open("highscores.txt", "w") as f:
                for score in self.high_scores:
                    f.write(f"{score}\n")
        except:
            pass
    
    def add_high_score(self, score):
        self.high_scores.append(score)
        self.high_scores = sorted(self.high_scores, reverse=True)[:10]
        self.save_high_scores()
    
    def start_game(self):
        # Limpiar grupos
        self.all_sprites.empty()
        self.asteroids.empty()
        self.bullets.empty()
        self.ufos.empty()
        self.power_ups.empty()
        self.particles.empty()
        
        # Resetear variables
        self.score = 0
        self.lives = 3
        self.level = 1
        self.active_power_ups = {
            "shield": 0,
            "triple_shot": 0,
            "slow_time": 0
        }
        self.ufo_spawn_timer = random.randint(600, 1200)
        self.power_up_spawn_timer = random.randint(900, 1800)
        
        # Crear nave
        self.ship = Ship(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.all_sprites.add(self.ship)
        
        # Crear asteroides iniciales
        self.spawn_asteroids(4)
        
        # Cambiar estado
        self.state = GameState.PLAYING
    
    def spawn_asteroids(self, count):
        for _ in range(count):
            # Asegurar que no aparezcan demasiado cerca de la nave
            while True:
                x = random.randint(50, SCREEN_WIDTH - 50)
                y = random.randint(50, SCREEN_HEIGHT - 50)
                
                # Calcular distancia a la nave
                dx = x - self.ship.x
                dy = y - self.ship.y
                distance = math.sqrt(dx**2 + dy**2)
                
                if distance > 100:  # Distancia mínima
                    break
            
            asteroid = Asteroid(x, y, "large")
            self.all_sprites.add(asteroid)
            self.asteroids.add(asteroid)
    
    def spawn_ufo(self):
        ufo = UFO()
        self.all_sprites.add(ufo)
        self.ufos.add(ufo)
    
    def spawn_power_up(self, x, y):
        # Elegir un tipo de power-up aleatorio
        power_type = random.choice(["shield", "triple_shot", "extra_life", "slow_time"])
        power_up = PowerUp(x, y, power_type)
        self.all_sprites.add(power_up)
        self.power_ups.add(power_up)
    
    def create_explosion(self, x, y, color, count=30):
        for _ in range(count):
            # Velocidad aleatoria
            speed = random.uniform(0.5, 3.0)
            angle = random.uniform(0, 360)
            angle_rad = math.radians(angle)
            vx = speed * math.sin(angle_rad)
            vy = -speed * math.cos(angle_rad)
            
            # Lifetime aleatorio
            lifetime = random.randint(20, 40)
            
            particle = Particle(x, y, color, (vx, vy), lifetime)
            self.all_sprites.add(particle)
            self.particles.add(particle)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.KEYDOWN:
                if self.state == GameState.MENU:
                    if event.key == pygame.K_RETURN:
                        self.start_game()
                    elif event.key == pygame.K_h:
                        self.state = GameState.HIGH_SCORES
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
                
                elif self.state == GameState.HIGH_SCORES:
                    if event.key == pygame.K_ESCAPE:
                        self.state = GameState.MENU
                
                elif self.state == GameState.PLAYING:
                    if event.key == pygame.K_SPACE and self.can_fire:
                        self.fire_bullet()
                    elif event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                        self.state = GameState.PAUSED
                
                elif self.state == GameState.PAUSED:
                    if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                        self.state = GameState.PLAYING
                
                elif self.state == GameState.GAME_OVER:
                    if event.key == pygame.K_RETURN:
                        self.start_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.state = GameState.MENU
    
    def fire_bullet(self):
        # Disparar una bala en la dirección de la nave
        if self.active_power_ups["triple_shot"] > 0:
            # Triple disparo
            for angle_offset in [-10, 0, 10]:
                angle = (self.ship.angle + angle_offset) % 360
                bullet = Bullet(self.ship.x, self.ship.y, angle)
                self.all_sprites.add(bullet)
                self.bullets.add(bullet)
        else:
            # Disparo normal
            bullet = Bullet(self.ship.x, self.ship.y, self.ship.angle)
            self.all_sprites.add(bullet)
            self.bullets.add(bullet)
        
        # Iniciar cooldown
        self.can_fire = False
        self.fire_cooldown_timer = FIRE_COOLDOWN
        
        # Efecto de sonido (simulado con partículas)
        self.create_explosion(self.ship.x, self.ship.y, YELLOW, 5)
    
    def update(self):
        if self.state != GameState.PLAYING:
            return
        
        # Obtener teclas presionadas
        keys = pygame.key.get_pressed()
        
        # Rotación de la nave
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.ship.rotate(-1)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.ship.rotate(1)
        
        # Thrust
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.ship.thrust()
            # Efecto de partículas para el thrust
            if random.random() < 0.7:
                angle_rad = math.radians(self.ship.angle + 180)
                vx = 2 * math.sin(angle_rad)
                vy = -2 * math.cos(angle_rad)
                particle = Particle(self.ship.x, self.ship.y, YELLOW, (vx, vy), 10)
                self.all_sprites.add(particle)
                self.particles.add(particle)
        
        # Actualizar cooldown de disparo
        if not self.can_fire:
            self.fire_cooldown_timer -= 1
            if self.fire_cooldown_timer <= 0:
                self.can_fire = True
        
        # Actualizar todos los sprites
        self.all_sprites.update()
        
        # Actualizar power-ups activos
        for power in self.active_power_ups:
            if self.active_power_ups[power] > 0:
                self.active_power_ups[power] -= 1
        
        # Comprobar colisiones
        
        # Balas con asteroides
        for bullet in self.bullets:
            asteroid_hits = pygame.sprite.spritecollide(bullet, self.asteroids, False, pygame.sprite.collide_circle)
            for asteroid in asteroid_hits:
                # Añadir puntuación
                self.score += asteroid.points
                
                # Crear explosión
                self.create_explosion(asteroid.x, asteroid.y, WHITE, 20)
                
                # Dividir asteroide si es grande o mediano
                new_asteroids = asteroid.split()
                for new_asteroid in new_asteroids:
                    self.all_sprites.add(new_asteroid)
                    self.asteroids.add(new_asteroid)
                
                # Eliminar asteroide y bala
                asteroid.kill()
                bullet.kill()
                
                # Posibilidad de generar power-up
                if random.random() < 0.1:  # 10% de probabilidad
                    self.spawn_power_up(asteroid.x, asteroid.y)
        
        # Nave con asteroides
        if not self.ship.invulnerable:
            asteroid_hits = pygame.sprite.spritecollide(self.ship, self.asteroids, False, pygame.sprite.collide_circle)
            for asteroid in asteroid_hits:
                if self.active_power_ups["shield"] > 0:
                    # El escudo protege
                    self.active_power_ups["shield"] = 0
                    self.create_explosion(self.ship.x, self.ship.y, BLUE, 30)
                else:
                    # Perder una vida
                    self.lives -= 1
                    self.create_explosion(self.ship.x, self.ship.y, RED, 40)
                    
                    if self.lives <= 0:
                        self.game_over()
                    else:
                        # Respawnear la nave con invulnerabilidad
                        self.ship.x = SCREEN_WIDTH // 2
                        self.ship.y = SCREEN_HEIGHT // 2
                        self.ship.vx = 0
                        self.ship.vy = 0
                        self.ship.invulnerable = True
                        self.ship.invulnerable_timer = 150  # 2.5 segundos a 60 FPS
                
                break
        
        # Nave con power-ups
        power_up_hits = pygame.sprite.spritecollide(self.ship, self.power_ups, True, pygame.sprite.collide_circle)
        for power_up in power_up_hits:
            if power_up.power_type == "shield":
                self.active_power_ups["shield"] = 300  # 5 segundos a 60 FPS
                self.create_explosion(power_up.x, power_up.y, BLUE, 20)
            elif power_up.power_type == "triple_shot":
                self.active_power_ups["triple_shot"] = 300  # 5 segundos a 60 FPS
                self.create_explosion(power_up.x, power_up.y, YELLOW, 20)
            elif power_up.power_type == "extra_life":
                self.lives += 1
                self.create_explosion(power_up.x, power_up.y, GREEN, 20)
            elif power_up.power_type == "slow_time":
                self.active_power_ups["slow_time"] = 300  # 5 segundos a 60 FPS
                self.create_explosion(power_up.x, power_up.y, MAGENTA, 20)
        
        # Balas con ovnis
        for bullet in self.bullets:
            ufo_hits = pygame.sprite.spritecollide(bullet, self.ufos, False, pygame.sprite.collide_circle)
            for ufo in ufo_hits:
                # Añadir puntuación
                self.score += 200
                
                # Crear explosión
                self.create_explosion(ufo.x, ufo.y, GREEN, 30)
                
                # Eliminar ovni y bala
                ufo.kill()
                bullet.kill()
        
        # Nave con ovnis
        if not self.ship.invulnerable:
            ufo_hits = pygame.sprite.spritecollide(self.ship, self.ufos, False, pygame.sprite.collide_circle)
            for ufo in ufo_hits:
                if self.active_power_ups["shield"] > 0:
                    # El escudo protege
                    self.active_power_ups["shield"] = 0
                    self.create_explosion(self.ship.x, self.ship.y, BLUE, 30)
                else:
                    # Perder una vida
                    self.lives -= 1
                    self.create_explosion(self.ship.x, self.ship.y, RED, 40)
                    
                    if self.lives <= 0:
                        self.game_over()
                    else:
                        # Respawnear la nave con invulnerabilidad
                        self.ship.x = SCREEN_WIDTH // 2
                        self.ship.y = SCREEN_HEIGHT // 2
                        self.ship.vx = 0
                        self.ship.vy = 0
                        self.ship.invulnerable = True
                        self.ship.invulnerable_timer = 150  # 2.5 segundos a 60 FPS
                
                # Eliminar ovni
                ufo.kill()
                break
        
        # Disparos de ovnis
        for ufo in self.ufos:
            should_shoot = ufo.update()
            if should_shoot:
                # Calcular dirección hacia la nave
                angle = ufo.get_shoot_direction(self.ship.x, self.ship.y)
                
                # Crear bala
                bullet = Bullet(ufo.x, ufo.y, angle)
                self.all_sprites.add(bullet)
                self.bullets.add(bullet)
        
        # Balas de ovnis con la nave
        if not self.ship.invulnerable:
            for bullet in self.bullets:
                # Comprobar si la bala es de un ovni (no de la nave)
                if bullet not in self.all_sprites:
                    continue
                
                # Calcular distancia a la nave
                dx = bullet.x - self.ship.x
                dy = bullet.y - self.ship.y
                distance = math.sqrt(dx**2 + dy**2)
                
                if distance < self.ship.radius + bullet.radius:
                    if self.active_power_ups["shield"] > 0:
                        # El escudo protege
                        self.active_power_ups["shield"] = 0
                        self.create_explosion(self.ship.x, self.ship.y, BLUE, 30)
                    else:
                        # Perder una vida
                        self.lives -= 1
                        self.create_explosion(self.ship.x, self.ship.y, RED, 40)
                        
                        if self.lives <= 0:
                            self.game_over()
                        else:
                            # Respawnear la nave con invulnerabilidad
                            self.ship.x = SCREEN_WIDTH // 2
                            self.ship.y = SCREEN_HEIGHT // 2
                            self.ship.vx = 0
                            self.ship.vy = 0
                            self.ship.invulnerable = True
                            self.ship.invulnerable_timer = 150  # 2.5 segundos a 60 FPS
                    
                    # Eliminar bala
                    bullet.kill()
                    break
        
        # Comprobar si se han destruido todos los asteroides
        if len(self.asteroids) == 0:
            self.level += 1
            self.spawn_asteroids(4 + self.level)  # Más asteroides por nivel
        
        # Spawnear ovnis
        self.ufo_spawn_timer -= 1
        if self.ufo_spawn_timer <= 0:
            self.spawn_ufo()
            self.ufo_spawn_timer = random.randint(600, 1200)  # 10-20 segundos
        
        # Spawnear power-ups
        self.power_up_spawn_timer -= 1
        if self.power_up_spawn_timer <= 0:
            # Posición aleatoria
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(50, SCREEN_HEIGHT - 50)
            self.spawn_power_up(x, y)
            self.power_up_spawn_timer = random.randint(900, 1800)  # 15-30 segundos
        
        # Aplicar efecto de tiempo lento
        if self.active_power_ups["slow_time"] > 0:
            # Reducir la velocidad de los asteroides y ovnis
            for asteroid in self.asteroids:
                asteroid.vx *= 0.5
                asteroid.vy *= 0.5
            for ufo in self.ufos:
                ufo.vx *= 0.5
    
    def game_over(self):
        self.state = GameState.GAME_OVER
        self.add_high_score(self.score)
    
    def draw(self):
        # Limpiar pantalla
        self.screen.fill(BLACK)
        
        # Dibujar todos los sprites
        for sprite in self.all_sprites:
            sprite.draw(self.screen)
        
        # Dibujar HUD
        self.draw_hud()
        
        # Dibujar menús o mensajes según el estado
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.PAUSED:
            self.draw_paused()
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over()
        elif self.state == GameState.HIGH_SCORES:
            self.draw_high_scores()
        
        # Actualizar pantalla
        pygame.display.flip()
    
    def draw_hud(self):
        # Puntuación
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Nivel
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, 10))
        
        # Vidas
        lives_text = self.font.render("Lives:", True, WHITE)
        self.screen.blit(lives_text, (SCREEN_WIDTH - 150, 10))
        
        # Dibujar iconos de vidas
        for i in range(self.lives):
            x = SCREEN_WIDTH - 80 + i * 25
            y = 15
            # Dibujar una pequeña nave
            points = [
                (x, y - 5),
                (x - 5, y + 5),
                (x + 5, y + 5)
            ]
            pygame.draw.polygon(self.screen, WHITE, points)
        
        # Power-ups activos
        y_offset = 50
        if self.active_power_ups["shield"] > 0:
            shield_text = self.font.render(f"Shield: {self.active_power_ups['shield'] // 60}s", True, BLUE)
            self.screen.blit(shield_text, (10, y_offset))
            y_offset += 30
        
        if self.active_power_ups["triple_shot"] > 0:
            triple_text = self.font.render(f"Triple Shot: {self.active_power_ups['triple_shot'] // 60}s", True, YELLOW)
            self.screen.blit(triple_text, (10, y_offset))
            y_offset += 30
        
        if self.active_power_ups["slow_time"] > 0:
            slow_text = self.font.render(f"Slow Time: {self.active_power_ups['slow_time'] // 60}s", True, MAGENTA)
            self.screen.blit(slow_text, (10, y_offset))
    
    def draw_menu(self):
        # Fondo semi-transparente
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Título
        title = self.big_font.render("ASTEROIDS", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
        
        # Opciones
        play_text = self.font.render("Press ENTER to Play", True, WHITE)
        self.screen.blit(play_text, (SCREEN_WIDTH // 2 - play_text.get_width() // 2, 250))
        
        high_scores_text = self.font.render("Press H for High Scores", True, WHITE)
        self.screen.blit(high_scores_text, (SCREEN_WIDTH // 2 - high_scores_text.get_width() // 2, 300))
        
        quit_text = self.font.render("Press ESC to Quit", True, WHITE)
        self.screen.blit(quit_text, (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, 350))
        
        # Controles
        controls_title = self.font.render("Controls:", True, WHITE)
        self.screen.blit(controls_title, (SCREEN_WIDTH // 2 - controls_title.get_width() // 2, 420))
        
        controls = [
            "Arrow Keys / A,D: Rotate",
            "Up / W: Thrust",
            "Space: Fire",
            "P / ESC: Pause"
        ]
        
        y_offset = 460
        for control in controls:
            control_text = self.font.render(control, True, WHITE)
            self.screen.blit(control_text, (SCREEN_WIDTH // 2 - control_text.get_width() // 2, y_offset))
            y_offset += 30
    
    def draw_paused(self):
        # Fondo semi-transparente
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Mensaje
        paused_text = self.big_font.render("PAUSED", True, WHITE)
        self.screen.blit(paused_text, (SCREEN_WIDTH // 2 - paused_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        
        continue_text = self.font.render("Press P or ESC to Continue", True, WHITE)
        self.screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
    
    def draw_game_over(self):
        # Fondo semi-transparente
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Mensaje
        game_over_text = self.big_font.render("GAME OVER", True, RED)
        self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
        
        score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 - 20))
        
        # Opciones
        restart_text = self.font.render("Press ENTER to Play Again", True, WHITE)
        self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
        
        menu_text = self.font.render("Press ESC for Main Menu", True, WHITE)
        self.screen.blit(menu_text, (SCREEN_WIDTH // 2 - menu_text.get_width() // 2, SCREEN_HEIGHT // 2 + 100))
    
    def draw_high_scores(self):
        # Fondo semi-transparente
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Título
        title = self.big_font.render("HIGH SCORES", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
        
        # High scores
        y_offset = 150
        for i, score in enumerate(self.high_scores[:10]):
            score_text = self.font.render(f"{i+1}. {score}", True, WHITE)
            self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, y_offset))
            y_offset += 40
        
        # Instrucción
        back_text = self.font.render("Press ESC to Go Back", True, WHITE)
        self.screen.blit(back_text, (SCREEN_WIDTH // 2 - back_text.get_width() // 2, SCREEN_HEIGHT - 50))
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()

# Iniciar el juego
if __name__ == "__main__":
    game = AsteroidsGame()
    game.run()