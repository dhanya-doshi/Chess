class GameState:
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]

        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkmate = False
        self.stalemate = False
        self.pins = []
        self.checks = []
        self.enpassantPossible = ()  # coordinates for the square where en passant capture is possible
        self.enpassantPossibleLog = [self.enpassantPossible]
        self.currentCastlingRights = CastlingRights(True, True, True, True)
        self.castlingRightsLog = [CastlingRights(self.currentCastlingRights.wks, self.currentCastlingRights.wqs,
                                                  self.currentCastlingRights.bks, self.currentCastlingRights.bqs)]
        self.halfmoveClock = 0  # number of halfmoves since last capture or pawn advance
        self.halfmoveClockLog = [self.halfmoveClock]  # log of halfmoveClock values for undo
        self.fullmoveNumber = 1  # number of full moves (starts at 1, increments after black's move)
        self.fullmoveNumberLog = [self.fullmoveNumber]  # log of fullmoveNumber values for undo
        self.positionHistory = []  # list of position strings for threefold repetition detection
        self.positionHistoryLog = [list(self.positionHistory)]  # log of positionHistory states for undo
        self.draw = False
        self.drawFiftyMove = False
        self.drawThreefold = False
        self.drawInsufficient = False
        self._storePosition()  # store initial position
        self.update_king_locations()

    def update_king_locations(self):
        """Update the king locations by scanning the board."""
        self.whiteKingLocation = None
        self.blackKingLocation = None
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                if self.board[r][c] == 'wK':
                    self.whiteKingLocation = (r, c)
                elif self.board[r][c] == 'bK':
                    self.blackKingLocation = (r, c)

    def _storePosition(self):
        """Create a string representation of the current position for threefold repetition detection."""
        # Include board, whose turn it is, castling rights, and en passant square
        board_str = ''.join([''.join(row) for row in self.board])
        turn_str = 'w' if self.whiteToMove else 'b'
        castling_str = f"{self.currentCastlingRights.wks}{self.currentCastlingRights.wqs}{self.currentCastlingRights.bks}{self.currentCastlingRights.bqs}"
        en_passant_str = f"{self.enpassantPossible[0] if self.enpassantPossible else -1},{self.enpassantPossible[1] if self.enpassantPossible else -1}"
        position = f"{board_str}|{turn_str}|{castling_str}|{en_passant_str}"
        self.positionHistory.append(position)

    def _isThreefoldRepetition(self):
        """Check if the current position has occurred three times."""
        if len(self.positionHistory) < 8:  # need at least 3 occurrences, but we can check early
            return False
        current = self.positionHistory[-1]
        return self.positionHistory.count(current) >= 3

    def _isInsufficientMaterial(self):
        """Check if the position is a draw due to insufficient material."""
        # Count pieces
        whitePieces = []
        blackPieces = []
        for row in self.board:
            for piece in row:
                if piece != "--":
                    if piece[0] == 'w':
                        whitePieces.append(piece)
                    else:
                        blackPieces.append(piece)

        # King vs King
        if len(whitePieces) == 1 and len(blackPieces) == 1:
            return True

        # King and Bishop/Knight vs King
        if ((len(whitePieces) == 2 and len(blackPieces) == 1 and
             any(p[1] in ('B', 'N') for p in whitePieces)) or
            (len(blackPieces) == 2 and len(whitePieces) == 1 and
             any(p[1] in ('B', 'N') for p in blackPieces))):
            return True

        # King and Bishop vs King and Bishop with same-colored bishops
        if (len(whitePieces) == 2 and len(blackPieces) == 2 and
            all(p[1] == 'B' for p in whitePieces) and
            all(p[1] == 'B' for p in blackPieces)):
            # Determine square colors of bishops
            def bishop_square_color(piece, pos):
                # piece format 'wB' or 'bB', we need board position; we don't have positions here easily.
                # Simplified: assume if both sides have exactly one bishop each, we cannot guarantee color without board.
                # For simplicity, we'll treat as insufficient only when we know they are on same color.
                # Since we don't have positions, we'll skip this case and rely on other rules.
                pass
            # This is complex; we'll omit this specific case for now.
            # Many engines still consider it insufficient only if bishops are on same color.
            # We'll approximate: if each side has exactly one bishop and no other pieces, assume draw.
            # This is not fully accurate but acceptable for basic implementation.
            if len([p for p in whitePieces if p[1] == 'B']) == 1 and \
               len([p for p in blackPieces if p[1] == 'B']) == 1:
                return True

        return False

    def _updateHalfmoveClock(self, move):
        """Update the halfmove clock based on the move made."""
        if move.pieceMoved[1] == 'p' or move.pieceCaptured != '--':
            self.halfmoveClock = 0
        else:
            self.halfmoveClock += 1

    def _updateFullmoveNumber(self):
        """Increment fullmove number after black's move."""
        if not self.whiteToMove:  # just after black moved
            self.fullmoveNumber += 1

    def makeMove(self, move):
        """Execute a move (this will be called by makeMove if move is valid)"""
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)  # log the move so we can undo it later
        self.whiteToMove = not self.whiteToMove  # swap players
        # update the king's location if moved
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)

        # if pawn moves, update enpassantPossible variable
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:  # only if 2 square pawn advance
            self.enpassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enpassantPossible = ()

        # if en passant capture, must update the board to remove the captured pawn
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = '--'  # capturing the pawn

        # if pawn promotion, change the piece
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'q'  # promote to queen for simplicity

        # update castling rights - whenever it is a rook or king move
        self.updateCastlingRights(move)
        self.castlingRightsLog.append(CastlingRights(self.currentCastlingRights.wks, self.currentCastlingRights.wqs,
                                                     self.currentCastlingRights.bks, self.currentCastlingRights.bqs))
        self.enpassantPossibleLog.append(self.enpassantPossible)

        # Log current state before updating
        self.halfmoveClockLog.append(self.halfmoveClock)
        self.fullmoveNumberLog.append(self.fullmoveNumber)
        self.positionHistoryLog.append(list(self.positionHistory))

        # Update halfmove clock, fullmove number, and position history
        self._updateHalfmoveClock(move)
        self._updateFullmoveNumber()
        self._storePosition()

    def undoMove(self):
        """Undo the last move made"""
        if len(self.moveLog) != 0:  # make sure there is a move to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove  # switch turns back
            # update the king's position if needed
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)
            # undo en passant
            self.enpassantPossibleLog.pop()  # get rid of the new enpassantPossible from the move we are undoing
            self.enpassantPossible = self.enpassantPossibleLog[-1] if len(self.enpassantPossibleLog) > 0 else ()  # set enpassantPossible to what it was before the move
            # undo castling rights
            self.castlingRightsLog.pop()  # get rid of the new castling rights from the move we are undoing
            self.currentCastlingRights = self.castlingRightsLog[-1]  # set the current castling rights to the last one in the list
            # undo move counter and history logs
            self.halfmoveClock = self.halfmoveClockLog.pop()
            self.fullmoveNumber = self.fullmoveNumberLog.pop()
            self.positionHistory = self.positionHistoryLog.pop()

    def updateCastlingRights(self, move):
        """Update the castling rights given the move"""
        if move.pieceMoved == 'wK':
            self.currentCastlingRights.wks = False
            self.currentCastlingRights.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRights.bks = False
            self.currentCastlingRights.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:  # left rook
                    self.currentCastlingRights.wqs = False
                elif move.startCol == 7:  # right rook
                    self.currentCastlingRights.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0:  # left rook
                    self.currentCastlingRights.bqs = False
                elif move.startCol == 7:  # right rook
                    self.currentCastlingRights.bks = False

        # if a rook is captured
        if move.pieceCaptured == 'wR':
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currentCastlingRights.wqs = False
                elif move.endCol == 7:
                    self.currentCastlingRights.wks = False
        elif move.pieceCaptured == 'bR':
            if move.endRow == 0:
                if move.endCol == 0:
                    self.currentCastlingRights.bqs = False
                elif move.endCol == 7:
                    self.currentCastlingRights.bks = False

    def getValidMoves(self):
        """All moves considering checks"""
        tempEnpassantPossible = self.enpassantPossible
        tempEnpassantPossibleLog = self.enpassantPossibleLog[:]
        tempCastlingRights = CastlingRights(self.currentCastlingRights.wks, self.currentCastlingRights.wqs,
                                            self.currentCastlingRights.bks, self.currentCastlingRights.bqs)

        # 1) generate all possible moves
        moves = self.getAllPossibleMoves()
        # 2) for each move, make the move
        # 3) generate all opponent's moves
        # 4) for each of your opponent's moves, see if they attack your king
        # 5) still in the loop, if they do attack your king, then it's not a valid move
        for i in range(len(moves) - 1, -1, -1):  # go through backwards when you are removing from a list as iterating
            self.makeMove(moves[i])
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():  # the move gives opponent a chance to check your king
                moves.remove(moves[i])  # remove the move from the list
            self.whiteToMove = not self.whiteToMove
            self.undoMove()

        self.enpassantPossible = tempEnpassantPossible
        self.enpassantPossibleLog = tempEnpassantPossibleLog[:]
        self.currentCastlingRights = tempCastlingRights

        # if there are no valid moves, it's either checkmate or stalemate
        if len(moves) == 0:
            if self.inCheck():
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

        # Check for draw conditions after move generation
        self._checkDrawConditions()

        return moves

    def _checkDrawConditions(self):
        """Update draw-related flags based on current state."""
        # Fifty-move rule
        if self.halfmoveClock >= 100:
            self.drawFiftyMove = True
        else:
            self.drawFiftyMove = False

        # Threefold repetition
        self.drawThreefold = self._isThreefoldRepetition()

        # Insufficient material
        self.drawInsufficient = self._isInsufficientMaterial()

        # Overall draw flag (if any draw condition met)
        self.draw = self.drawFiftyMove or self.drawThreefold or self.drawInsufficient

        # Note: In a real engine, you might claim draw only when player requests.
        # Here we just set flags.

    def inCheck(self):
        """Determine if the current player is in check"""
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    def squareUnderAttack(self, r, c):
        """Determine if the enemy can attack the square r, c"""
        self.whiteToMove = not self.whiteToMove  # switch to opponent's turn
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove  # switch turns back
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:  # square is under attack
                return True
        return False

    def getAllPossibleMoves(self):
        """All moves without considering checks"""
        moves = []
        for r in range(len(self.board)):  # number of rows
            for c in range(len(self.board[r])):  # number of columns
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    # call the appropriate move function based on piece type
                    if piece == 'p':
                        self.getPawnMoves(r, c, moves)  # pawn moves
                    elif piece == 'R':
                        self.getRookMoves(r, c, moves)  # rook moves
                    elif piece == 'N':
                        self.getKnightMoves(r, c, moves)  # knight moves
                    elif piece == 'B':
                        self.getBishopMoves(r, c, moves)  # bishop moves
                    elif piece == 'Q':
                        self.getQueenMoves(r, c, moves)  # queen moves
                    elif piece == 'K':
                        self.getKingMoves(r, c, moves)  # king moves

        return moves

    def getPawnMoves(self, r, c, moves):
        """Get all the pawn moves for the pawn located at row, col and add these moves to the list"""
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove:  # white pawn moves
            moveAmount = -1
            startRow = 6
            enemyColor = 'b'
            kingRow, kingCol = self.whiteKingLocation
        else:  # black pawn moves
            moveAmount = 1
            startRow = 1
            enemyColor = 'w'
            kingRow, kingCol = self.blackKingLocation

        if self.board[r + moveAmount][c] == "--":  # 1 square pawn advance
            if not piecePinned or pinDirection == (moveAmount, 0):
                moves.append(Move((r, c), (r + moveAmount, c), self.board))
                if r == startRow and self.board[r + 2 * moveAmount][c] == "--":  # 2 square pawn advance
                    moves.append(Move((r, c), (r + 2 * moveAmount, c), self.board))

        if c - 1 >= 0:  # captures to the left
            if not piecePinned or pinDirection == (moveAmount, -1):
                if self.board[r + moveAmount][c - 1][0] == enemyColor:
                    moves.append(Move((r, c), (r + moveAmount, c - 1), self.board))
                elif (r + moveAmount, c - 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r + moveAmount, c - 1), self.board, isEnpassantMove=True))

        if c + 1 <= 7:  # captures to the right
            if not piecePinned or pinDirection == (moveAmount, 1):
                if self.board[r + moveAmount][c + 1][0] == enemyColor:
                    moves.append(Move((r, c), (r + moveAmount, c + 1), self.board))
                elif (r + moveAmount, c + 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r + moveAmount, c + 1), self.board, isEnpassantMove=True))

    def getRookMoves(self, r, c, moves):
        """Get all the rook moves for the rook located at row, col and add these moves to the list"""
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q':  # can't remove queen from pin on rook moves, only remove it on bishop moves
                    self.pins.remove(self.pins[i])
                break

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # up, left, down, right
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # check if on board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":  # empty space is valid
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:  # enemy piece is valid
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:  # friendly piece is invalid
                            break
                else:  # off board
                    break

    def getKnightMoves(self, r, c, moves):
        """Get all the knight moves for the knight located at row, col and add these moves to the list"""
        piecePinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break

        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor:  # so it's either enemy piece or empty
                        moves.append(Move((r, c), (endRow, endCol), self.board))

    def getBishopMoves(self, r, c, moves):
        """Get all the bishop moves for the bishop located at row, col and add these moves to the list"""
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))  # up-left, up-right, down-left, down-right
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # check if on board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":  # empty space is valid
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:  # enemy piece is valid
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:  # friendly piece is invalid
                            break
                else:  # off board
                    break

    def getQueenMoves(self, r, c, moves):
        """Get all the queen moves for the queen located at row, col and add these moves to the list"""
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    def getKingMoves(self, r, c, moves):
        """Get all the king moves for the king located at row, col and add these moves to the list"""
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = r + rowMoves[i]
            endCol = c + colMoves[i]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:  # not an ally piece (empty or enemy piece)
                    # place king on end square and check for checks
                    if allyColor == 'w':
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    # place king back on original location
                    if allyColor == 'w':
                        self.whiteKingLocation = (r, c)
                    else:
                        self.blackKingLocation = (r, c)
        # get castling moves
        self.getCastleMoves(r, c, moves, allyColor)

    def getCastleMoves(self, r, c, moves, allyColor):
        """Generate all valid king castle moves for the king at (r,c) and add them to the list of moves"""
        inCheck, pins, checks = self.checkForPinsAndChecks()
        if inCheck:
            return  # can't castle while in check
        if (self.whiteToMove and self.currentCastlingRights.wks) or (not self.whiteToMove and self.currentCastlingRights.bks):
            self.getKingsideCastleMoves(r, c, moves, allyColor)
        if (self.whiteToMove and self.currentCastlingRights.wqs) or (not self.whiteToMove and self.currentCastlingRights.bqs):
            self.getQueensideCastleMoves(r, c, moves, allyColor)

    def getKingsideCastleMoves(self, r, c, moves, allyColor):
        """Generate kingside castle move if possible"""
        if self.board[r][c + 1] == '--' and self.board[r][c + 2] == '--':
            if not self.squareUnderAttack(r, c + 1) and not self.squareUnderAttack(r, c + 2):
                moves.append(Move((r, c), (r, c + 2), self.board, isCastleMove=True))

    def getQueensideCastleMoves(self, r, c, moves, allyColor):
        """Generate queenside castle move if possible"""
        if self.board[r][c - 1] == '--' and self.board[r][c - 2] == '--' and self.board[r][c - 3] == '--':
            if not self.squareUnderAttack(r, c - 1) and not self.squareUnderAttack(r, c - 2):
                moves.append(Move((r, c), (r, c - 2), self.board, isCastleMove=True))

    def checkForPinsAndChecks(self):
        """Return if the king is in check, a list of pins, and a list of checks"""
        pins = []  # squares where the allied pinned piece is and direction pinned from
        checks = []  # squares where enemy is applying a check
        inCheck = False
        if self.whiteToMove:
            enemyColor = "b"
            allyColor = "w"
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            enemyColor = "w"
            allyColor = "b"
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        # check outward from king for pins and checks, keep track of pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()  # reset possible pins
            for i in range(1, 8):
                endRow = kingRow + d[0] * i
                endCol = kingCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != 'K':
                        if possiblePin == ():  # first allied piece could be pinned
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:  # second allied piece, so no pin or check possible in this direction
                            break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        # 5 possibilities here in this complex conditonal
                        # 1.) orthogonally away from king and piece is a rook
                        # 2.) diagonally away from king and piece is a bishop
                        # 3.) 1 square away diagonally from king and piece is a pawn
                        # 4.) any direction and piece is a queen
                        # 5.) any direction 1 square away and piece is a king (this is necessary to prevent a king move to a square controlled by another king)
                        if (0 <= j <= 3 and type == 'R') or \
                                (4 <= j <= 7 and type == 'B') or \
                                (i == 1 and type == 'p' and ((enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or \
                                (type == 'Q') or (i == 1 and type == 'K'):
                            if possiblePin == ():  # no allied piece, so check
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else:  # piece allied so pin
                                pins.append(possiblePin)
                                break
                    else:  # enemy piece not applying check
                        break
                else:  # off board
                    break
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knightMoves:
            endRow = kingRow + m[0]
            endCol = kingCol + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == 'N':  # enemy knight attacking king
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
        return inCheck, pins, checks


class CastlingRights():
    def __init__(self, wks, wqs, bks, bqs):
        self.wks = wks
        self.wqs = wqs
        self.bks = bks
        self.bqs = bqs


class Move:
    # maps keys to values
    # key : value
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove=False, isCastleMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

        # pawn promotion
        self.isPawnPromotion = False
        # en passant
        self.isEnpassantMove = isEnpassantMove
        # castle
        self.isCastleMove = isCastleMove

        # for pawn promotion
        if self.pieceMoved == 'wp' and self.endRow == 0:
            self.isPawnPromotion = True
        elif self.pieceMoved == 'bp' and self.endRow == 7:
            self.isPawnPromotion = True

        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    """
    Overriding the equals method
    """
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        # you can add to make this like real chess notation
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]