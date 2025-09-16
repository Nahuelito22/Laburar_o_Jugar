# src/games/paperboy/paperboy_state.py
import pygame
import random
from ...states.base_state import BaseState
from ... import settings
from ...components.dynamic_background import DynamicBackground # <-- Importamos la nueva clase de fondo
from .entities import PlayerPaperboy, Buzon, Auto, Periodico, Casa # <-- Importamos la nueva clase Casa
from ... import save_manager

class PaperboyState(BaseState):
    def __init__(self):
        super().__init__()
        self.next_state = "HUB"
        
        # --- Usamos el fondo dinámico ---
        self.background = DynamicBackground(speed=300)
        
        # --- Grupos de Sprites ---
        self.all_sprites = pygame.sprite.Group()
        self.player_group = pygame.sprite.GroupSingle() # Grupo solo para el jugador
        self.obstacles = pygame.sprite.Group()
        self.targets = pygame.sprite.Group()     # Aquí irán los buzones
        self.projectiles = pygame.sprite.Group()
        self.scenery = pygame.sprite.Group()     # Aquí irán las casas

        # --- Creamos al jugador ---
        self.player = PlayerPaperboy()
        self.player_group.add(self.player) # Lo añadimos a su propio grupo
        
        # --- Variables de juego ---
        self.score = 0
        self.periodicos_restantes = 10
        self.fichas = 0
        self.dinero_total_inicial = 0 

        # --- Límites Dinámicos (basados en el nuevo fondo) ---
        self.player.limite_izquierdo = self.background.calle.left
        self.player.limite_derecho = self.background.calle.right
        self.buzon_limite_cesped_izq = self.background.vereda_izq.left
        self.buzon_limite_cesped_der = self.background.vereda_der.right

        # --- Sistema de Spawning Actualizado ---
        self.SPAWN_CASA_EVENT = pygame.USEREVENT + 1 # Ahora generamos casas (que tienen buzones)
        pygame.time.set_timer(self.SPAWN_CASA_EVENT, 1500)
        self.SPAWN_AUTO_EVENT = pygame.USEREVENT + 2
        pygame.time.set_timer(self.SPAWN_AUTO_EVENT, 3500)
    
    def startup(self, persistent):
        super().startup(persistent)
        self.fichas = self.persistent.get('fichas', 0)
        self.dinero_total_inicial = self.persistent.get('dinero_total', 0)

    def get_event(self, event):
        if event.type == pygame.QUIT:
            self.quit = True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.done = True
        
        # --- Spawning de Casas y Autos ---
        if event.type == self.SPAWN_CASA_EVENT:
            casa = Casa(self.background.speed, self.buzon_limite_cesped_izq, self.buzon_limite_cesped_der)
            self.scenery.add(casa)
            self.targets.add(casa.buzon) # El buzón de la casa es el objetivo
        
        if event.type == self.SPAWN_AUTO_EVENT:
            auto = Auto(self.background.speed, self.player.limite_izquierdo, self.player.limite_derecho)
            self.obstacles.add(auto)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.periodicos_restantes > 0:
                self.periodicos_restantes -= 1
                periodico = Periodico(self.player.rect.center, event.pos, self.background.speed)
                self.projectiles.add(periodico)
                if event.pos[0] < self.player.rect.centerx:
                    self.player.lanzar('throw_left')
                else:
                    self.player.lanzar('throw_right')

    def update(self, dt):
        self.background.update(dt)
        # Actualizamos los grupos por separado para controlar el orden
        self.scenery.update(dt)
        self.targets.update(dt)
        self.obstacles.update(dt)
        self.player_group.update(dt)
        self.projectiles.update(dt)

        # Lógica de Puntuación y Penalización
        hits = pygame.sprite.groupcollide(self.projectiles, self.targets, False, True)
        for periodico, buzones_golpeados in hits.items():
            if not periodico.acerto:
                self.score += 10
                self.periodicos_restantes += 2
                periodico.acerto = True
                periodico.kill()

        for buzon in list(self.targets):
            if buzon.rect.top > settings.SCREEN_HEIGHT:
                self.score -= 5
                buzon.kill()
        
        screen_rect = pygame.Rect(0, 0, settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
        for periodico in list(self.projectiles):
            if not screen_rect.colliderect(periodico.rect):
                if not periodico.acerto:
                    self.score -= 1
                periodico.kill()

        # Lógica de Derrota y Guardado
        lost = False
        obstaculos_activos = [obs for obs in self.obstacles if hasattr(obs, 'is_active') and obs.is_active]
        if self.player.hitbox.collidelist([obs.hitbox for obs in obstaculos_activos]) != -1:
            lost = True
        if self.periodicos_restantes <= 0 and not self.projectiles:
            lost = True

        if lost:
            save_data = save_manager.load_data()
            dinero_final = self.dinero_total_inicial + self.score
            save_data['dinero_total'] = dinero_final
            save_data['fichas'] = self.fichas
            if self.score > save_data.get('high_score', 0):
                save_data['high_score'] = self.score
            save_manager.save_data(save_data)
            self.persistent['last_score'] = self.score
            self.done = True
            self.next_state = "GAME_OVER"

    def draw(self, surface):
        self.background.draw(surface)
        
        # --- Dibujado por Capas ---
        self.scenery.draw(surface)
        self.targets.draw(surface)
        self.obstacles.draw(surface)
        self.player_group.draw(surface)
        self.projectiles.draw(surface)
        
        # HUD
        font = pygame.font.Font(None, 50)
        score_text = font.render(f"Puntos: {self.score}", True, settings.WHITE)
        ammo_text = font.render(f"Periodicos: {self.periodicos_restantes}", True, settings.WHITE)
        surface.blit(score_text, (10, 10))
        surface.blit(ammo_text, (10, 50))

        # DEBUG
        if settings.DEBUG_MODE:
            # Límites del jugador (Rojo)
            pygame.draw.line(surface, (255, 0, 0), (self.player.limite_izquierdo, 0), (self.player.limite_izquierdo, settings.SCREEN_HEIGHT), 2)
            pygame.draw.line(surface, (255, 0, 0), (self.player.limite_derecho, 0), (self.player.limite_derecho, settings.SCREEN_HEIGHT), 2)            
            # Hitbox de todos los sprites (Verde)
            # Dibujamos los hitboxes de todos los sprites que están en los grupos relevantes
            for sprite in self.player_group: pygame.draw.rect(surface, (0, 255, 0), sprite.hitbox, 2)
            for sprite in self.obstacles: 
                if hasattr(sprite, 'hitbox'): pygame.draw.rect(surface, (0, 255, 0), sprite.hitbox, 2)