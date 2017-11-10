import pygame
from pygame import Color

init_state = (0, 0, 0)
grid_length = 300
SHAPE = 'X'


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


class Game:
    def __init__(self, player_1, player_2):
        pygame.init()
        self.grid = Grid(partitions=3, width=300, height=325)
        self.player_1 = player_1
        self.player_2 = player_2
        self.current_player = self.player_1

    def start(self):

        # Used to manage how fast the screen updates
        clock = pygame.time.Clock()

        while True:
            for event in pygame.event.get():
                if event.type is pygame.QUIT:
                    done = True
                elif event.type is pygame.MOUSEBUTTONDOWN:
                    if self.grid.click_event(self.current_player.mark):
                        self.current_player = self.get_next_player()

            pygame.display.flip()

            if self.has_game_ended():
                self.end()
                break

            clock.tick(60)

    def has_game_ended(self):
        # print self.grid.is_grid_full()
        # print self.grid.is_winner()
        return self.grid.is_grid_full() or self.grid.is_winner()

    def get_next_player(self):
        if self.current_player == self.player_1:
            return self.player_2
        return self.player_1

    def end(self):
        pygame.quit()


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

        self.grid[row][column] = shape

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

if __name__ == "__main__":
    player_one = HumanPlayer("X")
    opponent_mark = player_one.opponent_mark()
    player_two = HumanPlayer(opponent_mark)

    game = Game(player_one, player_two)
    game.start()
