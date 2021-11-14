import time
import numpy as np

class Game:
    MINIMAX = 0
    ALPHABETA = 1
    AI = 2
    HUMAN = 3
    
    def __init__(self, recommend = True, board_size = 3, bloc_num=0, blocs_positions=[], win_size = 3, t = 0, max_depth_X=0, max_depth_O=0):
        self.recommend = recommend
        self.board_size = board_size
        self.bloc_num=bloc_num
        self.blocs_positions=blocs_positions
        self.win_size = win_size if (win_size <= board_size) else board_size
        self.t = t
        self.max_depth_X = max_depth_X
        self.max_depth_O = max_depth_O
        self.all_heuristic_run_time = []
        self.initialize_game()
        
    def initialize_game(self):
        # initialize the game board to an nxn square of '.'
        self.current_state = [ ['.']*self.board_size for i in range(self.board_size)]

        # generate blocs if any
        for bloc in self.blocs_positions:
            self.current_state[int(bloc[0])][int(bloc[2])] = '$'

        # Player X always plays first
        self.player_turn = 'X'

    def draw_board(self, trace = False, trace_file = None):
        if trace:
            print()
            trace_file.write("\n")
            for y in range(0, self.board_size):
                for x in range(0, self.board_size):
                    trace_file.write(str(self.current_state[x][y]))
                    print(F'{self.current_state[x][y]}', end="")
                print()
                trace_file.write("\n")
            print()
            trace_file.write("\n")
        else:
            print()
            for y in range(0, self.board_size):
                for x in range(0, self.board_size):
                    print(F'{self.current_state[x][y]}', end="")
                print()
            print()

    def is_valid(self, px, py):
        if px < 0 or px > (self.board_size-1) or py < 0 or py > (self.board_size-1):
            return False
        elif self.current_state[px][py] != '.':
            return False
        else:
            return True

    def is_end(self):
        # generate the win condition string for X and O
        win_X = 'X'*self.win_size
        win_O = 'O'*self.win_size
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
        diags = [matrix[::-1,:].diagonal(i) for i in range(-matrix.shape[0]+1,matrix.shape[1])]
        diags.extend(matrix.diagonal(i) for i in range(matrix.shape[1]-1,-matrix.shape[0],-1))

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
                print('The winner is X!')
                if (trace):
                    trace_file.write("The winner is X!")
            elif self.result == 'O':
                print('The winner is O!')
                if (trace):
                    trace_file.write("The winner is O!")
            elif self.result == '.':
                print("It's a tie!")
                if (trace):
                    trace_file.write("It's a tie!")
            self.initialize_game()
        return self.result

    def input_move(self):
        while True:
            print(F'Player {self.player_turn}, enter your move:')
            px = int(input('enter the x coordinate: '))
            py = int(input('enter the y coordinate: '))
            if self.is_valid(px, py):
                return (px,py)
            else:
                print('The move is not valid! Try again.')

    def switch_player(self):
        if self.player_turn == 'X':
            self.player_turn = 'O'
        elif self.player_turn == 'O':
            self.player_turn = 'X'
        return self.player_turn
        
    def calculate_current_max_depth(self):
        value = 0
        for i in range(0, self.board_size):
            row_string = "".join(str(x) for x in self.current_state[i])
            value+=row_string.count('.')
        return value

    def minimax(self, max=False, current_depth=0, currentX=0, currentY=0):
        # Maximizing for 'X' and minimizing for 'O'
        # Possible values are:
        # 10^win_size - win for 'X'
        # 0  - a tie
        # -10^win_size  - loss for 'X'
        # We're initially setting it to 2*10^win_size or -2*10^win_size as worse than the worst case:
        max_depth = self.max_depth_O
        value = -2*pow(10, self.win_size)

        if max:
            value = 2*pow(10, self.win_size)
            max_depth = self.max_depth_X

        if max_depth > self.calculate_current_max_depth():
            max_depth = self.calculate_current_max_depth()

        x = None
        y = None

        result = self.is_end()
        if result == 'X':
            return (1*pow(10, self.win_size), x, y)
        elif result == 'O':
            return (-1*pow(10, self.win_size), x, y)
        elif result == '.':
            return (0, x, y)
        if current_depth == max_depth:
            return (self.heuristic2_eval(), x, y)
            # return (self.heuristic1_eval(x=currentX, y=currentY), x, y)

        # no result, calculate for heuristic value when max_depth is reached
        for i in range(0, self.board_size):
            for j in range(0, self.board_size):
                if self.current_state[i][j] == '.':
                    if max:
                        self.current_state[i][j] = 'O'
                        (v, _, _) = self.minimax(max=False, current_depth=current_depth+1, currentX=i, currentY=j)
                        if v < value:
                            value = v
                            x = i
                            y = j
                    else:
                        self.current_state[i][j] = 'X'
                        (v, _, _) = self.minimax(max=True, current_depth=current_depth+1)
                        if v > value:
                            value = v
                            x = i
                            y = j
                    self.current_state[i][j] = '.'
        return (value, x, y)

    def alphabeta(self, alpha=-1*np.Inf, beta=np.Inf, max=False, currentX=0, currentY=0):
        # Minimizing for 'X' and maximizing for 'O'
        # Possible values are:
        # 10^win_size - win for 'X'
        # 0  - a tie
        # -10^win_size  - loss for 'X'
        # We're initially setting it to 2*10^win_size or -2*10^win_size as worse than the worst case:
        max_depth = self.max_depth_O    
        value = -2*pow(10, self.win_size)
        if max:
            value = 2*pow(10, self.win_size)
        x = None
        y = None
        result = self.is_end()
        if result == 'X':
            return (-1, x, y)
        elif result == 'O':
            return (1, x, y)
        elif result == '.':
            return (0, x, y)
        for i in range(0, self.board_size):
            for j in range(0, self.board_size):
                if self.current_state[i][j] == '.':
                    if max:
                        self.current_state[i][j] = 'O'
                        (v, _, _) = self.alphabeta(alpha, beta, max=False)
                        if v < value:
                            value = v
                            x = i
                            y = j
                        beta = min(beta, v)
                        if beta <= alpha:
                            break
                    else:
                        self.current_state[i][j] = 'X'
                        (v, _, _) = self.alphabeta(alpha, beta, max=True)
                        if v > value:
                            value = v
                            x = i
                            y = j
                        alpha = max(alpha, v)
                        if beta <= alpha:
                            break
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

    def play(self,algo=None,player_x=None,player_o=None):
        trace = False
        trace_file = None
        
        # only trace to file if it's AI vs AI
        if (player_x == self.AI and player_o == self.AI):
            trace = True
            trace_file_name = "gameTrace-n" + str(self.board_size) + "b" + str(self.bloc_num) + "s" + str(self.win_size) + "t" + str(self.t)
            trace_file = open(trace_file_name, 'w')
            trace_file.write("Board Size (n): " + str(self.board_size) + "\n")
            trace_file.write("Block Count (b): " + str(self.bloc_num) + "\n")
            trace_file.write("Win Size (s): " + str(self.win_size) + "\n")
            trace_file.write("AI Time (t): " + str(self.t) + "\n")
            trace_file.write("Player X: " + str(player_x) + "\n")
            trace_file.write("Player Y: " + str(player_o) + "\n")

        # default players if not specified
        if player_x == None:
            player_x = self.HUMAN
        if player_o == None:
            player_o = self.HUMAN

        # main game loop
        while True:
            self.draw_board(trace=trace, trace_file=trace_file)
            # if the game is over, stop tracing
            if self.check_end(trace, trace_file):
                if trace:
                    trace_file.write("\n")
                    trace_file.write("i\tAverage evaluation time: " + str(np.average(self.all_heuristic_run_time)) + "\n")
                    trace_file.write("ii\tTotal heuristic evaluations: " + str(len(self.all_heuristic_run_time)) + "\n")
                    # trace_file.write("iii\tEvaluations by depth: " + str(len(self.all_heuristic_run_time)) + "\n")
                    trace_file.flush()
                    trace_file.close()
                return
            start = time.time()
            if algo == self.MINIMAX:
                if self.player_turn == 'X':
                    (_, x, y) = self.minimax(max=False)
                else:
                    (_, x, y) = self.minimax(max=True)
            else: # algo == self.ALPHABETA
                if self.player_turn == 'X':
                    (m, x, y) = self.alphabeta(max=False)
                else:
                    (m, x, y) = self.alphabeta(max=True)
            end = time.time()
            # if it's human vs human, show recommendation based on `recommand`
            if (self.player_turn == 'X' and player_x == self.HUMAN) or (self.player_turn == 'O' and player_o == self.HUMAN):
                    if self.recommend:
                        print(F'Evaluation time: {round(end - start, 7)}s')
                        print(F'Recommended move: x = {x}, y = {y}')
                    (x,y) = self.input_move()
            if (self.player_turn == 'X' and player_x == self.AI) or (self.player_turn == 'O' and player_o == self.AI):
                        print(F'Evaluation time: {round(end - start, 7)}s')
                        print(F'Player {self.player_turn} under AI control plays: x = {x}, y = {y}')
            self.current_state[x][y] = self.player_turn
            if (trace):
                trace_file.write("Player: " + self.player_turn + "\n")
                trace_file.write("Move: (" + str(x) + ", " + str(y) + ")\n")
            self.switch_player()

    # Heuristic 1: simple heuristic, checks adjacent positions against proposed x, y
    def heuristic1_eval(self, x=0, y=0):
        start_time = time.time()
        e1 = 0
        char = self.current_state[x][y]
        if char == 'X': # maximize
            if x > 0: # left boarder
                e1 += 1 if self.current_state[x-1][y] == char else 0
                if y > 0:
                    e1 += 1 if self.current_state[x-1][y-1] == char else 0
                if y < self.board_size - 1:
                    e1 += 1 if self.current_state[x-1][y+1] == char else 0

            if x < self.board_size - 1: #right boarder
                e1 += 1 if self.current_state[x+1][y] == char else 0
                if y > 0:
                    e1 += 1 if self.current_state[x+1][y-1] == char else 0
                if y < self.board_size - 1:
                    e1 += 1 if self.current_state[x+1][y+1] == char else 0

            e1 += 1 if self.current_state[x][y] == char else 0
            if y > 0:
                e1 += 1 if self.current_state[x][y-1] == char else 0
            if y < self.board_size - 1:
                e1 += 1 if self.current_state[x][y+1] == char else 0

            elif char == 'O': # minimize
                if x > 0: # left boarder
                    e1 -= 1 if self.current_state[x-1][y] == char else 0
                    if y > 0:
                        e1 -= 1 if self.current_state[x-1][y-1] == char else 0
                    if y < self.board_size - 1:
                        e1 -= 1 if self.current_state[x-1][y+1] == char else 0

                if x < self.board_size - 1: #right boarder
                    e1 -= 1 if self.current_state[x+1][y] == char else 0
                    if y > 0:
                        e1 -= 1 if self.current_state[x+1][y-1] == char else 0
                    if y < self.board_size - 1:
                       e1 -= 1 if self.current_state[x+1][y+1] == char else 0

                e1 -= 1 if self.current_state[x][y] == char else 0
                if y > 0:
                    e1 -= 1 if self.current_state[x][y-1] == char else 0
                if y < self.board_size - 1:
                    e1 -= 1 if self.current_state[x][y+1] == char else 0
        end_time = time.time()
        execution_time = end_time - start_time
        self.all_heuristic_run_time.append(execution_time)
        return e1
        

    # Heuristic 2: more sophisticated and complex to compute
    def heuristic2_eval(self):
        start_time = time.time()
        e2=0
        tempx=0
        tempo=0
        # Vertical
        for i in range(0, self.board_size):
            column = [item[i] for item in self.current_state]
            column_string = "".join(str(x) for x in column)
            tempx=column_string.count("X")
            tempo=column_string.count("O")
            if(tempx>tempo):
               e2+=pow(10,tempx)
            if(tempo>tempx):
                e2-=pow(10,tempo)
            if(tempx==tempo and tempx!=0):
                e2+=pow(10,tempx)
            tempx=0
            tempo=0

        # Horizontal
        for i in range(0, self.board_size):
            row_string = "".join(str(x) for x in self.current_state[i])
            tempx=row_string.count("X")
            tempo=row_string.count("O")
            if(tempx>tempo):
               e2+=pow(10,tempx)
            if(tempo>tempx):
                e2-=pow(10,tempo)
            if(tempx==tempo and tempx!=0):
                e2+=pow(10,tempx)
            tempx=0
            tempo=0
                
        #Diagonal
        matrix = np.array(self.current_state)
        diags = [matrix[::-1,:].diagonal(i) for i in range(-matrix.shape[0]+1,matrix.shape[1])]
        diags.extend(matrix.diagonal(i) for i in range(matrix.shape[1]-1,-matrix.shape[0],-1))

        for y in diags:
            row_string = "".join(str(x) for x in y.tolist())
            tempx=row_string.count("X")
            tempo=row_string.count("O")
            if(tempx>tempo and len(y.tolist())>=self.win_size):
               e2+=pow(10,tempx)
            if(tempo>tempx and len(y.tolist())>=self.win_size):
                e2-=pow(10,tempo)
            if(tempx==tempo and len(y.tolist())>=self.win_size and tempx!=0):
                e2+=pow(10,tempx)
            tempx=0
            tempo=0
        end_time = time.time()
        execution_time = end_time - start_time
        self.all_heuristic_run_time.append(execution_time)
        return e2

def main():
    n = int(input('enter the size of the board n: '))
    b = int(input('enter the number of blocs b: '))
    s = int(input('enter the winning line-up size s: '))
    t = int(input('enter the maximum allowed time (in seconds) t: '))

    d1 = int(input('Player 1, enter maximum depth d1: '))
    d2 = int(input('Player 2, enter maximum depth d2: '))

    a1 = int(input('enter either minimax (0) or alphabeta (1) for game 1: '))
    a2 = int(input('enter either minimax (0) or alphabeta (1) for game 2: '))

    p1 = int(input('Player 1, enter either AI (2) or Human (3) p1: '))
    p2 = int(input('Player 2, enter either AI (2) or Human (3) p2: '))

    blocPositions = []
    for _ in range(0, b):
        bx = int(input('enter the bloc position x: '))
        by = int(input('enter the bloc position y: '))
        blocPositions.append(f'{bx} {by}')

    g = Game(recommend=True, board_size=n, bloc_num=b, blocs_positions=blocPositions, win_size=s, max_depth_X=d1, max_depth_O=d2, t=t)
    g.play(algo=a1, player_x=p1, player_o=p2)
    # g.play(algo=a2,player_x=p1,player_o=p2)

if __name__ == "__main__":
    main()

