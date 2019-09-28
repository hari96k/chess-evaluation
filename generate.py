import chess
import chess.engine
import chess.pgn

import signal
import os
import atexit
import pandas as pd
import random

if os.name == 'posix':
    engine = chess.engine.SimpleEngine.popen_uci('/mnt/c/Users/Hari/Downloads/stockfish-9-win/stockfish-9-win/Windows/stockfish_9_x64.exe')
else:
    engine = chess.engine.SimpleEngine.popen_uci('C:/Users/Hari/Documents/stockfish-9-win/Windows/stockfish_9_x64.exe')

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

    limit = chess.engine.Limit(depth=12)
    info = engine.analyse(board=board, multipv=5, limit=limit)

    if board.is_game_over():
        board = initBoard()
        continue

    topMoves = []
    try:
        for item in info:
            move = item["pv"][0]
            topMoves.append((move.from_square, move.to_square))

        while len(topMoves) < 5:
            topMoves.append(topMoves[-1])

    except TypeError:
        board = initBoard()
        continue

    #print('Evaluation value: ', score)
    temp_train.append([board.fen(), topMoves])

    #print(board)
    #print(str(score) + '\n\n')
    print(str(idx))
    idx += 1
