# main.py
import multiprocessing
from src.app import App

if __name__ == "__main__":
    multiprocessing.freeze_support()
    game_app = App()
    game_app.run()