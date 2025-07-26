# src/states/arcade_state.py
import pygame
from .base_state import BaseState
from .. import settings
from ..entities import PlayerHub # Reutilizamos el jugador del Hub

class ArcadeState(BaseState):
    def __init__(self):
        super().__init__()
        self.background_image = pygame.image.load("assets/images/hub_arcade.png").convert()
        self.background_image = pygame.transform.scale(self.background_image, settings.SCREEN_SIZE)

        # Creamos al jugador y lo posicionamos en la entrada
        self.player = PlayerHub(x=settings.SCREEN_WIDTH - 150, y=settings.SCREEN_HEIGHT - 80)
        self.all_sprites = pygame.sprite.Group(self.player)

        # --- Zonas interactivas para las máquinas (ajustá estas coordenadas) ---
        self.pong_machine = pygame.Rect(350, 280, 150, 300)
        self.otra_maquina = pygame.Rect(550, 280, 150, 300)
        # ... podés agregar más rectángulos para las otras máquinas

    def get_event(self, event):
        if event.type == pygame.QUIT:
            self.quit = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: # Con ESC volvemos al Hub principal
                self.next_state = "HUB"
                self.done = True
            # Podríamos añadir una tecla de "acción" como Enter
            # if event.key == pygame.K_RETURN:
            #     if self.player.rect.colliderect(self.pong_machine):
            #         self.next_state = "PONG"
            #         self.done = True

    def update(self, dt):
        self.all_sprites.update(dt)
        # Por ahora, la transición será automática al tocar la máquina
        if self.player.rect.colliderect(self.pong_machine):
            print("Entrando a PONG...")
            self.next_state = "PONG"
            self.done = True

    def draw(self, surface):
        surface.blit(self.background_image, (0, 0))
        self.all_sprites.draw(surface)

        # Modo Debug para ver las cajas de las máquinas
        if settings.DEBUG_MODE:
            pygame.draw.rect(surface, (255, 0, 255), self.pong_machine, 2)
            pygame.draw.rect(surface, (255, 255, 0), self.otra_maquina, 2)