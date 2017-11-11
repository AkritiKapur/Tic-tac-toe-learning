import copy
import pygame
import numpy as np
from pygame import Color

init_state = (0, 0, 0)
grid_length = 300


class Player(object):
    def __init__(self, mark):
        self.mark = mark

    def opponent_mark(self):
        if self.mark == 'X':
            return 'O'
        elif self.mark == 'O':
            return 'X'
        else:
            print("The player's mark must be either 'X' or 'O'.")


class HumanPlayer(Player):
    pass


class ComputerPlayer(Player):
    pass


class QAgent:
    def __init__(self):
        pass


class QPlayer(ComputerPlayer):
    def __init__(self, mark, Q, epsilon=0.2):
        super(QPlayer, self).__init__(mark=mark)
        self.Q = Q
        self.epsilon = epsilon

    def get_move(self, board):
        # get all available spaces on the board.
        moves_available = board.available_moves()
        if np.random.uniform() < self.epsilon:
            if moves_available:
                return moves_available[np.random.choice(len(moves_available))]
        else:
            state_key = self.make_and_maybe_add_key(board, self.mark, self.Q)
            Qs = self.Q[state_key]

            if self.mark == "X":
                return QPlayer.stochastic_argminmax(Qs, max)
            elif self.mark == "O":
                return QPlayer.stochastic_argminmax(Qs, min)

    @staticmethod
    def make_and_maybe_add_key(board, mark, Q):
        # Make a dictionary key for the current state (board + player turn) and if Q does not yet have it, add it to Q
        default_Qvalue = 1.0  # Encourages exploration
        state_key = board.make_key(mark)
        if Q.get(state_key) is None:
            moves = board.available_moves()
            # The available moves in each state are initially given a default value of zero
            Q[state_key] = {move: default_Qvalue for move in moves}

        return state_key

    @staticmethod
    def stochastic_argminmax(Qs, min_or_max):
        min_or_maxQ = min_or_max(list(Qs.values()))
        if list(Qs.values()).count(min_or_maxQ) > 1:
            best_options = [move for move in list(Qs.keys()) if Qs[move] == min_or_maxQ]
            move = best_options[np.random.choice(len(best_options))]
        else:
            move = min_or_max(Qs, key=Qs.get)
        return move


class Game:
    def __init__(self, player_1, player_2):
        pygame.init()
        self.grid = Grid(partitions=3, width=300, height=325)
        self.player_1 = player_1
        self.player_2 = player_2
        self.current_player = self.player_1
        self.other_player = self.player_2

    def start(self):
        if isinstance(self.player_1, HumanPlayer) and isinstance(self.player_2, HumanPlayer):
            self.trigger_event_loop_for_humans()
        if isinstance(self.player_1, ComputerPlayer) and isinstance(self.player_2, ComputerPlayer):
            self.train_Q_function()

    def trigger_event_loop_for_humans(self):
        # Used to manage how fast the screen updates
        clock = pygame.time.Clock()

        while True:
            for event in pygame.event.get():
                if event.type is pygame.QUIT:
                    self.end()
                elif event.type is pygame.MOUSEBUTTONDOWN:
                    if self.grid.click_event(self.current_player.mark):
                        self.current_player = self.get_next_player()

            pygame.display.flip()

            if self.has_game_ended():
                self.end()
                break

            clock.tick(60)

    def train_Q_function(self):
        while not self.has_game_ended():
            self.play_game()

    def play_game(self):
        move = self.current_player.get_move(self.grid)
        self.handle_move(move)

    def has_game_ended(self):
        return self.grid.is_grid_full() or self.grid.is_winner()

    def get_next_player(self):
        if self.current_player == self.player_1:
            return self.player_2
        return self.player_1

    def handle_move(self, move):
        if self.Q_learn:
            self.learn_Q(move)
        i, j = move
        self.grid.place_grid_mark(i, j, self.current_player.mark)
        if self.has_game_ended():
            if self.grid.is_winner():
                print "{} Player won", self.current_player.mark
            else:
                print "too bad.It's a draw"
        else:
            self.current_player = self.get_next_player()
            self.other_player = self.get_next_player()

    def end(self):
        pygame.quit()

    def reset(self):
        self.grid.reset()

    def learn_Q(self, move):
        # If Q-learning is toggled on, "learn_Q" should be called after receiving a move from an instance of Player and
        # before implementing the move (using Board's "place_mark" method)

        print self.Q
        state_key = QPlayer.make_and_maybe_add_key(self.board, self.current_player.mark, self.Q)
        next_board = self.grid.get_next_board(move, self.current_player.mark)
        reward = next_board.give_reward()
        next_state_key = QPlayer.make_and_maybe_add_key(next_board, self.other_player.mark, self.Q)
        if next_board.is_winner() or next_board.is_winner():
            expected = reward
        else:
            next_Qs = self.Q[next_state_key]
            if self.current_player.mark == "X":
                expected = reward + (self.gamma * min(next_Qs.values()))
            elif self.current_player.mark == "O":
                expected = reward + (self.gamma * max(next_Qs.values()))
        change = self.alpha * (expected - self.Q[state_key][move])
        self.Q[state_key][move] += change
        print self.Q


class Grid:
    def __init__(self, partitions, width, height):
        board = pygame.display.set_mode((width, height))
        board.fill(Color("white"))
        self.partitions = partitions
        self.grid = [[None for i in xrange(partitions)] for j in xrange(partitions)]
        self.board = board
        self.init_grid()

    def init_grid(self):

        for row in range(1, self.partitions):
            pygame.draw.line(self.board, init_state, (row * (grid_length / self.partitions), 0),
                             (row * (grid_length / self.partitions), grid_length), 2)

        for column in range(1, self.partitions):
            pygame.draw.line(self.board, init_state, (0, column * (grid_length / self.partitions)),
                             (grid_length, column * (grid_length / self.partitions)), 2)

    def board_pos(self, mouse_x, mouse_y):
        row = mouse_y / (grid_length / self.partitions)
        column = mouse_x / (grid_length / self.partitions)

        return row, column

    def click_event(self, mark):
        (mouse_x, mouse_y) = pygame.mouse.get_pos()
        row, col = self.board_pos(mouse_x, mouse_y)

        if self.grid[row][col]:
            return False

        self.draw_shape(mark, self.board, row, col)

        return True

    def draw_shape(self, shape, board, row, column):
        cell_width = grid_length / self.partitions
        center_X = (column * cell_width) + cell_width / 2
        center_Y = (row * cell_width) + cell_width / 2
    
        if shape == 'O':
            pygame.draw.circle(board, init_state, (center_X, center_Y), 33, 2)
        else:
            pygame.draw.line(board, init_state, (center_X - 22, center_Y - 22),
                             (center_X + 22, center_Y + 22), 2)
            pygame.draw.line(board, init_state, (center_X + 22, center_Y - 22),
                             (center_X - 22, center_Y + 22), 2)

        self.place_grid_mark(row, column, shape)

    def place_grid_mark(self, row, col, shape):
        self.grid[row][col] = shape

    def get_available_moves(self):
        return [(i, j) for i in range(0, self.partitions) for j in range(0, self.partitions)]

    def reset(self):
        self.grid = [[None for i in xrange(self.partitions)] for j in xrange(self.partitions)]

    def is_winner(self):
        # check for each row
        for row in range(0, self.partitions):
            row_set = set(self.grid[row][0:])
            if len(row_set) == 1 and None not in row_set:
                return self.grid[row][0]

        # check for winning columns
        for col in range(0, self.partitions):
            col_set = set(self.grid[0:][col])
            if len(col_set) == 1 and None not in col_set:
                return self.grid[0][col]

        # check for diagonal winners
        if (self.grid[0][0] == self.grid[1][1] == self.grid[2][2]) and self.grid[0][0]:
            return self.grid[0][0]

        if (self.grid[0][2] == self.grid[1][1] == self.grid[2][0]) and self.grid[0][2]:
            return self.grid[0][2]

        return False

    def is_grid_full(self):
        for row in range(0, self.partitions):
            for col in range(0, self.partitions):
                if not self.grid[row][col]:
                    return False
        return True

    def get_next_board(self, move, mark):
        next_board = copy.deepcopy(self)
        row, column = move
        next_board.place_grid_mark(row, column, mark)
        return next_board

    def make_key(self, mark):
        fill_val = 'N'
        key = []
        for row in range(0, self.partitions):
            for col in range(0, self.partitions):
                local_key = self.grid[row][col]
                if not local_key:
                    local_key = fill_val
                key.append(local_key)

        return ''.join(key) + mark

    def get_reward(self):
        if self.is_grid_full() or self.is_winner():
            winner = self.is_winner()
            if self.is_winner():
                if winner == 'X':
                    return 1
                else:
                    return -1
            if self.is_grid_full():
                return 0.5
        return 0.0


if __name__ == "__main__":
    player_one = HumanPlayer("X")
    opponent_mark = player_one.opponent_mark()
    player_two = HumanPlayer(opponent_mark)

    game = Game(player_one, player_two)
    game.start()
