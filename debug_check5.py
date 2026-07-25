import ChessEngine as chess_engine
import inspect

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

print("=== Testing getAllPossibleMoves ===")
print(f"Initial whiteToMove: {gs.whiteToMove}")

# Check the signature
sig = inspect.signature(gs.getAllPossibleMoves)
print(f"getAllOperations signature: {sig}")

# Test 1: Black to move (should get black's pieces)
print("\n--- Test 1: Black to move ---")
gs.whiteToMove = False
print(f"  whiteToMove = {gs.whiteToMove} (black to move)")
moves = gs.getAllPossibleMoves()  # It returns a list
print(f"  Got {len(moves)} moves")
if len(moves) > 0:
    print("  First few moves:")
    for i, m in enumerate(moves[:5]):
        print(f"    {i+1}. {m.getChessNotation()} ({m.pieceMoved})")
else:
    print("  No moves found - let's check what black pieces exist:")
    black_pieces = []
    for i in range(8):
        for j in range(8):
            piece = gs.board[i][j]
            if piece != '--' and piece[0] == 'b':
                black_pieces.append((piece, i, j))
    print(f"    Black pieces: {black_pieces}")

# Test 2: White to move (should get white's pieces)
print("\n--- Test 2: White to move ---")
gs.whiteToMove = True
print(f"  whiteToMove = {gs.whiteToMove} (white to move)")
moves = gs.getAllPossibleMoves()
print(f"  Got {len(moves)} moves")
if len(moves) > 0:
    print("  First few moves:")
    for i, m in enumerate(moves[:5]):
        print(f"    {i+1}. {m.getChessNotation()} ({m.pieceMoved})")
else:
    print("  No moves found!")

print("\n=== Done ===")
