import pygame as p
import os

IMAGES = {}

def loadImages():
    pieces = ["wp", "bp",
              "wR", "bR",
              "wN", "bN",
              "wB", "bB",
              "wQ", "bQ",
              "wK", "bK"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(
            p.image.load(os.path.join("images", piece + ".png")),
            (64, 64)  # assuming SQ_SIZE 64? but we can use same as ChessMain
        )
