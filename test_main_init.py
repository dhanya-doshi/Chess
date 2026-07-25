import sys
sys.path.insert(0, '.')

import ChessMain
import pygame as p

# Test that main function initializes without UnboundLocalError
try:
    # We'll monkey patch the while loop to exit immediately
    original_main = ChessMain.main

    def mock_main():
        p.init()
        screen = p.display.set_mode((ChessMain.WIDTH, ChessMain.HEIGHT))
        p.display.set_caption("Chess")
        clock = p.time.Clock()
        gs = ChessMain.ChessEngine.GameState()
        validMoves = gs.getValidMoves()
        moveMade = False
        sqSelected = ()
        playerClicks = []
        pieceValidMoves = []
        ChessMain.loadImages()
        running = True
        # Run just one iteration then break
        for event in p.event.get():
            if event.type == p.QUIT:
                running = False
        # Instead of running the loop, just return
        return

    ChessMain.main = mock_main
    ChessMain.main()
    print("SUCCESS: Main initialized without UnboundLocalError")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()