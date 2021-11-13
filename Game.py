# based on code from https://stackabuse.com/minimax-and-alpha-beta-pruning-in-python

import time


class Game:
    MINIMAX = 0
    ALPHABETA = 1
    AI = 2
    HUMAN = 3

    def __init__(self, recommend=True, board_size=3, bloc_num=0, blocs_positions=[], win_size=3):
        self.board_size = board_size
        self.bloc_num = bloc_num
        self.blocs_positions = blocs_positions
        self.win_size = win_size if (win_size <= board_size) else board_size
        self.initialize_game()
        self.recommend = recommend

    def initialize_game(self):
        # self.current_state = [['.','.','.'],
        #					  ['.','.','.'],
        #					  ['.','.','.']]
        # initialize the game board to an nxn square of '.'
        self.current_state = [['.'] * self.board_size for i in range(self.board_size)]
        for bloc in self.blocs_positions:
            self.current_state[int(bloc[0])][int(bloc[2])] = '$'

        # Player X always plays first
        self.player_turn = 'X'

    def draw_board(self):
        print()
        for y in range(0, self.board_size):
            for x in range(0, self.board_size):
                print(F'{self.current_state[x][y]}', end="")
            print()
        print()

    def is_valid(self, px, py):
        if px < 0 or px > (self.board_size - 1) or py < 0 or py > (self.board_size - 1):
            return False
        elif self.current_state[px][py] != '.':
            return False
        else:
            return True

    def is_diagonal_win(self):
        n = self.board_size
        s = self.win_size
        win = False
        # loop over all squares
        for x in range(n):
            for y in range(n):
                char = self.current_state[x][y]
                if (char == '$'):
                    # no point in checking the diagonal from a block
                    continue

                # check if a large enough positive diagonal can stem from this square
                if ((n - x >= s) and (n - y >= s)):
                    # check positive diagonal on this square
                    win = True
                    for i in range(s):
                        win = win and (self.current_state[x + i][y + i] == char)
                    if win:
                        return char

                # check if a large enough positive diagonal can stem from this square
                if ((n - x >= s) and (y >= s - 1)):
                    # check negative diagonal on this square
                    win = True
                    for j in range(s):
                        win = win and (self.current_state[x + j][y - j] == char)
                    if win:
                        return char
        return '.'

    def is_end(self):
        win_X = 'X' * self.win_size
        win_O = 'O' * self.win_size
        # Vertical win
        for i in range(0, self.board_size):
            column = [item[i] for item in self.current_state]
            column_string = "".join(str(x) for x in column)
            if (win_X in column_string):
                return 'X'
            if (win_O in column_string):
                return 'O'
        # Horizontal win
        for i in range(0, self.board_size):
            row_string = "".join(str(x) for x in self.current_state[i])
            if (win_X in row_string):
                return 'X'
            if (win_O in row_string):
                return 'O'

        # Diagonal Win
        diagonal_result = self.is_diagonal_win()
        if (diagonal_result != '.'):
            return diagonal_result

        # Is whole board full?
        for i in range(0, self.board_size):
            for j in range(0, self.board_size):
                # There's an empty field, we continue the game
                if (self.current_state[i][j] == '.'):
                    return None
        # It's a tie!
        return '.'

    def check_end(self):
        self.result = self.is_end()
        # Printing the appropriate message if the game has ended
        if self.result != None:
            if self.result == 'X':
                print('The winner is X!')
            elif self.result == 'O':
                print('The winner is O!')
            elif self.result == '.':
                print("It's a tie!")
            self.initialize_game()
        return self.result

    def input_move(self):
        while True:
            print(F'Player {self.player_turn}, enter your move:')
            px = int(input('enter the x coordinate: '))
            py = int(input('enter the y coordinate: '))
            if self.is_valid(px, py):
                return (px, py)
            else:
                print('The move is not valid! Try again.')

    def switch_player(self):
        if self.player_turn == 'X':
            self.player_turn = 'O'
        elif self.player_turn == 'O':
            self.player_turn = 'X'
        return self.player_turn

    def minimax(self, max=False):
        # Minimizing for 'X' and maximizing for 'O'
        # Possible values are:
        # -1 - win for 'X'
        # 0  - a tie
        # 1  - loss for 'X'
        # We're initially setting it to 2 or -2 as worse than the worst case:
        value = 2
        if max:
            value = -2
        x = None
        y = None
        result = self.is_end()
        if result == 'X':
            return (-1, x, y)
        elif result == 'O':
            return (1, x, y)
        elif result == '.':
            return (0, x, y)
        for i in range(0, 3):
            for j in range(0, 3):
                if self.current_state[i][j] == '.':
                    if max:
                        self.current_state[i][j] = 'O'
                        (v, _, _) = self.minimax(max=False)
                        if v > value:
                            value = v
                            x = i
                            y = j
                    else:
                        self.current_state[i][j] = 'X'
                        (v, _, _) = self.minimax(max=True)
                        if v < value:
                            value = v
                            x = i
                            y = j
                    self.current_state[i][j] = '.'
        return (value, x, y)

    def alphabeta(self, alpha=-2, beta=2, max=False):
        # Minimizing for 'X' and maximizing for 'O'
        # Possible values are:
        # -1 - win for 'X'
        # 0  - a tie
        # 1  - loss for 'X'
        # We're initially setting it to 2 or -2 as worse than the worst case:
        value = 2
        if max:
            value = -2
        x = None
        y = None
        result = self.is_end()
        if result == 'X':
            return (-1, x, y)
        elif result == 'O':
            return (1, x, y)
        elif result == '.':
            return (0, x, y)
        for i in range(0, 3):
            for j in range(0, 3):
                if self.current_state[i][j] == '.':
                    if max:
                        self.current_state[i][j] = 'O'
                        (v, _, _) = self.alphabeta(alpha, beta, max=False)
                        if v > value:
                            value = v
                            x = i
                            y = j
                    else:
                        self.current_state[i][j] = 'X'
                        (v, _, _) = self.alphabeta(alpha, beta, max=True)
                        if v < value:
                            value = v
                            x = i
                            y = j
                    self.current_state[i][j] = '.'
                    if max:
                        if value >= beta:
                            return (value, x, y)
                        if value > alpha:
                            alpha = value
                    else:
                        if value <= alpha:
                            return (value, x, y)
                        if value < beta:
                            beta = value
        return (value, x, y)

    def play(self, algo=None, player_x=None, player_o=None):
        print(player_x)
        print(player_o)
        if algo == None:
            algo = self.ALPHABETA
        if player_x == None:
            player_x = self.HUMAN
        if player_o == None:
            player_o = self.HUMAN
        while True:
            self.draw_board()
            if self.check_end():
                return
            start = time.time()
            if algo == self.MINIMAX:
                if self.player_turn == 'X':
                    (_, x, y) = self.minimax(max=False)
                else:
                    (_, x, y) = self.minimax(max=True)
            else:  # algo == self.ALPHABETA
                if self.player_turn == 'X':
                    (m, x, y) = self.alphabeta(max=False)
                else:
                    (m, x, y) = self.alphabeta(max=True)
            end = time.time()
            if (self.player_turn == 'X' and player_x == self.HUMAN) or (
                    self.player_turn == 'O' and player_o == self.HUMAN):
                if self.recommend:
                    print(F'Evaluation time: {round(end - start, 7)}s')
                    print(F'Recommended move: x = {x}, y = {y}')
                (x, y) = self.input_move()
            if (self.player_turn == 'X' and player_x == self.AI) or (self.player_turn == 'O' and player_o == self.AI):
                print(F'Evaluation time: {round(end - start, 7)}s')
                print(F'Player {self.player_turn} under AI control plays: x = {x}, y = {y}')
            self.current_state[x][y] = self.player_turn
            self.switch_player()

    def heuristic1_eval(self):
        e1 = 0
        temp = 0
        for y in range(0, self.board_size):
            for x in range(0, self.board_size):
                if (temp >= 0 and self.current_state[y][x] == 'X'):
                    temp += 1
                if (temp <= 0 and self.current_state[y][x] == '0'):
                    temp -= 1
                if (self.current_state[y][x] == '$'):
                    break


def main():
    n = int(input('enter the size of the board n: '))
    b = int(input('enter the number of blocs b: '))
    s = int(input('enter the winning line-up size s: '))
    t = int(input('enter the maximum allowed time (in seconds) t: '))

    d1 = int(input('Player 1, enter maximum depth d1: '))
    d2 = int(input('Player 2, enter maximum depth d2: '))

    a1 = bool(input('enter either minimax (0) or alphabeta (1) a1: '))
    a2 = bool(input('enter either minimax (0) or alphabeta (1) a2: '))

    p1 = int(input('enter either AI (2) or Human (3) p1: '))
    p2 = int(input('enter either AI (2) or Human (3) p2: '))

    blocPositions = []
    for bloc in range(0, b):
        bx = int(input('enter the bloc position x: '))
        by = int(input('enter the bloc position y: '))
        blocPositions.append(f'{bx} {by}')

    # g = Game(recommend=True)
    g = Game(recommend=True, board_size=n, bloc_num=b, blocs_positions=blocPositions, win_size=s)
    # g.play(algo=Game.ALPHABETA,player_x=p1,player_o=p2)
    g.play(algo=Game.ALPHABETA, player_x=p1, player_o=p2)


# g.play(algo=Game.MINIMAX,player_x=Game.AI,player_o=Game.HUMAN)

if __name__ == "__main__":
    main()

