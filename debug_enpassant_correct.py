import ChessEngine

print("Testing En Passant Scenario: e4 e5 exd6")
print("=" * 40)

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
print()

# Black e7e5
black_moves = gs.getValidMoves()
black_move = None
for m in black_moves:
    if m.getChessNotation() == 'e7e5':
        black_move = m
        break
print("Black e7e5 move:", black_move.getChessNotation() if black_move else "None")
if black_move:
    gs.makeMove(black_move)
    print("After e7e5, white to move")
    print("En passant target:", gs.enpassantPossible)
    print()

    white_moves = gs.getValidMoves()
    print("White moves count:", len(white_moves))
    en_passant = None
    for m in white_moves:
        if m.getChessNotation() == 'e4d5' and m.isEnpassantMove:
            en_passant = m
            break
    print("En passant capture e4d5:", en_passant.getChessNotation() if en_passant else "None")

    # Also show en passant captures specifically
    print("\nAll en passant captures available:")
    for m in white_moves:
        if m.isEnpassantMove:
            print(f"  {m.getChessNotation()}")

    if en_passant:
        print("\nMaking en passant capture e4d5...")
        gs.makeMove(en_passant)
        print("After exd6, black to move")
        print("En passant target:", gs.enpassantPossible)
        print("Board:")
        for row in gs.board:
            print(row)
    else:
        print("\nNo en passant capture available!")
else:
    print("Black e7e5 not found")