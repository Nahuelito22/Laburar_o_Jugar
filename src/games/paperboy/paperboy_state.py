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
        self.obstacles = pygame.sprite.Group() # Grupo para todo lo que colisiona con el jugador
        self.targets = pygame.sprite.Group()   # Grupo para los buzones
        self.projectiles = pygame.sprite.Group() # Grupo para los periódicos

        # --- Creamos al jugador ---
        self.player = PlayerPaperboy()
        self.all_sprites.add(self.player)
        self.score = 0

        # ---- NUEVO: Sistema de Spawning con Timers ----
        # Evento para crear un buzón
        self.SPAWN_BUZON_EVENT = pygame.USEREVENT + 1
        pygame.time.set_timer(self.SPAWN_BUZON_EVENT, 2500) # Cada 2.5 segundos

        # Evento para crear un auto
        self.SPAWN_AUTO_EVENT = pygame.USEREVENT + 2
        pygame.time.set_timer(self.SPAWN_AUTO_EVENT, 3500) # Cada 3.5 segundos

    def get_event(self, event):
        if event.type == pygame.QUIT:
            self.quit = True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.done = True
        
        # ---- NUEVO: Manejo de Spawning y Lanzamiento ----
        if event.type == self.SPAWN_BUZON_EVENT:
            buzon = Buzon(self.background.speed_y)
            self.all_sprites.add(buzon)
            self.targets.add(buzon)

        if event.type == self.SPAWN_AUTO_EVENT:
            auto = Auto(self.background.speed_y)
            self.all_sprites.add(auto)
            self.obstacles.add(auto)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Creamos un periódico que viaja desde el jugador hasta el clic del mouse
            periodico = Periodico(self.player.rect.center, event.pos, self.background.speed_y)
            self.all_sprites.add(periodico)
            self.projectiles.add(periodico)

            # Le decimos al jugador que inicie la animación de lanzamiento
            if event.pos[0] < self.player.rect.centerx:
                self.player.lanzar('throw_left')
            else:
                self.player.lanzar('throw_right')


    def update(self, dt):
        self.background.update(dt)
        self.all_sprites.update(dt) # Actualiza a TODOS los sprites (jugador, autos, buzones, periódicos)

        # ---- NUEVO: Lógica de Colisiones ----
        # Comprobamos si algún periódico choca con algún buzón
        hits = pygame.sprite.groupcollide(self.projectiles, self.targets, True, True)
        if hits:
            self.score += 10
            print(f"Puntaje: {self.score}")

        # Comprobamos si el jugador choca con algún obstáculo
        if pygame.sprite.spritecollide(self.player, self.obstacles, False):
            print("¡CHOQUE!")
            # Aquí podríamos terminar el juego, quitar una vida, etc.

    def draw(self, surface):
        self.background.draw(surface)
        self.all_sprites.draw(surface)
        
        # Dibujar el puntaje en pantalla
        font = pygame.font.Font(None, 50)
        score_text = font.render(f"Puntaje: {self.score}", True, settings.WHITE)
        surface.blit(score_text, (10, 10))

        # El modo debug sigue funcionando si lo activaste
        if settings.DEBUG_MODE:
            pygame.draw.line(surface, (255, 0, 0), (self.player.limite_izquierdo, 0), (self.player.limite_izquierdo, settings.SCREEN_HEIGHT), 2)
            pygame.draw.line(surface, (255, 0, 0), (self.player.limite_derecho, 0), (self.player.limite_derecho, settings.SCREEN_HEIGHT), 2)