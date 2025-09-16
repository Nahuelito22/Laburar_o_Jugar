import pygame
import random
from ...states.base_state import BaseState
from ... import settings
from .entities import Nave, Disparo, Enemigo, Explosion, Estrella, Asteroide, EnemigoDisparo

class SpaceInvadersState(BaseState):
    def __init__(self):
        super().__init__()
        self.next_state = "ARCADE"
        self.sonido_disparo = pygame.mixer.Sound(settings.resource_path('sounds/space_shot.mp3'))
        self.sonido_disparo.set_volume(0.1)
        self.sonido_enemigo_abatido = pygame.mixer.Sound(settings.resource_path("sounds/enemy_down.ogg"))
        self.sonido_nave_exp = pygame.mixer.Sound(settings.resource_path('sounds/explosion_nave.wav'))
        self.music_path = settings.resource_path('sounds/fondo_space.ogg')
        self.imagenes_enemigos = [
            pygame.image.load(settings.resource_path("images/green.png")).convert_alpha(),
            pygame.image.load(settings.resource_path("images/red.png")).convert_alpha(),
            pygame.image.load(settings.resource_path("images/yellow.png")).convert_alpha()
        ]
        sprite_sheet = pygame.image.load(settings.resource_path('images/nave_sheet.png')).convert_alpha()
        nave_cenital = pygame.transform.scale(sprite_sheet.subsurface((0, 0, 512, 512)), (80, 80))
        nave_derecha = pygame.transform.scale(sprite_sheet.subsurface((512, 0, 512, 512)), (90, 90))
        nave_izquierda = pygame.transform.scale(sprite_sheet.subsurface((1024, 0, 512, 512)), (90, 90))
        self.nave_template = Nave(nave_cenital, nave_izquierda, nave_derecha)
        self.imagenes_explosion = [pygame.transform.scale(pygame.image.load(settings.resource_path(f'images/explosion{i}.png')).convert_alpha(), (120, 120)) for i in range(1, 4)]
        self.font = pygame.font.Font(None, 60)
        self.game_over_font = pygame.font.Font(None, 80)

    def startup(self, persistent):
        super().startup(persistent)
        self.nave_group = pygame.sprite.GroupSingle()
        self.disparos_jugador = pygame.sprite.Group() # Renombrado para claridad
        self.disparos_enemigos = pygame.sprite.Group() # <-- NUEVO GRUPO
        self.enemigos = pygame.sprite.Group()
        self.explosiones = pygame.sprite.Group()
        self.estrellas_fondo = [Estrella(speed=50) for _ in range(50)]
        self.estrellas_medias = [Estrella(speed=150) for _ in range(30)]
        self.asteroides = pygame.sprite.Group()
        self.asteroide_spawn_timer = 0
        self.asteroide_spawn_interval = 1.0
        self.nave = self.nave_template
        self.nave.rect.centerx = settings.SCREEN_WIDTH / 2
        self.nave.rect.bottom = settings.SCREEN_HEIGHT - 20
        self.nave_group.add(self.nave)
        self.score = 0
        self.game_over = False
        self.direccion_enemigos = 1
        self.velocidad_enemigos = 120
        self.crear_oleada()
        pygame.mixer.music.load(self.music_path)
        pygame.mixer.music.set_volume(0.25)
        pygame.mixer.music.play(-1)

    def get_event(self, event):
        if event.type == pygame.QUIT: self.quit = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: self.done = True
            if not self.game_over and event.key == pygame.K_SPACE:
                if len(self.disparos_jugador) < 6:
                    d1 = Disparo(self.nave.rect.left + 15, self.nave.rect.top)
                    d2 = Disparo(self.nave.rect.right - 15, self.nave.rect.top)
                    self.disparos_jugador.add(d1, d2)
                    self.sonido_disparo.play()

    def update(self, dt):
        if self.game_over:
            self.explosiones.update(dt)
            return

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]: self.nave.speed = -400
        elif keys[pygame.K_d]: self.nave.speed = 400
        else: self.nave.speed = 0

        # Actualizamos todos los grupos
        for estrella in self.estrellas_fondo: estrella.update(dt)
        for estrella in self.estrellas_medias: estrella.update(dt)
        self.asteroides.update(dt); self.nave_group.update(dt); self.disparos_jugador.update(dt); self.disparos_enemigos.update(dt)
        
        # Spawning de asteroides
        self.asteroide_spawn_timer += dt
        if self.asteroide_spawn_timer >= self.asteroide_spawn_interval:
            self.asteroides.add(Asteroide()); self.asteroide_spawn_timer = 0
            self.asteroide_spawn_interval = random.uniform(0.5, 2.0)
        
        bajar = 0
        if any(e.rect.right >= settings.SCREEN_WIDTH or e.rect.left <= 0 for e in self.enemigos):
            self.direccion_enemigos *= -1
            bajar = 20
        
        for enemigo in self.enemigos:
            disparo_nuevo = enemigo.update(dt, self.direccion_enemigos * self.velocidad_enemigos, bajar)
            if disparo_nuevo:
                self.disparos_enemigos.add(disparo_nuevo)
        
        # Colisiones
        hits = pygame.sprite.groupcollide(self.disparos_jugador, self.enemigos, True, True)
        if hits:
            self.score += len(hits)
            self.sonido_enemigo_abatido.play()

        # --- NUEVO: Colisión de disparos enemigos con el jugador ---
        if pygame.sprite.spritecollide(self.nave, self.disparos_enemigos, True):
            self.trigger_game_over()
            
        if pygame.sprite.spritecollide(self.nave, self.enemigos, True) or any(e.rect.bottom >= settings.SCREEN_HEIGHT for e in self.enemigos):
            self.trigger_game_over()
            
        if not self.enemigos:
            self.velocidad_enemigos *= 1.15
            self.crear_oleada()

    def draw(self, surface):
        surface.fill(settings.BLACK)
        for estrella in self.estrellas_fondo: estrella.draw(surface)
        for estrella in self.estrellas_medias: estrella.draw(surface)
        self.asteroides.draw(surface)
        self.nave_group.draw(surface)
        self.disparos_jugador.draw(surface)
        self.disparos_enemigos.draw(surface) # <-- Dibujamos los disparos enemigos
        self.enemigos.draw(surface)
        self.explosiones.draw(surface)
        score_text = self.font.render(f"Puntaje: {self.score}", True, settings.WHITE)
        surface.blit(score_text, (10, 10))
        if self.game_over and not self.explosiones:
            game_over_text = self.game_over_font.render("GAME OVER", True, "red")
            surface.blit(game_over_text, game_over_text.get_rect(center=(settings.SCREEN_WIDTH/2, settings.SCREEN_HEIGHT/2)))


    def crear_oleada(self):
        imagen_oleada = random.choice(self.imagenes_enemigos)
        for fila in range(3):
            for columna in range(8):
                x = columna * 80 + 80
                y = fila * 60 + 50
                enemigo = Enemigo(x, y, imagen_oleada)
                self.enemigos.add(enemigo)
    
    def trigger_game_over(self):
        if not self.game_over:
            self.game_over = True
            self.sonido_nave_exp.play()
            pygame.mixer.music.stop()
            explosion = Explosion(self.nave.rect.center, self.imagenes_explosion)
            self.explosiones.add(explosion)
            self.nave.kill()
            
    def cleanup(self):
        pygame.mixer.music.stop()
        return super().cleanup()