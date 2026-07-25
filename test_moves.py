import ChessEngine
gs = ChessEngine.GameState()
moves = gs.getValidMoves()
print('Number of moves:', len(moves))
for m in moves[:10]:
    print(m.getChessNotation())
