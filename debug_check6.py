import ChessEngine as chess_engine

gs = chess_engine.GameState()
# Set up a simple test: just a white queen on a2
for i in range(8):
    for j in range(8):
        gs.board[i][j] = '--'
gs.whiteToMove = True
gs.board[6][0] = 'wq'  # white queen on a2 (row 6, col 0)

print("=== Debugging piece detection ===")
print("Board state:")
for i in range(8):
    rank = 8 - i
    row_str = [gs.board[i][j] for j in range(8)]
    print(f"Rank {rank}: {' '.join(row_str)}")

print(f"\nwhiteToMove: {gs.whiteToMove}")

print("\nChecking each square:")
for i in range(8):
    for j in range(8):
        piece = gs.board[i][j]
        if piece != '--':
            color = piece[0] if len(piece) > 0 else '?'
            piece_type = piece[1] if len(piece) > 1 else '?'
            is_white = (color == 'w')
            is_black = (color == 'b')
            should_process = (is_white and gs.whiteToMove) or (is_black and not gs.whiteToMove)
            print(f"  [{i},{j}] {piece}: color='{color}', type='{piece_type}'")
            print(f"    is_white={is_white}, is_black={is_black}")
            print(f"    whiteToMove={gs.whiteToMove}")
            print(f"    (white and whiteToMove)={(is_white and gs.whiteToMove)}")
            print(f"    (black and not whiteToMove)={(is_black and not gs.whiteToMove)}")
            print(f"    SHOULD PROCESS: {should_process}")

print("\n=== Now calling getAllPossibleMoves ===")
moves = gs.getAllPossibleMoves()
print(f"Got {len(moves)} moves")
if len(moves) > 0:
    for i, m in enumerate(moves[:10]):
        print(f"  {i+1}. {m.getChessNotation()}")
else:
    print("No moves generated")

# Let's also manually test what happens if we call getQueenMoves directly
print("\n=== Testing getQueenMoves directly ===")
test_moves = []
print(f"Before: {len(test_moves)} moves")
gs.getQueenMoves(6, 0, test_moves)
print(f"After: {len(test_moves)} moves")
if len(test_moves) > 0:
    print("First few queen moves:")
    for i, m in enumerate(test_moves[:5]):
        print(f"  {i+1}. {m.getChessNotation()}")
