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

print("Pieces on board:")
for i in range(8):
    for j in range(8):
        piece = gs.board[i][j]
        if piece != '--':
            print(f"  {piece} at ({i},{j}) which is {chr(ord('a')+j)}{8-i}")

print(f"\nWhite to move: {gs.whiteToMove}")

# Let's manually test what happens in getAllPossibleMoves when whiteToMove = True
print("\n=== Testing getAllPossibleMoves with white to move ===")
gs.whiteToMove = True
print(f"After setting whiteToMove = {gs.whiteToMove}")

# Check what pieces white has
white_pieces = []
for i in range(8):
    for j in range(8):
        piece = gs.board[i][j]
        if piece != '--' and piece[0] == 'w':
            white_pieces.append((piece, i, j))
            
print(f"White pieces: {white_pieces}")

# Now get all possible moves
moves = gs.getAllPossibleMoves()
print(f"Number of white moves: {len(moves)}")
if len(moves) > 0:
    print("First 10 white moves:")
    for i, m in enumerate(moves[:10]):
        print(f"  {m.getChessNotation()} ({m.pieceMoved})")
else:
    print("No white moves found! Let's debug why...")

# Let's manually check what the getPawnMoves etc functions would do for the queen
print("\nChecking what getQueenMoves would do for queen at (6,0):")
# We need to be in white's turn for this
original_turn = gs.whiteToMove
gs.whiteToMove = True
# Let's manually call the logic that would be in getAllPossibleMoves
# For each white piece, call the appropriate move function
from collections import defaultdict
pieces_found = []
for i in range(8):
    for j in range(8):
        piece = gs.board[i][j]
        if piece != '--' and piece[0] == 'w':
            pieces_found.append((piece, i, j))
            piece_type = piece[1]
            print(f"Found white {piece_type} at ({i},{j})")
            if piece_type == 'Q':
                print("  Would call getQueenMoves")
            elif piece_type == 'K':
                print("  Would call getKingMoves")
gs.whiteToMove = original_turn

print(f"\nPieces found: {pieces_found}")
