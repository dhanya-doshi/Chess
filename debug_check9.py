import ChessEngine as chess_engine

gs = chess_engine.GameState()
# Set up a simple test: just a white queen on a2
for i in range(8):
    for j in range(8):
        gs.board[i][j] = '--'
gs.whiteToMove = True
gs.board[6][0] = 'wq'  # white queen on a2 (row 6, col 0)

print(f"Self.pins: {gs.pins}")
print(f"Length of self.pins: {len(gs.pins)}")

# Let's manually step through getQueenMoves for the queen at (6,0)
print("\n=== Manual walkthrough of getQueenMoves(6, 0, []) ===")
r, c = 6, 0
print(f"Calling getRookMoves({r}, {c}, [])")
print(f"  self.pins before: {gs.pins}")
# We can't easily call the actual methods without modifying the source,
# but we can check what would happen

print("\nFor comparison, let's see what happens if we call the methods directly on an empty board with no pieces:")
gs2 = chess_engine.GameState()
print(f"  Fresh game state self.pins: {gs2.pins}")
# The initial position has pieces, so let's make a truly empty board
gs2.board = [['--' for _ in range(8)] for _ in range(8)]
print(f"  Empty board self.pins: {gs2.pins}")
print(f"  All squares empty: {all(gs2.board[r][c] == '--' for r in range(8) for c in range(8))}")
