import ChessEngine as chess_engine

# Let's create a debugging version by copying more of the logic
def debug_getAllPossibleMoves(gs):
    print("=== DEBUG getAllPossibleMoves ===")
    moves = []
    print(f"Board dimensions: {len(gs.board)} x {len(gs.board[0]) if len(gs.board) > 0 else 0}")
    print(f"whiteToMove: {gs.whiteToMove}")
    
    count_checked = 0
    count_pieces = 0
    count_to_process = 0
    
    for r in range(len(gs.board)):  # number of rows
        for c in range(len(gs.board[r])):  # number of columns
            count_checked += 1
            square_contents = gs.board[r][c]
            if square_contents == "--":
                continue  # Skip empty squares for cleaner output
            
            count_pieces += 1
            print(f"  [{r},{c}] contains '{square_contents}'")
            
            # This is the critical line from the original code
            if len(square_contents) > 0:
                turn = square_contents[0]
                print(f"    first char: '{turn}'")
                
                # The condition from the original code
                white_condition = (turn == 'w' and gs.whiteToMove)
                black_condition = (turn == 'b' and not gs.whiteToMove)
                should_process = white_condition or black_condition
                
                print(f"    white_condition: ({turn} == 'w' and {gs.whiteToMove}) = {white_condition}")
                print(f"    black_condition: ({turn} == 'b' and not {gs.whiteToMove}) = {black_condition}")
                print(f"    should_process: {should_process}")
                
                if should_process:
                    count_to_process += 1
                    piece = square_contents[1] if len(square_contents) > 1 else '?'
                    print(f"    >>> PROCESSING: {piece} at [{r},{c}]")
                    
                    # Now simulate what the original code does
                    print(f"    Calling get{piece.upper()}Moves({r}, {c}, moves)")
                    if piece == 'p':
                        print("    -> Would call getPawnMoves")
                    elif piece == 'R':
                        print("    -> Would call getRookMoves")
                    elif piece == 'N':
                        print("    -> Would call getKnightMoves")
                    elif piece == 'B':
                        print("    -> Would call getBishopMoves")
                    elif piece == 'Q':
                        print("    -> Calling getQueenMoves")
                        before_len = len(moves)
                        gs.getQueenMoves(r, c, moves)
                        after_len = len(moves)
                        print(f"    -> getQueenMoves added {after_len - before_len} moves")
                        print(f"    -> Total moves now: {len(moves)}")
                    elif piece == 'K':
                        print("    -> Would call getKingMoves")
                else:
                    print(f"    >>> SKIPPED")
            else:
                print(f"    WARNING: empty string at [{r},{c}]")
    
    print(f"\nSummary:")
    print(f"  Total squares checked: {count_checked}")
    print(f"  Squares with pieces: {count_pieces}")
    print(f"  Squares that should be processed: {count_to_process}")
    print(f"  Actual moves generated: {len(moves)}")
    
    return moves

# Test it
gs = chess_engine.GameState()
# Set up a simple test: just a white queen on a2
for i in range(8):
    for j in range(8):
        gs.board[i][j] = '--'
gs.whiteToMove = True
gs.board[6][0] = 'wq'  # white queen on a2 (row 6, col 0)

print("Test position:")
for i in range(8):
    rank = 8 - i
    row_str = [gs.board[i][j] for j in range(8)]
    print(f"Rank {rank}: {' '.join(row_str)}")

print()
moves = debug_getAllPossibleMoves(gs)
print(f"\nReturned {len(moves)} moves")
if len(moves) > 0:
    for i, m in enumerate(moves[:5]):
        print(f"  {i+1}. {m.getChessNotation()}")
