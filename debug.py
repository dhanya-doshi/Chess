import ChessEngine

gs = ChessEngine.GameState()
# Clear board
for i in range(8):
    for j in range(8):
        gs.board[i][j] = '--'
gs.whiteToMove = False  # black to move, but we will check if black king is in check by white
# Place white queen at a2 (row 6, col 0)
gs.board[6][0] = 'wq'
# Place black king at a8 (row 0, col 0)
gs.board[0][0] = 'bk'
# Place white king at e1 (row 7, col 4) to avoid being captured
gs.board[7][4] = 'wk'

print("Board:")
for i in range(8):
    row = []
    for j in range(8):
        row.append(gs.board[i][j])
    print(f"{8-i} {' '.join(row)}")
print("   a b c d e f g h")
print()

print(f"White to move: {gs.whiteToMove}")
print(f"Black king location: {gs.blackKingLocation}")
print(f"White queen location: {(6,0)}")
print()

# Now, let's see what happens when we call inCheck for black
print("Checking if black king is in check...")
in_check = gs.inCheck()
print(f"Black king in check? {in_check}")

# Let's also manually compute the opponent (white) moves
print("\nGenerating white moves (since black to move, opponent is white):")
# Temporarily flip whiteToMove to generate white moves
original_turn = gs.whiteToMove
gs.whiteToMove = True  # now white to move
white_moves = gs.getAllPossibleMoves()
gs.whiteToMove = original_turn
print(f"Number of white moves: {len(white_moves)}")
print("White moves:")
for i, move in enumerate(white_moves):
    print(f"  {i}: {move.getChessNotation()} (from ({move.startRow},{move.startCol}) to ({move.endRow},{move.endCol}))")
    if move.startRow == 6 and move.startCol == 0 and move.endRow == 0 and move.endCol == 0:
        print("    ^ This is the queen move from a2 to a8!")

# Let's also specifically call getQueenMoves for the queen at (6,0)
print("\nCalling getQueenMoves directly for queen at (6,0):")
queen_moves = []
gs.getQueenMoves(6, 0, queen_moves)
print(f"Number of queen moves: {len(queen_moves)}")
for move in queen_moves:
    print(f"  {move.getChessNotation()} (from ({move.startRow},{move.startCol}) to ({move.endRow},{move.endCol}))")
    if move.endRow == 0 and move.endCol == 0:
        print("    ^ This is the queen move to a8!")

# Let's also check what the rook moves are for the queen (since queen includes rook)
print("\nCalling getRookMoves directly for queen at (6,0):")
rook_moves = []
gs.getRookMoves(6, 0, rook_moves)
print(f"Number of rook moves: {len(rook_moves)}")
for move in rook_moves:
    print(f"  {move.getChessNotation()} (from ({move.startRow},{move.startCol}) to ({move.endRow},{move.endCol}))")
    if move.endRow == 0 and move.endCol == 0:
        print("    ^ This is the rook move to a8!")

# Let's check the pins array
print(f"\nPins: {gs.pins}")
print(f"Pin count: {len(gs.pins)}")
