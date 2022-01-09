# create list representing board
# place Cell or None, indexing used for coords

# main
# create q
# set root node

# print(" ", file=sys.stderr, flush=True)
import sys
from collections import deque


class Cell:
    def __init__(self, index: int):
        self.parent_i = None
        self.index = index
        self.distance = None
        self.coords = self.index2coords()
        self.children_i = []
        # self.type = get_cell_type(self.level, self.row, self.col)

    def __str__(self):
        return f'Distance from start: {self.distance}; Coord: {self.coords}; Kids: {self.children_i}'

    def index2coords(self):
        assert self.index is not None
        level_i, temp = divmod(self.index, rows_n * cols_n)
        row_i, col_i = divmod(temp, rows_n)
        return [level_i, row_i, col_i]

    def set_distance(self, parent_distance: int):
        self.distance = parent_distance + 1

    def add_children_i(self, indices: list[int]):
        self.children_i.extend(indices)

    def clear_children_i(self):
        self.children_i = []

    def add_parent_i(self, indices: list[int]):
        self.parent_i.extend(indices)


def test(var, additional_info=''):
    print(f'Variable: {var}, Info:" {additional_info}": ', var, file=sys.stderr)


def load_data():
    grid_map = []
    for _ in range(levels_n):  # per level
        single_level = []
        for __ in range(rows_n + 1):
            single_level.append(input())
        del single_level[0]
        grid_map.append(single_level)
    return grid_map


def initialize_board(grid_map):
    for level_i, level in enumerate(grid_map):
        for row_i, row in enumerate(level):
            for col_i, cell_type in enumerate(row):
                if cell_type == '#':
                    BOARD.append(None)
                else:
                    index = coords2index([level_i, row_i, col_i])
                    cell = Cell(index)
                    if cell_type == 'A':  # start
                        start_i = index
                        cell.set_distance(0)
                    elif cell_type == 'S':  # end
                        end_i = index
                        cell.set_distance(999)
                    BOARD.append(cell)

    assert start_i
    assert end_i
    return start_i, end_i


def coords2index(coords: list[int]):
    return (coords[0] * rows_n * cols_n) + (coords[1] * rows_n) + coords[2]


def bounds_check(new_coords: list[int]) -> bool:
    """Check coords with offset [x,y,z] and return True if are in bounds"""
    lvl, row, col = new_coords
    if (0 <= lvl <= levels_n - 1) and (0 <= row <= rows_n - 1) and (0 <= col <= cols_n - 1):
        return True


def find_path(start_i, end_i):
    explored_cells_i = []
    q = deque()
    q.append(BOARD[start_i])
    directions = [(0, 0, 1), (0, 1, 0), (0, 0, -1), (0, -1, 0), (-1, 0, 0), (1, 0, 0)]
    # end_found = None

    while q:
        cell = q.pop()
        #(cell, 'right after popping')
        explored_cells_i.append(cell.index)
        c_lvl, c_row, c_col = cell.coords
        for direction in directions:
            level_offset, row_offset, col_offset = direction
            new_coords = [c_lvl + level_offset, c_row + row_offset, c_col + col_offset]
            if bounds_check(new_coords):
                new_index = coords2index(new_coords)
                if BOARD[new_index] is not None and new_index not in explored_cells_i:
                    if new_index == end_i:  # found END, set as only available option
                        cell.clear_children_i()
                        cell.add_children_i([new_index])
                        break
                    else:
                        cell.add_children_i([new_index])
        # use cell.children to hold children indices, but put Cell objects into queue
        for child_i in cell.children_i:
            assert isinstance(child_i, int), 'Child index is not int'
            child_cell = Cell(child_i)
            child_cell.set_distance(cell.distance)
            q.append(child_cell)
            # test(child_cell)


def get_cell_type(level_i, row_i, col_i):
    return BOARD[level_i][row_i][col_i]


# ----------------------- INITIALIZE -----------------------
answer = 'NO PATH'
levels_n, rows_n, cols_n = [int(i) for i in input().split()]
ln = int(input())
BOARD = []

# ----------------------- MAIN -----------------------
grid_map = load_data()
start_i, end_i = initialize_board(grid_map)
print('Start/End', start_i, end_i, file=sys.stderr)

find_path(start_i, end_i)
# print(BOARD, file=sys.stderr)

# TODO: take index to coord out of Cell
# TODO: explored_cells_i is useless?
# TODO: Cell should have shortest distance, not parent_distance + 1
# TODO: TEST: green thingy
# TODO: proper assert syntax with msg
