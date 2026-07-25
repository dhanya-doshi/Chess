import ChessEngine

print("=== Debugging En Passant ===")

# Test 1: Standard en passant scenario
print("\nTest 1: Standard e2e4 d7d5 scenario")
gs = ChessEngine.GameState()
print("Initial position:")
print("  White to move:", gs.whiteToMove)
print("  En passant target:", gs.enpassantPossible)

# White e2e4
print("\nWhite plays e2e4")
e2e4 = None
for m in gs.getValidMoves():
    if m.getChessNotation() == 'e2e4':
        e2e4 = m
        break
print("  Found e2e4 move:", e2e4 is not None)
if e2e4:
    gs.makeMove(e2e4)
    print("  After e2e4:")
    print("    White to move:", gs.whiteToMove)
    print("    En passant target:", gs.enpassantPossible)
    print("    Board state:")
    for i in range(8):
        row_str = ""
        for j in range(8):
            row_str += gs.board[i][j] + " "
        print(f"    Rank {8-i}: {row_str}")

# Black d7d5
print("\nBlack plays d7d5")
black_move = None
for m in gs.getValidMoves():
    if m.getChessNotation() == 'd7d5':
        black_move = m
        break
print("  Found d7d5 move:", black_move is not None)
if black_move:
    gs.makeMove(black_move)
    print("  After d7d5:")
    print("    White to move:", gs.whiteToMove)
    print("    En passant target:", gs.enpassantPossible)
    print("    Board state:")
    for i in range(8):
        row_str = ""
        for j in range(8):
            row_str += gs.board[i][j] + " "
        print(f"    Rank {8-i}: {row_str}")

# Check white moves for en passant
print("\nWhite to move - checking for en passant captures:")
white_moves = gs.getValidMoves()
print(f"  Total white moves: {len(white_moves)}")
en_passant_moves = []
for m in white_moves:
    if m.isEnpassantMove:
        en_passant_moves.append(m)
        print(f"    En passant: {m.getChessNotation()}")

if en_passant_moves:
    print("  EN PASSANT MOVES FOUND!")
else:
    print("  NO EN PASSANT MOVES FOUND")
    print("  First 10 white moves:")
    for i, m in enumerate(white_moves[:10]):
        print(f"    {m.getChessNotation()}", end="")
        if m.isEnpassantMove:
            print(" (en passant)", end="")
        print()

# Test 2: Direct setup from test_fixed.py
print("\n\nTest 2: Direct setup from test_fixed.py")
gs2 = ChessEngine.GameState()
# Clear board
for i in range(8):
    for j in range(8):
        gs2.board[i][j] = '--'
gs2.whiteToMove = True
gs2.board[3][3] = 'bp'  # black d5
gs2.board[4][4] = 'wp'  # white e5
# Add kings
gs2.board[7][4] = 'wk'
gs2.board[0][3] = 'bk'

print("Board setup:")
print("  Black pawn on d5 (3,3)")
print("  White pawn on e5 (4,4)")
print("  White to move:", gs2.whiteToMove)

# But we need to set up the enpassantPossible correctly for this scenario
# For en passant to be possible, the black pawn must have just moved two squares
# So we need to simulate that it came from d7
gs2.enpassantPossible = ((1+3)//2, 3)  # (2,3) - d6
gs2.enpassantPossibleLog = [(), (), gs2.enpassantPossible]  # dummy log

print("  Manually set enpassantPossible:", gs2.enpassantPossible)

white_moves2 = gs2.getValidMoves()
print(f"  Total white moves: {len(white_moves2)}")
en_passant_moves2 = []
for m in white_moves2:
    if m.isEnpassantMove:
        en_passant_moves2.append(m)
        print(f"    En passant: {m.getChessNotation()}")

if en_passant_moves2:
    print("  EN PASSANT MOVES FOUND in test 2!")
else:
    print("  NO EN PASSANT MOVES in test 2")