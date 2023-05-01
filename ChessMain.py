import pygame
import ChessEngine
import AI
import tkinter as tk
from tkinter import *
from tkinter import simpledialog
pygame.init()



WIDTH = HEIGHT = 400
DIMENSION = 8 
SQ_SIZE = HEIGHT // DIMENSION

MAX_FPS = 15   

IMAGES = {}


def load_images():
    pieces = ["bR", "bN", "bB", "bQ", "bK", "wR", "wN", "wB", "wQ", "wK", "bP", "wP"]
    for piece in pieces:
        IMAGES[piece] = pygame.transform.scale(pygame.image.load("images/"+piece+".png"), (SQ_SIZE, SQ_SIZE))


def main():
    screen = pygame.display.set_mode([WIDTH, HEIGHT])
    clock = pygame.time.Clock()
    screen.fill(pygame.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False
    load_images()

    

    running = True
    doAnimate = False
    sqselected = ()
    playerClicks = []
    gameOver = False

   
    ROOT = tk.Tk()

    ROOT.withdraw()
    while True:


        choice = simpledialog.askstring(title="Options",
                                               prompt="Choose Your Desired Option: \n1) Player vs AI \n2) AI vs AI \n3)Player vs Player")

        print(choice)
        if choice == '1':
            player1 = True
            player2 = False
            break
        elif choice == '2':
            player1 = False
            player2 = False
            break
        elif choice == '3':
            player1 = True
            player2 = True
            break
        else:
            print("invalid Choice")



    print("\nPlayer White Turn")
    while running:

        userTurn = (gs.whiteToMove and player1) or (not gs.whiteToMove and player2)
        

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

           
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not gameOver and userTurn:
                    location = pygame.mouse.get_pos()
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if sqselected == (row, col):
                        sqselected = ()
                        playerClicks = []
                    else:
                        sqselected = (row, col)
                        playerClicks.append(sqselected)
                    if len(playerClicks) == 2:
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board, player1, player2)
                        print(move.getChessNotation())
                        print("Possible moves: ")
                        for temp in validMoves:
                                print(temp.getChessNotation(), end=", ")

                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                doAnimate = True
                                sqselected = ()
                                playerClicks = []

                        if not moveMade:
                            playerClicks = [sqselected]

            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z:
                    gs.undoMove()
                    print("\nUndoing Move\n")
                    moveMade = True
                    doAnimate = False
                    gameOver = False

                if event.key == pygame.K_r:
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqselected = ()
                    playerClicks = []
                    moveMade = False
                    doAnimate = False
                    gameOver = False

        
        if not gameOver and not userTurn:
            AIMove = AI.findBestMove(gs, validMoves)
            if AIMove is None:
                AIMove = AI.findRandomMove(validMoves)
            gs.makeMove(AIMove)
            print("Ai Moved: ", AIMove.getChessNotation())
            moveMade = True
            doAnimate = True

        
        if moveMade:
            if doAnimate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()

            if len(gs.getValidMoves()) == 0:
                if gs.inCheck:
                    gs.checkMate = True
                else:
                    gs.staleMate = True

            if(gs.whiteToMove):
                print("\n\nPlayer White Turn")
            else:
                print("\n\nPlayer Black Turn")
            moveMade = False
            print("checkMate:", gs.checkMate)
            print("staleMate:", gs.staleMate)
            print("Available Moves: ", len(validMoves))

        
        draw_game_state(screen, gs, validMoves, sqselected)

        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, "Check Mate !! Black Wins")
            else:
                drawText(screen, "Check Mate !! White Wins")
        elif gs.staleMate:
            gameOver = True
            drawText(screen, "Stale Mate !! Match Draws")

        clock.tick(MAX_FPS)


        pygame.display.flip()

    

    pygame.quit()


def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        row, col = sqSelected
        if gs.board[row][col][0] == ('w' if gs.whiteToMove else 'b'):
            title = pygame.Surface((SQ_SIZE, SQ_SIZE))
            title.set_alpha(100) # range 0 -255
            title.fill(pygame.Color('blue'))
            screen.blit(title, (col*SQ_SIZE, row*SQ_SIZE))
            title.fill(pygame.Color('Yellow'))
            for move in validMoves:
                if move.startRow == row and move.startCol == col:
                    screen.blit(title, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))


def animateMove(move, screen, board, clock):
    global colors
    deltaR = move.endRow - move.startRow
    deltaC = move.endCol - move.startCol
    fps = 6
    frameCount = (abs(deltaR) + abs(deltaC)) * fps

    for frame in range(frameCount+1):
        frameRatio = frame/frameCount
        row, col = (move.startRow +deltaR*frameRatio, move.startCol + deltaC*frameRatio)
        draw_board(screen)
        draw_pieces(screen, board)
        color = colors[(move.endRow + move.endCol) % 2]
        endSqr = pygame.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        pygame.draw.rect(screen, color, endSqr)

        if move.pieceCaptured != '--':
            screen.blit(IMAGES[move.pieceCaptured], endSqr)

        screen.blit(IMAGES[move.pieceMoved], pygame.Rect(col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        pygame.display.flip()
        clock.tick(60)

def drawText(screen, text):
    font = pygame.font.SysFont("Century Gothic", 28, True, False)
    textObject = font.render(text, 0, pygame.Color('black'))
    textLocation = pygame.Rect( 0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)

def draw_game_state(screen, gs, validMoves, sqSelected):

    draw_board(screen)
    highlightSquares(screen, gs, validMoves, sqSelected)

   
    draw_pieces(screen, gs.board)

   

def draw_board(screen):
    global colors
    colors = [pygame.Color("#eeeed2"), pygame.Color("#769656")]
   
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors[(row+col) % 2]
            pygame.draw.rect(screen, color, pygame.Rect(col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))


def draw_pieces(screen, board):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]
            if piece != "--":
                screen.blit(IMAGES[piece], pygame.Rect(col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))

    return

if __name__ == '__main__':
    main()