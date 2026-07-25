import ChessEngine

print("=== Detailed En Passant Debug ===")

# Set up position manually like in test_fixed.py
gs = ChessEngine.GameState()
# Clear board
gs.board = [["--" for _ in range(8)] for _ in range(8)]
# Place black pawn on d5
gs.board[3][3] = "bp"  # row 3, col 3 = d5
# Place white pawn on e5  
gs.board[4][4] = "wp"  # row 4, col 4 = e5
# Set turn to white
gs.whiteToMove = True
# Set en passant target
gs.enpassantPossible = (2, 3)  # d6

print("Board state:")
for i, row in enumerate(gs.board):
    rank = 8 - i
    print(f"Rank {rank}: {' '.join(row)}")
print(f"White to move: {gs.whiteToMove}")
print(f"En passant target: {gs.enpassantPossible}")
print()

# Get all white moves
white_moves = gs.getValidMoves()
print(f"Total white moves: {len(white_moves)}")
for i, m in enumerate(white_moves):
    print(f"  {i+1}. {m.getChessNotation()}", end="")
    if m.isEnpassantMove:
        print(" (EN PASSANT)", end="")
    print()
print()

# Let's manually check what the pawn moves function would generate
print("=== Manual pawn move generation for e5 pawn ===")
r, c = 4, 4  # e5 position
piece = gs.board[r][c]
print(f"Piece at {r},{c}: {piece}")
if piece == "wp":
    print("White pawn found")
    moveAmount = -1  # white moves up (decreasing row)
    startRow = 6  # white pawns start at row 6 (rank 2)
    enemyColor = 'b'
    
    print(f"moveAmount: {moveAmount}")
    print(f"Checking left capture: ({r + moveAmount}, {c - 1}) = ({r + moveAmount}, {c - 1})")
    print(f"Checking right capture: ({r + moveAmount}, {c + 1}) = ({r + moveAmount}, {c + 1})")
    print(f"En passant target: {gs.enpassantPossible}")
    
    # Check left
    if c - 1 >= 0:
        target_r, target_c = r + moveAmount, c - 1
        print(f"\nLeft capture check:")
        print(f"  Target square: ({target_r}, {target_c})")
        if 0 <= target_r < 8 and 0 <= target_c < 8:
            target_piece = gs.board[target_r][target_c]
            print(f"  Piece at target: {target_piece}")
            if target_piece != "--" and target_piece[0] == enemyColor:
                print(f"  -> Normal capture possible: {target_piece}")
            elif (target_r, target_c) == gs.enpassantPossible:
                print(f"  -> EN PASSANT capture possible!")
            else:
                print(f"  -> No capture (not enemy and not en passant target)")
        else:
            print(f"  -> Target off board")
    
    # Check right
    if c + 1 <= 7:
        target_r, target_c = r + moveAmount, c + 1
        print(f"\nRight capture check:")
        print(f"  Target square: ({target_r}, {target_c})")
        if 0 <= target_r < 8 and 0 <= target_c < 8:
            target_piece = gs.board[target_r][target_c]
            print(f"  Piece at target: {target_piece}")
            if target_piece != "--" and target_piece[0] == enemyColor:
                print(f"  -> Normal capture possible: {target_piece}")
            elif (target_r, target_c) == gs.enpassantPossible:
                print(f"  -> EN PASSANT capture possible!")
            else:
                print(f"  -> No capture (not enemy and not en passant target)")
        else:
            print(f"  -> Target off board")

print("\n=== Let's see what squares are being checked ===")
print("White pawn at e5 (4,4)")
print("Move amount for white: -1 (up one row)")
print()
print("Left diagonal: (4-1, 4-1) = (3,3) = d5")
print("Right diagonal: (4-1, 4+1) = (3,5) = f5")
print()
print("En passant target is set to: (2,3) = d6")
print()
print("For en passant, we need:")
print("  Left diagonal target to equal en passant target: (3,3) == (2,3)?", (3,3) == (2,3))
print("  Right diagonal target to equal en passant target: (3,5) == (2,3)?", (3,5) == (2,3))
print()
print("This shows why no en passant is detected!")
print("The en passant target should be where the pawn LANDS, not where it PASSES THROUGH.")
print()
print("For white e5 pawn to capture en passant:")
print("  It should land on d6 (2,3) or f6 (2,5)")
print("  But it moves to d5 (3,3) or f5 (3,5) to capture")
print("  So we need to check if the START of the capture move matches something...")
print()
print("Actually, let's re-read the code:")
print("  moves.append(Move((r, c), (r + moveAmount, c - 1), self.board, isEnpassantMove=True))")
print("  This creates a move FROM (r,c) TO (r+moveAmount, c-1)")
print("  And marks it as en passant if (r+moveAmount, c-1) == enpassantPossible")
print()
print("So enpassantPossible should be the DESTINATION square of the capture.")
print("For white e5 pawn capturing en passant to the left:")
print("  FROM: e5 (4,4)")
print("  TO: d6 (3,3)? No, that's not diagonal")
print("  TO: d6 would be (3,3) from (4,4) is (-1,-1) - that's diagonal but wrong direction?")
print()
print("Let's think about the board orientation:")
print("  Row 0 = rank 8 (top)")
print("  Row 7 = rank 1 (bottom)")
print("  White moves from higher row numbers to lower row numbers (up the board)")
print("  So white pawn move: (r, c) -> (r-1, c±1) for captures")
print()
print("White e5 pawn:")
print("  e5 = file e=4, rank 5")
print("  Rank 5 -> row = 8-5 = 3")
print("  So e5 = (3,4) NOT (4,4)! I had the coordinates wrong!")
print()
print("Let me recalculate with correct coordinates...")
