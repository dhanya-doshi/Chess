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

# AI Thinking state
aiThinking = False  # Is the AI currently thinking?
aiThoughtText = ""  # Display what the AI is "thinking"
aiThinkingDepth = 0  # Current search depth
aiBestMoveFound = None  # Best move found so far (for iterative deepening)

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
    global sliderDragging
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

    loadImages()

    running = True
    while running:
        for event in p.event.get():
            if event.type == p.QUIT:
                running = False
            elif event.type == p.MOUSEBUTTONDOWN:
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

                # After human move, if game not over and it's AI's turn (black), make AI move
                if not (gs.checkmate or gs.stalemate or gs.draw) and not gs.whiteToMove:
                    aimove = getAIMove(gs, selectedElo)
                    if aimove:
                        gs.makeMove(aimove)
                        moveMade = True
                        # After AI move, we need to update valid moves etc. Will be handled in next loop iteration

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

    # Captured pieces section
    captured_font = p.font.Font(None, 24)
    captured_title = captured_font.render("Captured Pieces", True, TURN_TEXT_COLOR)
    screen.blit(captured_title, (BOARD_WIDTH + 20, 170))

    # Calculate captured pieces from move log
    white_captured, black_captured = getCapturedPieces(gs.moveLog)

    # White captured pieces (black pieces captured by white)
    y_offset = 200
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

    # Material count
    score = 0
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = gs.board[row][col]
            if piece != "--":
                color = piece[0]
                pieceType = piece[1].lower()
                value = PIECE_VALUE[pieceType]
                if color == 'w':
                    score += value
                else:
                    score -= value
    return score


def orderMoves(gs, moves):
    """Order moves to improve alpha-beta pruning: captures first, then checks, etc."""
    def moveScore(move):
        score = 0
        # Captures
        if move.pieceCaptured != "--":
            score += PIECE_VALUE[move.pieceCaptured[1].lower()] * 10
        # Checks (simple: after making move, opponent in check?)
        # We'll skip for simplicity; could add but costs extra move generation.
        # Promotions
        if move.isPawnPromotion:
            score += PIECE_VALUE['q'] * 5
        return score
    return sorted(moves, key=moveScore, reverse=True)


def minimax(gs, depth, alpha, beta, maximizingPlayer):
    """Minimax with alpha-beta pruning.
    Returns (bestScore, bestMove)"""
    # Terminal condition
    if depth == 0 or gs.checkmate or gs.stalemate or gs.draw:
        return evaluateBoard(gs), None

    legalMoves = gs.getValidMoves()
    if not legalMoves:
        return evaluateBoard(gs), None

    orderedMoves = orderMoves(gs, legalMoves)

    if maximizingPlayer:
        maxEval = -math.inf
        bestMove = None
        for move in orderedMoves:
            gs.makeMove(move)
            eval, _ = minimax(gs, depth - 1, alpha, beta, False)
            gs.undoMove()
            if eval > maxEval:
                maxEval = eval
                bestMove = move
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return maxEval, bestMove
    else:
        minEval = math.inf
        bestMove = None
        for move in orderedMoves:
            gs.makeMove(move)
            eval, _ = minimax(gs, depth - 1, alpha, beta, True)
            gs.undoMove()
            if eval < minEval:
                minEval = eval
                bestMove = move
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return minEval, bestMove


def getAIMove(gs, elo):
    """Determine AI move based on Elo rating.
    Returns a Move object."""
    # Map Elo to search depth
    if elo <= 900:
        depth = 1
    elif elo <= 1100:
        depth = 2
    elif elo <= 1300:
        depth = 3
    elif elo <= 1500:
        depth = 4
    else:
        depth = 5  # cap at reasonable depth for performance

    # Get best move from minimax: white tries to maximize, black to minimize
    # (evaluation is from white's perspective)
    _, bestMove = minimax(gs, depth, -math.inf, math.inf, gs.whiteToMove)

    # If no best move (should not happen), pick random
    if bestMove is None:
        legalMoves = gs.getValidMoves()
        if legalMoves:
            bestMove = random.choice(legalMoves)

    # Apply randomness based on Elo to simulate weaker play
    # Lower Elo -> higher chance to play a random move instead of best
    if elo < 1600:
        # Probability of random move decreases linearly from 0.5 at 800 to 0 at 1600
        randProb = max(0.0, (1600 - elo) / 800.0)
        if random.random() < randProb:
            legalMoves = gs.getValidMoves()
            if legalMoves:
                return random.choice(legalMoves)

    return bestMove


if __name__ == "__main__":
    main()