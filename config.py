"""
Конфігураційний файл, що містить усі константи, розміри та параметри гри Goose Game.
"""

import os

# --- Game Constants ---
WIDTH = 800
HEIGHT = 600
FPS = 60

# --- Colors (RGB) ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# --- Object Sizes ---
PLAYER_SIZE = (100, 60)
ENEMY_SIZE = (60, 40)
BONUS_SIZE = (40, 40)

# --- Speed Settings ---
PLAYER_SPEED = 10
BG_SPEED = 3

# --- Timer Events (Pygame USEREVENTS) ---
CREATE_ENEMY_EVENT = 30001
CREATE_BONUS_EVENT = 30002
CHANGE_IMG_EVENT = 30003

# --- Timer Intervals (in milliseconds) ---
ENEMY_INTERVAL = 1500
BONUS_INTERVAL = 1500
ANIMATION_INTERVAL = 125

# --- File Paths ---
HIGHSCORE_FILE = "highscore.txt"
ASSETS_DIR = "assets"
GOOSE_DIR = os.path.join(ASSETS_DIR, "goose")

# --- Font Settings ---
FONT_FAMILY = "Verdana"
FONT_SIZE_SMALL = 20
FONT_SIZE_BIG = 50
