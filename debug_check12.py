import ChessEngine as ce

print("=== Reproducing the exact check detection test scenario ===")

# This is exactly what test_check_detection does:
gs = ce.GameState()
# Set up a simple check: white queen on a2, black king on a8, black to move
for i in range(8):
    for j in range(8):
        gs.board[i][j] = '--'
gs.whiteToMove = True
gs.board[6][0] = 'wq'  # white queen on a2 (row 6, col 0)
gs.board[0][0] = 'bk'  # black king on a8 (row 0, col 0)
# Add white king somewhere safe
gs.board[7][4] = 'wk'
# Now it's white to move; we want to test black in check, so switch turn
gs.whiteToMove = False  # black to move

print("Board state:")
for i in range(8):
    rank = 8 - i
    row_str = [gs.board[i][j] for j in range(8)]
    print(f"Rank {rank}: {' '.join(row_str)}")

print(f"\nWhite to move: {gs.whiteToMove}")
print(f"Black king location: {gs.blackKingLocation}")

# This is the exact line that's failing:
print(f"\nCalling gs.inCheck()...")
result = gs.inCheck()
print(f"Result: {result}")
print(f"Expected: True")
print(f"Test passes: {result == True}")

if not result:
    print("\nDEBUGGING WHY inCheck() RETURNS FALSE:")
    print("  inCheck() does:")
    print("    1. If whiteToMove: return squareUnderAttack(whiteKingLocation)")
    print("    2. Else: return squareUnderAttack(blackKingLocation)")
    print(f"  Since whiteToMove = {gs.whiteToMove}, we check black king")
    print(f"  Black king location: {gs.blackKingLocation}")
    print(f"  So we call squareUnderAttack({gs.blackKingLocation[0]}, {gs.blackKingLocation[1]})")
    
    # Let's trace through squareUnderAttack
    print(f"\n  Testing squareUnderAttack({gs.blackKingLocation[0]}, {gs.blackKingLocation[1]}):")
    print(f"    This method:")
    print(f"      1. Saves current whiteToMove ({gs.whiteToMove})")
    print(f"      2. Sets whiteToMove = NOT whiteToMove (to get opponent's turn)")
    print(f"      3. Calls getAllPossibleMoves() to get opponent's moves")
    print(f"      4. Checks if any of those moves end at the target square")
    print(f"      5. Restores original whiteToMove")
    print(f"      6. Returns True if target is under attack, False otherwise")
    
    # Let's manually execute this logic
    original_turn = gs.whiteToMove
    print(f"\n    Step 1: original_turn = {original_turn}")
    gs.whiteToMove = not gs.whiteToMove
    print(f"    Step 2: whiteToFlip = {gs.whiteToMove} (this is whose moves we're generating)")
    
    print(f"    Step 3: Calling getAllPossibleMoves()")
    opponent_moves = gs.getAllPossibleMoves()
    print(f"      Got {len(opponent_moves)} moves from opponent")
    
    if len(opponent_moves) > 0:
        print(f"      First few opponent moves:")
        for i, m in enumerate(opponent_moves[:5]):
            try:
                print(f"        {i+1}. {m.getChessNotation()}")
            except:
                print(f"        {i+1}. [ERROR]")
        
        print(f"    Step 4: Checking if any move ends at black king position {gs.blackKingLocation}")
        target_r, target_c = gs.blackKingLocation
        attacking_moves = []
        for m in opponent_moves:
            if m.endRow == target_r and m.endCol == target_c:
                attacking_moves.append(m)
        print(f"      Found {len(attacking_moves)} attacking moves")
        if len(attacking_moves) > 0:
            print(f"      First attacking move:")
            try:
                print(f"        {attacking_moves[0].getChessNotation()}")
            except:
                print(f"        [ERROR printing move]")
    else:
        print(f"      No opponent moves to check!")
    
    gs.whiteToMove = original_turn
    print(f"    Step 5: Restored whiteToMove = {gs.whiteToMove}")
    
    print(f"\n    CONCLUSION: squareUnderAttack should return {len(attacking_moves) > 0}")
    
    # Let's also check if the king is actually in check by manual inspection
    print(f"\n  MANUAL VERIFICATION:")
    print(f"    White queen at: a2 (6,0)")
    print(f"    Black king at: a8 (0,0)")
    print(f"    Are they on the same file? Yes (both file 'a')")
    print(f"    Squares between them: a3(5,0), a4(4,0), a5(3,0), a6(2,0), a7(1,0)")
    print(f"    Are all those squares empty?")
    between_squares = [(5,0), (4,0), (3,0), (2,0), (1,0)]
    all_empty = True
    for r, c in between_squares:
        piece = gs.board[r][c]
        print(f"      {chr(ord('a')+c)}{8-r}: '{piece}' -> empty? {piece == '--'}")
        if piece != '--':
            all_empty = False
    print(f"    All between squares empty: {all_empty}")
    print(f"    Therefore, white queen DOES check black king: {all_empty}")
    
