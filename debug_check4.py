import ChessEngine as chess_engine

gs = chess_engine.GameState()
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

print("Initial state:")
print(f"  whiteToMove: {gs.whiteToMove}")
print(f"  Queen at (6,0): {gs.board[6][0]}")
print(f"  King at (7,4): {gs.board[7][4]}")

# Manually test the condition in getAllPossibleMoves for the queen position
r, c = 6, 0
piece = gs.board[r][c]
print(f"\nChecking square ({r},{c}):")
print(f"  piece: '{piece}'")
if piece != '--':
    print(f"  piece[0]: '{piece[0]}'")
    print(f"  whiteToMove: {gs.whiteToMove}")
    condition = (piece[0] == 'w' and gs.whiteToMove) or (piece[0] == 'b' and not gs.whiteToMove)
    print(f"  (piece[0] == 'w' and whiteToMove): {(piece[0] == 'w' and gs.whiteToMove)}")
    print(f"  (piece[0] == 'b' and not whiteToMove): {(piece[0] == 'b' and not gs.whiteToMove)}")
    print(f"  Overall condition: {condition}")

# Now let's manually call getQueenMoves and see what happens
print("\nCalling getQueenMoves(6, 0, []):")
moves = []
print(f"  Before: moves = {moves}")
gs.getQueenMoves(6, 0, moves)
print(f"  After: moves = {moves}")
print(f"  Number of moves: {len(moves)}")
if len(moves) > 0:
    for i, m in enumerate(moves[:5]):
        print(f"    {i+1}. {m.getChessNotation()}")

# Let's also check if there are any pins that might be blocking moves
print("\nChecking for pins:")
print(f"  self.pins: {gs.pins}")

# And check if the king is in check currently (should be False since it's white's turn and we haven't moved yet)
print(f"\nIs white in check? {gs.inCheck()}")
print(f"Is black in check? {not gs.whiteToMove and gs.inCheck()}")  # This is wrong, let me think
# Actually, whiteToMove indicates whose turn it is
# So if whiteToMove = True, it's white's turn, we check if white is in check
# If whiteToMove = False, it's black's turn, we check if black is in check
print(f"Is current player in check? {gs.inCheck()}")
print(f"  (whiteToMove={gs.whiteToMove}, so checking if {'white' if gs.whiteToMove else 'black'} is in check)")
