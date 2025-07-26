# src/save_manager.py
import json

SAVE_FILE = "savegame.json"

def load_data():
    """Carga los datos de guardado. Si no existen, crea valores por defecto."""
    try:
        with open(SAVE_FILE, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {'high_score': 0}
    return data

def save_data(data):
    """Guarda los datos en el archivo."""
    with open(SAVE_FILE, 'w') as f:
        json.dump(data, f)