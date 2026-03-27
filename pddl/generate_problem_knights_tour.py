import sys

def generate_pddl_board(board_size, starting_square):
    width, height = board_size.lower().split('x')
    width = int(width)
    height = int(height)
    
    squares = []
    for col in range(width):
        letter = chr(ord('A')+col)
        for row in range(1, height+1):
            squares.append(f"{letter}{row}")
    
    moves = [(-2, -1), (-1, -2), (-2, 1), (-1, 2), (2, -1), (1, -2), (2, 1), (1, 2)]
    valid_moves = []
    for col in range(1, width+1):
        for row in range(1, height+1):
            from_square = f"{chr(ord('A')+col)}{row}"
            for m in moves:
                to_row = row + m[0]
                to_col = col + m[1]
                if to_row > 0 and to_row <= height and to_col > 0 and to_col <= width:
                    valid_moves.append((from_square, f"{chr(ord('A')+to_col-1)}{to_row}"))
    
    pddl_lines = []
    pddl_lines.append(f"(define (problem_knights_tour_{width}x{height}-{starting_square})")
    pddl_lines.append("(:domain board)")
    pddl_lines.append("(:objects")
    for square in squares:
        pddl_lines.append(f"{square} ")
    pddl_lines.append(")")
    pddl_lines.append("(:init")
    pddl_lines.append(f"(at {starting_square})")
    pddl_lines.append(f"(visited {starting_square})")
    for move in valid_moves:
        pddl_lines.append(f"(valid_move {move[0]} {move[1]})")
    pddl_lines.append(")")
    pddl_lines.append("(:goal (and")
    for square in squares:
        pddl_lines.append(f"(visited {square})")
    pddl_lines.append("))")
    pddl_lines.append(")")
    return pddl_lines
    