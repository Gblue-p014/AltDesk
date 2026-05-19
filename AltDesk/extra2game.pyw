import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Game Constants
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800  # Taller screen ratio works better for vertical games
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLUE = (50, 150, 255)
DARK_GREY = (30, 30, 30)
NEON_GREEN = (50, 255, 100)
LAVA_RED = (255, 50, 0)

# Setup Screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Infinite Wall Climber")
clock = pygame.time.Clock()

# --- PLAYER CLASS ---
class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 35, 50)
        self.vx = 0
        self.vy = 0
        self.speed = 7
        self.gravity = 0.7
        self.jump_strength = -13
        
        self.on_ground = False
        self.on_wall = False
        self.wall_direction = 0

    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        # Horizontal Control
        self.vx = 0
        if keys[pygame.K_LEFT]:
            self.vx = -self.speed
        if keys[pygame.K_RIGHT]:
            self.vx = self.speed

        # Jumping & The "Infinite Wall Scale" Feature
        if keys[pygame.K_SPACE]:
            if self.on_ground:
                self.vy = self.jump_strength
                self.on_ground = False
            elif self.on_wall:
                # The Feature: Launch straight up with maximum power when hugging a wall!
                self.vy = self.jump_strength * 1.05 
                
                # Give a tiny bit of inward push so they stay glued to the wall if holding toward it
                if keys[pygame.K_RIGHT] and self.wall_direction == 1:
                    self.vx = self.speed
                elif keys[pygame.K_LEFT] and self.wall_direction == -1:
                    self.vx = -self.speed
                    
                self.on_wall = False

    def apply_physics(self):
        # Slightly slower slide down walls to give time to spam spacebar
        if self.on_wall and self.vy > 0:
            self.vy += self.gravity * 0.2
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
                    if self.vy > 0: # Landing
                        self.rect.bottom = platform.top
                        self.vy = 0
                        self.on_ground = True
                    if self.vy < 0: # Hitting ceiling
                        self.rect.top = platform.bottom
                        self.vy = 0

    def check_wall_grip(self, platforms):
        self.on_wall = False
        self.wall_direction = 0
        if not self.on_ground:
            left_check = pygame.Rect(self.rect.x - 3, self.rect.y, 3, self.rect.height)
            right_check = pygame.Rect(self.rect.right, self.rect.y, 3, self.rect.height)
            
            for platform in platforms:
                if left_check.colliderect(platform):
                    self.on_wall = True
                    self.wall_direction = -1
                elif right_check.colliderect(platform):
                    self.on_wall = True
                    self.wall_direction = 1

    def draw(self, surface, camera_y):
        # Apply vertical camera offset
        draw_rect = self.rect.copy()
        draw_rect.y -= camera_y
        color = NEON_GREEN if self.on_wall else BLUE
        pygame.draw.rect(surface, color, draw_rect)


# --- GENERATOR SYSTEM ---
def generate_vertical_chunk(start_y):
    """Generates a random cluster of vertical shafts and platforms moving UPWARD (negative Y)"""
    new_platforms = []
    current_y = start_y
    
    # Generate chunks going upwards (remember, up is negative Y in Pygame)
    for _ in range(6):
        obstacle_type = random.choice(['left_wall', 'right_wall', 'center_platform', 'chasm'])
        current_y -= random.randint(120, 180) # Distance between steps
        
        if obstacle_type == 'left_wall':
            # Perfect for wall-running up the left side
            new_platforms.append(pygame.Rect(0, current_y, random.randint(80, 150), 200))
        
        elif obstacle_type == 'right_wall':
            # Perfect for wall-running up the right side
            width = random.randint(80, 150)
            new_platforms.append(pygame.Rect(SCREEN_WIDTH - width, current_y, width, 200))
            
        elif obstacle_type == 'center_platform':
            # Standard floating platform to jump across
            new_platforms.append(pygame.Rect(random.randint(150, 350), current_y, random.randint(100, 200), 25))
            
        elif obstacle_type == 'chasm':
            # Two walls close together—prime "light speed" climbing zone!
            new_platforms.append(pygame.Rect(0, current_y, 40, 250))
            new_platforms.append(pygame.Rect(SCREEN_WIDTH - 40, current_y, 40, 250))
            current_y -= 100 # Add extra spacing because chasms are tall
            
    return new_platforms, current_y


# --- INITIAL GAME SETUP ---
player = Player(SCREEN_WIDTH // 2, 650)
camera_y = 0

# Base platforms so player doesn't drop instantly at start
platforms = [
    pygame.Rect(0, 750, SCREEN_WIDTH, 50),                 # Floor
    pygame.Rect(0, 0, 30, SCREEN_HEIGHT),                  # Left safety border for start
    pygame.Rect(SCREEN_WIDTH - 30, 0, 30, SCREEN_HEIGHT),  # Right safety border for start
]
next_generation_y = 0

# Score tracking
highest_score = 0
font = pygame.font.SysFont(None, 36)

# Main Game Loop
while True:
    # 1. Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # 2. Update Game State
    player.update(platforms)

    # --- VERTICAL CAMERA SCROLLING ---
    # Camera follows player smoothly when they go above the upper half of the screen
    if player.rect.y - camera_y < SCREEN_HEIGHT / 2:
        camera_y += (player.rect.y - camera_y - SCREEN_HEIGHT / 2) * 0.1

    # --- ENDLESS GENERATION & CLEANUP (UPWARD) ---
    # If player approaches top of generated area, generate more above (negative Y)
    if player.rect.y - SCREEN_HEIGHT < next_generation_y:
        new_plats, next_generation_y = generate_vertical_chunk(next_generation_y)
        platforms.extend(new_plats)

    # Clean up platforms that fall off the bottom of the screen to keep it running smooth
    platforms = [p for p in platforms if p.top < camera_y + SCREEN_HEIGHT + 200]

    # Update Score based on highest altitude reached
    current_altitude = int(-player.rect.y + 650) // 10
    if current_altitude > highest_score:
        highest_score = current_altitude

    # --- GAME OVER CONDITION ---
    # If you fall off the bottom of the moving camera view, you die
    if player.rect.y > camera_y + SCREEN_HEIGHT:
        # Reset Game
        player = Player(SCREEN_WIDTH // 2, 650)
        camera_y = 0
        platforms = [
            pygame.Rect(0, 750, SCREEN_WIDTH, 50),
            pygame.Rect(0, 0, 30, SCREEN_HEIGHT),
            pygame.Rect(SCREEN_WIDTH - 30, 0, 30, SCREEN_HEIGHT),
        ]
        next_generation_y = 0
        highest_score = 0

    # 3. Drawing Everything
    screen.fill(DARK_GREY) # Dark theme looks cleaner for tower climbing
    
    # Draw Platforms with Y-camera offset
    for platform in platforms:
        draw_plat = platform.copy()
        draw_plat.y -= camera_y
        pygame.draw.rect(screen, WHITE, draw_plat)
        
    # Draw Player
    player.draw(screen, camera_y)

    # Draw Rising Danger Line at the bottom of the screen just to emphasize the stakes
    pygame.draw.rect(screen, LAVA_RED, (0, SCREEN_HEIGHT - 10, SCREEN_WIDTH, 10))

    # Draw Score UI
    score_text = font.render(f"Altitude: {highest_score}m", True, NEON_GREEN)
    screen.blit(score_text, (20, 20))

    # Refresh Screen
    pygame.display.flip()
    clock.tick(FPS)
