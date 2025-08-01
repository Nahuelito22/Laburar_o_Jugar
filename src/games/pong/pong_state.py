# src/games/pong/pong_state.py
import pygame
import random
from ...states.base_state import BaseState
from ... import settings

class PongState(BaseState):
    def __init__(self):
        super().__init__()
        self.next_state = "ARCADE"
        
        # --- Carga de Assets ---
        self.fondo = pygame.image.load(settings.resource_path("images/fondo_pong.jpg")).convert()
        self.fondo = pygame.transform.scale(self.fondo, settings.SCREEN_SIZE)
        
        self.golpe_p1_sound = pygame.mixer.Sound(settings.resource_path("sounds/pongP1.wav"))
        self.golpe_p2_sound = pygame.mixer.Sound(settings.resource_path("sounds/pongP2.wav"))
        self.point_sound = pygame.mixer.Sound(settings.resource_path('sounds/point.mp3'))
        self.music_path = settings.resource_path("sounds/music_pong.mp3") # Guardamos la ruta para usarla después

        # --- Fuentes
        self.score_font = pygame.font.Font(None, 100)
        self.player_font = pygame.font.Font(None, 40)
        self.pause_font = pygame.font.Font(None, 60)
        self.winner_font = pygame.font.Font(None, 80)
        
        # --- Objetos del Juego ---
        self.player1 = pygame.Rect(50, settings.SCREEN_HEIGHT / 2 - 45, 15, 90)
        self.player2 = pygame.Rect(settings.SCREEN_WIDTH - 65, settings.SCREEN_HEIGHT / 2 - 45, 15, 90)
        self.pelota = pygame.Rect(settings.SCREEN_WIDTH / 2 - 10, settings.SCREEN_HEIGHT / 2 - 10, 20, 20)
        
        self.reset_game()

    def startup(self, persistent):
        """Se ejecuta cada vez que entramos al estado."""
        super().startup(persistent)
        self.reset_game()
        pygame.mixer.music.load(self.music_path)
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

    def reset_game(self):
        """Reinicia las variables del juego a su estado inicial."""
        self.player1.y = settings.SCREEN_HEIGHT / 2 - 45
        self.player2.y = settings.SCREEN_HEIGHT / 2 - 45
        self.pelota.center = (settings.SCREEN_WIDTH / 2, settings.SCREEN_HEIGHT / 2)
        
        self.player1_speed = 0
        self.player2_speed = 0
        self.pelota_speed_x = 5 * random.choice((1, -1))
        self.pelota_speed_y = 5 * random.choice((1, -1))

        self.puntos_jugador1 = 0
        self.puntos_jugador2 = 0
        self.pausa = False
        self.winner_text = ""

    def get_event(self, event):
        if event.type == pygame.QUIT:
            self.quit = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.done = True
            if event.key == pygame.K_p:
                self.pausa = not self.pausa
            # Jugador 1
            if event.key == pygame.K_w: self.player1_speed = -6
            if event.key == pygame.K_s: self.player1_speed = 6
            # Jugador 2
            if event.key == pygame.K_UP: self.player2_speed = -6
            if event.key == pygame.K_DOWN: self.player2_speed = 6
        
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w or event.key == pygame.K_s: self.player1_speed = 0
            if event.key == pygame.K_UP or event.key == pygame.K_DOWN: self.player2_speed = 0

    def update(self, dt):
        if self.pausa or self.winner_text:
            return

        # Movimiento de jugadores
        self.player1.y += self.player1_speed
        self.player2.y += self.player2_speed

        # Límites de jugadores
        if self.player1.top < 0: self.player1.top = 0
        if self.player1.bottom > settings.SCREEN_HEIGHT: self.player1.bottom = settings.SCREEN_HEIGHT
        if self.player2.top < 0: self.player2.top = 0
        if self.player2.bottom > settings.SCREEN_HEIGHT: self.player2.bottom = settings.SCREEN_HEIGHT
        
        # Movimiento de la pelota
        self.pelota.x += self.pelota_speed_x
        self.pelota.y += self.pelota_speed_y

        # Colisiones de la pelota
        if self.pelota.top <= 0 or self.pelota.bottom >= settings.SCREEN_HEIGHT:
            self.pelota_speed_y *= -1
        
        if self.pelota.colliderect(self.player1) and self.pelota_speed_x < 0:
            self.pelota_speed_x *= -1.1
            self.golpe_p1_sound.play()
        if self.pelota.colliderect(self.player2) and self.pelota_speed_x > 0:
            self.pelota_speed_x *= -1.1
            self.golpe_p2_sound.play()
            
        # Puntuación
        if self.pelota.left <= 0:
            self.puntos_jugador2 += 1
            self.point_sound.play()
            self.pelota.center = (settings.SCREEN_WIDTH / 2, settings.SCREEN_HEIGHT / 2)
            self.pelota_speed_x = 5 * random.choice((1, -1))
        if self.pelota.right >= settings.SCREEN_WIDTH:
            self.puntos_jugador1 += 1
            self.point_sound.play()
            self.pelota.center = (settings.SCREEN_WIDTH / 2, settings.SCREEN_HEIGHT / 2)
            self.pelota_speed_x = 5 * random.choice((1, -1))
        
        # Condición de victoria
        if self.puntos_jugador1 >= 7:
            self.winner_text = "¡Ganó el Jugador 1!"
        if self.puntos_jugador2 >= 7:
            self.winner_text = "¡Ganó el Jugador 2!"

    def draw(self, surface):
        surface.blit(self.fondo, (0,0))
        pygame.draw.rect(surface, settings.WHITE, self.player1)
        pygame.draw.rect(surface, settings.WHITE, self.player2)
        pygame.draw.ellipse(surface, settings.WHITE, self.pelota)
        pygame.draw.aaline(surface, settings.WHITE, (settings.SCREEN_WIDTH/2, 0), (settings.SCREEN_WIDTH/2, settings.SCREEN_HEIGHT))

        # Dibujar puntajes
        texto1 = self.score_font.render(str(self.puntos_jugador1), True, settings.WHITE)
        texto2 = self.score_font.render(str(self.puntos_jugador2), True, settings.WHITE)
        surface.blit(texto1, (settings.SCREEN_WIDTH/4, 20))
        surface.blit(texto2, (settings.SCREEN_WIDTH * 3/4 - texto2.get_width(), 20))
        
        if self.pausa:
            texto_pausa = self.pause_font.render("PAUSA", True, settings.WHITE)
            surface.blit(texto_pausa, texto_pausa.get_rect(center=(settings.SCREEN_WIDTH/2, settings.SCREEN_HEIGHT/2)))
        
        if self.winner_text:
            pygame.mixer.music.stop()
            texto_ganador = self.winner_font.render(self.winner_text, True, (200, 200, 0))
            surface.blit(texto_ganador, texto_ganador.get_rect(center=(settings.SCREEN_WIDTH/2, settings.SCREEN_HEIGHT/2)))

    def cleanup(self):
        """Se ejecuta al salir del estado."""
        pygame.mixer.music.stop()
        return super().cleanup()