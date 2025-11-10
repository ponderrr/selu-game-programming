import random
import pygame
import time

def bit(i):
    return 1 << i

def build_win_masks():
    masks = []
    
    for r in range(3):
        s = 3 * r
        masks.append(bit(s) | bit(s + 1) | bit(s + 2))
    
    for c in range(3):
        masks.append(bit(c) | bit(c + 3) | bit(c + 6))
    
    masks.append(bit(0) | bit(4) | bit(8))
    masks.append(bit(2) | bit(4) | bit(6))
    
    return masks

WIN_MASKS = build_win_masks()
FULL_MASK = (1 << 9) - 1

WINDOW_SIZE = 600
CELL_SIZE = WINDOW_SIZE // 3
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

def get_board_position(mouse_x, mouse_y):
    row = mouse_y // CELL_SIZE
    col = mouse_x // CELL_SIZE
    if 0 <= row < 3 and 0 <= col < 3:
        return row * 3 + col
    return -1

def draw_x(screen, row, col):
    x = col * CELL_SIZE
    y = row * CELL_SIZE
    margin = 20
    pygame.draw.line(screen, RED, (x + margin, y + margin), (x + CELL_SIZE - margin, y + CELL_SIZE - margin), 5)
    pygame.draw.line(screen, RED, (x + CELL_SIZE - margin, y + margin), (x + margin, y + CELL_SIZE - margin), 5)

def draw_o(screen, row, col):
    x = col * CELL_SIZE
    y = row * CELL_SIZE
    center_x = x + CELL_SIZE // 2
    center_y = y + CELL_SIZE // 2
    radius = CELL_SIZE // 2 - 20
    pygame.draw.circle(screen, BLUE, (center_x, center_y), radius, 5)

def draw_board(screen, x_mask, o_mask, winner=None):
    screen.fill(WHITE)
    
    for i in range(1, 3):
        pygame.draw.line(screen, BLACK, (i * CELL_SIZE, 0), (i * CELL_SIZE, WINDOW_SIZE), 3)
        pygame.draw.line(screen, BLACK, (0, i * CELL_SIZE), (WINDOW_SIZE, i * CELL_SIZE), 3)
    
    for row in range(3):
        for col in range(3):
            index = row * 3 + col
            if (x_mask & bit(index)) != 0:
                draw_x(screen, row, col)
            elif (o_mask & bit(index)) != 0:
                draw_o(screen, row, col)
    
    if winner:
        font = pygame.font.Font(None, 72)
        text = font.render("Winner", True, BLACK)
        text_rect = text.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2))
        screen.blit(text, text_rect)

def cell_empty(i, x_mask, o_mask):
    occupied = x_mask | o_mask
    return (occupied & bit(i)) == 0

def apply_move(player_mask, i):
    return player_mask | bit(i)

def has_won(player_mask):
    for w in WIN_MASKS:
        if (player_mask & w) == w:
            return True
    return False

def is_draw(x_mask, o_mask):
    occupied = x_mask | o_mask
    return occupied == FULL_MASK

def random_ai_move(x_mask, o_mask):
    empties = []
    for i in range(9):
        if cell_empty(i, x_mask, o_mask):
            empties.append(i)
    
    if len(empties) > 0:
        return random.choice(empties)
    return -1

def two_player_game():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
    pygame.display.set_caption("Tic Tac Toe - Two Player")
    
    x_mask = 0
    o_mask = 0
    current = "X"
    running = True
    game_over = False
    winner = None
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                move = get_board_position(mouse_x, mouse_y)
                
                if move == -1 or not cell_empty(move, x_mask, o_mask):
                    continue
                
                if current == "X":
                    x_mask = apply_move(x_mask, move)
                    if has_won(x_mask):
                        game_over = True
                        winner = "X"
                    elif not is_draw(x_mask, o_mask):
                        current = "O"
                else:
                    o_mask = apply_move(o_mask, move)
                    if has_won(o_mask):
                        game_over = True
                        winner = "O"
                    elif not is_draw(x_mask, o_mask):
                        current = "X"
                
                if not game_over and is_draw(x_mask, o_mask):
                    game_over = True
                    winner = "Draw"
        
        draw_board(screen, x_mask, o_mask, winner)
        pygame.display.flip()
        
        if game_over and winner:
            time.sleep(3)
            running = False
    
    pygame.quit()

def ai_game():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
    pygame.display.set_caption("Tic Tac Toe - vs Computer")
    
    x_mask = 0
    o_mask = 0
    running = True
    game_over = False
    player_turn = True
    winner = None
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and not game_over and player_turn:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                move = get_board_position(mouse_x, mouse_y)
                
                if move == -1 or not cell_empty(move, x_mask, o_mask):
                    continue
                
                x_mask = apply_move(x_mask, move)
                player_turn = False
                
                if has_won(x_mask):
                    game_over = True
                    winner = "You"
                elif is_draw(x_mask, o_mask):
                    game_over = True
                    winner = "Draw"
        
        if not game_over and not player_turn:
            ai_move = random_ai_move(x_mask, o_mask)
            if ai_move != -1:
                o_mask = apply_move(o_mask, ai_move)
                print(f"computer plays {ai_move + 1}")
                
                if has_won(o_mask):
                    game_over = True
                    winner = "Computer"
                elif is_draw(x_mask, o_mask):
                    game_over = True
                    winner = "Draw"
                else:
                    player_turn = True
        
        draw_board(screen, x_mask, o_mask, winner)
        pygame.display.flip()
        
        if game_over and winner:
            time.sleep(3)
            running = False
    
    pygame.quit()

print("1: two player")
print("2: vs computer")
choice = input("pick mode: ")

if choice == "1":
    two_player_game()
elif choice == "2":
    ai_game()
else:
    print("invalid choice")
