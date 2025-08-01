# src/app.py
import pygame
from . import settings
from .states.intro_state import IntroState
from .states.hub_state import HubState
from .games.paperboy.paperboy_state import PaperboyState
from .states.game_over_state import GameOverState
from .states.arcade_state import ArcadeState
from .games.pong.pong_state import PongState
from .states.menu_state import MenuState
from .games.space_invaders.space_invaders_state import SpaceInvadersState
from .games.cxys.cxys_state import CXYSState

class App:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode(settings.SCREEN_SIZE)
        pygame.display.set_caption("Laburar o Jugar?")
        self.clock = pygame.time.Clock()
        
        self.state_classes = {
            'MENU': MenuState,
            'INTRO': IntroState,
            'HUB': HubState,
            'PAPERBOY': PaperboyState,
            'GAME_OVER': GameOverState,
            'ARCADE': ArcadeState,
            'PONG': PongState,
            'SF': SpaceInvadersState,
            'CXYS': CXYSState,
        }
        self.state_name = 'MENU'
        self.current_state = self.state_classes[self.state_name]()
        self.current_state.startup({})

    def run(self):
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
        previous_state_name = self.state_name
        self.state_name = self.current_state.next_state
        persistent_data = self.current_state.persistent
        
        # Limpiamos el estado actual antes de cambiar
        self.current_state.cleanup()
        
        # Creamos una NUEVA instancia del nuevo estado
        self.current_state = self.state_classes[self.state_name]()
        self.current_state.startup(persistent_data)