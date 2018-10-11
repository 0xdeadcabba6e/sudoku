import functools
import numpy as np
import copy

class Board(object):
    # board representation is array
    # array can contain either numbers or nan
    def __init__(self, position):
        # position: iterable of strings of length 9
        self.board = np.full((9, 9), 0, dtype=int)
        msg = 'Expected iterable of length 9:\ngot {}'.format(position)
        assert len(position) == 9, msg
        # self.possible will store all the possible values
        # that could be in this cell.
        START = set(range(1, 10))
        self.possible = np.full((9, 9), None, dtype=object)
        for idx, line in enumerate(position):
            for jdx, char in enumerate(line):
                try:
                    val = int(char)
                    self.board[idx, jdx] = val
                    self.possible[idx, jdx] = {val}
                except:
                    # ignore any non-ints
                    # don't bother eliminating yet
                    self.possible[idx, jdx] = copy.copy(START)
        

    def __str__(self):
        out = []
        for row in self.board:
            line = [str(c) if c > 0 else '.' for c in row]
            out.append(" ".join(line))
        return "\n".join(out)
                
    @staticmethod
    def from_file(fn):
        with open(fn, 'r') as fh:
            lines = fh.readlines()
            position = [l.strip() for l in lines if l.strip()]
            return Board(position)

    @staticmethod
    def _elim_diff(start_set, others):
        if len(start_set) == 1:
            # cannot eliminate. early return
            return 
        single = [item for item in others if len(item) == 1]
        if single:
            elim_set = functools.reduce(set.union, single)
            return start_set.difference(elim_set)
        
    def eliminate(self):
        # go through the individual blocks, rows, columns and
        # eliminate
        for row in range(0, 9):
            for col in range(0, 9):
                diff = self._elim_diff(self.possible[row, col],
                                       self.possible[row])
                if diff:
                    self.possible[row, col] = diff
                diff = self._elim_diff(self.possible[row, col],
                                       self.possible[:, col])
                if diff:
                    self.possible[row, col] = diff
                block_x = slice(row//3 * 3, row//3 * 3 + 3)
                block_y = slice(col//3 * 3, col//3 * 3 + 3)
                block = self.possible[block_x, block_y]
                diff = self._elim_diff(self.possible[row, col], block)
                if diff:
                    self.possible[row, col] = diff
        # If there are any items that can't be in any other cell,
        # then that item must be in this cell.
        for row in range(0, 9):
            for col in range(0, 9):
                possible = self.possible[row, col]
                # first compare with other items in the row.
                eliminated = set()
                for item in possible:
                    for other_col in range(0, 9):
                        if other_col == col:
                            continue
                        if item in eliminated:
                            break
                        if item in self.possible[row, other_col]:
                            eliminated.add(item)
                # if everything but one has been eliminated
                # there is only one possible.
                diff = possible.difference(eliminated)
                if len(diff) == 1:
                    msg = '[{},{}] can only contain {}'.format(
                        row, col, diff
                    )
                    print(msg)
                    self.possible[row, col] = diff
        # now for any cell that only has one item left,
        # set that board cell to that item.
        for row in range(0, 9):
            for col in range(0, 9):
                possible = self.possible[row, col]
                if len(possible) == 1:
                    self.board[row, col] = list(possible)[0]
                
                        
        

if __name__ == '__main__':
    b = Board.from_file('position.txt')
    print(b)
