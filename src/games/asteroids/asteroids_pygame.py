"""
Asteroids (classic look) - single-file Pygame implementation
- No external images or sounds: all graphics are drawn with Pygame primitives.
- Features: ship with rotation & thrust, bullets, asteroids (3 sizes) that split,
  wrap-around screen, scoring, lives, levels, simple menus, highscore saved to JSON.

Controls:
- Left / Right or A / D : rotate
- Up or W : thrust
- Space : shoot
- P or ESC : pause (ESC in-game returns to menu)
- Enter : confirm / start / restart

Run: pip install pygame
python asteroids_pygame.py
"""

import math
import random
import json
import os
import sys
from dataclasses import dataclass

import pygame

# ----------------------------- Constants -----------------------------
WIDTH, HEIGHT = 800, 600
FPS = 60

THRUST = 0.12
FRICTION = 0.995
MAX_SPEED = 6.0
ROTATION_SPEED = 200.0  # degrees per second

BULLET_SPEED = 10.0
BULLET_LIFETIME = 60  # frames ~1s at 60FPS
FIRE_COOLDOWN = 12  # frames

ASTEROID_SIZES = {
    3: {"radius": 50, "points": 20, "pieces": 2},
    2: {"radius": 30, "points": 50, "pieces": 2},
    1: {"radius": 15, "points": 100, "pieces": 0},
}

INITIAL_ASTEROIDS = 4
INVULNERABILITY_TIME = 2.5  # seconds
SPAWN_SAFE_DISTANCE = 150

HIGHSCORE_FILE = "highscore.json"

# Colors
WHITE = (255, 255, 255)
GRAY = (190, 190, 190)
BLACK = (0, 0, 0)
YELLOW = (255, 220, 80)

# ----------------------------- Utilities -----------------------------

def load_highscore():
    if os.path.exists(HIGHSCORE_FILE):
        try:
            with open(HIGHSCORE_FILE, "r", encoding="utf-8") as f:
                return json.load(f).get("highscore", 0)
        except Exception:
            return 0
    return 0


def save_highscore(score):
    try:
        with open(HIGHSCORE_FILE, "w", encoding="utf-8") as f:
            json.dump({"highscore": score}, f)
    except Exception:
        pass


def wrap_position(pos):
    x, y = pos
    x = x % WIDTH
    y = y % HEIGHT
    return pygame.math.Vector2(x, y)


def angle_to_vector(angle_degrees):
    rad = math.radians(angle_degrees)
    return pygame.math.Vector2(math.cos(rad), -math.sin(rad))


def random_offscreen_position(min_dist_from):
    # spawn anywhere but not too close to min_dist_from (Vector2)
    while True:
        x = random.uniform(0, WIDTH)
        y = random.uniform(0, HEIGHT)
        pos = pygame.math.Vector2(x, y)
        if pos.distance_to(min_dist_from) > SPAWN_SAFE_DISTANCE:
            return pos


def irregular_polygon(radius, variance=0.35, points=12):
    """Return list of points (relative to center) describing an irregular polygon."""
    pts = []
    for i in range(points):
        angle = (i / points) * math.tau
        r = radius * (1 + random.uniform(-variance, variance))
        x = math.cos(angle) * r
        y = math.sin(angle) * r
        pts.append((x, y))
    return pts

# ----------------------------- Entities -----------------------------

class Bullet:
    def __init__(self, pos, vel):
        self.pos = pygame.math.Vector2(pos)
        self.vel = pygame.math.Vector2(vel)
        self.lifetime = BULLET_LIFETIME

    def update(self):
        self.pos += self.vel
        self.pos = wrap_position(self.pos)
        self.lifetime -= 1

    def draw(self, surf):
        pygame.draw.circle(surf, WHITE, (int(self.pos.x), int(self.pos.y)), 2)

    def alive(self):
        return self.lifetime > 0


class Asteroid:
    def __init__(self, pos, size, vel=None):
        self.pos = pygame.math.Vector2(pos)
        self.size = size  # 3: large, 2: med, 1: small
        self.radius = ASTEROID_SIZES[size]["radius"]
        if vel is None:
            ang = random.uniform(0, 360)
            spd = random.uniform(0.5, 2.0) * (4 - size) / 2.0 + 0.4
            self.vel = angle_to_vector(ang) * spd
        else:
            self.vel = pygame.math.Vector2(vel)
        self.angle = random.uniform(0, 360)
        self.angular_speed = random.uniform(-30, 30)
        self.shape = irregular_polygon(self.radius, variance=0.45, points=12)

    def update(self):
        self.pos += self.vel
        self.pos = wrap_position(self.pos)
        self.angle = (self.angle + self.angular_speed / FPS) % 360

    def draw(self, surf):
        # draw polygon rotated
        pts = []
        rad = math.radians(self.angle)
        cos_r = math.cos(rad)
        sin_r = math.sin(rad)
        for x, y in self.shape:
            rx = x * cos_r - y * sin_r
            ry = x * sin_r + y * cos_r
            pts.append((int(self.pos.x + rx), int(self.pos.y + ry)))
        pygame.draw.polygon(surf, WHITE, pts, width=2)

    def split(self):
        pieces = []
        info = ASTEROID_SIZES[self.size]
        for _ in range(info["pieces"]):
            # new velocity is slight variation
            vel = self.vel.rotate(random.uniform(-40, 40)) * random.uniform(0.8, 1.3)
            pieces.append(Asteroid(self.pos, self.size - 1, vel=vel))
        return pieces


class Ship:
    def __init__(self):
        self.pos = pygame.math.Vector2(WIDTH / 2, HEIGHT / 2)
        self.vel = pygame.math.Vector2(0, 0)
        self.angle = 90.0  # facing up (degrees, 0 right, 90 up?) we'll use conventional math mapping
        self.radius = 12
        self.respawn()

    def respawn(self):
        self.pos = pygame.math.Vector2(WIDTH / 2, HEIGHT / 2)
        self.vel = pygame.math.Vector2(0, 0)
        self.angle = 90.0
        self.lives = 3
        self.invulnerable_timer = 0.0
        self.fire_cooldown = 0
        self.alive_flag = True

    def update(self, dt, keys):
        if not self.alive_flag:
            return

        rotate_dir = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            rotate_dir += 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            rotate_dir -= 1

        self.angle += rotate_dir * ROTATION_SPEED * dt
        thrusting = keys[pygame.K_UP] or keys[pygame.K_w]
        if thrusting:
            vec = angle_to_vector(self.angle)
            self.vel += vec * THRUST

        # clamp speed
        if self.vel.length() > MAX_SPEED:
            self.vel.scale_to_length(MAX_SPEED)

        # friction
        self.vel *= FRICTION

        self.pos += self.vel
        self.pos = wrap_position(self.pos)

        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= dt

        if self.fire_cooldown > 0:
            self.fire_cooldown -= 1

    def draw(self, surf):
        if not self.alive_flag:
            return
        # blinking when invulnerable
        if self.invulnerable_timer > 0 and (int(self.invulnerable_timer * 10) % 2 == 0):
            return

        # ship triangle
        tip = self.pos + angle_to_vector(self.angle) * (self.radius + 2)
        left = self.pos + angle_to_vector(self.angle + 130) * (self.radius)
        right = self.pos + angle_to_vector(self.angle - 130) * (self.radius)
        pygame.draw.polygon(surf, WHITE, [(int(tip.x), int(tip.y)), (int(left.x), int(left.y)), (int(right.x), int(right.y))], width=2)

        # draw thrust flame if thrusting (approximate by checking velocity along forward)
        forward_speed = self.vel.dot(angle_to_vector(self.angle))
        if forward_speed > 0.1:
            back = self.pos - angle_to_vector(self.angle) * (self.radius + 7)
            flame_left = self.pos + angle_to_vector(self.angle + 160) * (self.radius * 0.6)
            flame_right = self.pos + angle_to_vector(self.angle - 160) * (self.radius * 0.6)
            pygame.draw.polygon(surf, YELLOW, [(int(back.x), int(back.y)), (int(flame_left.x), int(flame_left.y)), (int(flame_right.x), int(flame_right.y))])

    def shoot(self):
        if self.fire_cooldown > 0 or not self.alive_flag:
            return None
        dir_vec = angle_to_vector(self.angle)
        pos = self.pos + dir_vec * (self.radius + 6)
        vel = self.vel + dir_vec * BULLET_SPEED
        self.fire_cooldown = FIRE_COOLDOWN
        return Bullet(pos, vel)

    def hit(self):
        # lose a life and become invulnerable temporarily
        if self.invulnerable_timer > 0 or not self.alive_flag:
            return False
        self.lives -= 1
        self.invulnerable_timer = INVULNERABILITY_TIME
        if self.lives <= 0:
            self.alive_flag = False
        else:
            # respawn to center and reset velocity
            self.pos = pygame.math.Vector2(WIDTH / 2, HEIGHT / 2)
            self.vel = pygame.math.Vector2(0, 0)
        return True

# ----------------------------- Game -----------------------------

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Asteroids - Classic (Pygame)")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 18)
        self.large_font = pygame.font.SysFont("consolas", 40)

        self.ship = Ship()
        self.bullets = []
        self.asteroids = []

        self.score = 0
        self.level = 1
        self.highscore = load_highscore()

        self.state = "menu"  # menu, playing, paused, gameover

        self.spawn_asteroids(INITIAL_ASTEROIDS)

    def spawn_asteroids(self, count):
        for _ in range(count):
            pos = random_offscreen_position(self.ship.pos)
            self.asteroids.append(Asteroid(pos, 3))

    def level_up(self):
        self.level += 1
        # more asteroids each level
        n = INITIAL_ASTEROIDS + (self.level - 1)
        self.spawn_asteroids(n)

    def reset(self):
        self.ship = Ship()
        self.bullets = []
        self.asteroids = []
        self.score = 0
        self.level = 1
        self.spawn_asteroids(INITIAL_ASTEROIDS)
        self.state = "playing"

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if self.state == "menu":
                        if event.key == pygame.K_RETURN:
                            self.reset()
                        elif event.key == pygame.K_ESCAPE:
                            running = False
                    elif self.state == "playing":
                        if event.key == pygame.K_SPACE:
                            b = self.ship.shoot()
                            if b:
                                self.bullets.append(b)
                        elif event.key in (pygame.K_p, pygame.K_ESCAPE):
                            self.state = "paused"
                    elif self.state == "paused":
                        if event.key in (pygame.K_p, pygame.K_ESCAPE):
                            self.state = "playing"
                    elif self.state == "gameover":
                        if event.key == pygame.K_RETURN:
                            self.reset()
                        elif event.key == pygame.K_ESCAPE:
                            running = False

            keys = pygame.key.get_pressed()

            if self.state == "playing":
                self.update(dt, keys)

            self.draw()
            pygame.display.flip()

        # Save highscore on exit
        if self.score > self.highscore:
            save_highscore(self.score)
        pygame.quit()
        sys.exit()

    def update(self, dt, keys):
        # ship
        self.ship.update(dt, keys)

        # bullets
        for b in list(self.bullets):
            b.update()
            if not b.alive():
                self.bullets.remove(b)

        # asteroids
        for a in self.asteroids:
            a.update()

        # collisions: bullets vs asteroids
        for b in list(self.bullets):
            for a in list(self.asteroids):
                if b.pos.distance_to(a.pos) < a.radius:
                    # hit
                    self.bullets.remove(b)
                    self.asteroids.remove(a)
                    self.score += ASTEROID_SIZES[a.size]["points"]
                    pieces = a.split()
                    self.asteroids.extend(pieces)
                    break

        # collisions: ship vs asteroids
        if self.ship.alive_flag and self.ship.invulnerable_timer <= 0:
            for a in list(self.asteroids):
                if self.ship.pos.distance_to(a.pos) < (self.ship.radius + a.radius):
                    # hit
                    self.ship.hit()
                    # simple explosion effect: remove asteroid
                    try:
                        self.asteroids.remove(a)
                    except ValueError:
                        pass
                    break

        # level complete?
        if not self.asteroids:
            self.level_up()

        # update highscore immediately if beaten
        if self.score > self.highscore:
            self.highscore = self.score
            save_highscore(self.highscore)

        # if ship dead -> game over
        if not self.ship.alive_flag:
            self.state = "gameover"

    def draw_hud(self):
        score_surf = self.font.render(f"Score: {self.score}", True, WHITE)
        hs_surf = self.font.render(f"Highscore: {self.highscore}", True, WHITE)
        self.screen.blit(score_surf, (10, 10))
        self.screen.blit(hs_surf, (10, 30))

        # lives
        for i in range(self.ship.lives):
            x = WIDTH - 20 - i * 28
            y = 15
            # draw a small ship icon for each life (triangle)
            pts = [
                (x + int(math.cos(math.radians(self.ship.angle)) * (self.ship.radius)), y + int(-math.sin(math.radians(self.ship.angle)) * (self.ship.radius))),
                (x + int(math.cos(math.radians(self.ship.angle + 130)) * (self.ship.radius)), y + int(-math.sin(math.radians(self.ship.angle + 130)) * (self.ship.radius))),
                (x + int(math.cos(math.radians(self.ship.angle - 130)) * (self.ship.radius)), y + int(-math.sin(math.radians(self.ship.angle - 130)) * (self.ship.radius))),
            ]
            pygame.draw.polygon(self.screen, WHITE, pts, width=1)

        # level in center
        level_surf = self.font.render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(level_surf, (WIDTH // 2 - level_surf.get_width() // 2, 10))

    def draw(self):
        self.screen.fill(BLACK)

        if self.state == "menu":
            title = self.large_font.render("ASTEROIDS", True, WHITE)
            instr = self.font.render("Press Enter to Start — Arrows/A/D to move, Space to shoot", True, GRAY)
            self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 80))
            self.screen.blit(instr, (WIDTH // 2 - instr.get_width() // 2, HEIGHT // 2 + 10))
            hs = self.font.render(f"Highscore: {self.highscore}", True, WHITE)
            self.screen.blit(hs, (WIDTH // 2 - hs.get_width() // 2, HEIGHT // 2 + 50))
            return

        # draw asteroids (and wrap-draw near edges to avoid clipping)
        for a in self.asteroids:
            a.draw(self.screen)
            # draw mirrored if near border
            if a.pos.x < a.radius + 2:
                saved = a.pos.x
                a.pos.x += WIDTH
                a.draw(self.screen)
                a.pos.x = saved
            elif a.pos.x > WIDTH - a.radius - 2:
                saved = a.pos.x
                a.pos.x -= WIDTH
                a.draw(self.screen)
                a.pos.x = saved
            if a.pos.y < a.radius + 2:
                saved = a.pos.y
                a.pos.y += HEIGHT
                a.draw(self.screen)
                a.pos.y = saved
            elif a.pos.y > HEIGHT - a.radius - 2:
                saved = a.pos.y
                a.pos.y -= HEIGHT
                a.draw(self.screen)
                a.pos.y = saved

        # bullets
        for b in self.bullets:
            b.draw(self.screen)

        # ship
        self.ship.draw(self.screen)

        # HUD
        self.draw_hud()

        if self.state == "paused":
            pa = self.large_font.render("PAUSED", True, WHITE)
            self.screen.blit(pa, (WIDTH // 2 - pa.get_width() // 2, HEIGHT // 2 - pa.get_height() // 2))

        if self.state == "gameover":
            go = self.large_font.render("GAME OVER", True, WHITE)
            info = self.font.render(f"Score: {self.score} — Press Enter to Restart or Esc to Quit", True, GRAY)
            self.screen.blit(go, (WIDTH // 2 - go.get_width() // 2, HEIGHT // 2 - 40))
            self.screen.blit(info, (WIDTH // 2 - info.get_width() // 2, HEIGHT // 2 + 20))


if __name__ == "__main__":
    Game().run()
