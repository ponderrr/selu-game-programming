import random

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

def mask_to_symbol(i, x_mask, o_mask):
    if (x_mask & bit(i)) != 0:
        return "X"
    if (o_mask & bit(i)) != 0:
        return "O"
    return str(i + 1)

def render_board(x_mask, o_mask):
    for r in range(3):
        row = []
        for c in range(3):
            index = 3 * r + c
            row.append(mask_to_symbol(index, x_mask, o_mask))
        print(" " + " | ".join(row))
        if r < 2:
            print("---+---+---")
    print()

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
    x_mask = 0
    o_mask = 0
    current = "X"
    
    while True:
        render_board(x_mask, o_mask)
        
        try:
            move = int(input(f"{current}'s turn (1-9): "))
            move = move - 1
        except:
            print("invalid input")
            continue
        
        if move < 0 or move > 8:
            print("pick 1-9")
            continue
        
        if not cell_empty(move, x_mask, o_mask):
            print("cell taken")
            continue
        
        if current == "X":
            x_mask = apply_move(x_mask, move)
            if has_won(x_mask):
                render_board(x_mask, o_mask)
                print("X wins")
                break
        else:
            o_mask = apply_move(o_mask, move)
            if has_won(o_mask):
                render_board(x_mask, o_mask)
                print("O wins")
                break
        
        if is_draw(x_mask, o_mask):
            render_board(x_mask, o_mask)
            print("cat game")
            break
        
        if current == "X":
            current = "O"
        else:
            current = "X"

def ai_game():
    x_mask = 0
    o_mask = 0
    
    while True:
        render_board(x_mask, o_mask)
        
        try:
            move = int(input("your turn (1-9): "))
            move = move - 1
        except:
            print("invalid input")
            continue
        
        if move < 0 or move > 8:
            print("pick 1-9")
            continue
        
        if not cell_empty(move, x_mask, o_mask):
            print("cell taken")
            continue
        
        x_mask = apply_move(x_mask, move)
        
        if has_won(x_mask):
            render_board(x_mask, o_mask)
            print("you win")
            break
        
        if is_draw(x_mask, o_mask):
            render_board(x_mask, o_mask)
            print("cat game")
            break
        
        ai_move = random_ai_move(x_mask, o_mask)
        if ai_move == -1:
            break
        
        o_mask = apply_move(o_mask, ai_move)
        print(f"computer plays {ai_move + 1}")
        
        if has_won(o_mask):
            render_board(x_mask, o_mask)
            print("computer wins")
            break
        
        if is_draw(x_mask, o_mask):
            render_board(x_mask, o_mask)
            print("cat game")
            break

print("1: two player")
print("2: vs computer")
choice = input("pick mode: ")

if choice == "1":
    two_player_game()
elif choice == "2":
    ai_game()
else:
    print("invalid choice")