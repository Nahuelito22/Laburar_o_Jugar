# src/games/space_invaders/space_invaders_state.py
import pygame
import random
from ...states.base_state import BaseState
from ... import settings
from .entities import Nave, Disparo, Enemigo, Explosion

class SpaceInvadersState(BaseState):
    def __init__(self):
        super().__init__()
        self.next_state = "ARCADE"
        self.game_over = False
        self.score = 0

        # --- Carga de Assets ---
        self.fondo = pygame.image.load(settings.resource_path("images/fondo_space.jpg")).convert()
        self.fondo = pygame.transform.scale(self.fondo, settings.SCREEN_SIZE)
        
        sprite_sheet = pygame.image.load(settings.resource_path('images/nave_sheet.png')).convert_alpha()
        nave_cenital = pygame.transform.scale(sprite_sheet.subsurface((0, 0, 512, 512)), (80, 80))
        nave_derecha = pygame.transform.scale(sprite_sheet.subsurface((512, 0, 512, 512)), (90, 90))
        nave_izquierda = pygame.transform.scale(sprite_sheet.subsurface((1024, 0, 512, 512)), (90, 90))
        
        self.nave_template = Nave(nave_cenital, nave_izquierda, nave_derecha)
        
        self.imagenes_explosion = []
        for i in range(1, 4):
            img = pygame.image.load(settings.resource_path(f'images/explosion{i}.png')).convert_alpha()
            self.imagenes_explosion.append(pygame.transform.scale(img, (80, 80)))

        self.font = pygame.font.Font(None, 60)
        self.game_over_font = pygame.font.Font(None, 80)

    def startup(self, persistent):
        super().startup(persistent)
        # --- Grupos de Sprites ---
        self.nave_group = pygame.sprite.GroupSingle()
        self.disparos = pygame.sprite.Group()
        self.enemigos = pygame.sprite.Group()
        self.explosiones = pygame.sprite.Group()
        
        # --- Reinicio del Juego ---
        self.nave = self.nave_template
        self.nave.rect.centerx = settings.SCREEN_WIDTH / 2
        self.nave.speed = 0
        self.nave_group.add(self.nave)
        
        self.score = 0
        self.game_over = False
        self.direccion_enemigos = 1
        self.velocidad_enemigos = 100
        
        self.crear_oleada()

    def get_event(self, event):
        if event.type == pygame.QUIT:
            self.quit = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.done = True
            
            if not self.game_over:
                if event.key == pygame.K_a: self.nave.speed = -400
                if event.key == pygame.K_d: self.nave.speed = 400
                if event.key == pygame.K_SPACE:
                    if len(self.disparos) < 8:
                        d1 = Disparo(self.nave.rect.left + 5, self.nave.rect.top + 35)
                        d2 = Disparo(self.nave.rect.right - 20, self.nave.rect.top + 35)
                        self.disparos.add(d1, d2)
        
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a or event.key == pygame.K_d:
                self.nave.speed = 0

    def update(self, dt):
        if self.game_over:
            self.explosiones.update(dt)
            return

        # --- ACTUALIZACIÓN SEPARADA DE GRUPOS ---
        self.nave_group.update(dt)
        self.disparos.update(dt)
        
        bajar = 0
        if any(e.rect.right >= settings.SCREEN_WIDTH or e.rect.left <= 0 for e in self.enemigos):
            self.direccion_enemigos *= -1
            bajar = 15
        
        for enemigo in self.enemigos:
            enemigo.update(dt, self.direccion_enemigos * self.velocidad_enemigos, bajar)
            if enemigo.rect.bottom >= self.nave.rect.top:
                self.trigger_game_over()

        # Colisiones
        for disparo in self.disparos:
            if pygame.sprite.spritecollide(disparo, self.enemigos, True):
                disparo.kill()
                self.score += 1
        
        if pygame.sprite.spritecollide(self.nave, self.enemigos, False):
            self.trigger_game_over()
            
        if not self.enemigos:
            self.velocidad_enemigos += 20
            self.crear_oleada()

    def draw(self, surface):
        surface.blit(self.fondo, (0, 0))
        # Dibujamos los grupos por separado
        self.nave_group.draw(surface)
        self.disparos.draw(surface)
        self.enemigos.draw(surface)
        self.explosiones.draw(surface)

        score_text = self.font.render(f"Puntaje: {self.score}", True, settings.WHITE)
        surface.blit(score_text, (10, 10))

        if self.game_over and not self.explosiones:
            game_over_text = self.game_over_font.render("GAME OVER", True, "red")
            surface.blit(game_over_text, game_over_text.get_rect(center=(settings.SCREEN_WIDTH/2, settings.SCREEN_HEIGHT/2)))

    def crear_oleada(self):
        for fila in range(3):
            for columna in range(8):
                x = columna * 80 + 80
                y = fila * 60 + 50
                enemigo = Enemigo(x, y)
                self.enemigos.add(enemigo)
    
    def trigger_game_over(self):
        if not self.game_over:
            self.game_over = True
            explosion = Explosion(self.nave.rect.center, self.imagenes_explosion)
            self.explosiones.add(explosion)
            self.nave.kill()
            
    def cleanup(self):
        pass