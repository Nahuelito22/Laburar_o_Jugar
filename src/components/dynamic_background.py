# src/components/dynamic_background.py
import pygame
import random
from .. import settings

class DynamicBackground:
    def __init__(self, speed):
        self.speed = speed

        # --- Colores del Escenario ---
        self.color_cesped = (34, 139, 34)
        self.color_vereda = (192, 192, 192)
        self.color_calle = (105, 105, 105)
        self.color_linea = settings.WHITE

        # --- Geometría de la Calle ---
        ancho_total = settings.SCREEN_WIDTH
        ancho_calle = ancho_total * 0.5
        ancho_vereda = ancho_total * 0.1
        ancho_cesped = (ancho_total - ancho_calle - 2 * ancho_vereda) / 2

        self.cesped_izq = pygame.Rect(0, 0, ancho_cesped, settings.SCREEN_HEIGHT)
        self.vereda_izq = pygame.Rect(self.cesped_izq.right, 0, ancho_vereda, settings.SCREEN_HEIGHT)
        self.calle = pygame.Rect(self.vereda_izq.right, 0, ancho_calle, settings.SCREEN_HEIGHT)
        self.vereda_der = pygame.Rect(self.calle.right, 0, ancho_vereda, settings.SCREEN_HEIGHT)
        
        # --- Líneas de la Calle (la parte que se mueve) ---
        self.lineas = []
        largo_linea = 40
        espacio_linea = 30
        for y in range(-largo_linea, settings.SCREEN_HEIGHT + largo_linea, largo_linea + espacio_linea):
            linea = pygame.Rect(self.calle.centerx - 5, y, 10, largo_linea)
            self.lineas.append(linea)

    def update(self, dt):
        # Movemos cada línea hacia abajo
        for linea in self.lineas:
            linea.y += self.speed * dt
            if linea.top > settings.SCREEN_HEIGHT:
                linea.bottom = 0

    def draw(self, surface):
        # Dibujamos las capas estáticas
        surface.fill(self.color_cesped)
        pygame.draw.rect(surface, self.color_vereda, self.vereda_izq)
        pygame.draw.rect(surface, self.color_vereda, self.vereda_der)
        pygame.draw.rect(surface, self.color_calle, self.calle)
        
        # Dibujamos las líneas que se mueven
        for linea in self.lineas:
            pygame.draw.rect(surface, self.color_linea, linea)