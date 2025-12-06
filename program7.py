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
boss_defeated = False
death_cause = None
running = True

stats = {
    'asteroids_destroyed': 0,
    'crimson_tide_destroyed': 0,
    'time_survived': 0,
    'boss_damage_dealt': 0,
    'game_start_time': 0
}

asteroid_image = None
boss_image = None

# Boss spawn system
BOSS_SPAWN_SCORE = 10  # Lowered for easier testing (was 50)
BOSS_WARNING_DURATION = 3000

BOSS_DRIFT_SPEED_MIN = 0.5
BOSS_DRIFT_SPEED_MAX = 1.5
BOSS_DRIFT_CHANGE_TIME = 2000
BOSS_DASH_SPEED_MIN = 5
BOSS_DASH_SPEED_MAX = 7
BOSS_DASH_COOLDOWN = 3000
BOSS_ROTATION_SPEED = 0.5

CRIMSON_TIDE_SIZE = 20
CRIMSON_TIDE_SPAWN_COOLDOWN = 2500
CRIMSON_TIDE_SPEED = 1.5
CRIMSON_TIDE_MAX_SPEED = 3.0
CRIMSON_TIDE_HOMING_ACCELERATION = 0.1

boss_active = False
boss_warning = False
boss_warning_start = 0
boss = None

def load_asteroid_image():
    global asteroid_image
    try:
        asteroid_image = pygame.image.load("public/bk-headshot.jpg")
    except:
        asteroid_image = None

def load_boss_image():
    global boss_image
    try:
        boss_image = pygame.image.load("public/nick-saban.png")
    except:
        boss_image = None

def create_asteroid(size_level, is_crimson_tide=False):
    if is_crimson_tide:
        size = CRIMSON_TIDE_SIZE
    else:
        size_map = {
            0: ASTEROID_MIN_SIZE,
            1: ASTEROID_MED_SIZE,
            2: ASTEROID_LARGE_SIZE
        }
        size = size_map.get(size_level, ASTEROID_MED_SIZE)
    
    x = random.randint(0, WINDOW_WIDTH)
    y = random.randint(0, WINDOW_HEIGHT)
    
    angle = random.uniform(0, 2 * math.pi)
    
    if is_crimson_tide:
        speed = CRIMSON_TIDE_SPEED
    else:
        speed = random.uniform(ASTEROID_MIN_SPEED, ASTEROID_MAX_SPEED)
    
    velocity_x = math.cos(angle) * speed
    velocity_y = math.sin(angle) * speed
    
    return {
        'x': x,
        'y': y,
        'velocity_x': velocity_x,
        'velocity_y': velocity_y,
        'size': size,
        'size_level': size_level,
        'is_crimson_tide': is_crimson_tide,
        'max_speed': CRIMSON_TIDE_MAX_SPEED if is_crimson_tide else ASTEROID_MAX_SPEED
    }

def create_boss():
    return {
        'x': WINDOW_WIDTH // 2,
        'y': 150,
        'velocity_x': 0,
        'velocity_y': 0,
        'health': 100,
        'max_health': 100,
        'size': 120,
        'heading': 0,
        'spawn_cooldown': pygame.time.get_ticks(),
        'last_drift_change': pygame.time.get_ticks(),
        'last_dash': pygame.time.get_ticks()
    }

def boss_drift():
    global boss
    
    if boss is None:
        return
    
    angle = random.uniform(0, 2 * math.pi)
    speed = random.uniform(BOSS_DRIFT_SPEED_MIN, BOSS_DRIFT_SPEED_MAX)
    
    boss['velocity_x'] = math.cos(angle) * speed
    boss['velocity_y'] = math.sin(angle) * speed
    boss['last_drift_change'] = pygame.time.get_ticks()

def boss_dash_at_player():
    global boss
    
    if boss is None or game_over:
        return
    
    dx = ship_x - boss['x']
    dy = ship_y - boss['y']
    distance = math.sqrt(dx * dx + dy * dy)
    
    if distance > 0:
        direction_x = dx / distance
        direction_y = dy / distance
        
        dash_speed = random.uniform(BOSS_DASH_SPEED_MIN, BOSS_DASH_SPEED_MAX)
        
        boss['velocity_x'] = direction_x * dash_speed
        boss['velocity_y'] = direction_y * dash_speed
        boss['last_dash'] = pygame.time.get_ticks()

def update_boss():
    global boss
    
    if not boss_active or boss is None or game_over:
        return
    
    current_time = pygame.time.get_ticks()
    phase = get_boss_phase()
    
    drift_cooldown = BOSS_DRIFT_CHANGE_TIME // phase
    dash_cooldown = BOSS_DASH_COOLDOWN // phase
    
    drift_elapsed = current_time - boss['last_drift_change']
    if drift_elapsed >= drift_cooldown:
        boss_drift()
    
    dash_elapsed = current_time - boss['last_dash']
    if dash_elapsed >= dash_cooldown:
        boss_dash_at_player()
    
    boss['x'] += boss['velocity_x'] * phase
    boss['y'] += boss['velocity_y'] * phase
    
    if boss['x'] < boss['size']:
        boss['x'] = boss['size']
        boss['velocity_x'] *= -1
    elif boss['x'] > WINDOW_WIDTH - boss['size']:
        boss['x'] = WINDOW_WIDTH - boss['size']
        boss['velocity_x'] *= -1
    
    if boss['y'] < boss['size']:
        boss['y'] = boss['size']
        boss['velocity_y'] *= -1
    elif boss['y'] > WINDOW_HEIGHT - boss['size']:
        boss['y'] = WINDOW_HEIGHT - boss['size']
        boss['velocity_y'] *= -1
    
    boss['heading'] += BOSS_ROTATION_SPEED * phase
    if boss['heading'] >= 360:
        boss['heading'] = 0

def spawn_crimson_tide():
    global asteroids, boss
    
    if not boss_active or boss is None:
        return
    
    current_time = pygame.time.get_ticks()
    phase = get_boss_phase()
    spawn_cooldown = CRIMSON_TIDE_SPAWN_COOLDOWN // phase
    
    spawn_elapsed = current_time - boss['spawn_cooldown']
    
    if spawn_elapsed >= spawn_cooldown:
        offset_x = random.uniform(-50, 50)
        offset_y = random.uniform(-50, 50)
        
        new_asteroid = create_asteroid(0, is_crimson_tide=True)
        new_asteroid['x'] = boss['x'] + offset_x
        new_asteroid['y'] = boss['y'] + offset_y
        
        asteroids.append(new_asteroid)
        boss['spawn_cooldown'] = current_time

def update_crimson_tide_homing():
    if game_over:
        return
    
    for asteroid in asteroids:
        if asteroid.get('is_crimson_tide', False):
            dx = ship_x - asteroid['x']
            dy = ship_y - asteroid['y']
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance > 0:
                direction_x = dx / distance
                direction_y = dy / distance
                
                asteroid['velocity_x'] += direction_x * CRIMSON_TIDE_HOMING_ACCELERATION
                asteroid['velocity_y'] += direction_y * CRIMSON_TIDE_HOMING_ACCELERATION
                
                speed = math.sqrt(asteroid['velocity_x']**2 + asteroid['velocity_y']**2)
                if speed > asteroid['max_speed']:
                    asteroid['velocity_x'] = (asteroid['velocity_x'] / speed) * asteroid['max_speed']
                    asteroid['velocity_y'] = (asteroid['velocity_y'] / speed) * asteroid['max_speed']

def get_boss_phase():
    if boss is None:
        return 1
    
    health_percent = (boss['health'] / boss['max_health']) * 100
    
    if health_percent > 70:
        return 1
    elif health_percent > 30:
        return 2
    else:
        return 3

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
    is_crimson = asteroid.get('is_crimson_tide', False)
    
    if asteroid_image and not is_crimson:
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
        color = RED if is_crimson else WHITE
        pygame.draw.circle(screen, color, (int(asteroid['x']), int(asteroid['y'])), asteroid['size'])

def draw_boss(screen):
    if not boss_active or boss is None:
        return
    
    if boss_image:
        scaled_size = boss['size'] * 2
        scaled_image = pygame.transform.scale(boss_image, (scaled_size, scaled_size))
        
        circle_surface = pygame.Surface((scaled_size, scaled_size), pygame.SRCALPHA)
        pygame.draw.circle(circle_surface, (255, 255, 255, 255), (scaled_size // 2, scaled_size // 2), boss['size'])
        
        final_surface = pygame.Surface((scaled_size, scaled_size), pygame.SRCALPHA)
        final_surface.blit(scaled_image, (0, 0))
        final_surface.blit(circle_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        rotated_surface = pygame.transform.rotate(final_surface, -boss['heading'])
        rect = rotated_surface.get_rect(center=(boss['x'], boss['y']))
        screen.blit(rotated_surface, rect)
    else:
        pygame.draw.circle(screen, WHITE, (int(boss['x']), int(boss['y'])), boss['size'])
        
        font = pygame.font.Font(None, 36)
        text = font.render("SABAN", True, RED)
        text_rect = text.get_rect(center=(boss['x'], boss['y']))
        screen.blit(text, text_rect)

def draw_boss_health_bar(screen):
    if not boss_active or boss is None:
        return
    
    bar_width = 200
    bar_height = 20
    bar_x = boss['x'] - bar_width // 2
    bar_y = boss['y'] - boss['size'] - 30
    
    health_percent = boss['health'] / boss['max_health']
    fill_width = int(bar_width * health_percent)
    
    if health_percent > 0.7:
        fill_color = (0, 255, 0)
    elif health_percent > 0.3:
        fill_color = (255, 255, 0)
    else:
        fill_color = (255, 0, 0)
    
    pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
    pygame.draw.rect(screen, fill_color, (bar_x, bar_y, fill_width, bar_height))
    pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)

def draw_bullet(screen, bullet):
    pygame.draw.circle(screen, RED, (int(bullet['x']), int(bullet['y'])), BULLET_RADIUS)

def draw_ui(screen):
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

def draw_end_screen(screen):
    if not game_over:
        return
    
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    overlay.set_alpha(220)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))
    
    y_offset = WINDOW_HEIGHT // 2 - 150
    
    if boss_defeated:
        title_font = pygame.font.Font(None, 72)
        title = title_font.render("ROLL TIDE DEFEATED!", True, (0, 255, 0))
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, y_offset))
        screen.blit(title, title_rect)
        
        subtitle_text = "Nick Saban has been vanquished!"
        color = (0, 255, 0)
    else:
        title_font = pygame.font.Font(None, 72)
        if death_cause == "boss":
            title = title_font.render("THE TIDE WAS TOO STRONG", True, RED)
            subtitle_text = "You were consumed by Nick Saban!"
        elif death_cause == "crimson_tide":
            title = title_font.render("GAME OVER", True, RED)
            subtitle_text = "Destroyed by a Crimson Tide asteroid!"
        else:
            title = title_font.render("GAME OVER", True, RED)
            subtitle_text = "Destroyed by an asteroid!"
        
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, y_offset))
        screen.blit(title, title_rect)
        color = RED
    
    font = pygame.font.Font(None, 48)
    
    score_text = font.render(f"Final Score: {score}", True, WHITE)
    score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, y_offset + 80))
    screen.blit(score_text, score_rect)
    
    subtitle_font = pygame.font.Font(None, 36)
    subtitle = subtitle_font.render(subtitle_text, True, color)
    subtitle_rect = subtitle.get_rect(center=(WINDOW_WIDTH // 2, y_offset + 140))
    screen.blit(subtitle, subtitle_rect)
    
    if stats['time_survived'] > 0:
        time_seconds = stats['time_survived'] // 1000
        stats_text = subtitle_font.render(f"Time Survived: {time_seconds}s", True, WHITE)
        stats_rect = stats_text.get_rect(center=(WINDOW_WIDTH // 2, y_offset + 190))
        screen.blit(stats_text, stats_rect)
    
    restart_text = font.render("Press R to Restart", True, WHITE)
    restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, y_offset + 250))
    screen.blit(restart_text, restart_rect)

def draw_warning_screen(screen):
    if not boss_warning:
        return
    
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    overlay.set_alpha(180)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))
    
    font = pygame.font.Font(None, 72)
    text = font.render("The Tide is Rising...", True, WHITE)
    text_rect = text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
    screen.blit(text, text_rect)

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
                
                if asteroid.get('is_crimson_tide', False):
                    stats['crimson_tide_destroyed'] += 1
                else:
                    stats['asteroids_destroyed'] += 1
                
                break

def check_ship_asteroid_collisions():
    global game_over, death_cause
    
    if game_over:
        return
    
    for asteroid in asteroids:
        dx = ship_x - asteroid['x']
        dy = ship_y - asteroid['y']
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance < (SHIP_SIZE + asteroid['size']):
            game_over = True
            if asteroid.get('is_crimson_tide', False):
                death_cause = "crimson_tide"
            else:
                death_cause = "asteroid"
            break

def check_bullet_boss_collisions():
    global bullets, boss, boss_defeated, game_over
    
    if not boss_active or boss is None or game_over:
        return
    
    for bullet in bullets[:]:
        dx = bullet['x'] - boss['x']
        dy = bullet['y'] - boss['y']
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance < (BULLET_RADIUS + boss['size']):
            bullets.remove(bullet)
            boss['health'] -= 1
            stats['boss_damage_dealt'] += 1
            
            if boss['health'] <= 0:
                boss_defeated = True
                game_over = True
            
            break

def check_ship_boss_collisions():
    global game_over, death_cause
    
    if not boss_active or boss is None or game_over:
        return
    
    dx = ship_x - boss['x']
    dy = ship_y - boss['y']
    distance = math.sqrt(dx * dx + dy * dy)
    
    if distance < (SHIP_SIZE + boss['size']):
        game_over = True
        death_cause = "boss"

def check_boss_spawn():
    global boss_warning, boss_warning_start, boss_active
    
    if game_over or boss_active or boss_warning:
        return
    
    if score >= BOSS_SPAWN_SCORE:
        boss_warning = True
        boss_warning_start = pygame.time.get_ticks()

def update_boss_state():
    global boss_warning, boss_active, boss
    
    if not boss_warning:
        return
    
    current_time = pygame.time.get_ticks()
    elapsed = current_time - boss_warning_start
    
    if elapsed >= BOSS_WARNING_DURATION:
        boss_warning = False
        boss_active = True
        boss = create_boss()
        boss_drift()

def reset_game():
    global ship_x, ship_y, ship_heading, ship_velocity_x, ship_velocity_y
    global asteroids, bullets, score, game_over
    global boss_active, boss_warning, boss_warning_start, boss, boss_defeated
    global death_cause
    
    ship_x = WINDOW_WIDTH // 2
    ship_y = WINDOW_HEIGHT // 2
    ship_heading = 0
    ship_velocity_x = 0
    ship_velocity_y = 0
    
    asteroids = []
    bullets = []
    score = 0
    game_over = False
    boss_active = False
    boss_warning = False
    boss_warning_start = 0
    boss = None
    boss_defeated = False
    death_cause = None
    
    stats['asteroids_destroyed'] = 0
    stats['crimson_tide_destroyed'] = 0
    stats['time_survived'] = 0
    stats['boss_damage_dealt'] = 0
    stats['game_start_time'] = pygame.time.get_ticks()
    
    initialize_asteroids()

def main():
    global running, game_over, boss_warning, boss_warning_start
    
    load_asteroid_image()
    load_boss_image()
    initialize_asteroids()
    
    stats['game_start_time'] = pygame.time.get_ticks()
    
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
                elif event.key == pygame.K_b and not game_over and not boss_active and not boss_warning:
                    # Cheat key: Press B to spawn boss immediately
                    boss_warning = True
                    boss_warning_start = pygame.time.get_ticks()
        
        if game_over and stats['time_survived'] == 0:
            stats['time_survived'] = pygame.time.get_ticks() - stats['game_start_time']
        
        if not game_over:
            update_ship()
            update_bullets()
            spawn_crimson_tide()
            update_crimson_tide_homing()
            update_asteroids()
            check_asteroid_collisions()
            check_bullet_asteroid_collisions()
            check_ship_asteroid_collisions()
            check_bullet_boss_collisions()
            check_ship_boss_collisions()
            check_boss_spawn()
            update_boss_state()
            update_boss()
        
        screen.fill(BLACK)
        
        for asteroid in asteroids:
            draw_asteroid(screen, asteroid)
        
        draw_boss(screen)
        draw_boss_health_bar(screen)
        
        for bullet in bullets:
            draw_bullet(screen, bullet)
        
        draw_ship(screen)
        draw_ui(screen)
        draw_warning_screen(screen)
        draw_end_screen(screen)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

main()

