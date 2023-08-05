import pygame
import random
import math
from pygame.locals import *
import gravitypy.config as var
from .button.button import *
from .particle.particle import *


def main():
    # Initialize button states
    increase_button_stateR = False
    decrease_button_stateR = False
    increase_button_stateM = False
    decrease_button_stateM = False
    increase_button_stateVx = False
    decrease_button_stateVx = False
    increase_button_stateVy = False
    decrease_button_stateVy = False
    add_button_statement = False
    add_button_statement_put = False
    move_particles = False
    pause = False
    reset_button_statement = False
    reset_scale_button_statement = False

    # Generate random particles
    for i in range(var.NUM_PARTICLES):
        if i == 0:
            x = var.WIDTH // 2
            y = var.HEIGHT// 2
            mass = 60
            var.PARTICLES.append(Particles(x, y, mass, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), random.randint(30, 30), pygame.Vector2(0, 0)))
        else:
            x = random.randint(0, var.WIDTH)
            y = random.randint(0, var.HEIGHT)
            mass = random.uniform(1, 10)
            mass = 5
            var.PARTICLES.append(Particles(x, y, mass, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), random.randint(0, 5), pygame.Vector2(0, 0)))

    def decrease_radius():
        if var.ADDED_RADIUS-1 != 0:
            var.ADDED_RADIUS -= 1
        return var.ADDED_RADIUS 

    def increase_radius():
        var.ADDED_RADIUS += 1
        return var.ADDED_RADIUS 

    def decrease_mass():
        if var.ADDED_MASS-1 != 0:
            var.ADDED_MASS -= 1
        return var.ADDED_MASS

    def increase_mass():
        var.ADDED_MASS += 1
        return var.ADDED_MASS

    def decrease_velocity_x():
        if not add_button_statement_put:
            var.ADDED_VELOCITY.x -= 0.05
        return var.ADDED_VELOCITY.x 
   
    def increase_velocity_x():
        if not add_button_statement_put:
            var.ADDED_VELOCITY.x += 0.05
        return var.ADDED_VELOCITY.x 
    
    def decrease_velocity_y():
        if not add_button_statement_put:
            var.ADDED_VELOCITY.y -= 0.05
        return var.ADDED_VELOCITY.y
    
    def increase_velocity_y():
        if not add_button_statement_put:
            var.ADDED_VELOCITY.y += 0.05
        return var.ADDED_VELOCITY.y
    
    def reset_particles():
        var.NUM_PARTICLES = 0
        var.PARTICLES = []
        reset_button_statement = False
        return var.NUM_PARTICLES, var.PARTICLES, reset_button_statement
    
    def reset_scale():
        var.SCALE = 1
        reset_scale_button_statement = False
        return var.SCALE, reset_scale_button_statement

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Left click
                if event.button == 1: 
                    # Check if the mouse click is inside the buttons
                    if button_increse_r.button_rect.collidepoint(event.pos):
                        increase_button_stateR = True
                    elif button_decrese_r.button_rect.collidepoint(event.pos):
                        decrease_button_stateR = True
                    elif button_increse_m.button_rect.collidepoint(event.pos):
                        increase_button_stateM = True
                    elif button_decrese_m.button_rect.collidepoint(event.pos):
                        decrease_button_stateM = True
                    elif button_increse_vx.button_rect.collidepoint(event.pos):
                        increase_button_stateVx = True
                    elif button_decrese_vx.button_rect.collidepoint(event.pos):
                        decrease_button_stateVx = True
                    elif button_increse_vy.button_rect.collidepoint(event.pos):
                        increase_button_stateVy = True
                    elif button_decrese_vy.button_rect.collidepoint(event.pos):
                        decrease_button_stateVy = True
                    elif add_button.button_rect.collidepoint(event.pos):
                        add_button_statement = True
                    elif add_button_statement:
                        add_button_statement_put = True
                    elif reset_button.button_rect.collidepoint(event.pos):
                        reset_button_statement = True
                    elif reset_scale_button.button_rect.collidepoint(event.pos):
                        reset_scale_button_statement = True
                    
                    for particle in var.PARTICLES:
                        scaled_x = int(var.MOUSE_X + (particle.position.x - var.MOUSE_X) * var.SCALE)
                        scaled_y = int(var.MOUSE_Y + (particle.position.y - var.MOUSE_Y) * var.SCALE)
                        distance = math.sqrt((event.pos[0] - scaled_x)**2 + (event.pos[1] - scaled_y)**2)
                        if distance <= particle.radius * var.SCALE:
                            particle.selected = not particle.selected
                # Right click
                if event.button == 3: 
                    if add_button_statement:
                        add_button_statement = False
                # Scroll Up
                elif event.button == 4:  
                    var.SCALE += 0.1
                    var.MOUSE_X, var.MOUSE_Y = pygame.mouse.get_pos()
                # Scroll Down 
                elif event.button == 5:  
                    if var.SCALE - 0.1 > 0:
                        var.SCALE -= 0.1
                        var.MOUSE_X, var.MOUSE_Y = pygame.mouse.get_pos()
                    
            elif event.type == pygame.MOUSEBUTTONUP:
                initial_mouse_pos = None
                if event.button == 1:
                    # Reset button states
                    increase_button_stateR = False
                    decrease_button_stateR = False
                    increase_button_stateM = False
                    decrease_button_stateM = False
                    increase_button_stateVx = False
                    decrease_button_stateVx = False
                    increase_button_stateVy = False
                    decrease_button_stateVy = False
                    reset_button_statement = False
                    reset_scale_button_statement = False

                    
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    move_particles = True
                    move_direction = pygame.Vector2(5/var.SCALE, 0)
                elif event.key == pygame.K_RIGHT:
                    move_particles = True
                    move_direction = pygame.Vector2(-5/var.SCALE, 0)
                elif event.key == pygame.K_UP:
                    move_particles = True
                    move_direction = pygame.Vector2(0, 5/var.SCALE)
                elif event.key == pygame.K_DOWN:
                    move_particles = True
                    move_direction = pygame.Vector2(0, -5/var.SCALE)
                elif event.key == pygame.K_SPACE:
                    pause = not pause
            elif event.type == pygame.KEYUP:
                if event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]:
                    move_particles = False

        var.SCREEN.fill((20,20,40))

        if increase_button_stateR:
            increase_radius()
        elif decrease_button_stateR:
            decrease_radius()
        elif increase_button_stateM:
            increase_mass()
        elif decrease_button_stateM:
            decrease_mass()
        elif increase_button_stateVx:
            increase_velocity_x()
        elif decrease_button_stateVx:
            decrease_velocity_x()
        elif increase_button_stateVy:
            increase_velocity_y()
        elif decrease_button_stateVy:
            decrease_velocity_y()
        elif reset_button_statement:
            reset_particles()
        elif reset_scale_button_statement:
            reset_scale()

        if add_button_statement:
            actual_mouse_x, actuale_mouse_y = pygame.mouse.get_pos()
            scaled_mouse_x = int(var.MOUSE_X + (actual_mouse_x - var.MOUSE_X) * var.SCALE)
            scaled_mouse_y = int(var.MOUSE_Y + (actuale_mouse_y - var.MOUSE_Y) * var.SCALE)
            circle_center = (scaled_mouse_x, scaled_mouse_y)
            circle_radius = int(var.ADDED_RADIUS * var.SCALE)
            if 0 < scaled_mouse_y < var.HEIGHT and 0 < scaled_mouse_x < var.WIDTH: 
                pygame.draw.circle(
                    var.SCREEN, 
                    var.ADDED_COLOR , 
                    circle_center, 
                    circle_radius
                    )

        if add_button_statement_put:
            particle_velocity = var.ADDED_VELOCITY.copy()
            var.PARTICLES.append(
                Particles(
                    actual_mouse_x,
                    actuale_mouse_y,
                    var.ADDED_MASS,
                    var.ADDED_COLOR ,
                    var.ADDED_RADIUS,
                    particle_velocity
                )
            )
            add_button_statement_put = False
            # Change color of the next particle
            var.ADDED_COLOR  = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            var.NUM_PARTICLES += 1

        # Sort in case bigger particles do not cover smaller ones 
        var.PARTICLES = sorted(var.PARTICLES, key=lambda x: x.radius, reverse=True)
        
        for particle in var.PARTICLES:
            if move_particles:
                particle.position += move_direction * var.SCALE
            elif pause:
                pass
            else:
                particle.update()
            
                for other_particle in var.PARTICLES:
                    if particle != other_particle:
                        particle.apply_gravitational_force(other_particle, var.G)
            particle.draw_scaled(var.MOUSE_X, var.MOUSE_Y)
        
        # Buttons
        button_increse_r = Buttons(50,50,"Increse R", pygame.Rect(50,50,120,25))
        button_decrese_r = Buttons(150,50,"Decrese R", pygame.Rect(50,85,120,25))
        button_increse_m = Buttons(250,50,"Increse M", pygame.Rect(200,50,120,25))
        button_decrese_m = Buttons(350,50,"Decrese M", pygame.Rect(200,85,120,25))
        button_increse_vx = Buttons(250,50,"+ Vx", pygame.Rect(350,50,50,25))
        button_decrese_vx = Buttons(350,50,"- Vx", pygame.Rect(350,85,50,25))
        button_increse_vy = Buttons(250,50,"+ Vy", pygame.Rect(410,50,50,25))
        button_decrese_vy = Buttons(350,50,"- Vy", pygame.Rect(410,85,50,25))
        add_button = Buttons(350,50,"Add", pygame.Rect(550,50,120,60))
        reset_button = Buttons(350,50,"Reset Praticles", pygame.Rect(850,50,160,25))
        reset_scale_button = Buttons(350,50,"Reset scale", pygame.Rect(1050,50,120,25))
        
        # Text
        text_radius = var.FONT.render(f'Radius: {var.ADDED_RADIUS}', True, (240,240,240))
        var.SCREEN.blit(text_radius, (50, 20))

        text_mass = var.FONT.render(f'Mass: {var.ADDED_MASS}', True, (240,240,240))
        var.SCREEN.blit(text_mass, (200, 20))
            
        text_mass = var.FONT.render(f'Velocity: {var.ADDED_VELOCITY}', True, (240,240,240))
        var.SCREEN.blit(text_mass, (350, 20))
        
        text_num_partciles = var.FONT.render(f'Number of particles: {var.NUM_PARTICLES}', True, (240,240,240))
        var.SCREEN.blit(text_num_partciles, (950, 0))
        
        text_num_partciles = var.FONT.render(f'Scale: {int(var.SCALE*100)}%', True, (240,240,240))
        var.SCREEN.blit(text_num_partciles, (950, 20))
        
        text_num_partciles = var.FONT.render('Move camera with arrows keys, pause with a space', True, (240,240,240))
        var.SCREEN.blit(text_num_partciles, (var.WIDTH // 2 - 200, 0))

        pygame.display.flip()
        var.CLOCK.tick(60)
    
    pygame.quit()