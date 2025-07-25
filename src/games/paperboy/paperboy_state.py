# src/games/paperboy/paperboy_state.py
import pygame
import random
from ...states.base_state import BaseState
from ... import settings
from ...components.scrolling_background import ScrollingBackground
from .entities import PlayerPaperboy # <-- Importamos la nueva clase del jugador

class PaperboyState(BaseState):
    def __init__(self):
        super().__init__()
        self.next_state = "HUB"
        
        # 1. Creamos el fondo con tus 8 imágenes de barrio
        bg_paths = [f"assets/images/barrio_{i}.png" for i in range(1, 9)] # Asume nombres como Barrio_1.png, Barrio_2.png, etc.
        self.background = ScrollingBackground(image_paths=bg_paths, speed=300)

        # 2. Creamos los grupos de sprites y al jugador
        self.all_sprites = pygame.sprite.Group()
        self.player = PlayerPaperboy()
        self.all_sprites.add(self.player)

    def get_event(self, event):
        if event.type == pygame.QUIT:
            self.quit = True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.done = True

    def update(self, dt):
        self.background.update(dt)
        self.all_sprites.update(dt)

    def draw(self, surface):
        self.background.draw(surface)
        self.all_sprites.draw(surface)