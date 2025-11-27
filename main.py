# main.py
import asyncio # Necesario para la Web
import pygame
from src.app import App
from src import settings

# Definimos la función principal como asíncrona
async def main():
    # Inicializamos la App
    game_app = App()
    
    # Bucle principal
    while not game_app.current_state.quit:
        # 1. Calcular DT
        dt = game_app.clock.tick(settings.FPS) / 1000.0
        
        # Corrección para Web: Si el navegador se traba, dt no debe ser gigante
        dt = min(dt, 0.05) 

        # 2. Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_app.current_state.quit = True
            game_app.current_state.get_event(event)

        # 3. Actualizar
        game_app.current_state.update(dt)
        
        # 4. Dibujar
        game_app.current_state.draw(game_app.screen)
        pygame.display.flip()

        # 5. Cambiar estado
        if game_app.current_state.done:
            game_app.flip_state()

        # --- ESTA LÍNEA ES VITAL PARA LA WEB ---
        # Permite al navegador actualizar la ventana sin congelarse
        await asyncio.sleep(0)

    pygame.quit()

# Ejecutamos la función asíncrona
if __name__ == "__main__":
    asyncio.run(main())