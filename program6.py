import pygame
import random

pygame.init()

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700
BOARD_WIDTH = 800
BOARD_HEIGHT = 600
BOARD_X = 100
BOARD_Y = 50

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

PADDLE_WIDTH = 20
PADDLE_HEIGHT = 80
PADDLE_SPEED = 5
BALL_RADIUS = 10
BULLET_RADIUS = 3

ball_x = BOARD_X + BOARD_WIDTH // 2
ball_y = BOARD_Y + BOARD_HEIGHT // 2
ball_velocity_x = 3
ball_velocity_y = 2

paddle1_x = BOARD_X + 10
paddle1_y = BOARD_Y + BOARD_HEIGHT // 2 - PADDLE_HEIGHT // 2
paddle1_width = PADDLE_WIDTH
paddle1_height = PADDLE_HEIGHT
paddle1_bullets = 0
paddle1_last_bullet_time = 0
paddle1_last_hit_time = 0

paddle2_x = BOARD_X + BOARD_WIDTH - 30
paddle2_y = BOARD_Y + BOARD_HEIGHT // 2 - PADDLE_HEIGHT // 2
paddle2_width = PADDLE_WIDTH
paddle2_height = PADDLE_HEIGHT
paddle2_bullets = 0
paddle2_last_bullet_time = 0
paddle2_last_hit_time = 0

bullets = []
score = [0, 0]
game_mode = "menu"
running = True

def draw_board():
    pygame.draw.rect(screen, WHITE, (BOARD_X, BOARD_Y, BOARD_WIDTH, BOARD_HEIGHT), 2)

def draw_paddle(x, y, width, height, facing_right=True):
    pygame.draw.rect(screen, WHITE, (x, y, width, height))
    
    if facing_right:
        bulb_x = x + width
        bulb_y = y + height // 2
    else:
        bulb_x = x
        bulb_y = y + height // 2
    
    pygame.draw.circle(screen, YELLOW, (bulb_x, bulb_y), 8)

def draw_ball():
    pygame.draw.circle(screen, WHITE, (int(ball_x), int(ball_y)), BALL_RADIUS)

def draw_bullet(x, y):
    pygame.draw.circle(screen, YELLOW, (int(x), int(y)), BULLET_RADIUS)

def draw_ui():
    font = pygame.font.Font(None, 36)
    
    score_text = font.render(f"P1: {score[0]}  P2: {score[1]}", True, WHITE)
    screen.blit(score_text, (10, 10))
    
    bullets_text = font.render(f"Bullets - P1: {paddle1_bullets}  P2: {paddle2_bullets}", True, WHITE)
    screen.blit(bullets_text, (10, 50))

def draw_menu():
    screen.fill(BLACK)
    font = pygame.font.Font(None, 48)
    
    title = font.render("PONG SHOOTOUT", True, WHITE)
    screen.blit(title, (WINDOW_WIDTH//2 - 150, 150))
    
    mode_text = font.render("1: Human vs Human", True, WHITE)
    screen.blit(mode_text, (WINDOW_WIDTH//2 - 120, 250))
    
    mode_text2 = font.render("2: Human vs Computer", True, WHITE)
    screen.blit(mode_text2, (WINDOW_WIDTH//2 - 150, 300))
    
    controls_text = font.render("P1: W/S move, D shoot", True, WHITE)
    screen.blit(controls_text, (WINDOW_WIDTH//2 - 140, 400))
    
    controls_text2 = font.render("P2: Arrows move, SPACE shoot", True, WHITE)
    screen.blit(controls_text2, (WINDOW_WIDTH//2 - 180, 450))

def update_ball():
    global ball_x, ball_y, ball_velocity_x, ball_velocity_y, score
    
    ball_x += ball_velocity_x
    ball_y += ball_velocity_y
    
    if ball_y <= BOARD_Y or ball_y >= BOARD_Y + BOARD_HEIGHT:
        ball_velocity_y *= -1
    
    if ball_x <= BOARD_X:
        score[1] += 1
        reset_ball()
    elif ball_x >= BOARD_X + BOARD_WIDTH:
        score[0] += 1
        reset_ball()

def reset_ball():
    global ball_x, ball_y, ball_velocity_x, ball_velocity_y
    ball_x = BOARD_X + BOARD_WIDTH // 2
    ball_y = BOARD_Y + BOARD_HEIGHT // 2
    ball_velocity_x = random.choice([-3, 3])
    ball_velocity_y = random.choice([-2, 2])

def update_bullets():
    global bullets
    
    for bullet in bullets[:]:
        bullet['x'] += bullet['velocity_x']
        bullet['y'] += bullet['velocity_y']
        
        if bullet['x'] < BOARD_X or bullet['x'] > BOARD_X + BOARD_WIDTH:
            bullets.remove(bullet)

def update_bullet_accumulation():
    global paddle1_bullets, paddle2_bullets, paddle1_last_bullet_time, paddle2_last_bullet_time
    
    current_time = pygame.time.get_ticks()
    
    if current_time - paddle1_last_bullet_time >= 1000:
        paddle1_bullets += 1
        paddle1_last_bullet_time = current_time
    
    if current_time - paddle2_last_bullet_time >= 1000:
        paddle2_bullets += 1
        paddle2_last_bullet_time = current_time

def update_paddle_regeneration():
    global paddle1_width, paddle2_width, paddle1_height, paddle2_height, paddle1_last_hit_time, paddle2_last_hit_time
    
    current_time = pygame.time.get_ticks()
    
    if current_time - paddle1_last_hit_time >= 10000 and paddle1_width < PADDLE_WIDTH:
        paddle1_width += 0.5
        paddle1_height += 0.5
    
    if current_time - paddle2_last_hit_time >= 10000 and paddle2_width < PADDLE_WIDTH:
        paddle2_width += 0.5
        paddle2_height += 0.5

def shoot_bullet(paddle_x, paddle_y, direction):
    global bullets, paddle1_bullets, paddle2_bullets, paddle1_last_bullet_time, paddle2_last_bullet_time
    
    if direction == "right" and paddle1_bullets > 0:
        bullets.append({
            'x': paddle_x + PADDLE_WIDTH,
            'y': paddle_y + PADDLE_HEIGHT // 2,
            'velocity_x': 8,
            'velocity_y': 0,
            'owner': 1
        })
        paddle1_bullets -= 1
        paddle1_last_bullet_time = pygame.time.get_ticks()
    
    elif direction == "left" and paddle2_bullets > 0:
        bullets.append({
            'x': paddle_x,
            'y': paddle_y + PADDLE_HEIGHT // 2,
            'velocity_x': -8,
            'velocity_y': 0,
            'owner': 2
        })
        paddle2_bullets -= 1
        paddle2_last_bullet_time = pygame.time.get_ticks()

def check_ball_paddle_collisions():
    global ball_velocity_x, ball_velocity_y
    
    if (ball_x <= paddle1_x + paddle1_width and ball_x >= paddle1_x and
        ball_y >= paddle1_y and ball_y <= paddle1_y + paddle1_height):
        ball_velocity_x = abs(ball_velocity_x)
        ball_velocity_y += (ball_y - (paddle1_y + paddle1_height // 2)) * 0.1
    
    if (ball_x <= paddle2_x + paddle2_width and ball_x >= paddle2_x and
        ball_y >= paddle2_y and ball_y <= paddle2_y + paddle2_height):
        ball_velocity_x = -abs(ball_velocity_x)
        ball_velocity_y += (ball_y - (paddle2_y + paddle2_height // 2)) * 0.1

def check_ball_bullet_collisions():
    global ball_velocity_x, ball_velocity_y, bullets
    
    for bullet in bullets[:]:
        distance = ((ball_x - bullet['x'])**2 + (ball_y - bullet['y'])**2)**0.5
        if distance < BALL_RADIUS + BULLET_RADIUS:
            ball_velocity_x += bullet['velocity_x'] * 0.1
            ball_velocity_y += bullet['velocity_y'] * 0.1
            bullets.remove(bullet)

def check_paddle_bullet_collisions():
    global paddle1_width, paddle1_height, paddle2_width, paddle2_height, paddle1_last_hit_time, paddle2_last_hit_time, bullets
    
    for bullet in bullets[:]:
        if bullet['owner'] == 2:
            if (bullet['x'] >= paddle1_x and bullet['x'] <= paddle1_x + paddle1_width and
                bullet['y'] >= paddle1_y and bullet['y'] <= paddle1_y + paddle1_height):
                paddle1_width = max(5, paddle1_width - 5)
                paddle1_height = max(20, paddle1_height - 5)
                paddle1_last_hit_time = pygame.time.get_ticks()
                bullets.remove(bullet)
        
        elif bullet['owner'] == 1:
            if (bullet['x'] >= paddle2_x and bullet['x'] <= paddle2_x + paddle2_width and
                bullet['y'] >= paddle2_y and bullet['y'] <= paddle2_y + paddle2_height):
                paddle2_width = max(5, paddle2_width - 5)
                paddle2_height = max(20, paddle2_height - 5)
                paddle2_last_hit_time = pygame.time.get_ticks()
                bullets.remove(bullet)

def ai_move():
    global paddle2_y
    
    if ball_y < paddle2_y + paddle2_height // 2:
        paddle2_y -= PADDLE_SPEED
    elif ball_y > paddle2_y + paddle2_height // 2:
        paddle2_y += PADDLE_SPEED
    
    if paddle2_y < BOARD_Y:
        paddle2_y = BOARD_Y
    elif paddle2_y > BOARD_Y + BOARD_HEIGHT - paddle2_height:
        paddle2_y = BOARD_Y + BOARD_HEIGHT - paddle2_height
    
    if paddle2_bullets > 0 and random.randint(1, 60) == 1:
        shoot_bullet(paddle2_x, paddle2_y, "left")

def handle_input():
    global paddle1_y, paddle2_y, game_mode
    
    keys = pygame.key.get_pressed()
    
    if keys[pygame.K_w] and paddle1_y > BOARD_Y:
        paddle1_y -= PADDLE_SPEED
    if keys[pygame.K_s] and paddle1_y < BOARD_Y + BOARD_HEIGHT - paddle1_height:
        paddle1_y += PADDLE_SPEED
    
    if game_mode == "two_player":
        if keys[pygame.K_UP] and paddle2_y > BOARD_Y:
            paddle2_y -= PADDLE_SPEED
        if keys[pygame.K_DOWN] and paddle2_y < BOARD_Y + BOARD_HEIGHT - paddle2_height:
            paddle2_y += PADDLE_SPEED

def main():
    global running, game_mode, screen, clock
    
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Pong Shootout")
    clock = pygame.time.Clock()
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if game_mode == "menu":
                    if event.key == pygame.K_1:
                        game_mode = "two_player"
                    elif event.key == pygame.K_2:
                        game_mode = "vs_computer"
                elif event.key == pygame.K_d:
                    shoot_bullet(paddle1_x, paddle1_y, "right")
                elif event.key == pygame.K_SPACE:
                    shoot_bullet(paddle2_x, paddle2_y, "left")
        
        if game_mode == "menu":
            draw_menu()
        else:
            handle_input()
            update_ball()
            update_bullets()
            update_bullet_accumulation()
            update_paddle_regeneration()
            
            check_ball_paddle_collisions()
            check_ball_bullet_collisions()
            check_paddle_bullet_collisions()
            
            if game_mode == "vs_computer":
                ai_move()
            
            screen.fill(BLACK)
            draw_board()
            draw_paddle(paddle1_x, paddle1_y, paddle1_width, paddle1_height, True)
            draw_paddle(paddle2_x, paddle2_y, paddle2_width, paddle2_height, False)
            draw_ball()
            
            for bullet in bullets:
                draw_bullet(bullet['x'], bullet['y'])
            
            draw_ui()
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

main()
