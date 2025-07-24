# src/games/paperboy/paperboy_state.py
import pygame
from ...states.base_state import BaseState
from ... import settings
from ...components.scrolling_background import ScrollingBackground
from .entities import PlayerBike

class PaperboyState(BaseState):
    def __init__(self):
        super().__init__()
        self.next_state = "HUB"
        
        # ---- CAMBIO PRINCIPAL AQUÍ ----
        # Ya no necesitamos una lista de imágenes.
        # Le pasamos la ruta de nuestra única imagen "tira larga".
        # Asegúrate de que el nombre del archivo sea el correcto.
        self.background = ScrollingBackground(
            image_path="assets/images/paperboy_level_strip.png", 
            speed=300
        )

        # El resto del código para el jugador no cambia
        self.all_sprites = pygame.sprite.Group()
        self.player = PlayerBike()
        self.all_sprites.add(self.player)

    def get_event(self, event):
        if event.type == pygame.QUIT:
            self.quit = True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.done = True

    def update(self, dt):
        # Actualizamos el fondo y todos los sprites (incluido el jugador)
        self.background.update(dt)
        self.all_sprites.update(dt) # Pasamos 'dt' para el movimiento

    def draw(self, surface):
        # Dibujamos el fondo primero y luego los sprites
        self.background.draw(surface)
        self.all_sprites.draw(surface)