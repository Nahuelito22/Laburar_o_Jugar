# src/games/paperboy/paperboy_state.py
import pygame
import random
from ...states.base_state import BaseState
from ... import settings
from ...components.scrolling_background import ScrollingBackground
from .entities import PlayerPaperboy, Buzon, Auto, Periodico

class PaperboyState(BaseState):
    def __init__(self):
        super().__init__()
        self.next_state = "HUB"
        self.background = ScrollingBackground(image_path="assets/images/paperboy_level_strip.png", speed=300)
        
        self.all_sprites = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.targets = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()

        self.player = PlayerPaperboy()
        self.all_sprites.add(self.player)
        
        self.score = 0
        self.periodicos_restantes = 10

        # --- NUEVO: Límites para los buzones ---
        # Ajustá estos valores para que coincidan con tus veredas
        self.buzon_limite_izq = 450
        self.buzon_limite_der = 860

        self.SPAWN_BUZON_EVENT = pygame.USEREVENT + 1
        pygame.time.set_timer(self.SPAWN_BUZON_EVENT, 2500)
        self.SPAWN_AUTO_EVENT = pygame.USEREVENT + 2
        pygame.time.set_timer(self.SPAWN_AUTO_EVENT, 3500)

    def get_event(self, event):
        if event.type == pygame.QUIT:
            self.quit = True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.done = True
        
        # --- Manejo de Spawning ACTUALIZADO ---
        if event.type == self.SPAWN_BUZON_EVENT:
            # Le pasamos los nuevos límites al Buzon
            buzon = Buzon(self.background.speed_y, self.buzon_limite_izq, self.buzon_limite_der)
            self.all_sprites.add(buzon)
            self.targets.add(buzon)

        if event.type == self.SPAWN_AUTO_EVENT:
            auto = Auto(self.background.speed_y)
            self.all_sprites.add(auto)
            self.obstacles.add(auto)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
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

        # Lógica de Puntuación
        hits = pygame.sprite.groupcollide(self.projectiles, self.targets, True, True)
        if hits:
            self.score += 10
            self.periodicos_restantes += 2
            print(f"Acierto! Puntaje: {self.score}, Periódicos: {self.periodicos_restantes}")

        for buzon in list(self.targets):
            if buzon.rect.top > settings.SCREEN_HEIGHT:
                self.score -= 5
                print(f"Buzón perdido! Puntaje: {self.score}")
                buzon.kill()

        # Lógica de Derrota y Colisión
        obstaculos_activos = [obs for obs in self.obstacles if hasattr(obs, 'is_active') and obs.is_active]
        
        for obs in obstaculos_activos:
            if self.player.hitbox.colliderect(obs.hitbox):
                print("¡CHOQUE! Fin del juego.")
                self.done = True
                self.next_state = "GAME_OVER"
                break

        if self.periodicos_restantes <= 0 and not self.projectiles:
            print("¡Sin periódicos! Fin del juego.")
            self.done = True
            self.next_state = "GAME_OVER"

    def draw(self, surface):
        self.background.draw(surface)
        self.all_sprites.draw(surface)
        
        # HUD
        font = pygame.font.Font(None, 50)
        score_text = font.render(f"Puntaje: {self.score}", True, settings.WHITE)
        ammo_text = font.render(f"Periodicos: {self.periodicos_restantes}", True, settings.WHITE)
        surface.blit(score_text, (10, 10))
        surface.blit(ammo_text, (10, 50))

        # --- DEBUG ACTUALIZADO ---
        if settings.DEBUG_MODE:
            # Límites del jugador (Rojo)
            pygame.draw.line(surface, (255, 0, 0), (self.player.limite_izquierdo, 0), (self.player.limite_izquierdo, settings.SCREEN_HEIGHT), 2)
            pygame.draw.line(surface, (255, 0, 0), (self.player.limite_derecho, 0), (self.player.limite_derecho, settings.SCREEN_HEIGHT), 2)
            
            # Límites de los buzones (Azul)
            pygame.draw.line(surface, (0, 0, 255), (self.buzon_limite_izq, 0), (self.buzon_limite_izq, settings.SCREEN_HEIGHT), 2)
            pygame.draw.line(surface, (0, 0, 255), (self.buzon_limite_der, 0), (self.buzon_limite_der, settings.SCREEN_HEIGHT), 2)

            # Hitbox de todos los sprites (Verde)
            for sprite in self.all_sprites:
                if hasattr(sprite, 'hitbox'):
                    pygame.draw.rect(surface, (0, 255, 0), sprite.hitbox, 2)