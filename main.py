import pygame
import random
import os
import sys

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sprite Collision Game")

# Colors
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 150, 255)
YELLOW = (255, 255, 0)
PURPLE = (200, 50, 200)
CYAN = (0, 200, 200)
ORANGE = (255, 150, 50)
BLACK = (20, 20, 20)

# Generate background with stars
def create_starfield_background():
    background = pygame.Surface((WIDTH, HEIGHT))
    background.fill(BLACK)
    
    # Draw stars
    for _ in range(200):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        radius = random.randint(1, 3)
        color = random.choice([WHITE, CYAN, YELLOW])
        pygame.draw.circle(background, color, (x, y), radius)
    
    # Draw some nebulae
    for _ in range(5):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        radius = random.randint(50, 150)
        color = random.choice([(50, 0, 100), (0, 50, 100), (100, 0, 50)])
        pygame.draw.circle(background, color, (x, y), radius, width=30)
    
    return background

# Create a simple sound effect
def create_collision_sound():
    sound = pygame.mixer.Sound
    try:
        # Try to create a sound with pygame
        collision_sound = pygame.mixer.Sound(buffer=bytearray([128] * 44100))
        # Generate a simple beep sound
        samples = bytearray(44100)
        for i in range(44100):
            samples[i] = int(128 + 127 * pygame.math.sin(i * 0.1))
        collision_sound = pygame.mixer.Sound(buffer=samples)
        return collision_sound
    except:
        # Return a dummy sound if creation fails
        class DummySound:
            def play(self):
                pass
        return DummySound()

# Player sprite
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, BLUE, [(20, 0), (40, 40), (20, 30), (0, 40)])
        pygame.draw.circle(self.image, CYAN, (20, 15), 8)
        self.rect = self.image.get_rect(center=(WIDTH//2, HEIGHT//2))
        self.speed = 5
        
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += self.speed
            
        # Keep player on screen
        self.rect.clamp_ip(screen.get_rect())

# Enemy sprite
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.size = random.randint(20, 40)
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        
        # Random enemy appearance
        enemy_type = random.randint(1, 4)
        color = random.choice([RED, GREEN, YELLOW, PURPLE, ORANGE])
        
        if enemy_type == 1:
            pygame.draw.circle(self.image, color, (self.size//2, self.size//2), self.size//2)
        elif enemy_type == 2:
            pygame.draw.rect(self.image, color, (0, 0, self.size, self.size))
        elif enemy_type == 3:
            pygame.draw.polygon(self.image, color, [(self.size//2, 0), (self.size, self.size), (0, self.size)])
        else:
            pygame.draw.polygon(self.image, color, [(0, 0), (self.size, self.size//2), (0, self.size)])
        
        # Random position off-screen
        side = random.choice(['top', 'right', 'bottom', 'left'])
        if side == 'top':
            self.rect = self.image.get_rect(center=(random.randint(0, WIDTH), -self.size))
        elif side == 'right':
            self.rect = self.image.get_rect(center=(WIDTH + self.size, random.randint(0, HEIGHT)))
        elif side == 'bottom':
            self.rect = self.image.get_rect(center=(random.randint(0, WIDTH), HEIGHT + self.size))
        else:
            self.rect = self.image.get_rect(center=(-self.size, random.randint(0, HEIGHT)))
            
        # Movement
        self.speed = random.randint(1, 3)
        self.direction = pygame.math.Vector2(
            random.uniform(-1, 1),
            random.uniform(-1, 1)
        ).normalize()
        
    def update(self):
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed
        
        # If enemy goes off screen, remove it
        if (self.rect.right < 0 or self.rect.left > WIDTH or 
            self.rect.bottom < 0 or self.rect.top > HEIGHT):
            self.kill()

# Create background
background = create_starfield_background()

# Create sprites
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

# Create initial enemies
for _ in range(7):
    enemy = Enemy()
    all_sprites.add(enemy)
    enemies.add(enemy)

# Create collision sound
collision_sound = create_collision_sound()

# Game variables
score = 0
font = pygame.font.SysFont(None, 36)
clock = pygame.time.Clock()
enemy_spawn_timer = 0

# Main game loop
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
    
    # Spawn new enemies periodically
    enemy_spawn_timer += 1
    if enemy_spawn_timer >= 60 and len(enemies) < 15:  # Spawn every 60 frames, max 15 enemies
        enemy = Enemy()
        all_sprites.add(enemy)
        enemies.add(enemy)
        enemy_spawn_timer = 0
    
    # Update
    all_sprites.update()
    
    # Check for collisions
    hits = pygame.sprite.spritecollide(player, enemies, True)
    for hit in hits:
        score += 1
        collision_sound.play()
    
    # Draw
    screen.blit(background, (0, 0))
    all_sprites.draw(screen)
    
    # Draw score
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    
    # Draw instructions
    instructions = font.render("Use arrow keys or WASD to move", True, WHITE)
    screen.blit(instructions, (WIDTH//2 - instructions.get_width()//2, HEIGHT - 40))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()