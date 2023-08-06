def solveNQueens(n : int):
    cols = set()
    posDiag = set()
    negDiag = set()

    res = []
    board = [['.' for _ in range(n)] for _ in range(n)]

    def backtrack(row):
        if (row == n):
            res.append([''.join(row) for row in board])
        for col in range(n):
            if (col in cols or row+col in posDiag or row-col in negDiag):
                continue
            cols.add(col)
            posDiag.add(row+col)
            negDiag.add(row-col)
            board[row][col] = 'Q'
            backtrack(row+1)
            cols.remove(col)
            posDiag.remove(row+col)
            negDiag.remove(row-col)
            board[row][col] = '.'
    backtrack(0)
    return res 

def printSolutions(boards):
    for board in enumerate(boards):
        print(f"Solution: {board[0]+1}")
        for row in board[1]:
            for col in row:
                print(col, end=' ')
            print()
        print()

if __name__ == "__main__":
    boards = solveNQueens(4)
    printSolutions(boards)