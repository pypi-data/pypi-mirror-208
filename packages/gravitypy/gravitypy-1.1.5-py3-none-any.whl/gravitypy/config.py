import pygame
import random
import os 

pygame.init()
pygame.display.set_caption("GravityPy")

current_file = __file__
current_dir = os.path.dirname(current_file)
font_file = os.path.join(current_dir, 'resources', 'fonts', 'minecraft_font.ttf')
font_size = 16
FONT = pygame.font.Font(font_file, font_size)

WIDTH, HEIGHT = 1200, 700
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
CLOCK = pygame.time.Clock()
G = 100
SCALE = 1.0
PARTICLES = []
ADDED_RADIUS = 20
ADDED_MASS = 20
ADDED_VELOCITY = pygame.Vector2(0, 0)
NUM_PARTICLES = 30
ADDED_COLOR = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
MOUSE_X, MOUSE_Y = pygame.mouse.get_pos()
