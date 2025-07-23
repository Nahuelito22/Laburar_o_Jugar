# src/app.py

import pygame
from . import settings
# Eliminamos la importación de MenuState por ahora y añadimos HubState
from .states.hub_state import HubState

class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(settings.SCREEN_SIZE)
        pygame.display.set_caption("Laburar o Jugar?")
        self.clock = pygame.time.Clock()
        
        self.state_dict = {
            # 'MENU': MenuState(), # Dejamos comentado MenuState por ahora
            'HUB': HubState(),    # <-- MODIFICACIÓN: Añadimos el nuevo estado
        }
        self.state_name = 'HUB'   # <-- MODIFICACIÓN: Hacemos que el juego inicie en el HUB
        self.current_state = self.state_dict[self.state_name]
        # <-- MODIFICACIÓN: Llamamos a startup() para el estado inicial
        self.current_state.startup({}) 

    def run(self):
        # El bucle principal no cambia
        while not self.current_state.quit:
            dt = self.clock.tick(settings.FPS) / 1000.0
            
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
        previous_state_name = self.state_name
        self.state_name = self.current_state.next_state
        persistent_data = self.current_state.persistent
        
        # Obtenemos el nuevo estado del diccionario
        self.current_state = self.state_dict[self.state_name]
        # Le pasamos los datos persistentes del estado anterior
        self.current_state.startup(persistent_data)