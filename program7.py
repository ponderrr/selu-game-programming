import pygame
import random
import math

pygame.init()

WINDOW_WIDTH = 2100
WINDOW_HEIGHT = 1350

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

SHIP_SPEED = 0.3
SHIP_ROTATION_SPEED = 3
SHIP_SIZE = 20
BULLET_SPEED = 10
BULLET_RADIUS = 3

ASTEROID_MIN_COUNT = 15
ASTEROID_MAX_COUNT = 25
ASTEROID_MIN_SIZE = 30
ASTEROID_MED_SIZE = 50
ASTEROID_LARGE_SIZE = 70
ASTEROID_MIN_SPEED = 1
ASTEROID_MAX_SPEED = 3

ship_x = WINDOW_WIDTH // 2
ship_y = WINDOW_HEIGHT // 2
ship_heading = 0
ship_velocity_x = 0
ship_velocity_y = 0

asteroids = []
bullets = []
score = 0
game_over = False
running = True

asteroid_image = None

def load_asteroid_image():
    global asteroid_image
    try:
        asteroid_image = pygame.image.load("public/bk-headshot.jpg")
    except:
        asteroid_image = None

def create_asteroid(size_level):
    size_map = {
        0: ASTEROID_MIN_SIZE,
        1: ASTEROID_MED_SIZE,
        2: ASTEROID_LARGE_SIZE
    }
    size = size_map.get(size_level, ASTEROID_MED_SIZE)
    
    x = random.randint(0, WINDOW_WIDTH)
    y = random.randint(0, WINDOW_HEIGHT)
    
    angle = random.uniform(0, 2 * math.pi)
    speed = random.uniform(ASTEROID_MIN_SPEED, ASTEROID_MAX_SPEED)
    velocity_x = math.cos(angle) * speed
    velocity_y = math.sin(angle) * speed
    
    return {
        'x': x,
        'y': y,
        'velocity_x': velocity_x,
        'velocity_y': velocity_y,
        'size': size,
        'size_level': size_level
    }

def initialize_asteroids():
    global asteroids
    asteroids = []
    count = random.randint(ASTEROID_MIN_COUNT, ASTEROID_MAX_COUNT)
    for _ in range(count):
        size_level = random.randint(0, 2)
        asteroids.append(create_asteroid(size_level))

def draw_ship(screen):
    if game_over:
        return
    
    angle_rad = math.radians(ship_heading)
    
    tip_x = ship_x + math.cos(angle_rad) * SHIP_SIZE
    tip_y = ship_y + math.sin(angle_rad) * SHIP_SIZE
    
    left_x = ship_x + math.cos(angle_rad + 2.5) * SHIP_SIZE * 0.7
    left_y = ship_y + math.sin(angle_rad + 2.5) * SHIP_SIZE * 0.7
    
    right_x = ship_x + math.cos(angle_rad - 2.5) * SHIP_SIZE * 0.7
    right_y = ship_y + math.sin(angle_rad - 2.5) * SHIP_SIZE * 0.7
    
    pygame.draw.polygon(screen, WHITE, [(tip_x, tip_y), (left_x, left_y), (right_x, right_y)])

def draw_asteroid(screen, asteroid):
    if asteroid_image:
        scaled_size = asteroid['size'] * 2
        scaled_image = pygame.transform.scale(asteroid_image, (scaled_size, scaled_size))
        
        circle_surface = pygame.Surface((scaled_size, scaled_size), pygame.SRCALPHA)
        pygame.draw.circle(circle_surface, (255, 255, 255, 255), (scaled_size // 2, scaled_size // 2), asteroid['size'])
        
        final_surface = pygame.Surface((scaled_size, scaled_size), pygame.SRCALPHA)
        final_surface.blit(scaled_image, (0, 0))
        final_surface.blit(circle_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        rect = final_surface.get_rect(center=(asteroid['x'], asteroid['y']))
        screen.blit(final_surface, rect)
    else:
        pygame.draw.circle(screen, WHITE, (int(asteroid['x']), int(asteroid['y'])), asteroid['size'])

def draw_bullet(screen, bullet):
    pygame.draw.circle(screen, RED, (int(bullet['x']), int(bullet['y'])), BULLET_RADIUS)

def draw_ui(screen):
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    
    if game_over:
        game_over_text = font.render("Game Over - Press R to Restart", True, WHITE)
        text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
        screen.blit(game_over_text, text_rect)

def update_ship():
    global ship_x, ship_y, ship_velocity_x, ship_velocity_y, ship_heading
    
    if game_over:
        return
    
    keys = pygame.key.get_pressed()
    
    if keys[pygame.K_a]:
        ship_heading -= SHIP_ROTATION_SPEED
        if ship_heading < 0:
            ship_heading += 360
    
    if keys[pygame.K_d]:
        ship_heading += SHIP_ROTATION_SPEED
        if ship_heading >= 360:
            ship_heading -= 360
    
    if keys[pygame.K_w]:
        angle_rad = math.radians(ship_heading)
        ship_velocity_x += math.cos(angle_rad) * SHIP_SPEED
        ship_velocity_y += math.sin(angle_rad) * SHIP_SPEED
    
    if keys[pygame.K_s]:
        angle_rad = math.radians(ship_heading)
        ship_velocity_x -= math.cos(angle_rad) * SHIP_SPEED
        ship_velocity_y -= math.sin(angle_rad) * SHIP_SPEED
    
    if not keys[pygame.K_w] and not keys[pygame.K_s]:
        ship_velocity_x *= 0.95
        ship_velocity_y *= 0.95
        if abs(ship_velocity_x) < 0.01:
            ship_velocity_x = 0
        if abs(ship_velocity_y) < 0.01:
            ship_velocity_y = 0
    
    ship_x += ship_velocity_x
    ship_y += ship_velocity_y
    
    if ship_x < 0:
        ship_x = WINDOW_WIDTH
    elif ship_x > WINDOW_WIDTH:
        ship_x = 0
    
    if ship_y < 0:
        ship_y = WINDOW_HEIGHT
    elif ship_y > WINDOW_HEIGHT:
        ship_y = 0

def shoot_bullet():
    if game_over:
        return
    
    angle_rad = math.radians(ship_heading)
    tip_x = ship_x + math.cos(angle_rad) * SHIP_SIZE
    tip_y = ship_y + math.sin(angle_rad) * SHIP_SIZE
    
    bullets.append({
        'x': tip_x,
        'y': tip_y,
        'velocity_x': math.cos(angle_rad) * BULLET_SPEED,
        'velocity_y': math.sin(angle_rad) * BULLET_SPEED
    })

def update_bullets():
    global bullets
    
    for bullet in bullets[:]:
        bullet['x'] += bullet['velocity_x']
        bullet['y'] += bullet['velocity_y']
        
        if bullet['x'] < 0 or bullet['x'] > WINDOW_WIDTH or bullet['y'] < 0 or bullet['y'] > WINDOW_HEIGHT:
            bullets.remove(bullet)

def update_asteroids():
    global asteroids
    
    for asteroid in asteroids:
        asteroid['x'] += asteroid['velocity_x']
        asteroid['y'] += asteroid['velocity_y']
        
        if asteroid['x'] < 0:
            asteroid['x'] = 0
            asteroid['velocity_x'] *= -1
        elif asteroid['x'] > WINDOW_WIDTH:
            asteroid['x'] = WINDOW_WIDTH
            asteroid['velocity_x'] *= -1
        
        if asteroid['y'] < 0:
            asteroid['y'] = 0
            asteroid['velocity_y'] *= -1
        elif asteroid['y'] > WINDOW_HEIGHT:
            asteroid['y'] = WINDOW_HEIGHT
            asteroid['velocity_y'] *= -1

def check_asteroid_collisions():
    global asteroids
    
    for i in range(len(asteroids)):
        for j in range(i + 1, len(asteroids)):
            a1 = asteroids[i]
            a2 = asteroids[j]
            
            dx = a1['x'] - a2['x']
            dy = a1['y'] - a2['y']
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance < (a1['size'] + a2['size']):
                v1x = a1['velocity_x']
                v1y = a1['velocity_y']
                v2x = a2['velocity_x']
                v2y = a2['velocity_y']
                
                a1['velocity_x'] = v2x
                a1['velocity_y'] = v2y
                a2['velocity_x'] = v1x
                a2['velocity_y'] = v1y
                
                overlap = (a1['size'] + a2['size']) - distance
                if distance > 0:
                    a1['x'] += (dx / distance) * overlap * 0.5
                    a1['y'] += (dy / distance) * overlap * 0.5
                    a2['x'] -= (dx / distance) * overlap * 0.5
                    a2['y'] -= (dy / distance) * overlap * 0.5

def check_bullet_asteroid_collisions():
    global bullets, asteroids, score
    
    for bullet in bullets[:]:
        for asteroid in asteroids[:]:
            dx = bullet['x'] - asteroid['x']
            dy = bullet['y'] - asteroid['y']
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance < asteroid['size']:
                bullets.remove(bullet)
                asteroids.remove(asteroid)
                score += 1
                break

def check_ship_asteroid_collisions():
    global game_over
    
    if game_over:
        return
    
    for asteroid in asteroids:
        dx = ship_x - asteroid['x']
        dy = ship_y - asteroid['y']
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance < (SHIP_SIZE + asteroid['size']):
            game_over = True
            break

def reset_game():
    global ship_x, ship_y, ship_heading, ship_velocity_x, ship_velocity_y
    global asteroids, bullets, score, game_over
    
    ship_x = WINDOW_WIDTH // 2
    ship_y = WINDOW_HEIGHT // 2
    ship_heading = 0
    ship_velocity_x = 0
    ship_velocity_y = 0
    
    asteroids = []
    bullets = []
    score = 0
    game_over = False
    
    initialize_asteroids()

def main():
    global running, game_over
    
    load_asteroid_image()
    initialize_asteroids()
    
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Asteroids")
    clock = pygame.time.Clock()
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_over:
                    shoot_bullet()
                elif event.key == pygame.K_r and game_over:
                    reset_game()
        
        if not game_over:
            update_ship()
            update_bullets()
            update_asteroids()
            check_asteroid_collisions()
            check_bullet_asteroid_collisions()
            check_ship_asteroid_collisions()
        
        screen.fill(BLACK)
        
        for asteroid in asteroids:
            draw_asteroid(screen, asteroid)
        
        for bullet in bullets:
            draw_bullet(screen, bullet)
        
        draw_ship(screen)
        draw_ui(screen)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

main()

