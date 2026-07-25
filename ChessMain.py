import pygame as p
import ChessEngine
import random
import math
import time
import threading

# Constants
BOARD_WIDTH = 512
BOARD_HEIGHT = 512
SIDEBAR_WIDTH = 200
WIDTH = BOARD_WIDTH + SIDEBAR_WIDTH
HEIGHT = BOARD_HEIGHT
DIMENSION = 8
SQ_SIZE = BOARD_WIDTH // DIMENSION
MAX_FPS = 15
IMAGES = {}

# Colors
HIGHLIGHT_COLOR = p.Color(186, 202, 68, 100)  # Semi-transparent yellow for possible moves
SELECT_COLOR = p.Color(255, 255, 0, 100)      # Semi-transparent yellow for selected piece
TURN_TEXT_COLOR = p.Color(255, 255, 255)
BACKGROUND_COLOR = p.Color(50, 50, 50)
SIDEBAR_COLOR = p.Color(70, 70, 70)
CONFIG_BG_COLOR = p.Color(30, 30, 30, 200)   # Semi-transparent dark for config panel
CONFIG_TEXT_COLOR = p.Color(220, 220, 220)
CONFIG_HIGHLIGHT_COLOR = p.Color(100, 200, 255)
BUTTON_COLOR = p.Color(70, 130, 180)
BUTTON_HOVER_COLOR = p.Color(100, 160, 210)
BUTTON_TEXT_COLOR = p.Color(255, 255, 255)
THINKING_COLOR = p.Color(255, 200, 0)  # Gold for thinking indicator

# Piece values for evaluation
PIECE_VALUE = {
    'p': 100,   # pawn
    'n': 320,   # knight
    'b': 330,   # bishop
    'r': 500,   # rook
    'q': 900,   # queen
    'k': 20000  # king (large value to avoid trading king)
}

# Piece-Square Tables (PST) for positional evaluation
# Based on chess programming principles - pieces are worth more on good squares
# Values are in centipawns (same scale as PIECE_VALUE)
# Format: [row][col] where row 0 = white's back rank (white's perspective)

# Pawn PST - reward central control and advancement
PAWN_PST = [
    [0,  0,  0,  0,  0,  0,  0,  0],
    [50, 50, 50, 50, 50, 50, 50, 50],
    [10, 10, 20, 30, 30, 20, 10, 10],
    [5,  5, 10, 25, 25, 10,  5,  5],
    [0,  0,  0, 20, 20,  0,  0,  0],
    [5, -5,-10,  0,  0,-10, -5,  5],
    [5, 10, 10,-20,-20, 10, 10,  5],
    [0,  0,  0,  0,  0,  0,  0,  0]
]

# Knight PST - reward central squares and penalize edges
KNIGHT_PST = [
    [-50,-40,-30,-30,-30,-30,-40,-50],
    [-40,-20,  0,  0,  0,  0,-20,-40],
    [-30,  0, 10, 15, 15, 10,  0,-30],
    [-30,  5, 15, 20, 20, 15,  5,-30],
    [-30,  0, 15, 20, 20, 15,  0,-30],
    [-30,  5, 10, 15, 15, 10,  5,-30],
    [-40,-20,  0,  5,  5,  0,-20,-40],
    [-50,-40,-30,-30,-30,-30,-40,-50]
]

# Bishop PST - reward diagonals and central control
BISHOP_PST = [
    [-20,-10,-10,-10,-10,-10,-10,-20],
    [-10,  0,  0,  0,  0,  0,  0,-10],
    [-10,  0,  5, 10, 10,  5,  0,-10],
    [-10,  5,  5, 10, 10,  5,  5,-10],
    [-10,  0, 10, 10, 10, 10,  0,-10],
    [-10, 10, 10, 10, 10, 10, 10,-10],
    [-10,  5,  0,  0,  0,  0,  5,-10],
    [-20,-10,-10,-10,-10,-10,-10,-20]
]

# Rook PST - reward open files and centralization
ROOK_PST = [
    [0,  0,  0,  0,  0,  0,  0,  0],
    [5, 10, 10, 10, 10, 10, 10,  5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [0,  0,  0,  5,  5,  0,  0,  0]
]

# Queen PST - reward central control and threaten
QUEEN_PST = [
    [-20,-10,-10, -5, -5,-10,-10,-20],
    [-10,  0,  0,  0,  0,  0,  0,-10],
    [-10,  0,  5,  5,  5,  5,  0,-10],
    [-5,  0,  5,  5,  5,  5,  0, -5],
    [0,  0,  5,  5,  5,  5,  0, -5],
    [-10,  5,  5,  5,  5,  5,  0,-10],
    [-10,  0,  5,  0,  0,  0,  0,-10],
    [-20,-10,-10, -5, -5,-10,-10,-20]
]

# King PST - reward safety in early game, centralization in endgame
KING_PST = [
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-20,-30,-30,-40,-40,-30,-30,-20],
    [-10,-20,-20,-20,-20,-20,-20,-10],
    [20, 20,  0,  0,  0,  0, 20, 20],
    [20, 30, 10,  0,  0, 10, 30, 20]
]

PIECE_PST = {
    'P': PAWN_PST,
    'N': KNIGHT_PST,
    'B': BISHOP_PST,
    'R': ROOK_PST,
    'Q': QUEEN_PST,
    'K': KING_PST
}

# Killer moves - moves that caused cutoffs at each depth (for move ordering)
# Format: [depth][slot] - we track 2 killer moves per depth
MAX_SEARCH_DEPTH = 12
KILLER_MOVES = [[None, None] for _ in range(MAX_SEARCH_DEPTH)]

# History table - scores for move ordering based on success
# Format: history[color][from_square][to_square]
HISTORY_SIZE = 64  # 8x8 board
HISTORY = [[[0 for _ in range(HISTORY_SIZE)] for _ in range(HISTORY_SIZE)] for _ in range(2)]

# Quiescence search parameters
MAX_QUIESCENCE_DEPTH = 20  # Max depth for quiescence search
STAND_PAT_THRESHOLD = 150  # Don't search captures ifeval is this much above beta

# AI Thinking state
aiThinking = False  # Is the AI currently thinking?
aiThoughtText = ""  # Display what the AI is "thinking"
aiThinkingDepth = 0  # Current search depth
aiBestMoveFound = None  # Best move found so far (for iterative deepening)
aiMoveFound = None  # Move computed by AI thread, consumed by main loop

# UI state
gameStarted = False
selectedElo = 1200  # default Elo
hoveringButton = False
sliderDragging = False

def loadImages():
    pieces = [
        "wp", "bp",
        "wR", "bR",
        "wN", "bN",
        "wB", "bB",
        "wQ", "bQ",
        "wK", "bK"
    ]

    for piece in pieces:
        IMAGES[piece] = p.transform.scale(
            p.image.load("images/" + piece + ".png"),
            (SQ_SIZE, SQ_SIZE)
        )


def main():
    global sliderDragging, aiThinking, aiMoveFound
    p.init()

    screen = p.display.set_mode((WIDTH, HEIGHT))
    p.display.set_caption("Chess")

    clock = p.time.Clock()

    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False  # flag variable for when a move is made
    sqSelected = ()  # no square is selected, keep track of the last click of the user (tuple: (row, col))
    playerClicks = []  # keep track of player clicks (two tuples: [(6, 4), (4, 4)])
    pieceValidMoves = []  # valid moves for the currently selected piece
    aiMoveFound = None  # Move found by AI thread

    loadImages()

    running = True
    while running:
        for event in p.event.get():
            if event.type == p.QUIT:
                running = False
            elif event.type == p.MOUSEBUTTONDOWN:
                # Ignore board clicks while AI is thinking or game over
                if aiThinking or (not (gs.checkmate or gs.stalemate or gs.draw)):
                    continue

                location = p.mouse.get_pos()  # (x, y) location of mouse
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE

                if not gameStarted:
                    # Handle config UI clicks
                    handleConfigClick(location)
                else:
                    # Ignore clicks outside the board (in sidebar area)
                    if col >= DIMENSION:
                        continue

                    if sqSelected == (row, col):  # the user clicked the same square twice
                        sqSelected = ()  # deselect
                        playerClicks = []  # clear player clicks
                        pieceValidMoves = []  # clear move visualization
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)  # append for both 1st and 2nd click
                        # Get valid moves for the selected piece
                        pieceValidMoves = getPieceValidMoves(gs, row, col)

                    if len(playerClicks) == 2:  # after 2nd click
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                sqSelected = ()  # reset user clicks
                                playerClicks = []
                                pieceValidMoves = []  # clear move visualization
                        if not moveMade:
                            playerClicks = [sqSelected]  # if user clicked on an invalid square, just keep the first click
                            # Keep pieceValidMoves for the selected square

            elif event.type == p.MOUSEMOTION and not gameStarted:
                # Update button hover state
                updateButtonHover(p.mouse.get_pos())
            elif event.type == p.MOUSEBUTTONUP and sliderDragging:
                sliderDragging = False

        if gameStarted:
            # update the valid moves list if a move was made
            if moveMade:
                validMoves = gs.getValidMoves()
                moveMade = False

                # After human move, if game not over and it's AI's turn (black), start AI thinking
                if not (gs.checkmate or gs.stalemate or gs.draw) and not gs.whiteToMove:
                    # Start AI thinking in a separate thread
                    def aiThreadFunc():
                        global aiThinking, aiMoveFound, aiThoughtText
                        aiThinking = True
                        aiThoughtText = "Thinking..."
                        move = getAIMove(gs, selectedElo)
                        aiMoveFound = move
                        aiThinking = False
                        aiThoughtText = ""

                    aiThinking = False
                    aiMoveFound = None
                    aiThread = threading.Thread(target=aiThreadFunc)
                    aiThread.start()

            # Process AI move when it's ready (while keeping UI responsive)
            if aiMoveFound is not None and not aiThinking:
                gs.makeMove(aiMoveFound)
                moveMade = True
                aiMoveFound = None

            drawGameState(screen, gs, sqSelected, pieceValidMoves)
        else:
            drawConfigScreen(screen)

        clock.tick(MAX_FPS)
        p.display.flip()

    p.quit()


def handleConfigClick(pos):
    """Handle mouse clicks in configuration mode"""
    global selectedElo, sliderDragging, gameStarted, hoveringButton
    x, y = pos

    # Start button area
    buttonRect = p.Rect(WIDTH // 2 - 60, HEIGHT // 2 + 80, 120, 40)
    if buttonRect.collidepoint(x, y):
        gameStarted = True
        return

    # Slider area
    sliderRect = p.Rect(WIDTH // 2 - 150, HEIGHT // 2, 300, 20)
    if sliderRect.collidepoint(x, y):
        sliderDragging = True
        updateSliderFromPos(x)
        return


def updateButtonHover(pos):
    """Update hoveringButton flag based on mouse position"""
    global hoveringButton
    x, y = pos
    buttonRect = p.Rect(WIDTH // 2 - 60, HEIGHT // 2 + 80, 120, 40)
    hoveringButton = buttonRect.collidepoint(x, y)


def updateSliderFromPos(x):
    """Update selectedElo based on slider x position"""
    global selectedElo
    sliderMinX = WIDTH // 2 - 150
    sliderMaxX = WIDTH // 2 + 150
    # Clamp x to slider range
    if x < sliderMinX:
        x = sliderMinX
    elif x > sliderMaxX:
        x = sliderMaxX
    # Map position to Elo range 800-2000
    ratio = (x - sliderMinX) / (sliderMaxX - sliderMinX)
    selectedElo = int(800 + ratio * (2000 - 800))


def drawConfigScreen(screen):
    """Draw the configuration screen before game starts"""
    # Darken background
    overlay = p.Surface((WIDTH, HEIGHT), p.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    # Config panel
    panelRect = p.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 100, 400, 200)
    p.draw.rect(screen, CONFIG_BG_COLOR, panelRect, border_radius=10)
    p.draw.rect(screen, CONFIG_HIGHLIGHT_COLOR, panelRect, width=2, border_radius=10)

    # Title
    fontTitle = p.font.Font(None, 48)
    title = fontTitle.render("Chess Engine", True, CONFIG_TEXT_COLOR)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 80))

    # Elo label
    fontLabel = p.font.Font(None, 28)
    label = fontLabel.render(f"Computer Elo: {selectedElo}", True, CONFIG_TEXT_COLOR)
    screen.blit(label, (WIDTH // 2 - label.get_width() // 2, HEIGHT // 2 - 20))

    # Slider track
    sliderTrackRect = p.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 10, 300, 10)
    p.draw.rect(screen, p.Color(80, 80, 80), sliderTrackRect)
    # Slider fill
    ratio = (selectedElo - 800) / (2000 - 800)
    fillWidth = int(ratio * 300)
    sliderFillRect = p.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 10, fillWidth, 10)
    p.draw.rect(screen, CONFIG_HIGHLIGHT_COLOR, sliderFillRect)
    # Slider handle
    handleRadius = 10
    handleX = WIDTH // 2 - 150 + fillWidth
    handleY = HEIGHT // 2 + 15  # center of track
    p.draw.circle(screen, CONFIG_HIGHLIGHT_COLOR, (handleX, handleY), handleRadius)

    # Start button
    buttonRect = p.Rect(WIDTH // 2 - 60, HEIGHT // 2 + 80, 120, 40)
    buttonColor = BUTTON_HOVER_COLOR if hoveringButton else BUTTON_COLOR
    p.draw.rect(screen, buttonColor, buttonRect, border_radius=5)
    fontButton = p.font.Font(None, 28)
    buttonText = fontButton.render("Start", True, BUTTON_TEXT_COLOR)
    screen.blit(buttonText, (buttonRect.centerx - buttonText.get_width() // 2,
                             buttonRect.centery - buttonText.get_height() // 2))


def getPieceValidMoves(gs, row, col):
    """Get all valid moves for a piece at the given position"""
    # Generate all valid moves for the current position
    allValidMoves = gs.getValidMoves()
    # Filter moves that start from the selected position
    pieceMoves = []
    for move in allValidMoves:
        if move.startRow == row and move.startCol == col:
            pieceMoves.append(move)
    return pieceMoves


def drawGameState(screen, gs, sqSelected=None, pieceValidMoves=None):
    drawBoard(screen, sqSelected)
    drawPieces(screen, gs.board)
    if pieceValidMoves:
        drawMoveIndicators(screen, pieceValidMoves)
    drawSidebar(screen, gs)


def drawBoard(screen, sqSelected=None):
    colors = [p.Color("white"), p.Color("gray")]
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors[(row + col) % 2]
            p.draw.rect(
                screen,
                color,
                p.Rect(
                    col * SQ_SIZE,
                    row * SQ_SIZE,
                    SQ_SIZE,
                    SQ_SIZE
                )
            )

    # Highlight selected square
    if sqSelected:
        highlight = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)
        highlight.fill(SELECT_COLOR)
        screen.blit(highlight, (sqSelected[1] * SQ_SIZE, sqSelected[0] * SQ_SIZE))


def drawMoveIndicators(screen, moves):
    """Draw indicators for possible moves"""
    for move in moves:
        # Draw a circle in the center of the destination square
        center = (
            move.endCol * SQ_SIZE + SQ_SIZE // 2,
            move.endRow * SQ_SIZE + SQ_SIZE // 2
        )
        radius = SQ_SIZE // 4
        # Only draw if it's a valid board position
        if 0 <= move.endRow < DIMENSION and 0 <= move.endCol < DIMENSION:
            # Create a surface for the circle with alpha
            circle_surface = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)
            p.draw.circle(circle_surface, HIGHLIGHT_COLOR, (SQ_SIZE // 2, SQ_SIZE // 2), radius)
            screen.blit(circle_surface, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))


def drawPieces(screen, board):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]
            if piece != "--":
                screen.blit(
                    IMAGES[piece],
                    p.Rect(
                        col * SQ_SIZE,
                        row * SQ_SIZE,
                        SQ_SIZE,
                        SQ_SIZE
                    )
                )


def drawSidebar(screen, gs):
    """Draw the sidebar with game information"""
    # Sidebar background
    sidebar_rect = p.Rect(BOARD_WIDTH, 0, SIDEBAR_WIDTH, HEIGHT)
    p.draw.rect(screen, SIDEBAR_COLOR, sidebar_rect)

    # Sidebar title
    font = p.font.Font(None, 36)
    title_text = font.render("Chess Game", True, TURN_TEXT_COLOR)
    screen.blit(title_text, (BOARD_WIDTH + 20, 20))

    # Current turn
    turn_text = "White to move" if gs.whiteToMove else "Black to move"
    turn_color = p.Color(255, 255, 255) if gs.whiteToMove else p.Color(192, 192, 192)
    turn_font = p.font.Font(None, 28)
    turn_surface = turn_font.render(turn_text, True, turn_color)
    screen.blit(turn_surface, (BOARD_WIDTH + 20, 80))

    # Turn indicator
    indicator_size = 20
    indicator_x = BOARD_WIDTH + 20
    indicator_y = 120
    if gs.whiteToMove:
        p.draw.circle(screen, p.Color(255, 255, 255), (indicator_x, indicator_y), indicator_size)
    else:
        p.draw.circle(screen, p.Color(96, 96, 96), (indicator_x, indicator_y), indicator_size)

    # AI Thinking indicator
    if aiThinking:
        thinking_font = p.font.Font(None, 22)
        # Animated dots
        dot_count = (int(time.time() * 3) % 4)
        dots = "." * dot_count
        think_text = f"AI thinking{dots}"
        think_surface = thinking_font.render(think_text, True, THINKING_COLOR)
        screen.blit(think_surface, (BOARD_WIDTH + 20, 160))
        if aiThoughtText:
            sub_text = thinking_font.render(aiThoughtText, True, p.Color(180, 180, 180))
            screen.blit(sub_text, (BOARD_WIDTH + 20, 182))
        if aiBestMoveFound:
            move_text = f"Move: {aiBestMoveFound.getChessNotation()}"
            move_surface = thinking_font.render(move_text, True, THINKING_COLOR)
            screen.blit(move_surface, (BOARD_WIDTH + 20, 204))
        y_start = 230
    else:
        y_start = 170

    # Captured pieces section
    captured_font = p.font.Font(None, 24)
    captured_title = captured_font.render("Captured Pieces", True, TURN_TEXT_COLOR)
    screen.blit(captured_title, (BOARD_WIDTH + 20, y_start))

    # Calculate captured pieces from move log
    white_captured, black_captured = getCapturedPieces(gs.moveLog)

    # White captured pieces (black pieces captured by white)
    y_offset = y_start + 30
    if white_captured:
        white_label = captured_font.render("White captured:", True, TURN_TEXT_COLOR)
        screen.blit(white_label, (BOARD_WIDTH + 20, y_offset))
        y_offset += 25
        for i, piece in enumerate(white_captured):
            if piece in IMAGES:
                img = p.transform.scale(IMAGES[piece], (SQ_SIZE // 2, SQ_SIZE // 2))
                screen.blit(img, (BOARD_WIDTH + 20 + (i % 8) * (SQ_SIZE // 2 + 5),
                                y_offset + (i // 8) * (SQ_SIZE // 2 + 5)))
    else:
        no_captured = captured_font.render("None", True, TURN_TEXT_COLOR)
        screen.blit(no_captured, (BOARD_WIDTH + 20, y_offset))
        y_offset += 25

    # Black captured pieces (white pieces captured by black)
    y_offset += 10
    if black_captured:
        black_label = captured_font.render("Black captured:", True, TURN_TEXT_COLOR)
        screen.blit(black_label, (BOARD_WIDTH + 20, y_offset))
        y_offset += 25
        for i, piece in enumerate(black_captured):
            if piece in IMAGES:
                img = p.transform.scale(IMAGES[piece], (SQ_SIZE // 2, SQ_SIZE // 2))
                screen.blit(img, (BOARD_WIDTH + 20 + (i % 8) * (SQ_SIZE // 2 + 5),
                                y_offset + (i // 8) * (SQ_SIZE // 2 + 5)))
    else:
        no_captured = captured_font.render("None", True, TURN_TEXT_COLOR)
        screen.blit(no_captured, (BOARD_WIDTH + 20, y_offset))


def getCapturedPieces(moveLog):
    """Extract captured pieces from the move log"""
    white_captured = []  # Pieces captured by white (black pieces)
    black_captured = []  # Pieces captured by black (white pieces)

    for move in moveLog:
        if move.pieceCaptured != "--":
            # Determine who captured the piece based on the piece moved
            if move.pieceMoved[0] == 'w':  # White piece moved
                black_captured.append(move.pieceCaptured)  # White captured black piece
            else:  # Black piece moved
                white_captured.append(move.pieceCaptured)  # Black captured white piece

    return white_captured, black_captured


def getPiecePositionalValue(piece, row, col):
    """Get the positional value from piece-square table for a piece.
    For white pieces, we look up directly; for black, we flip the row"""
    if piece == "--":
        return 0
    pieceType = piece[1].upper()
    if pieceType not in PIECE_PST:
        return 0
    pst = PIECE_PST[pieceType]
    if piece[0] == 'w':
        return pst[row][col]
    else:
        return pst[7 - row][col]  # flip row for black


def evaluateBoard(gs):
    """Evaluate the board from white's perspective.
    Returns a positive score if white is ahead, negative if black is ahead.
    Terminal states return large magnitude scores."""
    # Check for terminal states
    if gs.checkmate:
        # If checkmate, the side to move is checkmated and loses.
        if gs.whiteToMove:
            # White to move is checkmated -> black wins -> bad for white
            return -20000
        else:
            # Black to move is checkmated -> white wins -> good for white
            return 20000
    if gs.stalemate or gs.draw:
        return 0

    # Material count + positional evaluation
    score = 0
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = gs.board[row][col]
            if piece != "--":
                color = piece[0]
                pieceType = piece[1].lower()
                # Material value
                value = PIECE_VALUE[pieceType]
                # Positional value from PST
                posValue = getPiecePositionalValue(piece, row, col)
                if color == 'w':
                    score += value + posValue
                else:
                    score -= value + posValue
    return score


def orderMoves(gs, moves, depth=0, killerMoves=None, history=None):
    """Order moves to improve alpha-beta pruning: captures first, then checks, etc.
    Uses killer moves and history heuristic for better ordering."""
    if killerMoves is None:
        killerMoves = KILLER_MOVES
    if history is None:
        history = HISTORY

    def moveScore(move):
        score = 0
        colorIndex = 0 if gs.whiteToMove else 1

        # Captures - sort by MVV-LVA (Most Valuable Victim - Least Valuable Attacker)
        if move.pieceCaptured != "--":
            victim = PIECE_VALUE[move.pieceCaptured[1].lower()]
            attacker = PIECE_VALUE[move.pieceMoved[1].lower()]
            score += 10000 + victim * 10 - attacker  # MVV-LVA scoring
        else:
            # Non-capture moves
            # Killer moves - moves that caused cutoffs at this depth
            if depth < MAX_SEARCH_DEPTH:
                for km in killerMoves[depth]:
                    if km is not None and move == km:
                        score += 800
                        break

            # History heuristic - successful moves get higher scores
            fromSq = move.startRow * 8 + move.startCol
            toSq = move.endRow * 8 + move.endCol
            score += history[colorIndex][fromSq][toSq]

        # Promotions - high priority
        if move.isPawnPromotion:
            score += PIECE_VALUE['q'] * 8  # Strong bonus for promotion

        return score
    return sorted(moves, key=moveScore, reverse=True)


def quiescenceSearch(gs, alpha, beta, depth):
    """Quiescence search - only search 'noisy' moves (captures, promotions) until position is quiet.
    Returns (bestScore, bestMove)"""
    standPat = evaluateBoard(gs)

    # Beta cutoff - if we're already too far ahead, don't search captures
    if standPat >= beta:
        return beta, None
    if standPat > alpha:
        alpha = standPat

    if depth >= MAX_QUIESCENCE_DEPTH:
        return standPat, None

    # Get only capture moves (noise moves) for quiescence
    moves = gs.getValidMoves()
    captureMoves = [m for m in moves if m.pieceCaptured != "--" or m.isPawnPromotion]

    if not captureMoves:
        return standPat, None

    # Sort captures by MVV-LVA for best ordering
    captureMoves = sorted(captureMoves, key=lambda m: (
        PIECE_VALUE[m.pieceCaptured[1].lower()] if m.pieceCaptured != "--" else 0
    ), reverse=True)

    bestMove = None
    for move in captureMoves:
        gs.makeMove(move)
        score, _ = quiescenceSearch(gs, -beta, -alpha, depth + 1)
        score = -score  # Flip sign for maximizing/minimizing
        gs.undoMove()

        if score >= beta:
            return beta, None
        if score > alpha:
            alpha = score
            bestMove = move

    return alpha, bestMove


def minimax(gs, depth, alpha, beta, maximizingPlayer, currentDepth=0):
    """Minimax with alpha-beta pruning and killer move ordering.
    Returns (bestScore, bestMove)"""
    if currentDepth >= MAX_SEARCH_DEPTH:
        depth = 0  # Force quiescence search at max depth

    # Terminal condition
    if depth == 0 or gs.checkmate or gs.stalemate or gs.draw:
        if depth == 0:
            # At zero depth in main search, do quiescence to get stable eval
            return quiescenceSearch(gs, alpha, beta, 0)
        return evaluateBoard(gs), None

    legalMoves = gs.getValidMoves()
    if not legalMoves:
        if depth == 0:
            return quiescenceSearch(gs, alpha, beta, 0)
        return evaluateBoard(gs), None

    orderedMoves = orderMoves(gs, legalMoves, currentDepth, KILLER_MOVES, HISTORY)

    if maximizingPlayer:
        maxEval = -math.inf
        bestMove = None
        for move in orderedMoves:
            gs.makeMove(move)
            eval_score, _ = minimax(gs, depth - 1, alpha, beta, False, currentDepth + 1)
            gs.undoMove()
            if eval_score > maxEval:
                maxEval = eval_score
                bestMove = move
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                # Killer move: store this move for move ordering at other nodes
                if move not in KILLER_MOVES[currentDepth]:
                    # Shift existing killers and add this one
                    KILLER_MOVES[currentDepth][1] = KILLER_MOVES[currentDepth][0]
                    KILLER_MOVES[currentDepth][0] = move
                # History: record successful move for white
                fromSq = move.startRow * 8 + move.startCol
                toSq = move.endRow * 8 + move.endCol
                HISTORY[0][fromSq][toSq] += depth * depth
                break
        return maxEval, bestMove
    else:
        minEval = math.inf
        bestMove = None
        for move in orderedMoves:
            gs.makeMove(move)
            eval_score, _ = minimax(gs, depth - 1, alpha, beta, True, currentDepth + 1)
            gs.undoMove()
            if eval_score < minEval:
                minEval = eval_score
                bestMove = move
            beta = min(beta, eval_score)
            if beta <= alpha:
                # Killer move
                if move not in KILLER_MOVES[currentDepth]:
                    KILLER_MOVES[currentDepth][1] = KILLER_MOVES[currentDepth][0]
                    KILLER_MOVES[currentDepth][0] = move
                # History: record successful move for black
                fromSq = move.startRow * 8 + move.startCol
                toSq = move.endRow * 8 + move.endCol
                HISTORY[1][fromSq][toSq] += depth * depth
                break
        return minEval, bestMove


def iterativeDeepening(gs, maxDepth, callback):
    """Iterative deepening search that calls callback after each depth completes.
    callback(depth, bestMove, score) is called to update UI with progress.
    Returns the best move found at the deepest depth."""
    bestMove = None
    for depth in range(1, maxDepth + 1):
        _, bestMove = minimax(gs, depth, -math.inf, math.inf, gs.whiteToMove)
        if bestMove is not None:
            callback(depth, bestMove)
        # Small delay between depths to allow UI updates
        time.sleep(0.05)
    return bestMove


def getAIMove(gs, elo):
    """Determine AI move based on Elo rating with iterative deepening.
    Returns a Move object. Updates global thinking state for UI."""
    global aiThinking, aiThoughtText, aiThinkingDepth, aiBestMoveFound

    # Map Elo to max search depth
    if elo <= 900:
        maxDepth = 2
    elif elo <= 1100:
        maxDepth = 3
    elif elo <= 1300:
        maxDepth = 4
    elif elo <= 1500:
        maxDepth = 5
    else:
        maxDepth = 6  # cap at reasonable depth

    # Minimum thinking time in seconds based on Elo (weaker = thinks less)
    minThinkTime = max(0.5, (elo - 800) / 400)  # 0.5s at 800 Elo, 3s at 2000 Elo

    thinkStart = time.time()

    def updateCallback(depth, move):
        """Called after each depth completes with current best move"""
        global aiThoughtText, aiThinkingDepth, aiBestMoveFound
        aiThinkingDepth = depth
        aiBestMoveFound = move
        if move:
            eval_score = evaluateBoard(gs)
            # Translating evaluation to a more human description
            if abs(eval_score) > 15000:
                quality = "Checkmate in " + str(abs(int((15000 - abs(eval_score)) / 100)))
            elif eval_score > 300:
                quality = "Winning"
            elif eval_score > 50:
                quality = "Slight advantage"
            elif eval_score > -50:
                quality = "Equal"
            elif eval_score > -300:
                quality = "Slight disadvantage"
            else:
                quality = "Losing"
            aiThoughtText = f"Depth {depth}: {quality}"

    # Run iterative deepening
    aiThinking = True
    aiThoughtText = "Starting search..."
    bestMove = iterativeDeepening(gs, maxDepth, updateCallback)

    # Ensure minimum thinking time
    elapsed = time.time() - thinkStart
    if elapsed < minThinkTime:
        time.sleep(minThinkTime - elapsed)

    # Apply randomness based on Elo to simulate weaker play
    # Lower Elo -> higher chance to play a random move instead of best
    if elo < 1600:
        # Probability of random move decreases linearly from 0.5 at 800 to 0 at 1600
        randProb = max(0.0, (1600 - elo) / 800.0)
        if random.random() < randProb:
            legalMoves = gs.getValidMoves()
            if legalMoves:
                aiThoughtText = "Hmm, let me think again..."
                time.sleep(0.3)
                aiThinking = False
                return random.choice(legalMoves)

    aiThinking = False
    aiThoughtText = ""

    # If no best move (should not happen), pick random
    if bestMove is None:
        legalMoves = gs.getValidMoves()
        if legalMoves:
            bestMove = random.choice(legalMoves)

    return bestMove


if __name__ == "__main__":
    main()