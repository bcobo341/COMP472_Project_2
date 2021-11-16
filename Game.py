import time
import numpy as np


class Game:
    MINIMAX = 0
    ALPHABETA = 1
    AI = 2
    HUMAN = 3
    COLUMN = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
              'V', 'W', 'X', 'Y', 'Z']

    def __init__(self, recommend=True, board_size=3, bloc_num=0, blocs_positions=[], win_size=3, t=0, max_depth_X=0, max_depth_O=0, series=False, winner='.'):
        self.recommend = recommend
        # game parameters
        self.board_size = board_size
        self.bloc_num = bloc_num
        self.blocs_positions = blocs_positions
        self.win_size = win_size if (win_size <= board_size) else board_size
        self.t = t
        self.max_depth_X = max_depth_X
        self.max_depth_O = max_depth_O
        self.series = series
        self.winner = winner

        # stats
        self.all_evaluation_run_time = []
        self.all_evaluation_run_time_per_round = []
        self.evaluation_count = 0
        self.evaluation_count_per_round = 0
        self.evaluation_count_by_depth = {}
        self.evaluation_count_by_depth_per_round = {}

        self.turn_count = 0
        self.initialize_game()

    def initialize_game(self):
        # initialize the game board to an nxn square of '.'
        self.current_state = [['.'] * self.board_size for i in range(self.board_size)]

        # generate blocs if any
        for bloc in self.blocs_positions:
            self.current_state[int(bloc[0])][int(bloc[2])] = '$'

        # Player X always plays first
        self.player_turn = 'X'

    def draw_board(self, trace=False, trace_file=None):
        # if game trace option is on, output it in the .txt file
        if trace:
            space = ' '
            trace_file.write("\n")
            for y in range(0, self.board_size):
                if (y != 0):
                    space = ''
                trace_file.write(str(space * 2) + str(self.COLUMN[y]))
            trace_file.write("\n")
            trace_file.write(" +" + str("-" * self.board_size) + "\n")
            for y in range(0, self.board_size):
                for x in range(0, self.board_size):
                    if (x == 0):
                        trace_file.write(str(y) + "|" + str(self.current_state[x][y]))
                    else:
                        trace_file.write(str(self.current_state[x][y]))
                trace_file.write("\n")
            trace_file.write("\n")
        space = ' '
        print()
        for y in range(0, self.board_size):
            if (y != 0):
                space = ''
            print(F'{space * 2}{self.COLUMN[y]}', end="")
        print()
        print(" +" + "-" * self.board_size)
        for y in range(0, self.board_size):
            for x in range(0, self.board_size):
                if (x == 0):
                    print(F'{y}|{self.current_state[x][y]}', end="")
                else:
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

    def is_end(self):
        # generate the win condition string for X and O
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
        matrix = np.array(self.current_state)
        diags = [matrix[::-1, :].diagonal(i) for i in range(-matrix.shape[0] + 1, matrix.shape[1])]
        diags.extend(matrix.diagonal(i) for i in range(matrix.shape[1] - 1, -matrix.shape[0], -1))

        for y in diags:
            diag_string = "".join(str(x) for x in y.tolist())
            if (win_X in diag_string):
                return 'X'
            if (win_O in diag_string):
                return 'O'

        # Is whole board full?
        for i in range(0, self.board_size):
            for j in range(0, self.board_size):
                # There's an empty field, we continue the game
                if (self.current_state[i][j] == '.'):
                    return None
        # It's a tie!
        return '.'

    def check_end(self, trace=False, trace_file=None):
        self.result = self.is_end()
        # Printing the appropriate message if the game has ended
        if self.result != None:
            if self.result == 'X':
                self.winner = 'X'
                print('The winner is X!')
                if (trace):
                    trace_file.write("The winner is X!")
            elif self.result == 'O':
                self.winner = 'O'
                print('The winner is O!')
                if (trace):
                    trace_file.write("The winner is O!")
            elif self.result == '.':
                self.winner = '.'
                print("It's a tie!")
                if (trace):
                    trace_file.write("It's a tie!")
            self.initialize_game()
        return self.result

    def input_move(self):
        while True:
            p = str(input(F'Player {self.player_turn}, enter your move:'))
            move = p.split(' ')
            px = -1
            py = int(move[1])
            for y in range(0, len(self.COLUMN)):
                if (self.COLUMN[y] == move[0]):
                    px = y
                    break

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

    def calculate_current_max_depth(self):
        # to calculate the max_depth the tree currently has (how many moves are available)
        value = 0
        for i in range(0, self.board_size):
            row_string = "".join(str(x) for x in self.current_state[i])
            value += row_string.count('.')
        return value

    def update_evaluation_stat(self, current_depth = 0):
        try:
            self.evaluation_count_by_depth[str(current_depth)] = self.evaluation_count_by_depth.get(str(current_depth)) + 1
        except TypeError:
            self.evaluation_count_by_depth[str(current_depth)] = 1
        try:
            self.evaluation_count_by_depth_per_round[str(current_depth)] = self.evaluation_count_by_depth_per_round.get(str(current_depth)) + 1
        except TypeError:
            self.evaluation_count_by_depth_per_round[str(current_depth)] = 1
        self.evaluation_count_per_round +=1
        self.evaluation_count += 1

    def minimax(self, max=False, current_depth=0, currentX=0, currentY=0, h=0, startTime=0, currentTime = 0, max_depth = -1):
        # Maximizing for 'X' and minimizing for 'O'
        # Possible values are:
        # 10^win_size - win for 'X'
        # 0  - a tie
        # -10^win_size  - loss for 'X'
        # We're initially setting it to 2*10^win_size or -2*10^win_size as worse than the worst case:
        currentTime = time.time()
        if max_depth == -1:
            max_depth = self.max_depth_X
            if max:
                max_depth = self.max_depth_O
            if max_depth > self.calculate_current_max_depth():
                max_depth = self.calculate_current_max_depth()
        
        value = -2 * pow(10, self.win_size)
        if max:
            value = 2 * pow(10, self.win_size)

        x = None
        y = None

        result = self.is_end()
        if result == 'X':
            self.update_evaluation_stat(current_depth=current_depth)
            return (1 * pow(10, self.win_size), x, y)
        elif result == 'O':
            self.update_evaluation_stat(current_depth=current_depth)
            return (-1 * pow(10, self.win_size), x, y)
        elif result == '.':
            self.update_evaluation_stat(current_depth=current_depth)
            return (0, x, y)
        # if result is not any of the ending condition, calculate the heuristic value and return
        if current_depth == max_depth:
            if h == 1:
                h_value = self.heuristic1_eval(x=currentX, y=currentY)
                self.update_evaluation_stat(current_depth=current_depth)
                return (h_value, x, y)
            elif h == 2:
                h_value = self.heuristic2_eval()
                self.update_evaluation_stat(current_depth=current_depth)
                return (h_value, x, y)
        if currentTime - startTime >= self.t - 0.15:
            if h == 1:
                h_value = self.heuristic1_eval(x=currentX, y=currentY)
                self.update_evaluation_stat(current_depth=current_depth)
                return (h_value, x, y)
            elif h == 2:
                h_value = self.heuristic2_eval()
                self.update_evaluation_stat(current_depth=current_depth)
                return (h_value, x, y)

        for i in range(0, self.board_size):
            for j in range(0, self.board_size):
                if self.current_state[i][j] == '.':
                    if max:
                        self.current_state[i][j] = 'O'
                        (v, _, _) = self.minimax(max=False, current_depth=current_depth + 1, currentX=i, currentY=j, h=h, startTime=startTime, currentTime = time.time(), max_depth=max_depth)
                        if v < value:
                            value = v
                            x = i
                            y = j
                    else:
                        self.current_state[i][j] = 'X'
                        (v, _, _) = self.minimax(max=True, current_depth=current_depth + 1, h=h, startTime=startTime, currentTime = time.time(), max_depth=max_depth)
                        if v > value:
                            value = v
                            x = i
                            y = j
                    self.current_state[i][j] = '.'
        return (value, x, y)

    def alphabeta(self, alpha=np.Inf, beta=-1 * np.Inf, max=False, current_depth=0, currentX=0, currentY=0, h=0, startTime=0, currentTime = 0, max_depth = -1):
        # Minimizing for 'X' and maximizing for 'O'
        # Possible values are:
        # 10^win_size - win for 'X'
        # 0  - a tie
        # -10^win_size  - loss for 'X'
        # We're initially setting it to 2*10^win_size or -2*10^win_size as worse than the worst case:
        if max_depth == -1:
            max_depth = self.max_depth_X
            if max:
                max_depth = self.max_depth_O
            if max_depth > self.calculate_current_max_depth():
                max_depth = self.calculate_current_max_depth()

        value = -2 * pow(10, self.win_size)
        if max:
            value = 2 * pow(10, self.win_size)
        x = None
        y = None

        result = self.is_end()
        if result == 'X':
            self.update_evaluation_stat(current_depth=current_depth)
            return (1 * pow(10, self.win_size), x, y)
        elif result == 'O':
            self.update_evaluation_stat(current_depth=current_depth)
            return (-1 * pow(10, self.win_size), x, y)
        elif result == '.':
            self.update_evaluation_stat(current_depth=current_depth)
            return (0, x, y)
        # if result is not any of the ending condition, calculate the heuristic value and return
        if current_depth == max_depth:
            if h == 1:
                h_value = self.heuristic1_eval(x=currentX, y=currentY)
                self.update_evaluation_stat(current_depth=current_depth)
                return (h_value, x, y)
            elif h == 2:
                h_value = self.heuristic2_eval()
                self.update_evaluation_stat(current_depth=current_depth)
                return (h_value, x, y)
        if currentTime - startTime >= self.t - 0.15:
            if h == 1:
                h_value = self.heuristic1_eval(x=currentX, y=currentY)
                self.update_evaluation_stat(current_depth=current_depth)
                return (h_value, x, y)
            elif h == 2:
                h_value = self.heuristic2_eval()
                self.update_evaluation_stat(current_depth=current_depth)
                return (h_value, x, y)

        for i in range(0, self.board_size):
            for j in range(0, self.board_size):
                if self.current_state[i][j] == '.':
                    if max:
                        self.current_state[i][j] = 'O'
                        (v, _, _) = self.alphabeta(alpha, beta, max=False, current_depth=current_depth + 1, h=h, startTime=startTime, currentTime = time.time(), max_depth=max_depth)
                        if v < value:
                            value = v
                            x = i
                            y = j
                    else:
                        self.current_state[i][j] = 'X'
                        (v, _, _) = self.alphabeta(alpha, beta, max=True, current_depth=current_depth + 1, h=h, startTime=startTime, currentTime = time.time(), max_depth=max_depth)
                        if v > value:
                            value = v
                            x = i
                            y = j
                    self.current_state[i][j] = '.'
                    if max:
                        if value <= beta:
                            return (value, x, y)
                        if value < alpha:
                            alpha = value
                    else:
                        if value >= alpha:
                            return (value, x, y)
                        if value > beta:
                            beta = value
        return (value, x, y)

    def play(self, algo1=None, algo2=None, player_x=None, player_o=None, heuristic_x=0, heuristic_o=0):
        trace = False
        trace_file = None

        # only trace to file if it's AI vs AI
        if (player_x == self.AI and player_o == self.AI):
            trace = True
            trace_file_name = "gameTrace-" + str(self.board_size) + str(self.bloc_num) + str(self.win_size) + str(self.t) + ".txt"
            trace_file = open(trace_file_name, 'a')
            trace_file.write("\n==================================================================================\n\n")
            trace_file.write("n=" + str(self.board_size) + " ")
            trace_file.write("b=" + str(self.bloc_num) + " ")
            trace_file.write("s=" + str(self.win_size) + " ")
            trace_file.write("t=" + str(self.t) + "\n")
            trace_file.write("blocs=" + str(self.blocs_positions) + "\n")
            trace_file.write("Player 1: AI ")
            trace_file.write("d=" + str(self.max_depth_X))
            if (algo1==self.MINIMAX):
                trace_file.write(" a=False e1(regular)\n")
            else:
                trace_file.write(" a=True e1(regular)\n")
            trace_file.write("Player 2: AI ")
            trace_file.write("d=" + str(self.max_depth_O))
            if (algo2==self.MINIMAX):
                trace_file.write(" a=False e2(defensive)\n")
            else:
                trace_file.write(" a=True e2(defensive)\n")

        # default players if not specified
        if player_x == None:
            player_x = self.HUMAN
        if player_o == None:
            player_o = self.HUMAN

        # main game loop
        while True:
            if trace and self.all_evaluation_run_time!=[]:
                trace_file.write("\n")
                trace_file.write("i\tAverage evaluation time(s): " + str(np.average(self.all_evaluation_run_time_per_round)) + "\n")
                trace_file.write("ii\tHeuristic evaluations: " + str(self.evaluation_count_per_round) + "\n")
                trace_file.write("iii\tEvaluations by depth: " + str(self.evaluation_count_by_depth_per_round) + "\n")
                trace_file.write("iv\tAverage evaluation depth: " + str(np.average(list(map(int, self.evaluation_count_by_depth_per_round.keys())))) + "\n")
                self.evaluation_count_per_round = 0
                self.all_evaluation_run_time_per_round = []
                self.evaluation_count_by_depth_per_round = {}

            self.draw_board(trace=trace, trace_file=trace_file)

             # if the game is over, stop tracing
            if self.check_end(trace, trace_file):
                trace_file.write("\n")
                trace_file.write("i\tAverage evaluation time(s): " + str(np.average(self.all_evaluation_run_time)) + "\n")
                trace_file.write("ii\tHeuristic evaluations: " + str(self.evaluation_count) + "\n")
                trace_file.write("iii\tEvaluations by depth: " + str(self.evaluation_count_by_depth) + "\n")
                trace_file.write("iv\tAverage evaluation depth: " + str(np.average(list(map(int, self.evaluation_count_by_depth.keys())))) + "\n")
                trace_file.write("vi\tTotal moves: " + str(self.turn_count) + "\n")
                trace_file.flush()
                trace_file.close()
                return
        
            start = time.time()
            if self.player_turn == 'X':
                if algo1 == self.MINIMAX:
                    triplet = self.minimax(max=False, h=heuristic_x, startTime=time.time())
                    if triplet == None:
                        continue
                    (_, x, y) = triplet
                else:
                    triplet = self.alphabeta(max=False, h=heuristic_x, startTime=time.time())
                    if triplet == None:
                        continue
                    (m, x, y) = triplet
            else:
                if algo2 == self.MINIMAX:
                    triplet = self.minimax(max=True, h=heuristic_o, startTime=time.time())
                    if triplet == None:
                        continue
                    (_, x, y) = triplet
                else:
                    triplet = self.alphabeta(max=True, h=heuristic_o, startTime=time.time())
                    if triplet == None:
                        continue
                    (m, x, y) = triplet
            end = time.time()
            # if it's human vs human, show recommendation based on `recommand`
            if (self.player_turn == 'X' and player_x == self.HUMAN) or (
                    self.player_turn == 'O' and player_o == self.HUMAN):
                if self.recommend:
                    execution_time = round(end - start, 7)
                    self.all_evaluation_run_time.append(execution_time)
                    self.all_evaluation_run_time_per_round.append(execution_time)
                    print(F'Evaluation time: {execution_time}s')
                    print(F'Recommended move: {self.COLUMN[x]}{y}')
                (x, y) = self.input_move()
            if (self.player_turn == 'X' and player_x == self.AI) or (self.player_turn == 'O' and player_o == self.AI):
                execution_time = round(end - start, 7)
                self.all_evaluation_run_time.append(execution_time)
                self.all_evaluation_run_time_per_round.append(execution_time)
                print(F'Evaluation time: {execution_time}s')
                print(F'Player {self.player_turn} under AI control plays: {self.COLUMN[x]}{y}')
            self.current_state[x][y] = self.player_turn
            if (trace):
                if (self.player_turn == 'X' and player_x == self.HUMAN) or (
                        self.player_turn == 'O' and player_o == self.HUMAN):
                    trace_file.write(
                        "\nPlayer " + self.player_turn + " plays: " + str(self.COLUMN[x]) + "" + str(y) + "\n")
                if (self.player_turn == 'X' and player_x == self.AI) or (
                        self.player_turn == 'O' and player_o == self.AI):
                    trace_file.write(
                        "\nPlayer " + self.player_turn + " plays under AI control: " + str(self.COLUMN[x]) + "" + str(
                            y) + "\n")
            self.switch_player()
            self.turn_count += 1

    # Heuristic 1: simple heuristic, checks adjacent positions against proposed x, y
    def heuristic1_eval(self, x=0, y=0):
        e1 = 0
        char = self.current_state[x][y]
        if char == 'X':  # maximize
            if x > 0:  # left boarder
                e1 += 1 if self.current_state[x - 1][y] == char else 0
                if y > 0:
                    e1 += 1 if self.current_state[x - 1][y - 1] == char else 0
                if y < self.board_size - 1:
                    e1 += 1 if self.current_state[x - 1][y + 1] == char else 0

            if x < self.board_size - 1:  # right boarder
                e1 += 1 if self.current_state[x + 1][y] == char else 0
                if y > 0:
                    e1 += 1 if self.current_state[x + 1][y - 1] == char else 0
                if y < self.board_size - 1:
                    e1 += 1 if self.current_state[x + 1][y + 1] == char else 0

            e1 += 1 if self.current_state[x][y] == char else 0
            if y > 0:
                e1 += 1 if self.current_state[x][y - 1] == char else 0
            if y < self.board_size - 1:
                e1 += 1 if self.current_state[x][y + 1] == char else 0

            elif char == 'O':  # minimize
                if x > 0:  # left boarder
                    e1 -= 1 if self.current_state[x - 1][y] == char else 0
                    if y > 0:
                        e1 -= 1 if self.current_state[x - 1][y - 1] == char else 0
                    if y < self.board_size - 1:
                        e1 -= 1 if self.current_state[x - 1][y + 1] == char else 0

                if x < self.board_size - 1:  # right boarder
                    e1 -= 1 if self.current_state[x + 1][y] == char else 0
                    if y > 0:
                        e1 -= 1 if self.current_state[x + 1][y - 1] == char else 0
                    if y < self.board_size - 1:
                        e1 -= 1 if self.current_state[x + 1][y + 1] == char else 0

                e1 -= 1 if self.current_state[x][y] == char else 0
                if y > 0:
                    e1 -= 1 if self.current_state[x][y - 1] == char else 0
                if y < self.board_size - 1:
                    e1 -= 1 if self.current_state[x][y + 1] == char else 0
        return e1

    # Heuristic 2: more sophisticated and complex to compute
    def heuristic2_eval(self):
        e2 = 0
        tempx = 0
        tempo = 0
        # Vertical
        for i in range(0, self.board_size):
            column = [item[i] for item in self.current_state]
            column_string = "".join(str(x) for x in column)
            tempx = column_string.count("X")
            tempo = column_string.count("O")
            if (tempx > tempo):
                e2 += pow(10, tempx)
            if (tempo > tempx):
                e2 -= pow(10, tempo)
            if (tempx == tempo and tempx != 0):
                e2 += pow(10, tempx)
            tempx = 0
            tempo = 0
        # Horizontal
        for i in range(0, self.board_size):
            row_string = "".join(str(x) for x in self.current_state[i])
            tempx = row_string.count("X")
            tempo = row_string.count("O")
            if (tempx > tempo):
                e2 += pow(10, tempx)
            if (tempo > tempx):
                e2 -= pow(10, tempo)
            if (tempx == tempo and tempx != 0):
                e2 += pow(10, tempx)
            tempx = 0
            tempo = 0
        # Diagonal
        matrix = np.array(self.current_state)
        diags = [matrix[::-1, :].diagonal(i) for i in range(-matrix.shape[0] + 1, matrix.shape[1])]
        diags.extend(matrix.diagonal(i) for i in range(matrix.shape[1] - 1, -matrix.shape[0], -1))

        for y in diags:
            row_string = "".join(str(x) for x in y.tolist())
            tempx = row_string.count("X")
            tempo = row_string.count("O")
            if (tempx > tempo and len(y.tolist()) >= self.win_size):
                e2 += pow(10, tempx)
            if (tempo > tempx and len(y.tolist()) >= self.win_size):
                e2 -= pow(10, tempo)
            if (tempx == tempo and len(y.tolist()) >= self.win_size and tempx != 0):
                e2 += pow(10, tempx)
            tempx = 0
            tempo = 0
        return e2


def combine_dict(d1, d2):
    return {key: d1.get(key, 0) + d2.get(key, 0) for key in d2}


def main():
    series = input('Run multiple games in series? (Y)es / (N)o: ')
    series = (series == 'Y' or series == 'y')
    r = 1

    if (series):
        r = int(input('enter the number of rounds r: '))

    n = int(input('enter the size of the board n: '))
    b = int(input('enter the number of blocs b: '))
    s = int(input('enter the winning line-up size s: '))
    t = int(input('enter the maximum allowed time (in seconds) t: '))

    d1 = int(input('Player 1, enter maximum depth d1: '))
    d2 = int(input('Player 2, enter maximum depth d2: '))

    a1 = int(input('enter either minimax (0) or alphabeta (1) for player 1: '))
    a2 = int(input('enter either minimax (0) or alphabeta (1) for player 2: '))

    if (not series):
        p1 = int(input('Player 1, enter either AI (2) or Human (3) p1: '))
        p2 = int(input('Player 2, enter either AI (2) or Human (3) p2: '))
    else:
        print("\nIn series mode, both players are AI.")
        p1 = 2
        p2 = 2

    h1 = 0
    h2 = 0
    if (not series):
        if p1 == 2:
            h1 = int(input('Player 1, enter either heuristic (1) or (2) h1: '))
        if p2 == 2:
            h2 = int(input('Player 2, enter either heuristic (1) or (2) h2: '))
    else:
        h1 = 1
        h2 = 2
        print("\nIn series mode, one player is set to use each heuristic.")

    blocPositions = []
    for _ in range(0, b):
        bx = int(input('enter the bloc position x: '))
        by = int(input('enter the bloc position y: '))
        blocPositions.append(f'{bx} {by}')

    if (series):
        scoreboard = open("scoreboard.txt", "a")
        scoreboard.write("New Series:\n")
        scoreboard.write("=============================================\n")
        scoreboard.write("Board Size (n): " + str(n) + "\n")
        scoreboard.write("Block Count (b): " + str(b) + "\n")
        scoreboard.write("Win Size (s): " + str(s) + "\n")
        scoreboard.write("AI Time (t): " + str(t) + "\n")
        scoreboard.write("Bloc Positions: " + str(blocPositions) + "\n")
        scoreboard.write("\nPlayer 1 info: \n")
        scoreboard.write("max depth:\t" + str(d1) + "\n")
        algoName = "Minimax" if a1 == 0 else "Alpha Beta"
        scoreboard.write("algorithm:\t" + str(algoName) + "\n")
        scoreboard.write("heuristic:\te" + str(h1) + "\n")
        scoreboard.write("\nPlayer 2 info: \n")
        scoreboard.write("max depth:\t" + str(d2) + "\n")
        algoName = "Minimax" if a2 == 0 else "Alpha Beta"
        scoreboard.write("algorithm:\t" + str(algoName) + "\n")
        scoreboard.write("heuristic:\te" + str(h2) + "\n")
        scoreboard.flush()
        scoreboard.close()

        e1_wins = 0
        e2_wins = 0

        series_all_heuristic_run_times = []
        series_evaluation_count_by_depths = {}
        series_heuristic_evaluation_count = 0
        turn_counts = []

        for i in range(2 * r):
            g = Game(recommend=True, board_size=n, bloc_num=b, blocs_positions=blocPositions, win_size=s, max_depth_X=d1, max_depth_O=d2, t=t, series=True)
            g.play(algo1=a1, algo2=a2, player_x=p1, player_o=p2, heuristic_x=h1, heuristic_o=h2)
            winner = g.winner

            turn_counts.append(g.turn_count)
            series_heuristic_evaluation_count += g.evaluation_count
            series_all_heuristic_run_times.extend(g.all_evaluation_run_time)
            series_evaluation_count_by_depths = combine_dict(g.evaluation_count_by_depth, series_evaluation_count_by_depths) if bool(series_evaluation_count_by_depths) else g.evaluation_count_by_depth

            if i % 2 == 0:
                if winner == 'X':
                    e1_wins += 1
                else:
                    e2_wins += 1
            else:
                if winner == 'O':
                    e1_wins += 1
                else:
                    e2_wins += 1

            # swap players
            a_temp = a1
            a1 = a2
            a2 = a_temp
            h_temp = h1
            h1 = h2
            h2 = h_temp

        scoreboard = open("scoreboard.txt", "a")
        scoreboard.write("\n\nGames played: " + str(2 * r) + "\n")
        scoreboard.write("e1 win percentage: " + str(100 * e1_wins / (2 * r)) + "%\n")
        scoreboard.write("e2 win percentage: " + str(100 * e2_wins / (2 * r)) + "%\n")
        scoreboard.write("\n")

        scoreboard.write("i\tAverage evaluation time(s): " + str(np.average(series_all_heuristic_run_times)) + "\n")
        scoreboard.write("ii\tTotal heuristic evaluations: " + str(series_heuristic_evaluation_count) + "\n")
        scoreboard.write("iii\tEvaluations by depth: " + str(series_evaluation_count_by_depths) + "\n")
        scoreboard.write("iv\tAverage evaluation depth: " + str(np.average(list(map(int, series_evaluation_count_by_depths)))) + "\n")
        scoreboard.write("iv\tAverage turn count: " + str(np.average(turn_counts)) +"\n")
        scoreboard.write("\n=============================================\n\n\n")
        scoreboard.flush()
        scoreboard.close()

    else:
        g = Game(recommend=True, board_size=n, bloc_num=b, blocs_positions=blocPositions, win_size=s, max_depth_X=d1, max_depth_O=d2, t=t)
        g.play(algo1=a1, algo2=a2, player_x=p1, player_o=p2, heuristic_x=h1, heuristic_o=h2)

if __name__ == "__main__":
    main()

