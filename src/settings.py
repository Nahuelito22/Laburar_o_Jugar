# src/settings.py
import pygame
import sys
import os

# --- Función de ayuda para PyInstaller ---
def resource_path(relative_path):
    """ Obtiene la ruta absoluta al recurso, funciona para dev y para PyInstaller """
    try:
        # PyInstaller crea una carpeta temporal y guarda la ruta en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Si no se está ejecutando como .exe, la ruta base es la del proyecto
        base_path = os.path.abspath(".")
    
    # Unimos la ruta base con "assets" y la ruta relativa del archivo
    return os.path.join(base_path, "assets", relative_path)

# El resto de settings no cambia

# Dimensiones de la pantalla
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)

# Fotogramas por segundo
FPS = 60

# Colores (en formato RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

DEBUG_MODE = False