# src/games/paperboy/paperboy_state.py
import pygame
import random
from ...states.base_state import BaseState
from ... import settings
from ...components.dynamic_background import DynamicBackground
from .entities import PlayerPaperboy, Buzon, Auto, Periodico, Casa
from ... import save_manager


# src/games/paperboy/paperboy_state.py
import pygame
import random
from ...states.base_state import BaseState
from ... import settings
from ...components.dynamic_background import DynamicBackground
from .entities import PlayerPaperboy, Buzon, Auto, Periodico, Casa, ManchaAceite, PeriodicoDevuelto
from ... import save_manager

class PaperboyState(BaseState):
    def __init__(self):
        super().__init__()
        self.next_state = "HUB"
        self.background = DynamicBackground(speed=300)
        
        # --- Grupos de Sprites ---
        self.player_group = pygame.sprite.GroupSingle()
        self.obstacles = pygame.sprite.Group()
        self.targets = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.scenery = pygame.sprite.Group()
        self.devueltos = pygame.sprite.Group()
        self.charcos = pygame.sprite.Group()

        # --- Creamos al jugador ---
        self.player = PlayerPaperboy()
        self.player_group.add(self.player)
        
        # --- Variables de juego ---
        self.score = 0
        self.periodicos_restantes = 10
        self.fichas = 0
        self.dinero_total_inicial = 0 

        # --- Dificultad Progresiva ---
        self.difficulty_level = 1
        self.next_difficulty_score = 100
        self.auto_spawn_interval = 3500
        self.casa_spawn_interval = 1800

        # --- Límites Dinámicos ---
        self.player.limite_izquierdo = self.background.vereda_izq.left
        self.player.limite_derecho = self.background.vereda_der.right
        self.casa_spawn_limite_izq = self.background.cesped_izq.right
        self.casa_spawn_limite_der = self.background.cesped_der.left

        # --- Sistema de Spawning ---
        self.SPAWN_CASA_EVENT = pygame.USEREVENT + 1
        pygame.time.set_timer(self.SPAWN_CASA_EVENT, self.casa_spawn_interval)
        self.SPAWN_AUTO_EVENT = pygame.USEREVENT + 2
        pygame.time.set_timer(self.SPAWN_AUTO_EVENT, self.auto_spawn_interval)
        self.SPAWN_ACEITE_EVENT = pygame.USEREVENT + 3
        pygame.time.set_timer(self.SPAWN_ACEITE_EVENT, 5000)
    
    def startup(self, persistent):
        super().startup(persistent)
        self.fichas = self.persistent.get('fichas', 0)
        self.dinero_total_inicial = self.persistent.get('dinero_total', 0)

    def aumentar_dificultad(self):
        """Aumenta la dificultad del juego."""
        self.difficulty_level += 1
        self.next_difficulty_score += 100
        self.auto_spawn_interval = max(1000, self.auto_spawn_interval * 0.9)
        self.casa_spawn_interval = max(500, self.casa_spawn_interval * 0.95)
        pygame.time.set_timer(self.SPAWN_AUTO_EVENT, int(self.auto_spawn_interval))
        pygame.time.set_timer(self.SPAWN_CASA_EVENT, int(self.casa_spawn_interval))
        print(f"¡Dificultad aumentada a nivel {self.difficulty_level}!")

    def get_event(self, event):
        if event.type == pygame.QUIT: self.quit = True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: self.done = True
        
        if event.type == self.SPAWN_CASA_EVENT:
            casa = Casa(self.background.speed, self.casa_spawn_limite_izq, self.casa_spawn_limite_der)
            self.scenery.add(casa)
            self.targets.add(casa.buzon)
        
        if event.type == self.SPAWN_AUTO_EVENT:
            auto = Auto(self.background.speed, self.player.limite_izquierdo, self.player.limite_derecho)
            self.obstacles.add(auto)

        if event.type == self.SPAWN_ACEITE_EVENT:
            aceite = ManchaAceite(self.background.speed, self.player.limite_izquierdo, self.player.limite_derecho)
            self.obstacles.add(aceite)
            self.charcos.add(aceite)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.periodicos_restantes > 0:
                self.periodicos_restantes -= 1
                periodico = Periodico(self.player.rect.center, event.pos, self.background.speed)
                self.projectiles.add(periodico)
                if event.pos[0] < self.player.rect.centerx: self.player.lanzar('throw_left')
                else: self.player.lanzar('throw_right')
                
    def update(self, dt):
        self.background.update(dt)
        # Actualizamos todos los grupos
        self.scenery.update(dt)
        self.targets.update(dt)
        self.obstacles.update(dt)
        self.player_group.update(dt)
        self.projectiles.update(dt)
        self.devueltos.update(dt)

        # 1. Aumentar dificultad
        if self.score >= self.next_difficulty_score:
            self.aumentar_dificultad()

        # 2. Colisiones de periódicos
        # vs Buzones
        hits_buzon = pygame.sprite.groupcollide(self.projectiles, self.targets, False, True)
        for periodico, _ in hits_buzon.items():
            if not periodico.acerto:
                self.score += 10; self.periodicos_restantes += 2; periodico.acerto = True; periodico.kill()
        
        # --- LÓGICA DE COLISIÓN CORREGIDA ---
        # vs Obstáculos
        hits_obstaculos = pygame.sprite.groupcollide(self.projectiles, self.obstacles, True, False)
        for _, obstaculos_golpeados in hits_obstaculos.items():
            obstaculo = obstaculos_golpeados[0]
            
            # Primero, comprobamos si el obstáculo es un Auto
            if isinstance(obstaculo, Auto):
                # Si es un auto, entonces sí podemos preguntar si es de policía
                if obstaculo.es_policia and random.random() < 0.3:
                    devuelto = PeriodicoDevuelto(obstaculo.rect.center, self.player.rect.center, self.background.speed)
                    self.devueltos.add(devuelto)
                    print("¡La policía te devuelve el periódico!")

        # 3. Colisiones del jugador
        if pygame.sprite.spritecollide(self.player, self.charcos, True):
            self.player.ralentizar()
        if pygame.sprite.spritecollide(self.player, self.devueltos, True):
            self.periodicos_restantes = max(0, self.periodicos_restantes - 5)
            
        # 4. Lógica de penalización y derrota
        for buzon in list(self.targets):
            if buzon.rect.top > settings.SCREEN_HEIGHT: self.score -= 5; buzon.kill()
        screen_rect = pygame.Rect(0, 0, settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
        for periodico in list(self.projectiles):
            if not screen_rect.colliderect(periodico.rect):
                if not periodico.acerto: self.score -= 1
                periodico.kill()
        
        lost = False
        obstaculos_activos = [obs for obs in self.obstacles if hasattr(obs, 'is_active') and obs.is_active]
        if self.player.hitbox.collidelist([obs.hitbox for obs in obstaculos_activos]) != -1: lost = True
        if self.periodicos_restantes <= 0 and not self.projectiles: lost = True
        
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
        self.scenery.draw(surface)
        self.targets.draw(surface)
        self.obstacles.draw(surface)
        self.player_group.draw(surface)
        self.projectiles.draw(surface)
        self.devueltos.draw(surface)
        
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
            all_drawable_sprites = [self.player_group.sprite] + self.scenery.sprites() + self.targets.sprites() + self.obstacles.sprites() + self.projectiles.sprites()
            for sprite in all_drawable_sprites:
                if hasattr(sprite, 'hitbox'):
                    pygame.draw.rect(surface, (0, 255, 0), sprite.hitbox, 2)