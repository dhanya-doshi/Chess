import ChessEngine

gs = ChessEngine.GameState()
# White e2e4
e2e4 = None
for m in gs.getValidMoves():
    if m.getChessNotation() == 'e2e4':
        e2e4 = m
        break
print("White e2e4 move:", e2e4.getChessNotation() if e2e4 else "None")
gs.makeMove(e2e4)
print("After e2e4, black to move")
print("En passant target:", gs.enpassantPossible)
# Black d7d5
black_moves = gs.getValidMoves()
black_move = None
for m in black_moves:
    if m.getChessNotation() == 'd7d5':
        black_move = m
        break
print("Black d7d5 move:", black_move.getChessNotation() if black_move else "None")
if black_move:
    gs.makeMove(black_move)
    print("After d7d5, white to move")
    print("En passant target:", gs.enpassantPossible)
    white_moves = gs.getValidMoves()
    print("White moves count:", len(white_moves))
    en_passant = None
    for m in white_moves:
        if m.getChessNotation() == 'e5d6' and m.isEnpassantMove:
            en_passant = m
            break
    print("En passant capture e5d6:", en_passant.getChessNotation() if en_passant else "None")
    # Also print a few white moves to see what's available
    print("First 10 white moves:")
    for i, m in enumerate(white_moves[:10]):
        print(f"  {m.getChessNotation()}", end="")
        if m.isEnpassantMove:
            print(" (en passant)", end="")
        print()
else:
    print("Black d7d5 not found")