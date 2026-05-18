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
pygame.display.set_caption("Endless Platform Fighter - Chaos Mode")

# Colors
BACKGROUND_COLOR = (30, 30, 40)
PLAYER_COLOR = (0, 150, 255)     # Neon Blue (YOU)
ENEMY_COLOR = (255, 50, 50)      # Crimson Red (ENEMY)
TEXT_COLOR = (255, 255, 255)
CD_READY_COLOR = (0, 255, 100)   # Green for ready cooldown
CD_WAIT_COLOR = (255, 150, 0)    # Orange for waiting

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

# Combat Settings
score = 0
crit_cooldown = 5000  # 5 seconds in milliseconds
last_crit_time = -5000  # Allows player to crit immediately on game start

# Enemy Settings
ENEMY_SIZE = 35
base_enemy_speed = 2.0
enemies_list = []

def create_enemy():
    """Generates a dictionary containing independent properties for a new enemy"""
    return {
        "x": random.randint(100, SCREEN_WIDTH - 100),
        "y": FLOOR_Y - ENEMY_SIZE,
        "hp": 100,
        "speed": random.uniform(base_enemy_speed, base_enemy_speed + 1.0),
        "dir": random.choice([-1, 0, 1]),  # -1: Left, 0: Still, 1: Right
        "wander_timer": random.randint(30, 90)  # How many frames to walk in this direction
    }

# Start the game with 3 enemies on screen
for _ in range(3):
    enemies_list.append(create_enemy())

# Setup Font for UI
font = pygame.font.SysFont("Arial", 26)
clock = pygame.time.Clock()

# --- MAIN GAME LOOP ---
while True:
    current_time = pygame.time.get_ticks()
    
    # Calculate critical hit cooldown remaining
    time_since_last_crit = current_time - last_crit_time
    crit_cd_remaining = max(0, (crit_cooldown - time_since_last_crit) / 1000)

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
                
            # BASIC ATTACK: Z Key
            if event.key == pygame.K_z:
                for enemy in enemies_list:
                    distance = math.sqrt((player_x - enemy["x"])**2 + (player_y - enemy["y"])**2)
                    if distance < 70:
                        enemy["hp"] -= 34
                        print(f"SLASH! Enemy HP: {enemy['hp']}")

            # CRITICAL ATTACK: X Key (5-second cooldown, instant kill)
            if event.key == pygame.K_x:
                if time_since_last_crit >= crit_cooldown:
                    last_crit_time = current_time
                    print("CRITICAL SMASH!!!")
                    
                    # Hit all enemies in radius
                    for enemy in enemies_list:
                        distance = math.sqrt((player_x - enemy["x"])**2 + (player_y - enemy["y"])**2)
                        if distance < 100:  # Slightly larger range for crit
                            enemy["hp"] -= 100  # Instant obliteration
                else:
                    print(f"Critical Hit on cooldown! Wait {crit_cd_remaining:.1f}s")

    # Smooth Continuous Movement (Left / Right)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player_x -= player_speed
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
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

    # Process all active enemies
    for enemy in enemies_list[:]:  # Iterate over a slice copy to safely remove items
        # Random Wandering AI
        enemy["wander_timer"] -= 1
        if enemy["wander_timer"] <= 0:
            enemy["dir"] = random.choice([-1, 0, 1])
            enemy["wander_timer"] = random.randint(30, 120)  # Pick new time limit

        # Move enemy based on direction
        enemy["x"] += enemy["dir"] * enemy["speed"]

        # Keep enemies inside screen borders
        if enemy["x"] < 0:
            enemy["x"] = 0
            enemy["dir"] = 1
        if enemy["x"] > SCREEN_WIDTH - ENEMY_SIZE:
            enemy["x"] = SCREEN_WIDTH - ENEMY_SIZE
            enemy["dir"] = -1

        # Check if enemy is dead
        if enemy["hp"] <= 0:
            score += 1
            enemies_list.remove(enemy)
            
            # Spawn a replacement
            enemies_list.append(create_enemy())
            
            # Difficulty Spike: Spawn an EXTRA enemy every 5 kills (Max 10 total)
            if score % 5 == 0 and len(enemies_list) < 10:
                enemies_list.append(create_enemy())
                base_enemy_speed += 0.2  # Everything gets slightly faster too!

    # 3. DRAWING / RENDERING
    screen.fill(BACKGROUND_COLOR) # Clear screen
    
    # Draw the Ground Floor
    pygame.draw.rect(screen, (60, 60, 80), [0, FLOOR_Y, SCREEN_WIDTH, SCREEN_HEIGHT - FLOOR_Y])
    
    # Draw Player (Blue)
    pygame.draw.rect(screen, PLAYER_COLOR, [player_x, player_y, player_size, player_size])
    
    # Draw All Enemies (Red)
    for enemy in enemies_list:
        pygame.draw.rect(screen, ENEMY_COLOR, [enemy["x"], enemy["y"], ENEMY_SIZE, ENEMY_SIZE])
        
        # Draw Individual Enemy Health Bars
        if enemy["hp"] > 0:
            pygame.draw.rect(screen, (255, 0, 0), [enemy["x"], enemy["y"] - 10, ENEMY_SIZE, 4])
            pygame.draw.rect(screen, (0, 255, 0), [enemy["x"], enemy["y"] - 10, ENEMY_SIZE * (enemy["hp"] / 100), 4])
    
    # Draw UI Text (Score)
    score_text = font.render(f"Kills: {score}  |  Enemies: {len(enemies_list)}/10", True, TEXT_COLOR)
    screen.blit(score_text, (20, 20))
    
    # Draw UI Text (Crit Cooldown Status)
    if crit_cd_remaining == 0:
        crit_text = font.render("CRIT (X): READY", True, CD_READY_COLOR)
    else:
        crit_text = font.render(f"CRIT (X): {crit_cd_remaining:.1f}s", True, CD_WAIT_COLOR)
    screen.blit(crit_text, (20, 55))

    pygame.display.flip()
    clock.tick(60)
