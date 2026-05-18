import pygame
import sys
import random
import math

# 1. Initialize Pygame
pygame.init()

# Setup screen
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Endless Platform Fighter")

# Colors (SWAPPED)
BACKGROUND_COLOR = (30, 30, 40)
PLAYER_COLOR = (0, 150, 255)     # Neon Blue (YOU)
ENEMY_COLOR = (255, 50, 50)      # Crimson Red (ENEMY)
TEXT_COLOR = (255, 255, 255)

# Floor Level
FLOOR_Y = 500

# Player Properties
player_x = 100
player_y = FLOOR_Y - 40  # Start on the floor
player_size = 40
player_speed = 6

# Physics / Jumping Variables
gravity = 0.8
y_velocity = 0
jump_power = -16
is_grounded = True

# Enemy Properties
enemy_size = 35
enemy_x = 600
enemy_y = FLOOR_Y - enemy_size
enemy_hp = 100
enemy_speed = 2.0
score = 0

def spawn_enemy():
    """Spawns an enemy at a random horizontal spot on the floor"""
    x = random.randint(100, SCREEN_WIDTH - 100)
    y = FLOOR_Y - enemy_size
    hp = 100
    return x, y, hp

# Setup Font for Score
font = pygame.font.SysFont("Arial", 30)
clock = pygame.time.Clock()

# --- MAIN GAME LOOP ---
while True:
    # 1. INPUTS / EVENTS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        if event.type == pygame.KEYDOWN:
            # JUMP: Space Bar
            if event.key == pygame.K_SPACE and is_grounded:
                y_velocity = jump_power
                is_grounded = False
                
            # ATTACK: Z Key
            if event.key == pygame.K_z:
                # Distance check to see if enemy is close enough to hit
                distance = math.sqrt((player_x - enemy_x)**2 + (player_y - enemy_y)**2)
                if distance < 70:
                    enemy_hp -= 34
                    print(f"SLASH! Enemy HP: {enemy_hp}")

    # Horizontal Movement (Left / Right)
    keys = pygame.key.get_pressed()
    if keys[keys[pygame.K_LEFT] or keys[pygame.K_a]]:
        player_x -= player_speed
    if keys[keys[pygame.K_RIGHT] or keys[pygame.K_d]]:
        player_x += player_speed

    # Keep player inside screen horizontal borders
    if player_x < 0: player_x = 0
    if player_x > SCREEN_WIDTH - player_size: player_x = SCREEN_WIDTH - player_size

    # 2. PHYSICS & GAME LOGIC
    
    # Apply Gravity to Player
    y_velocity += gravity
    player_y += y_velocity

    # Floor Collision Check
    if player_y >= FLOOR_Y - player_size:
        player_y = FLOOR_Y - player_size
        y_velocity = 0
        is_grounded = True

    # Enemy AI: Run toward the player horizontally on the floor
    if enemy_x < player_x: enemy_x += enemy_speed
    if enemy_x > player_x: enemy_x -= enemy_speed

    # Check if enemy is dead
    if enemy_hp <= 0:
        score += 1
        enemy_x, enemy_y, enemy_hp = spawn_enemy()
        enemy_speed += 0.4  # Next enemy gets faster!
        print(f"Enemy Defeated! Kills: {score}")

    # 3. DRAWING / RENDERING
    screen.fill(BACKGROUND_COLOR) # Clear screen
    
    # Draw the Ground Floor
    pygame.draw.rect(screen, (60, 60, 80), [0, FLOOR_Y, SCREEN_WIDTH, SCREEN_HEIGHT - FLOOR_Y])
    
    # Draw Enemy (Now Red)
    pygame.draw.rect(screen, ENEMY_COLOR, [enemy_x, enemy_y, enemy_size, enemy_size])
    
    # Draw Player (Now Blue)
    pygame.draw.rect(screen, PLAYER_COLOR, [player_x, player_y, player_size, player_size])
    
    # Draw UI (Score)
    score_text = font.render(f"Kills: {score}", True, TEXT_COLOR)
    screen.blit(score_text, (20, 20))
    
    # Draw Enemy Health Bar
    if enemy_hp > 0:
        pygame.draw.rect(screen, (255, 0, 0), [enemy_x, enemy_y - 10, enemy_size, 5])
        pygame.draw.rect(screen, (0, 255, 0), [enemy_x, enemy_y - 10, enemy_size * (enemy_hp / 100), 5])

    pygame.display.flip()
    clock.tick(60)
