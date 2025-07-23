# src/app.py
import pygame
from . import settings
from .states.menu_state import MenuState # Importar el primer estado

class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(settings.SCREEN_SIZE)
        pygame.display.set_caption("Laburar o Jugar?")
        self.clock = pygame.time.Clock()
        self.state_dict = {
            'MENU': MenuState(),
            # Aquí irán los otros estados: 'HUB', 'PONG', 'PAPERBOY', 'GAME_OVER'
        }
        self.state_name = 'MENU'
        self.current_state = self.state_dict[self.state_name]

    def run(self):
        while not self.current_state.quit:
            dt = self.clock.tick(settings.FPS) / 1000.0 # Delta time en segundos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.current_state.quit = True
                self.current_state.get_event(event)

            self.current_state.update(dt)
            self.current_state.draw(self.screen)
            pygame.display.flip()

            if self.current_state.done:
                self.flip_state()

        pygame.quit()

    def flip_state(self):
        """Función para cambiar de un estado a otro."""
        previous_state = self.state_name
        self.state_name = self.current_state.next_state
        persistent_data = self.current_state.persist # Guardar datos entre estados si es necesario
        self.current_state = self.state_dict[self.state_name]
        self.current_state.startup(persistent_data)