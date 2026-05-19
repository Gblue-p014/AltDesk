import pygame
import sys

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

# Setup Screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("2D Parkour Prototype")
clock = pygame.time.Clock()

# --- PLAYER CLASS ---
class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 60)
        self.vx = 0
        self.vy = 0
        self.speed = 6
        self.gravity = 0.8
        self.jump_strength = -14
        
        # Status flags
        self.on_ground = False
        self.on_wall = False
        self.wall_direction = 0  # -1 for left wall, 1 for right wall

    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        # Horizontal Movement
        self.vx = 0
        if keys[pygame.K_LEFT]:
            self.vx = -self.speed
        if keys[pygame.K_RIGHT]:
            self.vx = self.speed

        # Jumping / Wall Jumping
        if keys[pygame.K_SPACE]:
            if self.on_ground:
                self.vy = self.jump_strength
                self.on_ground = False
            elif self.on_wall:
                # Wall Jump: Push away from the wall and upward
                self.vy = self.jump_strength
                self.vx = -self.wall_direction * self.speed * 2
                self.on_wall = False

    def apply_physics(self):
        # Apply Gravity
        if self.on_wall and self.vy > 0:
            # Slide down walls slowly (Parkour mechanic!)
            self.vy += self.gravity * 0.3
        else:
            self.vy += self.gravity

        # Limit falling speed
        if self.vy > 15:
            self.vy = 15

    def update(self, platforms):
        self.handle_input()
        self.apply_physics()

        # Move horizontally and check collisions
        self.rect.x += self.vx
        self.check_collisions(platforms, 'horizontal')

        # Move vertically and check collisions
        self.rect.y += self.vy
        self.check_collisions(platforms, 'vertical')
        
        # Check if we are gripping a wall
        self.check_wall_grip(platforms)

    def check_collisions(self, platforms, direction):
        if direction == 'horizontal':
            for platform in platforms:
                if self.rect.colliderect(platform):
                    if self.vx > 0: # Moving right
                        self.rect.right = platform.left
                    if self.vx < 0: # Moving left
                        self.rect.left = platform.right
                        
        if direction == 'vertical':
            self.on_ground = False
            for platform in platforms:
                if self.rect.colliderect(platform):
                    if self.vy > 0: # Falling down
                        self.rect.bottom = platform.top
                        self.vy = 0
                        self.on_ground = True
                    if self.vy < 0: # Jumping up
                        self.rect.top = platform.bottom
                        self.vy = 0

    def check_wall_grip(self, platforms):
        """Checks if the player is airborne and hugging a side wall."""
        self.on_wall = False
        self.wall_direction = 0
        
        if not self.on_ground:
            # Create slightly expanded hitboxes to detect adjacent walls
            left_check = pygame.Rect(self.rect.x - 2, self.rect.y, 2, self.rect.height)
            right_check = pygame.Rect(self.rect.right, self.rect.y, 2, self.rect.height)
            
            for platform in platforms:
                if left_check.colliderect(platform):
                    self.on_wall = True
                    self.wall_direction = -1
                elif right_check.colliderect(platform):
                    self.on_wall = True
                    self.wall_direction = 1

    def draw(self, surface):
        # Color changes if you are wall-sliding
        color = RED if self.on_wall else BLUE
        pygame.draw.rect(surface, color, self.rect)

# --- GAME SETUP ---
player = Player(100, 450)

# Level Design: A list of pygame.Rect objects acting as solid ground/walls
platforms = [
    pygame.Rect(0, 560, 800, 40),      # Floor
    pygame.Rect(300, 450, 150, 20),    # Low Platform
    pygame.Rect(500, 350, 40, 150),    # Tall Wall 1
    pygame.Rect(650, 200, 40, 200),    # Tall Wall 2
    pygame.Rect(150, 250, 200, 20),    # High Left Platform
]

# --- MAIN GAME LOOP ---
while True:
    # 1. Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # 2. Update Game State
    player.update(platforms)

    # 3. Drawing Everything
    screen.fill(WHITE) # Clear screen
    
    # Draw Platforms
    for platform in platforms:
        pygame.draw.rect(screen, DARK_GREY, platform)
        
    # Draw Player
    player.draw(screen)

    # Refresh Screen
    pygame.display.flip()
    clock.tick(FPS)
