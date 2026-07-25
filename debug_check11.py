import ChessEngine as chess_engine

# Exact setup from the failing test
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

print("=== Test position from failing unit test ===")
print("Board:")
for i in range(8):
    rank = 8 - i
    row_str = [gs.board[i][j] for j in range(8)]
    print(f"Rank {rank}: {' '.join(row_str)}")

print(f"\nwhiteToMove: {gs.whiteToMove} (False means black to move)")

# Let's debug what happens when we call getAllPossibleMoves
print("\n=== Debugging getAllPossibleMoves ===")
# We'll manually walk through the logic

print("Checking each piece:")

# White pieces
white_pieces = []
for i in range(8):
    for j in range(8):
        piece = gs.board[i][j]
        if piece != '--' and piece[0] == 'w':
            white_pieces.append(((i, j), piece))

print(f"White pieces: {white_pieces}")

# Black pieces
black_pieces = []
for i in range(8):
    for j in range(8):
        piece = gs.board[i][j]
        if piece != '--' and piece[0] == 'b':
            black_pieces.append(((i, j), piece))

print(f"Black pieces: {black_pieces}")

print(f"\nSince whiteToMove = {gs.whiteToMove}, we should generate moves for:")
if gs.whiteToMove:
    print("  WHITE pieces")
    relevant_pieces = white_pieces
else:
    print("  BLACK pieces")
    relevant_pieces = black_pieces

print(f"Relevant pieces: {relevant_pieces}")

# Now let's see what happens when we try to generate moves for these pieces
print("\n=== Testing move generation for each relevant piece ===")
all_moves = []

for (r, c), piece in relevant_pieces:
    piece_type = piece[1]
    print(f"\nProcessing {piece} at ({r},{c}):")
    moves_before = len(all_moves)
    
    if piece_type == 'p':
        print("  Calling getPawnMoves")
        gs.getPawnMoves(r, c, all_moves)
    elif piece_type == 'R':
        print("  Calling getRookMoves")
        gs.getRookMoves(r, c, all_moves)
    elif piece_type == 'N':
        print("  Calling getKnightMoves")
        gs.getKnightMoves(r, c, all_moves)
    elif piece_type == 'B':
        print("  Calling getBishopMoves")
        gs.getBishopMoves(r, c, all_moves)
    elif piece_type == 'Q':
        print("  Calling getQueenMoves")
        gs.getQueenMoves(r, c, all_moves)
    elif piece_type == 'K':
        print("  Calling getKingMoves")
        gs.getKingMoves(r, c, all_moves)
    
    moves_after = len(all_moves)
    print(f"  Added {moves_after - moves_before} moves (total now: {len(all_moves)})")

print(f"\nTotal moves generated: {len(all_moves)}")
if len(all_moves) > 0:
    print("First 10 moves:")
    for i, m in enumerate(all_moves[:10]):
        print(f"  {i+1}. {m.getChessNotation()}")

# Now let's see what the actual getAllPossibleMoves returns
print("\n=== Calling actual getAllPossibleMoves ===")
actual_moves = gs.getAllPossibleMoves()
print(f"Actual getAllPossibleMoves returned: {len(actual_moves)} moves")
if len(actual_moves) > 0:
    print("First 10 moves:")
    for i, m in enumerate(actual_moves[:10]):
        print(f"  {i+1}. {m.getChessNotation()}")
else:
    print("  No moves!")

# The key test: is the black king in check?
print(f"\n=== Check detection ===")
print(f"Black king position: {gs.blackKingLocation}")
print(f"Is black in check? {gs.inCheck()}")
print(f"(This calls gs.inCheck() which should return True if black king is under attack)")

# Let's also manually verify if the white queen attacks the black king
print(f"\n=== Manual verification ===")
print(f"White queen at: (6, 0)")
print(f"Black king at: (0, 0)")
print(f"Same file? {0 == 0} (both file a)")
print(f"Same rank? {6 == 0} (rank 2 vs rank 8)")
print(f"Same diagonal? {abs(6-0) == abs(0-0)} -> {6 == 0} -> False")
print(f"Wait, that's not right. Let me recalculate:")
print(f"  Queen: row=6, col=0")
print(f"  King: row=0, col=0")
print(f"  Row diff: {abs(6-0)} = 6")
print(f"  Col diff: {abs(0-0)} = 0")
print(f"  Same file: col equal? {0 == 0} -> True")
print(f"  Same rank: row equal? {6 == 0} -> False")
print(f"  Same diagonal: abs(row_diff) == abs(col_diff)? {abs(6-0)} == {abs(0-0)} -> {6} == {0} -> False")
print(f"  Actually, for rook movement: same file OR same rank")
print(f"  For bishop movement: abs(row_diff) == abs(col_diff)")
print(f"  Queen can move like rook OR bishop")
print(f"  So queen can attack if: (same file) OR (same rank) OR (same diagonal)")
print(f"  Here: same file = True, same rank = False, same diagonal = False")
print(f"  Therefore: Queen CAN attack the king (same file)!")

print(f"\nThe path from queen (6,0) to king (0,0) is:")
print(f"  (6,0) -> (5,0) -> (4,0) -> (3,0) -> (2,0) -> (1,0) -> (0,0)")
print(f"Let's check if any pieces are blocking:")

blocked = False
for row in range(5, 0, -1):  # rows 5,4,3,2,1
    piece = gs.board[row][0]
    print(f"  Checking ({row},0): '{piece}'")
    if piece != '--':
        print(f"    BLOCKED by {piece}!")
        blocked = True
        break

if not blocked:
    print(f"  Path is clear - queen CAN attack king!")
else:
    print(f"  Path is blocked - queen CANNOT attack king!")
