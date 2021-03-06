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
        msg = 'Board is invalid!\n{}'.format(self)
        assert self.valid, msg
        

    def __str__(self):
        out = []
        for row in self.board:
            line = [str(c) if c > 0 else '.' for c in row]
            out.append(" ".join(line))
        return "\n".join(out)
                
    @staticmethod
    def from_file(fn):
        with open(fn, 'r') as fh:
            lines = fh.read()
            return Board.from_string(lines)

    @staticmethod
    def from_string(s):
        # s can start and end with whitespace
        # s can contain empty lines
        # s can use any non-int non-whitespace character
        # for the blanks
        lines = s.strip().split("\n")
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

    @staticmethod
    def _to_block(row, col):
        # return the slices that extract the appropriate block
        block_x = slice(row//3 * 3, row//3 * 3 + 3)
        block_y = slice(col//3 * 3, col//3 * 3 + 3)
        return block_x, block_y
        
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
                block_x, block_y = self._to_block(row, col)
                block = self.possible[block_x, block_y]
                diff = self._elim_diff(self.possible[row, col], block)
                if diff:
                    self.possible[row, col] = diff
        # If there are any items that can't be in any other cell,
        # then that item must be in this cell.
        for row in range(0, 9):
            for col in range(0, 9):
                possible = self.possible[row, col]
                if len(possible) == 1:
                    continue
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
                    msg = 'Eliminating in row: [{},{}] can only contain {}'.format(
                        row, col, diff
                    )
                    print(msg)
                    self.possible[row, col] = diff
        for col in range(0, 9):
            for row in range(0, 9):
                possible = self.possible[row, col]
                if len(possible) == 1:
                    continue
                # first compare with other items in the row.
                eliminated = set()
                for item in possible:
                    for other_row in range(0, 9):
                        if other_row == row:
                            continue
                        if item in eliminated:
                            break
                        if item in self.possible[other_row, col]:
                            eliminated.add(item)
                # if everything but one has been eliminated
                # there is only one possible.
                diff = possible.difference(eliminated)
                if len(diff) == 1:
                    msg = 'Eliminating in column: [{},{}] can only contain {}'.format(
                        row, col, diff
                    )
                    print(msg)
                    self.possible[row, col] = diff

        for row in range(0, 9):
            for col in range(0, 9):
                possible = self.possible[row, col]
                if len(possible) == 1:
                    continue
                # compare with other items in block
                eliminated = set()
                block_x, block_y = self._to_block(row, col)
                block = self.possible[block_x, block_y].ravel()
                for item in possible:
                    for other_block in block:
                        if other_block == possible:
                            continue
                        if item in eliminated:
                            continue
                        if item in other_block:
                            eliminated.add(item)
                # if everything but one has been eliminated
                # there is only one possible.
                diff = possible.difference(eliminated)
                if len(diff) == 1:
                    msg = 'Eliminating in block: [{},{}] can only contain {}'.format(
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

    @property
    def solved(self):
        # all rows, columns, blocks must contain all 9
        valid = set(range(1, 10))
        ok = True
        for r in range(0, 9):
            ok &= set(self.board[r]) == valid
            ok &= set(self.board[:, r]) == valid
        # check blocks
        for r in (0, 3, 6):
            for c in (0, 3, 6):
                block_x, block_y = self._to_block(r, c)
                block = self.board[block_x, block_y].ravel()
                ok &= set(block) == valid
        return ok


    @property
    def valid(self):
        # a board is valid even if unsolved,
        # as long as it has no duplicates in row, column or block
        valid = set(range(1, 10))
        def count(a):
            d = {}
            for item in a:
                if item not in valid:
                    continue
                d.setdefault(item, 0)
                d[item] += 1
            return d
        ok = True
        for r in range(0, 9):
            ok &= set(count(self.board[r]).values()) == {1}
            ok &= set(count(self.board[:, r]).values()) == {1}
        # check blocks
        for r in (0, 3, 6):
            for c in (0, 3, 6):
                block_x, block_y = self._to_block(r, c)
                block = self.board[block_x, block_y].ravel()
                ok &= set(count(block).values()) == {1}
        return ok
    
    def solve(self):
        # need to check if previous board position
        # is the same as current, and stop otherwise.
        lastboard = self.board.copy()
        while True:
            self.eliminate()
            msg = 'Board reached invalid state!\n{}'.format(self)
            assert self.valid, msg
            if self.solved:
                break
            if np.allclose(self.board, lastboard):
                raise ValueError('Cannot be solved by simple elimination')
            lastboard = self.board.copy()

if __name__ == '__main__':
    b = Board.from_file('position.txt')
    print(b)
