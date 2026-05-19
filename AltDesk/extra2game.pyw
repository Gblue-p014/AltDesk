import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Game Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLUE = (50, 150, 255)
DARK_GREY = (50, 50, 50)
RED = (255, 80, 80)
GREEN = (40, 180, 100)

# Setup Screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Endless 2D Parkour")
clock = pygame.time.Clock()

# --- PLAYER CLASS ---
class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 60)
        self.vx = 0
        self.vy = 0
        self.speed = 7
        self.gravity = 0.8
        self.jump_strength = -14
        
        self.on_ground = False
        self.on_wall = False
        self.wall_direction = 0

    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        # In an endless runner, we can force forward movement or let them control it
        self.vx = 0
        if keys[pygame.K_LEFT]:
            self.vx = -self.speed
        if keys[pygame.K_RIGHT]:
            self.vx = self.speed

        if keys[pygame.K_SPACE]:
            if self.on_ground:
                self.vy = self.jump_strength
                self.on_ground = False
            elif self.on_wall:
                self.vy = self.jump_strength
                self.vx = -self.wall_direction * self.speed * 2.5  # Stronger push off wall
                self.on_wall = False

    def apply_physics(self):
        if self.on_wall and self.vy > 0:
            self.vy += self.gravity * 0.25  # Smooth wall slide
        else:
            self.vy += self.gravity

        if self.vy > 15:
            self.vy = 15

    def update(self, platforms):
        self.handle_input()
        self.apply_physics()

        # X movement & collision
        self.rect.x += self.vx
        self.check_collisions(platforms, 'horizontal')

        # Y movement & collision
        self.rect.y += self.vy
        self.check_collisions(platforms, 'vertical')
        
        self.check_wall_grip(platforms)

    def check_collisions(self, platforms, direction):
        if direction == 'horizontal':
            for platform in platforms:
                if self.rect.colliderect(platform):
                    if self.vx > 0:
                        self.rect.right = platform.left
                    if self.vx < 0:
                        self.rect.left = platform.right
                        
        if direction == 'vertical':
            self.on_ground = False
            for platform in platforms:
                if self.rect.colliderect(platform):
                    if self.vy > 0:
                        self.rect.bottom = platform.top
                        self.vy = 0
                        self.on_ground = True
                    if self.vy < 0:
                        self.rect.top = platform.bottom
                        self.vy = 0

    def check_wall_grip(self, platforms):
        self.on_wall = False
        self.wall_direction = 0
        if not self.on_ground:
            left_check = pygame.Rect(self.rect.x - 2, self.rect.y, 2, self.rect.height)
            right_check = pygame.Rect(self.rect.right, self.rect.y, 2, self.rect.height)
            
            for platform in platforms:
                if left_check.colliderect(platform):
                    self.on_wall = True
                    self.wall_direction = -1
                elif right_check.colliderect(platform):
                    self.on_wall = True
                    self.wall_direction = 1

    def draw(self, surface, camera_x):
        # Apply camera offset to the drawing position
        draw_rect = self.rect.copy()
        draw_rect.x -= camera_x
        color = RED if self.on_wall else BLUE
        pygame.draw.rect(surface, color, draw_rect)


# --- GENERATOR SYSTEM ---
def generate_world_chunk(start_x):
    """Generates a random cluster of platforms and parkour walls."""
    new_platforms = []
    current_x = start_x
    
    # Generate 5 random obstacles per chunk
    for _ in range(5):
        obstacle_type = random.choice(['floor', 'tall_wall', 'floating_island'])
        
        if obstacle_type == 'floor':
            width = random.randint(150, 300)
            new_platforms.append(pygame.Rect(current_x, 500, width, 100))
            current_x += width + random.randint(100, 200) # Gap size
            
        elif obstacle_type == 'tall_wall':
            # Great for wall jumping!
            width = 40
            height = random.randint(150, 300)
            new_platforms.append(pygame.Rect(current_x, 600 - height, width, height))
            current_x += width + random.randint(120, 220)
            
        elif obstacle_type == 'floating_island':
            width = random.randint(100, 200)
            y_pos = random.randint(250, 400)
            new_platforms.append(pygame.Rect(current_x, y_pos, width, 30))
            current_x += width + random.randint(100, 200)
            
    return new_platforms, current_x


# --- INITIAL GAME SETUP ---
player = Player(100, 300)
camera_x = 0

# Base starter platforms so the player doesn't instantly fall
platforms = [
    pygame.Rect(0, 500, 500, 100),
    pygame.Rect(300, 350, 100, 20)
]
next_generation_x = 500

# Score tracking
score = 0
font = pygame.font.SysFont(None, 36)

# --- MAIN GAME LOOP ---
while True:
    # 1. Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # 2. Update Game State
    player.update(platforms)

    # --- CAMERA SCROLLING LOGIC ---
    # The camera smoothly follows the player when they pass the center of the screen
    if player.rect.x - camera_x > SCREEN_WIDTH / 2:
        camera_x += (player.rect.x - camera_x - SCREEN_WIDTH / 2) * 0.1

    # --- ENDLESS GENERATION & CLEANUP ---
    # If the player is getting close to the end of generated platforms, make more
    if player.rect.x + SCREEN_WIDTH > next_generation_x:
        new_plats, next_generation_x = generate_world_chunk(next_generation_x)
        platforms.extend(new_plats)

    # Remove platforms that are far behind the screen to save memory
    platforms = [p for p in platforms if p.right > camera_x - 200]

    # Update Score based on distance traveled
    if player.rect.x > score:
        score = int(player.rect.x // 10)

    # --- GAME OVER CONDITION ---
    if player.rect.y > SCREEN_HEIGHT:
        # Reset Game
        player = Player(100, 300)
        camera_x = 0
        platforms = [pygame.Rect(0, 500, 500, 100), pygame.Rect(300, 350, 100, 20)]
        next_generation_x = 500
        score = 0

    # 3. Drawing Everything
    screen.fill(WHITE)
    
    # Draw Platforms with camera offset
    for platform in platforms:
        draw_plat = platform.copy()
        draw_plat.x -= camera_x
        pygame.draw.rect(screen, DARK_GREY, draw_plat)
        
    # Draw Player
    player.draw(screen, camera_x)

    # Draw Score UI
    score_text = font.render(f"Score: {score}m", True, GREEN)
    screen.blit(score_text, (20, 20))

    # Refresh Screen
    pygame.display.flip()
    clock.tick(FPS)
