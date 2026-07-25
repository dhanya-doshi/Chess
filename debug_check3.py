import ChessEngine

# Let's monkey patch the getQueenMoves function to add debug prints
original_getQueenMoves = ChessEngine.GameState.getQueenMoves

def debug_getQueenMoves(self, r, c, moves):
    print(f"    getQueenMoves called for queen at ({r},{c})")
    result = original_getQueenMoves(self, r, c, moves)
    print(f"    After getQueenMoves, moves list has {len(moves)} moves")
    return result

ChessEngine.GameState.getQueenMoves = debug_getQueenMoves

# Also debug getAllPossibleMoves
original_getAllPossibleMoves = ChessEngine.GameState.getAllPossibleMoves

def debug_getAllPossibleMoves(self):
    print("  getAllPossibleMoves called")
    result = original_getAllPossibleMoves(self)
    print(f"  getAllPossibleMoves returning {len(result)} moves")
    return result

ChessEngine.GameState.getAllPossibleMoves = debug_getAllPossibleMoves

# Also debug getQueenMoves internal loops
original_getQueenMoves_inner = ChessEngine.GameState.getQueenMoves

def debug_getQueenMoves_inner(self, r, c, moves):
    print(f"    >>> getQueenMoves({r}, {c}) called")
    # Call the original but let's see what it does
    # Actually, let's just reimplement with debug
    piecePinned = False
    pinDirection = ()
    # Simplified - just check if piece is pinned (we'll skip this for now)
    # In our test position, neither piece should be pinned
    
    directions = [(-1, -1), (-1, 1), (1, -1), (1, 1),  # diagonals
                  (-1, 0), (1, 0), (0, -1), (0, 1)]      # orthogonals
                  
    enemyColor = "b" if self.whiteToMove else "w"
    print(f"      Looking for enemy color: {enemyColor}")
    
    for d in directions:
        print(f"      Checking direction {d}")
        for i in range(1, 8):
            endRow = r + d[0] * i
            endCol = c + d[1] * i
            print(f"        Checking square ({endRow}, {endCol})")
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                print(f"          Piece at target: '{endPiece}'")
                if endPiece == "--":  # empty space
                    print(f"          Empty square, adding move")
                    move = chess_engine.Move((r, c), (endRow, endCol), self.board)
                    moves.append(move)
                    print(f"          Move added: {move.getChessNotation()}")
                elif endPiece[0] == enemyColor:  # enemy piece
                    print(f"          Enemy piece, adding move and stopping")
                    move = chess_engine.Move((r, c), (endRow, endCol), self.board)
                    moves.append(move)
                    print(f"          Move added: {move.getChessNotation()}")
                    break
                else:  # friendly piece
                    print(f"          Friendly piece, stopping")
                    break
            else:
                print(f"          Off board, stopping")
                break

# Let's just run a simple test
gs = ChessEngine.GameState()
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

print("Testing getAllPossibleMoves with white to move:")
gs.whiteToMove = True
moves = gs.getAllPossibleMoves()
print(f"Total moves: {len(moves)}")
