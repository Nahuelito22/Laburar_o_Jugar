# src/components/spritesheet.py
import pygame

class SpriteSheet:
    def __init__(self, filename):
        """Carga la hoja de sprites."""
        try:
            self.sheet = pygame.image.load(filename).convert_alpha()
        except pygame.error as e:
            print(f"No se pudo cargar la hoja de sprites: {filename}")
            raise SystemExit(e)

    def get_image(self, x, y, width, height):
        """
        Recorta y devuelve un fotograma específico de la hoja.
        """
        # Creamos una nueva superficie transparente del tamaño del fotograma
        image = pygame.Surface((width, height), pygame.SRCALPHA)
        # Dibujamos solo la porción de la hoja de sprites en la nueva superficie
        image.blit(self.sheet, (0, 0), (x, y, width, height))
        return image