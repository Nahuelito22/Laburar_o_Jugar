# src/states/base_state.py
import pygame

class BaseState:
    def __init__(self):
        self.done = False
        self.quit = False
        self.next_state = None
        self.persistent = {}

    def startup(self, persistent):
        self.persistent = persistent

    def get_event(self, event):
        pass

    def update(self, dt):
        pass

    def draw(self, surface):
        pass

    def cleanup(self):
        """Se ejecuta justo antes de salir del estado."""
        print(f"Limpiando estado: {self.__class__.__name__}")