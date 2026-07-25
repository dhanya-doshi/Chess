import ChessEngine

def test_basic_moves():
    """Test basic chess functionality"""
    print("Testing basic chess engine functionality...")

    # Initialize game state
    gs = ChessEngine.GameState()
    print("Initial board:")
    for row in gs.board:
        print(row)
    print()

    # Get initial valid moves
    validMoves = gs.getValidMoves()
    print(f"Number of valid moves for white: {len(validMoves)}")
    print("First few white moves:")
    for i, move in enumerate(validMoves[:5]):
        print(f"  {move.getChessNotation()}")
    print()

    # Test making a move (pawn to e4)
    e4_move = None
    for move in validMoves:
        if move.getChessNotation() == "e2e4":
            e4_move = move
            break

    if e4_move:
        print("Making move: e2e4")
        gs.makeMove(e4_move)
        print("Board after e2e4:")
        for row in gs.board:
            print(row)
        print()

        # Check if it's black's turn now
        print(f"White to move: {gs.whiteToMove}")
        print()

        # Get black's valid moves
        blackMoves = gs.getValidMoves()
        print(f"Number of valid moves for black: {len(blackMoves)}")
        print("First few black moves:")
        for i, move in enumerate(blackMoves[:5]):
            print(f"  {move.getChessNotation()}")
        print()

        # Test making a black move (pawn to e5)
        e5_move = None
        for move in blackMoves:
            if move.getChessNotation() == "e7e5":
                e5_move = move
                break

        if e5_move:
            print("Making move: e7e5")
            gs.makeMove(e5_move)
            print("Board after e7e5:")
            for row in gs.board:
                print(row)
            print()

            # Check if it's white's turn now
            print(f"White to move: {gs.whiteToMove}")
            print()

            # Test some basic validation
            whiteMoves = gs.getValidMoves()
            print(f"Number of valid moves for white after e4 e5: {len(whiteMoves)}")

            # Test if we can make an illegal move (should be prevented by validation logic in main)
            # Try to move a piece to its own square (should not be in valid moves)
            fake_move = ChessEngine.Move((6, 4), (6, 4), gs.board)  # e2 to e2
            is_valid = False
            for move in whiteMoves:
                if move == fake_move:
                    is_valid = True
                    break
            print(f"Is e2e2 a valid move? {is_valid} (should be False)")

            # Test moving opponent's piece (should not be in valid moves)
            fake_move2 = ChessEngine.Move((0, 4), (1, 4), gs.board)  # e7 to e6 (black pawn, but white to move)
            is_valid2 = False
            for move in whiteMoves:
                if move == fake_move2:
                    is_valid2 = True
                    break
            print(f"Is e7e6 (moving black pawn) a valid move for white? {is_valid2} (should be False)")
    else:
        print("Could not find e2e4 move in valid moves")
        print("Available moves:", [m.getChessNotation() for m in validMoves[:10]])

if __name__ == "__main__":
    test_basic_moves()