# src/games/pong/pong_state.py
import pygame
import random
from ...states.base_state import BaseState
from ... import settings

class PongState(BaseState):
    def __init__(self):
        super().__init__()
        self.next_state = "ARCADE"
        
        # --- Carga de Sonidos ---
        self.golpe_p1_sound = pygame.mixer.Sound(settings.resource_path("sounds/pongP1.wav"))
        self.golpe_p2_sound = pygame.mixer.Sound(settings.resource_path("sounds/pongP2.wav"))
        self.point_sound = pygame.mixer.Sound(settings.resource_path('sounds/point.mp3'))
        self.music_path = settings.resource_path("sounds/music_pong.mp3")

        # --- Fuentes ---
        self.menu_font = pygame.font.Font(None, 70)
        self.score_font = pygame.font.Font(None, 100)
        self.pause_font = pygame.font.Font(None, 60)
        self.winner_font = pygame.font.Font(None, 80)
        
        # --- Objetos del Juego ---
        self.player1 = pygame.Rect(50, settings.SCREEN_HEIGHT / 2 - 45, 15, 90)
        self.player2 = pygame.Rect(settings.SCREEN_WIDTH - 65, settings.SCREEN_HEIGHT / 2 - 45, 15, 90)
        self.pelota = pygame.Rect(settings.SCREEN_WIDTH / 2 - 10, settings.SCREEN_HEIGHT / 2 - 10, 20, 20)
        
        # --- Lógica de Modos de Juego ---
        self.game_mode = "MENU"
        self.bot_speed = 6
        
        # --- Variables para el fondo dinámico ---
        self.hit_counter = 0
        self.max_hits_for_color_change = 20
        self.line_color = settings.WHITE

    def startup(self, persistent):
        super().startup(persistent)
        self.game_mode = "MENU"
        self.reset_game()
        pygame.mixer.music.load(self.music_path)
        pygame.mixer.music.set_volume(0.5)

    def reset_ball(self, direction=1):
        self.pelota.center = (settings.SCREEN_WIDTH / 2, settings.SCREEN_HEIGHT / 2)
        self.pelota_speed_x = 7 * direction
        self.pelota_speed_y = 7 * random.choice((1, -1))

    def reset_game(self):
        self.hit_counter = 0
        self.line_color = settings.WHITE
        self.player1.y = settings.SCREEN_HEIGHT / 2 - 45
        self.player2.y = settings.SCREEN_HEIGHT / 2 - 45
        self.reset_ball()
        self.player1_speed = 0
        self.player2_speed = 0
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
            
            if self.game_mode == "MENU":
                if event.key == pygame.K_1:
                    self.game_mode = "JVSJ"
                    pygame.mixer.music.play(-1)
                if event.key == pygame.K_2:
                    self.game_mode = "CPUVSJ"
                    pygame.mixer.music.play(-1)
            
            elif not self.winner_text:
                if event.key == pygame.K_p:
                    self.pausa = not self.pausa
                if event.key == pygame.K_w: self.player1_speed = -7
                if event.key == pygame.K_s: self.player1_speed = 7
                if self.game_mode == "JVSJ":
                    if event.key == pygame.K_UP: self.player2_speed = -7
                    if event.key == pygame.K_DOWN: self.player2_speed = 7
        
        if event.type == pygame.KEYUP:
            if not self.winner_text:
                if event.key == pygame.K_w or event.key == pygame.K_s: self.player1_speed = 0
                if self.game_mode == "JVSJ":
                    if event.key == pygame.K_UP or event.key == pygame.K_DOWN: self.player2_speed = 0

    def actualizar_color_linea(self):
        self.hit_counter += 1
        ratio = min(self.hit_counter / self.max_hits_for_color_change, 1.0)
        gb_value = int(255 * (1 - ratio))
        self.line_color = (255, gb_value, gb_value)

    def update(self, dt):
        if self.pausa or self.winner_text or self.game_mode == "MENU":
            return

        self.player1.y += self.player1_speed
        if self.game_mode == "JVSJ":
            self.player2.y += self.player2_speed
        elif self.game_mode == "CPUVSJ":
            if self.player2.centery < self.pelota.centery: self.player2.y += self.bot_speed
            if self.player2.centery > self.pelota.centery: self.player2.y -= self.bot_speed

        if self.player1.top < 0: self.player1.top = 0
        if self.player1.bottom > settings.SCREEN_HEIGHT: self.player1.bottom = settings.SCREEN_HEIGHT
        if self.player2.top < 0: self.player2.top = 0
        if self.player2.bottom > settings.SCREEN_HEIGHT: self.player2.bottom = settings.SCREEN_HEIGHT
        
        self.pelota.x += self.pelota_speed_x
        self.pelota.y += self.pelota_speed_y
        
        if self.pelota.top <= 0 or self.pelota.bottom >= settings.SCREEN_HEIGHT:
            self.pelota_speed_y *= -1
        
        if self.pelota.colliderect(self.player1) and self.pelota_speed_x < 0:
            self.pelota_speed_x *= -1.1
            self.golpe_p1_sound.play()
            self.actualizar_color_linea()
        if self.pelota.colliderect(self.player2) and self.pelota_speed_x > 0:
            self.pelota_speed_x *= -1.1
            self.golpe_p2_sound.play()
            self.actualizar_color_linea()
            
        if self.pelota.left <= 0:
            self.puntos_jugador2 += 1
            self.point_sound.play()
            self.reset_ball(1)
        if self.pelota.right >= settings.SCREEN_WIDTH:
            self.puntos_jugador1 += 1
            self.point_sound.play()
            self.reset_ball(-1)
        
        if self.puntos_jugador1 >= 7: self.winner_text = "¡Ganó el Jugador 1!"
        if self.puntos_jugador2 >= 7: self.winner_text = "¡Ganó CPU!" if self.game_mode == "CPUVSJ" else "¡Ganó el Jugador 2!"

    def draw(self, surface):
        surface.fill(settings.BLACK)
        
        # Dibuja la línea de guiones en el centro con el color dinámico
        line_width = 5
        dash_height = 20
        gap_height = 15
        for y in range(0, settings.SCREEN_HEIGHT, dash_height + gap_height):
            start_pos = (settings.SCREEN_WIDTH / 2 - line_width / 2, y)
            end_pos = (settings.SCREEN_WIDTH / 2 - line_width / 2, y + dash_height)
            pygame.draw.line(surface, self.line_color, start_pos, end_pos, line_width)
            
        pygame.draw.rect(surface, settings.WHITE, self.player1)
        pygame.draw.rect(surface, settings.WHITE, self.player2)
        pygame.draw.ellipse(surface, settings.WHITE, self.pelota)

        texto1 = self.score_font.render(str(self.puntos_jugador1), True, settings.WHITE)
        texto2 = self.score_font.render(str(self.puntos_jugador2), True, settings.WHITE)
        surface.blit(texto1, (settings.SCREEN_WIDTH/4, 20))
        surface.blit(texto2, (settings.SCREEN_WIDTH * 3/4 - texto2.get_width(), 20))
        
        if self.game_mode == "MENU":
            dim_surface = pygame.Surface(settings.SCREEN_SIZE)
            dim_surface.set_alpha(200); dim_surface.fill(settings.BLACK)
            surface.blit(dim_surface, (0,0))
            texto_menu1 = self.menu_font.render("Presiona 1 para JUGADOR vs JUGADOR", True, settings.WHITE)
            texto_menu2 = self.menu_font.render("Presiona 2 para JUGADOR vs CPU", True, settings.WHITE)
            surface.blit(texto_menu1, texto_menu1.get_rect(center=(settings.SCREEN_WIDTH/2, settings.SCREEN_HEIGHT/2 - 50)))
            surface.blit(texto_menu2, texto_menu2.get_rect(center=(settings.SCREEN_WIDTH/2, settings.SCREEN_HEIGHT/2 + 50)))

        if self.pausa:
            texto_pausa = self.pause_font.render("PAUSA", True, settings.WHITE)
            surface.blit(texto_pausa, texto_pausa.get_rect(center=(settings.SCREEN_WIDTH/2, settings.SCREEN_HEIGHT/2)))
        
        if self.winner_text:
            pygame.mixer.music.stop()
            texto_ganador = self.winner_font.render(self.winner_text, True, (200, 200, 0))
            surface.blit(texto_ganador, texto_ganador.get_rect(center=(settings.SCREEN_WIDTH/2, settings.SCREEN_HEIGHT/2)))

    def cleanup(self):
        pygame.mixer.music.stop()
        return super().cleanup()