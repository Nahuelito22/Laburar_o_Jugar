import json
import os

SAVE_FILE = "savegame.json"

def load_data():
    """Carga los datos de guardado. Si no existen, crea valores por defecto."""
    try:
        with open(SAVE_FILE, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        # Valores por defecto si no hay partida guardada
        data = {
            'nombre_usuario': 'Jugador',
            'high_score': 0,
            'dinero_total': 0,
            'fichas': 0
        }
    return data

def save_data(data):
    """Guarda los datos en el archivo."""
    with open(SAVE_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def load_high_scores(game_name):
    """Carga los high scores para un juego específico."""
    score_file = f"{game_name}_scores.json"
    if not os.path.exists(score_file):
        return []
    try:
        with open(score_file, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_high_score(game_name, score):
    """Guarda un nuevo high score para un juego específico."""
    scores = load_high_scores(game_name)
    scores.append(score)
    scores = sorted(scores, reverse=True)[:10] # Mantener el top 10
    score_file = f"{game_name}_scores.json"
    with open(score_file, 'w') as f:
        json.dump(scores, f, indent=4)