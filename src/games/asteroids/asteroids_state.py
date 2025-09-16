import pygame
import random
import math
from ...states.base_state import BaseState
from ... import settings
from ... import save_manager
from .entities import Ship, Bullet, Asteroid, UFO, PowerUp, Particle, BLACK, WHITE, RED, BLUE, YELLOW, MAGENTA

class AsteroidsState(BaseState):
    def __init__(self):
        super().__init__()
        self.next_state = "ARCADE"
        self.font = pygame.font.SysFont('Arial', 24)
        self.big_font = pygame.font.SysFont('Arial', 48)

    def startup(self, persistent):
        super().startup(persistent)
        self.all_sprites = pygame.sprite.Group()
        self.asteroids = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.ufos = pygame.sprite.Group()
        self.power_ups = pygame.sprite.Group()
        self.particles = pygame.sprite.Group()

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

        self.can_fire = True
        self.fire_cooldown_timer = 0

        self.ship = Ship(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2, settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
        self.all_sprites.add(self.ship)

        self.spawn_asteroids(4)
        self.game_over_flag = False

    def get_event(self, event):
        if event.type == pygame.QUIT:
            self.quit = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.done = True
            elif not self.game_over_flag and event.key == pygame.K_SPACE and self.can_fire:
                self.fire_bullet()

    def update(self, dt):
        if self.game_over_flag:
            return

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.ship.rotate(-1)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.ship.rotate(1)
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

        if not self.can_fire:
            self.fire_cooldown_timer -= 1
            if self.fire_cooldown_timer <= 0:
                self.can_fire = True

        # Actualizar power-ups activos
        for power in self.active_power_ups:
            if self.active_power_ups[power] > 0:
                self.active_power_ups[power] -= 1

        self.all_sprites.update()

        # Disparos de ovnis
        for ufo in self.ufos:
            should_shoot = ufo.update()
            if should_shoot:
                angle = ufo.get_shoot_direction(self.ship.x, self.ship.y)
                bullet = Bullet(ufo.x, ufo.y, angle, settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT, owner="ufo")
                self.all_sprites.add(bullet)
                self.bullets.add(bullet)

        # Collisions
        self.handle_collisions()

        if len(self.asteroids) == 0:
            self.level += 1
            self.spawn_asteroids(4 + self.level)

        self.ufo_spawn_timer -= 1
        if self.ufo_spawn_timer <= 0:
            self.spawn_ufo()
            self.ufo_spawn_timer = random.randint(600, 1200)

        self.power_up_spawn_timer -= 1
        if self.power_up_spawn_timer <= 0:
            x = random.randint(50, settings.SCREEN_WIDTH - 50)
            y = random.randint(50, settings.SCREEN_HEIGHT - 50)
            self.spawn_power_up(x, y)
            self.power_up_spawn_timer = random.randint(900, 1800)

    def draw(self, surface):
        surface.fill(BLACK)
        self.all_sprites.draw(surface)
        self.draw_hud(surface)

        if self.game_over_flag:
            self.draw_game_over(surface)

    def handle_collisions(self):
        # Bullets with asteroids
        for bullet in self.bullets:
            if bullet.owner == "player" and bullet.frames_alive < 5: # Grace period
                continue
            asteroid_hits = pygame.sprite.spritecollide(bullet, self.asteroids, False, pygame.sprite.collide_circle)
            for asteroid in asteroid_hits:
                self.score += asteroid.points
                self.create_explosion(asteroid.x, asteroid.y, WHITE, 20)
                new_asteroids = asteroid.split()
                for new_asteroid in new_asteroids:
                    self.all_sprites.add(new_asteroid)
                    self.asteroids.add(new_asteroid)
                asteroid.kill()
                bullet.kill()
                if random.random() < 0.1:
                    self.spawn_power_up(asteroid.x, asteroid.y)

        # Ship with asteroids
        if not self.ship.invulnerable:
            asteroid_hits = pygame.sprite.spritecollide(self.ship, self.asteroids, False, pygame.sprite.collide_circle)
            if asteroid_hits:
                if self.active_power_ups["shield"] > 0:
                    self.active_power_ups["shield"] = 0
                    self.create_explosion(self.ship.x, self.ship.y, BLUE, 30)
                else:
                    self.lives -= 1
                    self.create_explosion(self.ship.x, self.ship.y, RED, 40)
                    if self.lives <= 0:
                        self.game_over()
                    else:
                        self.respawn_ship()

        # Ship with power-ups
        power_up_hits = pygame.sprite.spritecollide(self.ship, self.power_ups, True, pygame.sprite.collide_circle)
        for power_up in power_up_hits:
            if power_up.power_type == "shield":
                self.active_power_ups["shield"] = 300
            elif power_up.power_type == "triple_shot":
                self.active_power_ups["triple_shot"] = 300
            elif power_up.power_type == "extra_life":
                self.lives += 1
            elif power_up.power_type == "slow_time":
                self.active_power_ups["slow_time"] = 300
            self.create_explosion(power_up.x, power_up.y, WHITE, 20)

        # UFO bullets with ship
        if not self.ship.invulnerable:
            for bullet in self.bullets:
                if bullet.owner == "ufo":
                    if pygame.sprite.collide_rect(self.ship, bullet):
                        if self.active_power_ups["shield"] > 0:
                            self.active_power_ups["shield"] = 0
                            self.create_explosion(self.ship.x, self.ship.y, BLUE, 30)
                        else:
                            self.lives -= 1
                            self.create_explosion(self.ship.x, self.ship.y, RED, 40)
                            if self.lives <= 0:
                                self.game_over()
                            else:
                                self.respawn_ship()
                        bullet.kill()

    def fire_bullet(self):
        if self.active_power_ups["triple_shot"] > 0:
            for angle_offset in [-10, 0, 10]:
                angle = (self.ship.angle + angle_offset) % 360
                bullet = Bullet(self.ship.x, self.ship.y, angle, settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
                self.all_sprites.add(bullet)
                self.bullets.add(bullet)
        else:
            bullet = Bullet(self.ship.x, self.ship.y, self.ship.angle, settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
            self.all_sprites.add(bullet)
            self.bullets.add(bullet)
        self.can_fire = False
        self.fire_cooldown_timer = 12

    def spawn_asteroids(self, count):
        for _ in range(count):
            while True:
                x = random.randint(50, settings.SCREEN_WIDTH - 50)
                y = random.randint(50, settings.SCREEN_HEIGHT - 50)
                distance = math.sqrt((x - self.ship.x)**2 + (y - self.ship.y)**2)
                if distance > 100:
                    break
            asteroid = Asteroid(x, y, settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT, "large")
            self.all_sprites.add(asteroid)
            self.asteroids.add(asteroid)

    def spawn_ufo(self):
        ufo = UFO(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
        self.all_sprites.add(ufo)
        self.ufos.add(ufo)

    def spawn_power_up(self, x, y):
        power_type = random.choice(["shield", "triple_shot", "extra_life", "slow_time"])
        power_up = PowerUp(x, y, power_type)
        self.all_sprites.add(power_up)
        self.power_ups.add(power_up)

    def create_explosion(self, x, y, color, count=30):
        for _ in range(count):
            speed = random.uniform(0.5, 3.0)
            angle = random.uniform(0, 360)
            angle_rad = math.radians(angle)
            vx = speed * math.sin(angle_rad)
            vy = -speed * math.cos(angle_rad)
            lifetime = random.randint(20, 40)
            particle = Particle(x, y, color, (vx, vy), lifetime)
            self.all_sprites.add(particle)
            self.particles.add(particle)

    def respawn_ship(self):
        self.ship.x = settings.SCREEN_WIDTH // 2
        self.ship.y = settings.SCREEN_HEIGHT // 2
        self.ship.vx = 0
        self.ship.vy = 0
        self.ship.invulnerable = True
        self.ship.invulnerable_timer = 150

    def game_over(self):
        self.game_over_flag = True
        save_manager.save_high_score("ASTEROIDS", self.score)

    def draw_hud(self, surface):
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        surface.blit(score_text, (10, 10))
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        surface.blit(level_text, (settings.SCREEN_WIDTH // 2 - level_text.get_width() // 2, 10))
        lives_text = self.font.render("Lives:", True, WHITE)
        surface.blit(lives_text, (settings.SCREEN_WIDTH - 150, 10))
        for i in range(self.lives):
            x = settings.SCREEN_WIDTH - 80 + i * 25
            y = 15
            points = [(x, y - 5), (x - 5, y + 5), (x + 5, y + 5)]
            pygame.draw.polygon(surface, WHITE, points)

    def draw_game_over(self, surface):
        overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        game_over_text = self.big_font.render("GAME OVER", True, RED)
        surface.blit(game_over_text, (settings.SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, settings.SCREEN_HEIGHT // 2 - 100))
        score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        surface.blit(score_text, (settings.SCREEN_WIDTH // 2 - score_text.get_width() // 2, settings.SCREEN_HEIGHT // 2 - 20))
        restart_text = self.font.render("Press ESC for Main Menu", True, WHITE)
        surface.blit(restart_text, (settings.SCREEN_WIDTH // 2 - restart_text.get_width() // 2, settings.SCREEN_HEIGHT // 2 + 50))