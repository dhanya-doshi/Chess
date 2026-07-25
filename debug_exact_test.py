import ChessEngine

print("=== Reproducing test_fixed.py en passant test exactly ===")

# Set up exactly like test_fixed.py
gs = ChessEngine.GameState()
# White e2e4
e2e4 = [m for m in gs.getValidMoves() if m.getChessNotation() == 'e2e4'][0]
print(f"White e2e4 move: {e2e4.getChessNotation()}")
gs.makeMove(e2e4)
print(f"After e2e4: black to move, en passant target = {gs.enpassantPossible}")

# Black plays a7a5
black_move1 = [m for m in gs.getValidMoves() if m.getChessNotation() == 'a7a5'][0]
print(f"Black a7a5 move: {black_move1.getChessNotation()}")
gs.makeMove(black_move1)
print(f"After a7a5: white to move, en passant target = {gs.enpassantPossible}")

# White e4e5
white_move = [m for m in gs.getValidMoves() if m.getChessNotation() == 'e4e5'][0]
print(f"White e4e5 move: {white_move.getChessNotation()}")
gs.makeMove(white_move)
print(f"After e4e5: black to move, en passant target = {gs.enpassantPossible}")

# Black d7d5 (the move that sets up en passant)
black_move2 = [m for m in gs.getValidMoves() if m.getChessNotation() == 'd7d5'][0]
print(f"Black d7d5 move: {black_move2.getChessNotation()}")
gs.makeMove(black_move2)
print(f"After d7d5: white to move, en passant target = {gs.enpassantPossible}")
print(f"En passant target log: {gs.enpassantPossibleLog}")

# Now white to move, en passant target should be at d6 (square black passed over)
# White pawn on e5 can capture to d6 via en passant
white_moves = gs.getValidMoves()
print(f"\nWhite has {len(white_moves)} legal moves:")
en_passant_found = None
for i, m in enumerate(white_moves):
    print(f"  {i+1:2d}. {m.getChessNotation()}", end="")
    if m.isEnpassantMove:
        print(" (EN PASSANT)", end="")
        en_passant_found = m
    print()

if en_passant_found is not None:
    print(f"\n✓ EN PASSANT FOUND: {en_passant_found.getChessNotation()}")
    print(f"  From: ({en_passant_found.startRow},{en_passant_found.startCol}) to ({en_passant_found.endRow},{en_passant_found.endCol})")
else:
    print("\n✗ NO EN PASSANT MOVE FOUND")
    print("Let's debug why...")

    # Let's manually check what should happen
    print("\n--- Manual debug ---")
    # Find white e5 pawn
    white_pawn_pos = None
    for r in range(8):
        for c in range(8):
            if gs.board[r][c] == 'wp':
                white_pawn_pos = (r, c)
                print(f"Found white pawn at {white_pawn_pos}")
                break
        if white_pawn_pos:
            break
    
    if white_pawn_pos:
        r, c = white_pawn_pos
        print(f"White pawn at ({r},{c})")
        print(f"  This is file {chr(ord('a')+c)} rank {8-r}")
        
        # Check what moves it thinks it can make
        moveAmount = -1  # white moves up
        print(f"  moveAmount = {moveAmount} (white moves up: decreasing row)")
        
        # Left diagonal
        print(f"  Left diagonal check:")
        target_r, target_c = r + moveAmount, c - 1
        print(f"    Target square: ({target_r}, {target_c}) = {chr(ord('a')+target_c)}{8-target_r}")
        if target_r >= 0 and target_r < 8 and target_c >= 0 and target_c < 8:
            target_piece = gs.board[target_r][target_c]
            print(f"    Piece at target: '{target_piece}'")
            if target_piece == "--":
                print(f"    -> Empty square")
                print(f"    -> Checking if ({target_r}, {target_c}) == enpassantPossible {gs.enpassantPossible}")
                is_match = (target_r, target_c) == gs.enpassantPossible
                if is_match:
                    print(f"    -> MATCH! This should be an en passant move")
                else:
                    print(f"    -> No match")
            elif target_piece != "--" and target_piece[0] == 'b':
                print(f"    -> Black piece! Normal capture possible")
            else:
                print(f"    -> White piece or off-board")
        else:
            print(f"    -> Target off board")
            
        # Right diagonal
        print(f"  Right diagonal check:")
        target_r, target_c = r + moveAmount, c + 1
        print(f"    Target square: ({target_r}, {target_c}) = {chr(ord('a')+target_c)}{8-target_r}")
        if target_r >= 0 and target_r < 8 and target_c >= 0 and target_c < 8:
            target_piece = gs.board[target_r][target_c]
            print(f"    Piece at target: '{target_piece}'")
            if target_piece == "--":
                print(f"    -> Empty square")
                print(f"    -> Checking if ({target_r}, {target_c}) == enpassantPossible {gs.enpassantPossible}")
                is_match = (target_r, target_c) == gs.enpassantPossible
                if is_match:
                    print(f"    -> MATCH! This should be an en passant move")
                else:
                    print(f"    -> No match")
            elif target_piece != "--" and target_piece[0] == 'b':
                print(f"    -> Black piece! Normal capture possible")
            else:
                print(f"    -> White piece or off-board")
        else:
            print(f"    -> Target off board")
    else:
        print("Could not find white pawn")

print("\n=== Let's also check the black pawn move that set up en passant ===")
# Find black d5 pawn
black_pawn_pos = None
for r in range(8):
    for c in range(8):
        if gs.board[r][c] == 'bp':
            if chr(ord('a')+c) == 'd' and 8-r == 5:  # d5
                black_pawn_pos = (r, c)
                break
    if black_pawn_pos:
        break

if black_pawn_pos:
    r, c = black_pawn_pos
    print(f"Black pawn at {black_pawn_pos} = {chr(ord('a')+c)}{8-r}")
    print(f"This came from d7: file d=3, rank 7 -> row=1 -> (1,3)")
    print(f"So it moved from (1,3) to ({r},{c})")
    print(f"The square it passed through is: ({ (1+r)//2 }, {c}) = ({ (1+3)//2 }, {3}) = ({2}, {3})")
    print(f"Which is {chr(ord('a')+3)}{8-2} = d6")
    print(f"Our enpassantPossible is set to: {gs.enpassantPossible}")
    print(f"So enpassantPossible SHOULD be {(2,3)} for the d6 square")
    print(f"Match: {gs.enpassantPossible == (2,3)}")
