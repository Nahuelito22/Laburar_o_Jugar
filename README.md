# Laburar o Jugar? - Proyecto para Programación 2

Este repositorio contiene el Trabajo Práctico Nº3 para la materia Programación 2, dictada por el profesor Pietrobon.C. 
El objetivo es desarrollar un videojuego 2D aplicando conceptos de Programación Orientada a Objetos y patrones de diseño.

## 🎮 Descripción del Juego
Laburar o Jugar? es un videojuego 2D que combina un "hub world" (mundo central) con múltiples mini-juegos de estilo arcade.

El jugador se encuentra en la piel de un personaje que, al salir de su casa, debe decidir entre dos caminos:

- Ir a trabajar: Esta opción desencadena un mini-juego de habilidad y reflejos inspirado en el clásico Paperboy.

- Ir al salón de Arcade: Esta opción lleva al jugador a un salón de videojuegos donde puede explorar y elegir entre distintas máquinas, cada una con su propio juego clásico (como Pong, Breakout, etc.).

Como característica especial, algunos mini-juegos podrán ser controlados mediante la cámara web utilizando OpenCV para la detección de movimiento de manos.

## 💡 Conceptos Aplicados
A lo largo del proyecto se trabajaron los siguientes temas principales:

- Programación Orientada a Objetos (POO): El juego está estructurado en clases (Player, Enemy, Obstacle, GameState) para un código más modular y escalable.

- Patrones de Diseño: Se implementaron al menos 3 patrones para resolver problemas comunes de arquitectura:

- State Pattern: Para gestionar las diferentes pantallas y estados del juego (Menú, Hub, Pong, Game Over).

- Factory Pattern: Para la creación de objetos complejos como enemigos u obstáculos de forma organizada.

- Singleton Pattern: Para garantizar una única instancia de clases gestoras globales (ej: SoundManager).

- Desarrollo de Videojuegos 2D con Pygame: Uso de la librería para renderizado de gráficos, manejo de sprites, detección de colisiones, gestión de eventos (teclado/mouse) y reproducción de audio.

- Integración de Librerías Externas: Uso de OpenCV y NumPy para implementar el control por cámara web.

## ▶️ Instalación y Ejecución
Para ejecutar el juego, necesitas tener instalado Python 3.10 o superior.

Pasos:

1. Clonar el repositorio (reemplazá la URL si es necesario):

```bash
git clone https://github.com/Nahuelito22/laburar-o-jugar.git
```

2. Navegar hasta el directorio del proyecto:
```bash
cd laburar-o-jugar
```

3. Crear y activar un entorno virtual (recomendado):


- En Windows
```bash
python -m venv .venv
```
```bash
.venv\Scripts\activate
```

4. Instalar todas las dependencias del proyecto:

```bash
pip install -r requirements.txt
```

5. Ejecutar el juego:

```bash
python main.py
```
## 🚀 Ejecutable del Juego (Versión Portable)
* Para facilitar el acceso y la ejecución del juego sin necesidad de instalar Python o sus dependencias, se ha utilizado PyInstaller para generar un archivo ejecutable (.exe).

Existen dos maneras de utilizarlo:

    1) Descarga Directa:  
    Podés descargar únicamente la carpeta dist/ (generalmente comprimida en un .zip desde la sección de "Releases" de GitHub). 
    Una vez descomprimida, simplemente ejecutá el archivo Laburar o Jugar.exe que se encuentra adentro.

    2) Acceso Directo en el Repositorio: 
    Si clonaste el repositorio completo, se ha incluido un acceso directo en la carpeta raíz que apunta al ejecutable dentro de la carpeta dist/.

## ⚙️ Tecnologías Utilizadas
- Lenguaje: Python 3
    - Librería Principal: Pygame
    - Interfaz de Usuario: Pygame-GUI
    - Control por Cámara: OpenCV-Python, NumPy
- Control de Versiones: Git y GitHub


## 👨‍💻 Autores
**Gustavo Garcia**  
GitHub: [@Gusti Garcia](https://github.com/GustiGarcia)  
Email: profegusgarcia@gmail.com

**Nahuel Ghilardi**  
GitHub: [@Nahuelito22](https://github.com/Nahuelito22)  
Email: matiasghilardisalinas@gmail.com

## 📄 Licencia
Este proyecto está licenciado bajo los términos de la Licencia MIT.

## 🤝 Agradecimientos
Un agradecimiento especial al profesor Pietrobon.C y a los compañeros de cursada por el apoyo y la colaboración.
