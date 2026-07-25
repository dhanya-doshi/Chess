import ChessEngine

gs = ChessEngine.GameState()
# Set up a simple check: white queen on a2, black king on a8, black to move
for i in range(8):
    for j in range(8):
        gs.board[i][j] = '--'
gs.whiteToMove = True
gs.board[6][0] = 'wq'  # white queen on a2 (row 6, col 0)
gs.board[0][0] = 'bk'  # black king on a8 (row 0, col 0)
# Add white king somewhere safe
gs.board[7][4] = 'wk'
# Now it's white to move; we want to test black in check, so switch turn
gs.whiteToMove = False  # black to move

print("Board state:")
for i in range(8):
    rank = 8 - i
    row_str = []
    for j in range(8):
        row_str.append(gs.board[i][j])
    print(f"Rank {rank}: {' '.join(row_str)}")

print(f"\nWhite to move: {gs.whiteToMove}")
# Find king and queen positions
bk_pos = None
wq_pos = None
wk_pos = None
for i in range(8):
    for j in range(8):
        if gs.board[i][j] == 'bk':
            bk_pos = (i, j)
        elif gs.board[i][j] == 'wq':
            wq_pos = (i, j)
        elif gs.board[i][j] == 'wk':
            wk_pos = (i, j)
            
print(f"Black king location: {bk_pos}")
print(f"White queen location: {wq_pos}")
print(f"White king location: {wk_pos}")

# Check if black king is in check
print(f"\nBlack king in check according to inCheck(): {gs.inCheck()}")

# Let's manually check if the square is under attack
print("\nChecking if a8 (0,0) is under attack by white pieces:")
# Temporarily set whiteToMove to True to get white's moves
original_turn = gs.whiteToMove
gs.whiteToMove = True
white_moves = gs.getAllPossibleMoves()
gs.whiteToMove = original_turn

print(f"White has {len(white_moves)} possible moves")
if len(white_moves) > 0:
    print("First few white moves:")
    for i, m in enumerate(white_moves[:5]):
        print(f"  {m.getChessNotation()}")
else:
    print("White has no moves!")

attacking_moves = [m for m in white_moves if m.endRow == 0 and m.endCol == 0]
print(f"White moves that attack a8 (0,0): {len(attacking_moves)}")
for m in attacking_moves:
    print(f"  {m.getChessNotation()} from ({m.startRow},{m.startCol}) to ({m.endRow},{m.endCol})")

# Let's also test the squareUnderAttack method directly
print(f"\nTesting squareUnderAttack(0, 0):")
# We need to set whiteToMove = True for this test since we're checking if white attacks the square
original_turn = gs.whiteToMove
gs.whiteToMove = True  # white to move, so we can see if white attacks the black king
result = gs.squareUnderAttack(0, 0)
gs.whiteToMove = original_turn  # restore
print(f"squareUnderAttack(0, 0) with white to move: {result}")
