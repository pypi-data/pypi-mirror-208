import pygame
from gravitypy.config import * 

class Buttons:
    def __init__(self, x_pos, y_pos, text_input, button_rect):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.text_input = text_input
        self.button_rect = button_rect
        self.text = FONT.render(self.text_input, True, "white")
        self.text_rect = self.text.get_rect(center=(self.button_rect.center))
        self.surface = pygame.Surface(self.button_rect.size, pygame.SRCALPHA)  # Create a surface with transparency
        color = (100, 80, 90, 128)  # Set the color with transparency
        pygame.draw.rect(self.surface, color, (0, 0, *self.button_rect.size))  # Draw the rectangle on the surface
        SCREEN.blit(self.surface, self.button_rect)  # Blit the surface onto the screen
        SCREEN.blit(self.text, self.text_rect)