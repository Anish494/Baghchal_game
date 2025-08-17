import pygame
import sys
import math
import copy

#gui for mode selection
def main_menu():
    global game_mode, ai_side
    menu_running = True
    pygame.display.set_caption("Bagh-Chal Menu")
    
    # Fonts
    title_font = pygame.font.SysFont(None, 72, bold=True)
    btn_font = pygame.font.SysFont(None, 40, bold=True)

    # Buttons
    button_2p = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 70, 300, 60)
    button_ai = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 20, 300, 60)

    while menu_running:
        # Gradient background
        for y in range(HEIGHT):
            color = (50 + y//12, 100 + y//8, 180 + y//15)
            pygame.draw.line(screen, color, (0, y), (WIDTH, y))

        # Title
        title_text = title_font.render("Bagh-Chal", True, (255, 255, 255))
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 100))

        mouse_pos = pygame.mouse.get_pos()

        # Button colors with hover effect
        color_2p = (255, 100, 100) if button_2p.collidepoint(mouse_pos) else (200, 50, 50)
        color_ai = (100, 200, 100) if button_ai.collidepoint(mouse_pos) else (50, 150, 50)

        # Draw shadow first
        pygame.draw.rect(screen, (0,0,0,100), button_2p.move(5,5), border_radius=12)
        pygame.draw.rect(screen, (0,0,0,100), button_ai.move(5,5), border_radius=12)

        # Draw buttons
        pygame.draw.rect(screen, color_2p, button_2p, border_radius=12)
        pygame.draw.rect(screen, color_ai, button_ai, border_radius=12)

        # Draw button text
        text_2p = btn_font.render("2 Player Mode", True, (255, 255, 255))
        text_ai = btn_font.render("Play vs AI", True, (255, 255, 255))
        screen.blit(text_2p, (button_2p.x + (button_2p.width - text_2p.get_width())//2, button_2p.y + 12))
        screen.blit(text_ai, (button_ai.x + (button_ai.width - text_ai.get_width())//2, button_ai.y + 12))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_2p.collidepoint(event.pos):
                    game_mode = "2p"
                    menu_running = False
                elif button_ai.collidepoint(event.pos):
                    game_mode = "vs_ai"
                    ai_side = "tiger"
                    menu_running = False

#initializing pygame
pygame.init()

#some constant values that we will use for game to be functionng smoothly
WIDTH, HEIGHT = 600,600
ROWS, COLS= 5 ,5
GAP=WIDTH//(COLS+1)
RADIUS=20


#DIFFERENT COLOR FOR DIFFERENT ITEMS
BG_COLOR=(240,230,220)
LINE_COLOR=(0,0,0)
TIGER_COLOR=(255,100,100)
GOAT_COLOR=(255,255,255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bagh-Chal")


font = pygame.font.SysFont(None, 36)

def draw_turn_text():
    text_color = (0, 0, 0)
    text = font.render(f"Turn: {state['turn'].capitalize()}", True, text_color)
    screen.blit(text, (10, 10))


# POINTS AT WHICH WE WILL STORE GOATS OR TIGER
points = {}
for i in range(5):
    for j in range(5):
        x = GAP * (j + 1)
        y = GAP * (i + 1)
        points[(i, j)] = (x, y)


# Define all possible directions: orthogonal + diagonal
directions = [(-1, 0), (1, 0), (0, -1), (0, 1),
              (-1, -1), (-1, 1), (1, -1), (1, 1)]

connections = {}

for (i, j) in points:
    neighbors = []
    for dx, dy in directions:
        ni, nj = i + dx, j + dy
        if (ni, nj) in points:
            neighbors.append((ni, nj))
    connections[(i, j)] = neighbors



# TIGERS ARE PLACED AT THIS POSITION AT START OF GAME
# tigers = [(0, 0), (0, 4), (4, 0), (4, 4)]
selected_tiger=None 
selected_goat = None
ai_move_pending = False


# goats=[]
# MAX_GOATS=20
game_over=False 
move_history = []  # To store previous game states

state = {
    "tigers": [(0, 0), (0, 4), (4, 0), (4, 4)],
    "goats": [],
    "goats_to_place": 20,   
    "turn": "goat"          # "goat" or "tiger"
}

game_mode = "vs_ai"   # "2p" or "vs_ai"
ai_side   = "tiger"   
ai_depth  = 3         


def next_turn(p): return "goat" if p == "tiger" else "tiger"

def captured_count(st):
    # total goats = 20; captured = placed - on_board
    placed = 20 - st["goats_to_place"]
    return placed - len(st["goats"])


#function that will check if the clicked two points are neighbouring or not
def is_adjacent(pos1, pos2):
    return pos2 in connections.get(pos1, [])

#it helps ai let know what are all possible moves that can be taken
def get_all_moves(st, player):
    moves = []

    if player == "goat":
        if st["goats_to_place"] > 0:
            for pos in points:
                if pos not in st["goats"] and pos not in st["tigers"]:
                    moves.append(("place", pos))
        else:
            for g in st["goats"]:
                for n in connections[g]:
                    if n not in st["goats"] and n not in st["tigers"]:
                        moves.append(("move", g, n))

    else:  # tiger
        for t in st["tigers"]:
            for n in connections[t]:
                # simple move
                if n not in st["goats"] and n not in st["tigers"]:
                    moves.append(("move", t, n))

                # capture: n must be a goat and jump must be empty AND reachable from n
                if n in st["goats"]:
                    jump = (2*n[0] - t[0], 2*n[1] - t[1])
                    if (jump in points and
                        jump not in st["goats"] and
                        jump not in st["tigers"] and
                        jump in connections[n]):  # ensure a valid edge n->jump
                        moves.append(("capture", t, n, jump))

    return moves


def simulate_move(st, move, player):
    ns = copy.deepcopy(st)

    if player == "goat":
        kind = move[0]
        if kind == "place":
            _, pos = move
            ns["goats"].append(pos)
            ns["goats_to_place"] -= 1
        else:  # "move"
            _, a, b = move
            ns["goats"].remove(a)
            ns["goats"].append(b)

    else:  # tiger
        kind = move[0]
        if kind == "move":
            _, a, b = move
            ns["tigers"].remove(a)
            ns["tigers"].append(b)
        else:  # "capture"
            _, tpos, gpos, jpos = move
            ns["tigers"].remove(tpos)
            ns["tigers"].append(jpos)
            ns["goats"].remove(gpos)

    return ns


#function to define score for deciding which step to take in minimax
def evaluate(st):
    # + capture is good for tiger
    score = 0
    score += captured_count(st) * 60

    # more goats on board is bad for tiger
    score -= len(st["goats"]) * 8

    # tiger mobility: count empty neighbors (encourages activity)
    mob = 0
    for t in st["tigers"]:
        mob += sum(1 for n in connections[t] if n not in st["goats"] and n not in st["tigers"])
    score += mob * 2

    # bonus if any capture available (threat)
    any_cap = any(m[0]=="capture" for m in get_all_moves(st, "tiger"))
    if any_cap: score += 25

    # penalty if all tigers blocked (goats winning)
    if are_all_tigers_blocked_state(st):
        score -= 200

    return score

def are_all_tigers_blocked_state(st):
    for t in st["tigers"]:
        for n in connections[t]:
            if n not in st["goats"] and n not in st["tigers"]:
                return False
            # capture possible?
            if n in st["goats"]:
                jump = (2*n[0]-t[0], 2*n[1]-t[1])
                if (jump in points and
                    jump not in st["goats"] and
                    jump not in st["tigers"] and
                    jump in connections[n]):
                    return False
    return True


#minimax algorithm for baghchal game
#brain of AI
def minimax(st, depth, player):
    # return a numeric score (tiger POV)
    if depth == 0:
        return evaluate(st)

    moves = get_all_moves(st, player)
    if not moves:
        # no moves: if player is tiger, that's bad for tiger; if goat, neutral-ish
        return -9999 if player == "tiger" else 0

    if player == "tiger":
        best = float("-inf")
        for mv in moves:
            ns = simulate_move(st, mv, "tiger")
            best = max(best, minimax(ns, depth-1, "goat"))
        return best
    else:
        best = float("inf")
        for mv in moves:
            ns = simulate_move(st, mv, "goat")
            best = min(best, minimax(ns, depth-1, "tiger"))
        return best


def find_best_move(st, player, depth):
    moves = get_all_moves(st, player)
    if not moves: return None

    if player == "tiger":
        best_score, best_move = float("-inf"), None
        for mv in moves:
            ns = simulate_move(st, mv, "tiger")
            sc = minimax(ns, depth-1, "goat")
            if sc > best_score:
                best_score, best_move = sc, mv
        return best_move
    else:
        best_score, best_move = float("inf"), None
        for mv in moves:
            ns = simulate_move(st, mv, "goat")
            sc = minimax(ns, depth-1, "tiger")
            if sc < best_score:
                best_score, best_move = sc, mv
        return best_move

# to get closest point on screen where mouse is clicked
def get_closest_point(pos):
    mx, my = pos
    for i in range(5):
        for j in range(5):
            x, y = points[(i,j)]
            dist = math.hypot(mx - x, my - y)
            if dist <= RADIUS * 1.5:
                return (i, j)
    return None


# Draw the board
def draw_board():
    screen.fill(BG_COLOR)
    draw_turn_text()
    # Draw lines
    for i in range(5):
        for j in range(5):
            start = points[(i,j)]
            # Horizontal lines
            if j < 4:
                pygame.draw.line(screen, LINE_COLOR, start, points[(i,j+1)], 2)
            # Vertical lines
            if i < 4:
                pygame.draw.line(screen, LINE_COLOR, start, points[(i+1,j)], 2)
            # Diagonal lines
            if i < 4 and j < 4:
                pygame.draw.line(screen, LINE_COLOR, start, points[(i+1,j+1)], 2)
            if i < 4 and j > 0:
                pygame.draw.line(screen, LINE_COLOR, start, points[(i+1,j-1)], 2)


    # Display captured goats count
    text = font.render(f"Goats Captured: {captured_count(state)}", True, (0,0,0))
    screen.blit(text, (WIDTH-text.get_width()-10, 10))

    # Draw Undo and Restart buttons
    global undo_rect, restart_rect
    undo_rect = pygame.Rect(20, HEIGHT-60, 120, 40)
    restart_rect = pygame.Rect(WIDTH-140, HEIGHT-60, 120, 40)
    
    pygame.draw.rect(screen, (100, 100, 200), undo_rect)
    pygame.draw.rect(screen, (200, 100, 100), restart_rect)
    
    undo_text = font.render("Undo", True, (255, 255, 255))
    restart_text = font.render("Restart", True, (255, 255, 255))
    
    screen.blit(undo_text, (undo_rect.x + 20, undo_rect.y + 5))
    screen.blit(restart_text, (restart_rect.x + 10, restart_rect.y + 5))

    # Draw tiger pieces
    for tiger in state["tigers"]:
        i, j = tiger
        x, y = points[(i,j)]

        if tiger == selected_tiger:
            pygame.draw.circle(screen, (255, 200, 200), (x, y), RADIUS + 6)  # light red outer glow

        pygame.draw.circle(screen, TIGER_COLOR, (x, y), RADIUS)
        # Show possible tiger moves
        if selected_tiger:
            for neighbor in connections[selected_tiger]:
                if neighbor not in state["tigers"] and neighbor not in state["goats"]:
                    x, y = points[neighbor]
                    pygame.draw.circle(screen, (200, 255, 200), (x, y), RADIUS + 5, 2)  # green glow


    # Draw goats
    for goat in state["goats"]:
        i, j = goat
        x, y = points[(i,j)]
        if goat == selected_goat:
            pygame.draw.circle(screen, (200, 200, 255), (x, y), RADIUS + 6)  # light blue outer glow

        pygame.draw.circle(screen, GOAT_COLOR, (x, y), RADIUS)
        # Highlight possible goat moves if a goat is selected
        if selected_goat:
            for neighbor in connections[selected_goat]:
                if neighbor not in state["goats"] and neighbor not in state["tigers"]:
                    x, y = points[neighbor]
                    pygame.draw.circle(screen, (200, 255, 200), (x, y), RADIUS + 5, 2)  # green outline


    pygame.display.update()

history=[]
def save_state(ai_move=False):
    snapshot = {
        "goats": state["goats"].copy(),
        "tigers": state["tigers"].copy(),
        "turn": state["turn"],
        "goats_to_place": state["goats_to_place"],
        "selected_goat": selected_goat,
        "selected_tiger": selected_tiger,
        "ai_move":ai_move 
    }
    history.append(snapshot)



def undo_move():
    global history
    if len(history) > 1:  # ensure at least one state remains
        last_snapshot = history.pop()
        # If last move was AI, pop one more to revert human move too
        if last_snapshot.get("ai_move") and len(history) > 1:
            history.pop()
        # restore the last available snapshot
        restore_state(history[-1])
    else:
        print("Nothing to undo!")


def restore_state(snapshot):
    global state, selected_goat, selected_tiger
    state["goats"] = snapshot["goats"].copy()
    state["tigers"] = snapshot["tigers"].copy()
    state["turn"] = snapshot["turn"]
    state["goats_to_place"] = snapshot["goats_to_place"]
    selected_goat = snapshot["selected_goat"]
    selected_tiger = snapshot["selected_tiger"]


def restart_game():
    global history, selected_goat, selected_tiger, game_over
    # Clear history
    history = []

    # Reset state
    state["tigers"] = [(0,0),(0,4),(4,0),(4,4)]
    state["goats"] = []
    state["goats_to_place"] = 20
    state["turn"] = "goat"

    # Clear selections and flags
    selected_goat = None
    selected_tiger = None
    game_over = False

    # Save initial state to history
    save_state()


#to check winner after each successful move
def check_win_condition(st):
    if captured_count(st) >= 5:
        return "tiger"
    if are_all_tigers_blocked_state(st):
        return "goat"
    return None

def handle_win_check():
    global game_over
    winner = check_win_condition(state)
    if winner and not game_over:
        game_over = True  # stop further moves

        # Display a meaningful message with correct counts
        font_big = pygame.font.SysFont(None, 60)
        text = font_big.render(f"{winner.capitalize()} Wins!", True, (255, 0, 0))
        rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))

        # Draw on top of current board
        draw_board()
        screen.blit(text, rect)
        pygame.display.flip()

        # Wait a moment so player can see the message
        pygame.time.wait(2000)

# Main loop
main_menu()
def main():
    global selected_tiger, selected_goat, ai_move_pending
    running = True

    while running:
        draw_board()
        if ai_move_pending and not game_over:
            # save_state()
            mv = find_best_move(state, ai_side, ai_depth)
            if mv:
                ns = simulate_move(state, mv, ai_side)
                state.clear()
                state.update(ns)
                save_state(ai_move=True)
            handle_win_check()
            if not game_over:
                state["turn"] = next_turn(state["turn"])
                if state["turn"] != ai_side:  # next turn is human
                    ai_move_pending = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if restart_rect.collidepoint(event.pos):
                    restart_game()
                    continue
                elif undo_rect.collidepoint(event.pos):
                    undo_move()
                    continue
                elif not game_over:
                    if undo_rect.collidepoint(event.pos):
                        undo_move()
                    else:
                        pos = pygame.mouse.get_pos()
                        grid_pos = get_closest_point(pos)
                        if grid_pos is None:
                            continue
                        if state["turn"] == "goat" and (game_mode == "2p" or ai_side != "goat"):
                            # Goat placement phase
                            if state["goats_to_place"] >0:
                                if grid_pos not in state["goats"] and grid_pos not in state["tigers"]:
                                    save_state()
                                    state["goats"].append(grid_pos)
                                    state["goats_to_place"] -= 1
                                    selected_goat=None
                                    selected_tiger=None
                                    handle_win_check()
                                    if not game_over:
                                        state["turn"] = next_turn(state["turn"])
                                        if game_mode == "vs_ai" and state["turn"] == ai_side:
                                            ai_move_pending = True



                            else:
                                # After all goats placed, allow goat and tiger movement
                                
                                # -- Goat Movement --
                                if selected_goat is None:
                                    # Select goat to move
                                    if grid_pos in state["goats"]:
                                        selected_goat = grid_pos
                                else:
                                    # Move selected goat if target spot valid
                                    if grid_pos not in state["goats"] and grid_pos not in state["tigers"]:
                                        if grid_pos in connections[selected_goat]:
                                            # Move goat
                                            save_state()
                                            state["goats"].remove(selected_goat)
                                            state["goats"].append(grid_pos)
                                            selected_goat = None  # Deselect after move
                                            selected_tiger=None
                                            handle_win_check()
                                            if not game_over:
                                                state["turn"] = next_turn(state["turn"])
                                                if game_mode == "vs_ai" and state["turn"] == ai_side:
                                                    ai_move_pending = True


                                        else:
                                            selected_goat = None  # Deselect on invalid move
                        elif state["turn"] == "tiger" and (game_mode == "2p" or ai_side != "tiger"):
                            # -- Tiger Movement --
                            if selected_goat is None:  # only if no goat selected (avoid confusion)
                                if selected_tiger is None:
                                    # Select tiger
                                    if grid_pos in state["tigers"]:
                                        selected_tiger = grid_pos
                                else:
                                    si, sj = selected_tiger
                                    gi, gj = grid_pos
                                    if grid_pos not in state["tigers"] and grid_pos not in state["goats"] and grid_pos in connections[selected_tiger]:
                                        save_state()
                                        state["tigers"].remove(selected_tiger)
                                        state["tigers"].append(grid_pos)
                                        selected_tiger=None
                                        selected_goat=None
                                        handle_win_check()
                                        if not game_over:
                                            state["turn"] = next_turn(state["turn"])
                                            if game_mode == "vs_ai" and state["turn"] == ai_side:
                                                ai_move_pending = True

                                    elif abs(gi - si) == 2 or abs(gj - sj) == 2:
                                        mi, mj = (si + gi) // 2, (sj + gj) // 2
                                        if (mi, mj) in state["goats"] and grid_pos not in state["goats"] and grid_pos not in state["tigers"]:
                                            save_state()
                                            state["goats"].remove((mi, mj))
                                            state["tigers"].remove(selected_tiger)
                                            state["tigers"].append(grid_pos)
                                            selected_tiger=None
                                            selected_goat=None 
                                            handle_win_check()
                                            if not game_over:
                                                state["turn"] = next_turn(state["turn"])
                                                if game_mode == "vs_ai" and state["turn"] == ai_side:
                                                    ai_move_pending = True

main()