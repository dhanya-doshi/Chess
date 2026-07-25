import ChessEngine

gs = ChessEngine.GameState()
moves = gs.getValidMoves()
print(f"Number of valid moves: {len(moves)}")
for i, move in enumerate(moves):
    print(f"{i+1}: {move.getChessNotation()}")