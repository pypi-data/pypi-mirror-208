import pygame
import gravitypy.config as var 
import math

class Particles:
    def __init__(self, x, y, mass, color, radius, velocity):
        self.position = pygame.Vector2(x, y)
        self.velocity = velocity
        self.mass = mass
        self.radius = radius
        self.color = color
        self.stats_text = None
        self.selected = None
    def apply_force(self, force):
        acceleration = force / self.mass
        self.velocity += acceleration
    def update(self):
        self.position += self.velocity
    
    def draw_scaled(self, mouse_x, mouse_y):
        scaled_x = int(mouse_x + (self.position.x - mouse_x) * var.SCALE)
        scaled_y = int(mouse_y + (self.position.y - mouse_y) * var.SCALE)
        circle_center = (scaled_x, scaled_y)
        if 0 < scaled_y < var.HEIGHT and 0 < scaled_x < var.WIDTH: 
            pygame.draw.circle(var.SCREEN, self.color, circle_center, int(self.radius * var.SCALE))

        # Render and position the statistics text
        if self.selected:
            stats_lines = [
                f"Mass: {self.mass}",
                f"Radius: {self.radius}",
                f"Velocity: {round(self.velocity.x, 2), round(self.velocity.y, 2)}"
            ]
            line_height = 20  
            text_y = scaled_y + int(self.radius * var.SCALE) + 10  
            for i, line in enumerate(stats_lines):
                stats_text = var.FONT.render(line, True, (255, 255, 255))
                stats_text_rect = stats_text.get_rect(center=(scaled_x, text_y + i * line_height))
                var.SCREEN.blit(stats_text, stats_text_rect)
    def apply_gravitational_force(self, other_particle, G):
        dx = abs(self.position.x - other_particle.position.x)
        dy = abs(self.position.y - other_particle.position.y)

        if dx < self.radius or dy < self.radius:
            pass
        else:
            try:
                r = math.sqrt(dx**2 + dy**2)
                a = G * other_particle.mass / r**2
                theta = math.asin(dy / r)

                if self.position.y  > other_particle.position.y:
                    self.apply_force(pygame.Vector2(0, -math.sin(theta) * a))
                else:
                    self.apply_force(pygame.Vector2(0, math.sin(theta) * a))

                if self.position.x > other_particle.position.x:
                    self.apply_force(pygame.Vector2(-math.cos(theta) * a, 0))
                else:
                    self.apply_force(pygame.Vector2(math.cos(theta) * a, 0))
            except ZeroDivisionError:
                pass
    def is_clicked(self, mouse_pos):
        return self.position.distance_to(pygame.Vector2(*mouse_pos)) <= self.radiusresources                
