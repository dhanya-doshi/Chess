import ChessEngine
import ChessMain
import time

def test_ai_game():
    print("=== AI vs AI game test (few plies) ===")
    gs = ChessEngine.GameState()
    max_ply = 10  # half-moves
    for ply in range(max_ply):
        if gs.checkmate or gs.stalemate or getattr(gs, 'draw', False):
            print(f"Game over at ply {ply}: checkmate={gs.checkmate}, stalemate={gs.stalemate}, draw={getattr(gs, 'draw', False)}")
            break
        # Determine which side is AI: we'll make both sides AI with same elo for simplicity
        move = ChessMain.getAIMove(gs, 1200)
        if move is None:
            print("AI returned no move")
            break
        print(f"Ply {ply}: {move.getChessNotation()} (white to move? {gs.whiteToMove})")
        gs.makeMove(move)
        # Optional: print board
        # for row in gs.board:
        #     print(' '.join(r if r != '--' else '.' for r in row))
        # print()
    print("AI game test completed")

if __name__ == '__main__':
    try:
        test_ai_game()
        print("🎉 AI game test passed")
    except Exception as e:
        print(f"❌ AI game test failed: {e}")
        import traceback
        traceback.print_exc()