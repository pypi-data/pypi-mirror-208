import pygame
import random

pygame.init()
pygame.display.set_caption("GravityPy")

FONT = pygame.font.Font('gravitypy/resources/fonts/minecraft_font.ttf', 16)

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
