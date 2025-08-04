import pygame
import sys
import math
import time 


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
    text = font.render(f"Turn: {current_turn.capitalize()}", True, text_color)
    screen.blit(text, (10, 10))

current_turn = "goat"
captured_goats = 0




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
tigers = [(0, 0), (0, 4), (4, 0), (4, 4)]
selected_tiger=None 
selected_goat = None

goats=[]
goat_count=0
MAX_GOATS=20
game_over=False 
move_history = []  # To store previous game states


#function that will check if the clicked two points are neighbouring or not
def is_adjacent(pos1, pos2):
    return pos2 in connections.get(pos1, [])


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

def are_all_tigers_blocked():
    for tiger in tigers:
        for neighbor in connections[tiger]:
            if neighbor not in goats and neighbor not in tigers:
                return False  # Tiger can still move
            # Check for jump capture
            dx = neighbor[0] - tiger[0]
            dy = neighbor[1] - tiger[1]
            jump = (neighbor[0] + dx, neighbor[1] + dy)
            if neighbor in goats and jump in connections[tiger]:
                if jump not in goats and jump not in tigers:
                    return False
    return True



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

    font = pygame.font.SysFont(None, 36)

    # Display captured goats count
    text = font.render(f"Goats Captured: {captured_goats}", True, (0,0,0))
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
    for tiger in tigers:
        i, j = tiger
        x, y = points[(i,j)]

        if tiger == selected_tiger:
            pygame.draw.circle(screen, (255, 200, 200), (x, y), RADIUS + 6)  # light red outer glow

        pygame.draw.circle(screen, TIGER_COLOR, (x, y), RADIUS)
        # Show possible tiger moves
        if selected_tiger:
            for neighbor in connections[selected_tiger]:
                if neighbor not in tigers and neighbor not in goats:
                    x, y = points[neighbor]
                    pygame.draw.circle(screen, (200, 255, 200), (x, y), RADIUS + 5, 2)  # green glow


    # Draw goats
    for goat in goats:
        i, j = goat
        x, y = points[(i,j)]
        if goat == selected_goat:
            pygame.draw.circle(screen, (200, 200, 255), (x, y), RADIUS + 6)  # light blue outer glow

        pygame.draw.circle(screen, GOAT_COLOR, (x, y), RADIUS)
        # Highlight possible goat moves if a goat is selected
        if selected_goat:
            for neighbor in connections[selected_goat]:
                if neighbor not in goats and neighbor not in tigers:
                    x, y = points[neighbor]
                    pygame.draw.circle(screen, (200, 255, 200), (x, y), RADIUS + 5, 2)  # green outline


    pygame.display.update()

def save_state():
    move_history.append((
        list(goats),
        list(tigers),
        selected_tiger,
        selected_goat,
        captured_goats,
        current_turn,
        game_over
    ))

def undo_move():
    global goats, tigers, selected_tiger, selected_goat, captured_goats, current_turn, game_over
    if move_history:
        last_state = move_history.pop()
        goats, tigers, selected_tiger, selected_goat, captured_goats, current_turn,game_over = last_state
        game_over = False

def restart_game():
    global goats, tigers, captured_goats, selected_goat, selected_tiger, current_turn, game_over, move_history, goat_count
    goats = []
    tigers = [(0, 0), (0, 4), (4, 0), (4, 4)]
    captured_goats = 0
    selected_goat = None
    selected_tiger = None
    current_turn = "goat"
    game_over = False
    move_history = []
    goat_count=0



#to check winner after each successful move
def check_win_condition():
    if captured_goats >= 5:
        return "tiger"
    elif are_all_tigers_blocked():
        return "goat"
    return None


def handle_win_check():
    global game_over
    winner = check_win_condition()
    if winner:
        font = pygame.font.SysFont(None, 60)
        text = font.render(f"{winner.capitalize()} Wins!", True, (255, 0, 0))
        rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(text, rect)
        game_over=True 
        pygame.display.flip()
        pygame.time.wait(3000)
        pygame.quit()
        sys.exit()

# Main loop

def main():
    global goat_count, selected_tiger, selected_goat, current_turn, captured_goats
    running = True

    while running:
        draw_board()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if restart_rect.collidepoint(event.pos):
                    restart_game()
                elif not game_over:
                    if undo_rect.collidepoint(event.pos):
                        undo_move()
                    else:
                        pos = pygame.mouse.get_pos()
                        grid_pos = get_closest_point(pos)
                        if grid_pos is None:
                            continue
                        if current_turn == "goat":
                            # Goat placement phase
                            if goat_count < MAX_GOATS:
                                if grid_pos not in goats and grid_pos not in tigers:
                                    save_state()
                                    goats.append(grid_pos)
                                    goat_count += 1
                                    handle_win_check()
                                    current_turn="tiger"
                            else:
                                # After all goats placed, allow goat and tiger movement
                                
                                # -- Goat Movement --
                                if selected_goat is None:
                                    # Select goat to move
                                    if grid_pos in goats:
                                        selected_goat = grid_pos
                                else:
                                    # Move selected goat if target spot valid
                                    if grid_pos not in goats and grid_pos not in tigers:
                                        if grid_pos in connections[selected_goat]:
                                            # Move goat
                                            save_state()
                                            goats.remove(selected_goat)
                                            goats.append(grid_pos)
                                            selected_goat = None  # Deselect after move
                                            handle_win_check()
                                            current_turn="tiger"
                                        else:
                                            print("Invalid goat move")
                                            selected_goat = None  # Deselect on invalid move
                                    else:
                                        # Deselect if clicked invalid spot or same goat
                                        selected_goat = None
                        elif current_turn == "tiger" :
                            # -- Tiger Movement --
                            if selected_goat is None:  # only if no goat selected (avoid confusion)
                                if selected_tiger is None:
                                    # Select tiger
                                    if grid_pos in tigers:
                                        selected_tiger = grid_pos
                                else:
                                    si, sj = selected_tiger
                                    gi, gj = grid_pos
                                    if grid_pos not in tigers and grid_pos not in goats and grid_pos in connections[selected_tiger]:
                                        save_state()
                                        tigers.remove(selected_tiger)
                                        tigers.append(grid_pos)
                                        handle_win_check()
                                        selected_tiger=None 
                                        current_turn="goat"

                                    elif abs(gi - si) == 2 or abs(gj - sj) == 2:
                                        mi, mj = (si + gi) // 2, (sj + gj) // 2
                                        if (mi, mj) in goats and grid_pos not in goats and grid_pos not in tigers:
                                            save_state()
                                            goats.remove((mi, mj))
                                            tigers.remove(selected_tiger)
                                            tigers.append(grid_pos)
                                            captured_goats+=1
                                            handle_win_check()
                                            selected_tiger=None 
                                            current_turn="goat"


main()