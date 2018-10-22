from queue import PriorityQueue
import curses
import time

class Board(object):
    
    def __init__(self, board=None, moves=0, previous=None):
       
        if board is None:
            self.board = [0,1, 2, 3, 4, 5, 6, 7, 8]
        else:
            self.board = board
        self.previous = previous
        self.moves = moves

    def is_goal(self):
       
        for i in range(0, 9):
            if i != 8:
                if self.board[i] != i + 1:
                    return False

        return True

    def move_blank(self, where):
        
        blank = self.find_blank()

        if where == 'left':
            if blank % 3 != 0:
                t_col = (blank % 3) - 1
                t_row = int(blank / 3)
                self.exchange(blank, t_row * 3 + t_col)

        if where == 'right':
            if blank % 3 != 2:
                t_col = (blank % 3) + 1
                t_row = int(blank / 3)
                self.exchange(blank, t_row * 3 + t_col)

        if where == 'up':
            if int(blank / 3) != 0:
                t_col = (blank % 3)
                t_row = int(blank / 3) - 1
                self.exchange(blank, t_row * 3 + t_col)

        if where == 'down':
            if int(blank / 3) != 2:
                t_col = (blank % 3)
                t_row = int(blank / 3) + 1
                self.exchange(blank, t_row * 3 + t_col)

    def find_blank(self):
        
        blank = None
        for i in range(0, 9):
            if self.board[i] == 0:
                blank = i
                break
        return blank

    def clone(self):
        
        return Board(self.board.copy(), self.moves + 1, self)


    def exchange(self, source, target):
        
        # print('Exchanging: {} <-> {}'.format(source, target))
        self.board[source], self.board[target] = self.board[target], self.board[source]


    def neighbours(self):
      
        blank_index = self.find_blank()

        neighbours = []

        # print('Blank found: {}, := {}, {}'.format(blank_index, int(blank_index / 3), blank_index % 3))
        # Can we move blank tile left?
        if blank_index % 3 != 0:
            new_board = self.clone()
            new_board.move_blank('left')
            neighbours.append(new_board)

        # right?
        if blank_index % 3 != 2:
            new_board = self.clone()
            new_board.move_blank('right')
            neighbours.append(new_board)

        # up?
        if int(blank_index / 3) != 0:
            new_board = self.clone()
            new_board.move_blank('up')
            neighbours.append(new_board)

        # down?
        if int(blank_index / 3) != 2:
            new_board = self.clone()
            new_board.move_blank('down')
            neighbours.append(new_board)

        return neighbours


    def manhattan(self):
       
        manhattan = 0
        for i in range(0, 9):
            if self.board[i] != i + 1 and self.board[i] != 0:
                correct_pos = 8 if self.board[i] == 0 else self.board[i] - 1
                s_row = int(i / 3)
                s_col = i % 3
                t_row = int(correct_pos / 3)
                t_col = correct_pos % 3
                manhattan += abs(s_row - t_row) + abs(s_col - t_col)

        return manhattan

    def to_pq_entry(self, count):
        
        return (self.moves + self.manhattan(), count, self)

    def __str__(self):
        
        string = ''
        string = string + '+---+---+---+\n'
        for i in range(3):
            for j in range(3):
                tile = self.board[i * 3 + j]
                string = string + '| {} '.format(' ' if tile == 0 else tile)
            string = string + '|\n'
            string = string + '+---+---+---+\n'
        return string

    def __eq__(self, other):
       
        if other is None:
            return False
        else:
            return self.board == other.board

    def get_previous_states(self):
       
        states = [self]
        prev = self.previous
        while prev is not None:
            states.append(prev)
            prev = prev.previous

        states.reverse()
        return states

def diff_boards_str(board1, board2):
   
    if board1 is None:
        return 'Intial State'

    if board2 is None:
        return ''

    blank1 = board1.find_blank()
    blank2 = board2.find_blank()

    s_row = int(blank1 / 3)
    s_col = blank1 % 3
    t_row = int(blank2 / 3)
    t_col = blank2 % 3

    dx = s_col - t_col
    dy = s_row - t_row

    if dx == 1:
        return 'Move Left'
    if dx == -1:
        return 'Move Right'
    if dy == 1:
        return 'Move Up'
    if dy == -1:
        return 'Move Down'

def solve(initial_board):
    
    queue = PriorityQueue()
    queue.put(initial_board.to_pq_entry(0))

    i = 1
    while not queue.empty():
        board = queue.get()[2]
        if not board.is_goal():
            for neighbour in board.neighbours():
                if neighbour != board.previous:
                    queue.put(neighbour.to_pq_entry(i))
                    i += 1
        else:
            return board.get_previous_states()

    return None


def main2(window):
   
    initial = Board()
    window.insstr(0, 0, 'Enter starting state of the board: ')
    window.insstr(1, 0, str(initial))
    window.insstr(8, 0, 'Controls: Up, Down, Left, Right to move, Enter to solve')
    ch = window.getch()
    while str(ch) != '10':
        if ch == curses.KEY_UP:
            # Move blank up
            initial.move_blank('up')
        if ch == curses.KEY_DOWN:
            # Move blank down
            initial.move_blank('down')
        if ch == curses.KEY_LEFT:
            # Move blank left
            initial.move_blank('left')
        if ch == curses.KEY_RIGHT:
            # Move blank right
            initial.move_blank('right')
        window.insstr(1, 0, str(initial))
        ch = window.getch()
        window.refresh()

    moves = solve(initial)
    prev = None
    window.clear()
    for move in moves:
        window.clear()
        window.insstr(0, 0, 'Solving puzzle: ')
        window.insstr(1, 0, str(move))
        window.insstr(8, 0, diff_boards_str(prev, move))
        window.refresh()
        time.sleep(1)
        prev = move

    window.insstr(9, 0, 'Puzzle solved.')
    window.getch()

if __name__ == '__main__':
	curses.wrapper(main2)
