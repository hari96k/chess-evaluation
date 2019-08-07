import chess
import chess.uci
import chess.pgn

import signal
import os
import atexit
import pandas as pd
import random


handler = chess.uci.InfoHandler()

if os.name == 'posix':
    engine = chess.uci.popen_engine('/mnt/c/Users/Hari/Downloads/stockfish-9-win/stockfish-9-win/Windows/stockfish_9_x64.exe')
else:
    engine = chess.uci.popen_engine('C:/Users/Hari/Documents/stockfish-9-win/Windows/stockfish_9_x64.exe')
engine.info_handlers.append(handler)


df_cols = ['Position', 'Score']
if os.path.isfile('train.csv'):
    df = pd.read_csv('train.csv')
else:
    df = pd.DataFrame(columns = df_cols)


def exit_handler():
    fin = pd.concat([df, pd.DataFrame(temp_train, columns = df_cols)], ignore_index = True)
    fin.to_csv('train.csv', index=False)
    print('Train.csv Updated!')
    print(fin.head())


atexit.register(exit_handler)
signal.signal(signal.SIGINT, exit_handler)

'''
Guarantees the initial board is not in checkmate
initMoves specifies the number of random moves past the starting position
'''


def initBoard():
    initMoves = 3
    board = chess.Board()

    for i in range(0, initMoves):
        randMove = random.choice(list(board.legal_moves))
        board.push(randMove)

        if board.is_checkmate():
            board.reset()
            i = 0
    return board


numPositions = 50000

board = initBoard()
temp_train = []
idx = 0

while True:
#for i in range(0, numPositions):
    randMove = random.choice(list(board.legal_moves))
    # print('Random move: ', randMove)

    board.push(randMove)
    engine.position(board)

    if board.is_game_over():
        board = initBoard()
        continue

    engine.go(depth=16)
    try:
        score = handler.info["score"][1].cp / 100.0
    except TypeError:
        board = initBoard()
        continue

    #print('Evaluation value: ', score)
    temp_train.append([board.fen(), score])

    #print(board)
    #print(str(score) + '\n\n')
    print(str(idx))
    idx += 1
