# src/states/base_state.py
class BaseState:
    def __init__(self):
        self.done = False
        self.quit = False
        self.next_state = None
        self.screen_rect = pygame.display.get_surface().get_rect()

    def startup(self, persistent):
        """Se llama una vez cuando el estado se activa."""
        self.persistent = persistent

    def get_event(self, event):
        """Maneja un solo evento."""
        pass

    def update(self, dt):
        """Actualiza la lógica del estado."""
        pass

    def draw(self, surface):
        """Dibuja todo en la pantalla."""
        pass