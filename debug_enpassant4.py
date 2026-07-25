import ChessEngine

print("=== Correct En Passant Debug ===")
print("Coordinate system:")
print("  Row 0 = Rank 8 (top)")
print("  Row 7 = Rank 1 (bottom)")
print("  Col 0 = File A")
print("  Col 7 = File H")
print()

# Set up position for en passant test
# We want: black just played d7-d5, white has pawn on e5
gs = ChessEngine.GameState()
# Clear board
gs.board = [["--" for _ in range(8)] for _ in range(8)]

# Place black pawn on d5
# d5 = file d=3, rank 5
# rank 5 -> row = 8 - 5 = 3
gs.board[3][3] = "bp"  # row 3, col 3

# Place white pawn on e5  
# e5 = file e=4, rank 5
# rank 5 -> row = 8 - 5 = 3
gs.board[3][4] = "wp"  # row 3, col 4

# Set turn to black just moved, so now white to move
gs.whiteToMove = True

# After black played d7-d5, set en passant target
# d7-d5: from d7 to d5
# d7 = file d=3, rank 7 -> row = 8-7 = 1
# d5 = file d=3, rank 5 -> row = 8-5 = 3
# Passed through d6 = file d=3, rank 6 -> row = 8-6 = 2
# So en passant target should be d6 = (2, 3)
gs.enpassantPossible = (2, 3)

print("Position after black's d7-d5:")
print("  Black pawn on d5")
print("  White pawn on e5")
print("  White to move")
print("  En passant target: d6 (2,3)")
print()

print("Board:")
for i in range(8):
    rank = 8 - i
    row_str = []
    for j in range(8):
        row_str.append(gs.board[i][j])
    print(f"Rank {rank}: {' '.join(row_str)}")
print()

# Generate white moves
print("Generating white moves...")
white_moves = gs.getValidMoves()

print(f"Total white moves: {len(white_moves)}")
en_passant_moves = []
normal_moves = []
for i, m in enumerate(white_moves):
    if m.isEnpassantMove:
        en_passant_moves.append(m)
    else:
        normal_moves.append(m)

print(f"En passant moves: {len(en_passant_moves)}")
print(f"Normal moves: {len(normal_moves)}")

if en_passant_moves:
    print("En passant moves found:")
    for m in en_passant_moves:
        print(f"  {m.getChessNotation()} from {m.startRow},{m.startCol} to {m.endRow},{m.endCol}")
else:
    print("NO EN PASSANT MOVES FOUND")
    print("\nLet's debug why:")
    print("White pawn is at e5")
    e5_row, e5_col = 3, 4  # e5 = file e=4, rank 5 -> row=3
    print(f"  Position: ({e5_row}, {e5_col})")
    print("  White move amount: -1 (up one row)")
    print("  Checking captures:")
    print(f"    Left:  ({e5_row + (-1)}, {e5_col - 1}) = ({e5_row - 1}, {e5_col - 1}) = ({e5_row-1}, {e5_col-1})")
    print(f"    Right: ({e5_row + (-1)}, {e5_col + 1}) = ({e5_row - 1}, {e5_col + 1}) = ({e5_row-1}, {e5_col+1})")
    print(f"  En passant target: {gs.enpassantPossible}")
    print()
    print("For en passant, we need:")
    print(f"    Left target equals EP: ({e5_row-1}, {e5_col-1}) == {gs.enpassantPossible} ? {((e5_row-1, e5_col-1) == gs.enpassantPossible)}")
    print(f"    Right target equals EP: ({e5_row-1}, {e5_col+1}) == {gs.enpassantPossible} ? {((e5_row-1, e5_col+1) == gs.enpassantPossible)}")
    
    # What should the en passant target be for a capture to work?
    print()
    print("What EN PASSANT TARGET would make this work?")
    print("For left capture to be en passant:")
    print(f"  We want: ({e5_row-1}, {e5_col-1}) == EP_TARGET")
    print(f"  So EP_TARGET should be: ({e5_row-1}, {e5_col-1}) = ({e5_row-1}, {e5_col-1})")
    print("For right capture to be en passant:")
    print(f"  We want: ({e5_row-1}, {e5_col+1}) == EP_TARGET")  
    print(f"  So EP_TARGET should be: ({e5_row-1}, {e5_col+1}) = ({e5_row-1}, {e5_col+1})")
    
    left_ep_target = (e5_row-1, e5_col-1)
    right_ep_target = (e5_row-1, e5_col+1)
    print(f"  Left EP target would be: {left_ep_target}")
    print(f"  Right EP target would be: {right_ep_target}")
    
    # What are these in chess notation?
    def to_chess_notation(row, col):
        file = chr(ord('a') + col)
        rank = 8 - row
        return f"{file}{rank}"
        
    print(f"  Left EP target {left_ep_target} = {to_chess_notation(*left_ep_target)}")
    print(f"  Right EP target {right_ep_target} = {to_chess_notation(*right_ep_target)}")
    
    print()
    print("But wait - let's think about what square the pawn actually MOVES TO:")
    print("For white e5 pawn capturing en passant to the left:")
    print("  It should move to d6")
    print("  d6 = file d=3, rank 6")
    print("  rank 6 -> row = 8-6 = 2")
    print("  So d6 = (2,3)")
    print("  And we have: white e5 (3,4) -> d6 (2,3)")
    print("  This is: Δrow = -1, Δcol = -1")
    print("  But white pawns capture diagonally forward:")
    print("    White moves up the board (decreasing row numbers)")
    print("    So from white's perspective, 'forward' is decreasing row")
    print("    Therefore, white pawn captures are: (r-1, c-1) and (r-1, c+1)")
    print("  For e5 (3,4):")
    print("    Left capture: (3-1, 4-1) = (2,3) = d6 ✓")
    print("    Right capture: (3-1, 4+1) = (2,5) = f6 ✓")
    print()
    print("So the capture move is TO (2,3) or (2,5)")
    print("And this should EQUAL the en passant target")
    print("Therefore: en passant target should be (2,3) or (2,5)")
    print("Which matches what we have set: (2,3)")
    print()
    print("So why isn't it being detected?")
    print("Let's look at the actual move generation code logic:")
    print()
    print("In getPawnMoves():")
    print("  if not piecePinned or pinDirection == (moveAmount, -1):")
    print("      if self.board[r + moveAmount][c - 1][0] == enemyColor:")
    print("          moves.append(Move((r, c), (r + moveAmount, c - 1), self.board))")
    print("      elif (r + moveAmount, c - 1) == self.enpassantPossible:")
    print("          moves.append(Move((r, c), (r + moveAmount, c - 1), self.board, isEnpassantMove=True))")
    print()
    print("So it FIRST checks if there's an enemy piece for a normal capture")
    print("  Only if THAT fails, it checks for en passant")
    print()
    print("In our position:")
    print("  Left check: (r+moveAmount, c-1) = (3-1, 4-1) = (2,3)")
    print("  Board[2][3] = ? Let's check...")
    
    target_r, target_c = 2, 3
    target_piece = gs.board[target_r][target_c]
    print(f"  Board[{target_r}][{target_c}] = '{target_piece}'")
    if target_piece == "--":
        print("  -> Square is empty, so no normal capture")
        print("  -> Now checking if (2,3) == enpassantPossible (2,3)...")
        if (target_r, target_c) == gs.enpassantPossible:
            print("  -> YES! This SHOULD trigger en passant!")
        else:
            print("  -> No, not equal")
    elif target_piece[0] == 'b':
        print("  -> Black piece found! This would be a normal capture")
        print("  -> The en passant check is skipped because we found a capture first")
    else:
        print("  -> White piece or something else")
        
    print()
    print("AH HA! The issue is that we're checking in this order:")
    print("  1. Is there an enemy piece at the target square? (for normal capture)")
    print("  2. Only if NO, then check if target square equals en passant target")
    print()
    print("In our case, the target square (2,3) for the purported capture")
    print("is actually where we want to move FOR en passant,")
    print("but we're checking if there's an enemy piece there first.")
    print("Since it's empty, we THEN check for en passant.")
    print("This SHOULD work...")
    print()
    print("Let me trace through the actual code execution:")
    
    # Let's manually execute the logic
    r, c = 3, 4  # e5
    moveAmount = -1
    print(f"For white pawn at ({r},{c}):")
    print(f"  moveAmount = {moveAmount}")
    
    # Left diagonal
    print(f"  Left check:")
    target_r, target_c = r + moveAmount, c - 1
    print(f"    Target: ({target_r}, {target_c})")
    if 0 <= target_r < 8 and 0 <= target_c < 8:
        target_piece = gs.board[target_r][target_c]
        print(f"    Piece: '
