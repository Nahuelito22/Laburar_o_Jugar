# src/states/hub_state.py

import pygame
from .base_state import BaseState
from .. import settings

class HubState(BaseState):
    def __init__(self):
        # Llama al __init__ de la clase base (BaseState)
        super(HubState, self).__init__()
        
        # Carga la imagen de fondo y la escala al tamaño de la pantalla
        self.background_image = pygame.image.load("assets/images/background_hub.png").convert()
        self.background_image = pygame.transform.scale(self.background_image, (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        
        # Carga la imagen del jugador con transparencia
        self.player_image = pygame.image.load("assets/images/player.png").convert_alpha()
        # Obtiene el rectángulo del jugador para poder posicionarlo
        self.player_rect = self.player_image.get_rect(center=(settings.SCREEN_WIDTH / 2, settings.SCREEN_HEIGHT / 1.5))
        
        # Carga la fuente para el texto
        try:
            self.font = pygame.font.Font("assets/fonts/font.ttf", 48)
        except FileNotFoundError:
            print("Advertencia: No se encontró el archivo de fuente. Usando fuente por defecto.")
            self.font = pygame.font.Font(None, 60) # Usa la fuente por defecto de Pygame si no encuentra la tuya

    def startup(self, persistent):
        """Se llama cuando este estado se vuelve activo."""
        self.persistent = persistent
        # Podríamos recibir datos del estado anterior, como el dinero del jugador
        # self.player_money = persistent.get('money', 0)

    def get_event(self, event):
        """Maneja los eventos del usuario (teclado, mouse)."""
        if event.type == pygame.QUIT:
            self.quit = True

    def update(self, dt):
        """Actualiza la lógica del estado (por ahora, no hay nada que actualizar)."""
        pass

    def draw(self, surface):
        """Dibuja todo en la pantalla."""
        # 1. Dibuja el fondo primero, cubriendo toda la pantalla
        surface.blit(self.background_image, (0, 0))
        
        # 2. Dibuja al jugador encima del fondo
        surface.blit(self.player_image, self.player_rect)
        
        # 3. Dibuja las opciones de texto
        self.draw_text("1. Ir a Trabajar", self.font, settings.WHITE, surface, settings.SCREEN_WIDTH / 4, settings.SCREEN_HEIGHT / 3)
        self.draw_text("2. Ir al Arcade", self.font, settings.WHITE, surface, settings.SCREEN_WIDTH * 3 / 4, settings.SCREEN_HEIGHT / 3)

    def draw_text(self, text, font, color, surface, x, y):
        """Función de ayuda para dibujar texto centrado."""
        text_obj = font.render(text, True, color)
        text_rect = text_obj.get_rect(center=(x, y))
        surface.blit(text_obj, text_rect)