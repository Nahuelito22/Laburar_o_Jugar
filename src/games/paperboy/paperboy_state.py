# src/games/paperboy/paperboy_state.py
import pygame
import random
from ...states.base_state import BaseState
from ... import settings
from ...components.scrolling_background import ScrollingBackground
from .entities import PlayerPaperboy, Buzon, Auto, Periodico # <-- Importamos todo

class PaperboyState(BaseState):
    def __init__(self):
        super().__init__()
        self.next_state = "HUB"
        self.background = ScrollingBackground(image_path="assets/images/paperboy_level_strip.png", speed=300)
        
        # --- Grupos de Sprites ---
        self.all_sprites = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.targets = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()

        # --- Creamos al jugador ---
        self.player = PlayerPaperboy()
        self.all_sprites.add(self.player)
        
        # --- NUEVO: Variables de juego ---
        self.score = 0
        self.periodicos_restantes = 10

        # --- Sistema de Spawning con Timers ---
        self.SPAWN_BUZON_EVENT = pygame.USEREVENT + 1
        pygame.time.set_timer(self.SPAWN_BUZON_EVENT, 2500)
        self.SPAWN_AUTO_EVENT = pygame.USEREVENT + 2
        pygame.time.set_timer(self.SPAWN_AUTO_EVENT, 3500)

    def get_event(self, event):
        if event.type == pygame.QUIT:
            self.quit = True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.done = True
        
        # --- Manejo de Spawning ---
        if event.type == self.SPAWN_BUZON_EVENT:
            buzon = Buzon(self.background.speed_y)
            self.all_sprites.add(buzon)
            self.targets.add(buzon)

        if event.type == self.SPAWN_AUTO_EVENT:
            auto = Auto(self.background.speed_y)
            self.all_sprites.add(auto)
            self.obstacles.add(auto)

        # --- Lógica de Lanzamiento Actualizada ---
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Solo lanza si le quedan periódicos
            if self.periodicos_restantes > 0:
                self.periodicos_restantes -= 1
                periodico = Periodico(self.player.rect.center, event.pos, self.background.speed_y)
                self.all_sprites.add(periodico)
                self.projectiles.add(periodico)

                if event.pos[0] < self.player.rect.centerx:
                    self.player.lanzar('throw_left')
                else:
                    self.player.lanzar('throw_right')

    def update(self, dt):
        self.background.update(dt)
        self.all_sprites.update(dt)

        # --- Lógica de Puntuación Actualizada ---
        
        # Aciertos en buzones
        hits = pygame.sprite.groupcollide(self.projectiles, self.targets, True, True)
        if hits:
            self.score += 10
            self.periodicos_restantes += 2 # Recupera 2 periódicos
            print(f"Acierto! Puntaje: {self.score}, Periódicos: {self.periodicos_restantes}")

        # Penalización por buzones no entregados
        for buzon in list(self.targets): # Usamos list() para poder modificar el grupo mientras iteramos
            if buzon.rect.top > settings.SCREEN_HEIGHT:
                self.score -= 5 # Pierde 5 puntos
                print(f"Buzón perdido! Puntaje: {self.score}")
                buzon.kill()

        # Choques con autos
        if pygame.sprite.spritecollide(self.player, self.obstacles, False):
            print("¡CHOQUE!")

    def draw(self, surface):
        self.background.draw(surface)
        self.all_sprites.draw(surface)
        
        # --- NUEVO: HUD actualizado ---
        font = pygame.font.Font(None, 50)
        score_text = font.render(f"Puntaje: {self.score}", True, settings.WHITE)
        ammo_text = font.render(f"Periodicos: {self.periodicos_restantes}", True, settings.WHITE)
        surface.blit(score_text, (10, 10))
        surface.blit(ammo_text, (10, 50))

        # El modo debug sigue funcionando
        if settings.DEBUG_MODE:
            pygame.draw.line(surface, (255, 0, 0), (self.player.limite_izquierdo, 0), (self.player.limite_izquierdo, settings.SCREEN_HEIGHT), 2)
            pygame.draw.line(surface, (255, 0, 0), (self.player.limite_derecho, 0), (self.player.limite_derecho, settings.SCREEN_HEIGHT), 2)