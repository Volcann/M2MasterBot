import random

from config.constants import GRID_LENGTH, GRID_WIDTH
from game_logic.utils.utils import (
    rearrange,
    print_matrix,
    random_value
)


class GameLogic:
    def __init__(self):
        self._matrix = [[0] * GRID_LENGTH for i in range(GRID_WIDTH)]
        self._score = 0
        
    def _reset(self):
        self._matrix = [[0] * GRID_LENGTH for i in range(GRID_WIDTH)]
        self._score = 0

    def get_matrix(self):
        return self._matrix
    
    def set_matrix(self, matrix):
        self._matrix = matrix
        
    def get_score(self):
        return self._score

    def get_random_value(self):
        value, matrix = random_value(self._matrix, self._score)
        self._matrix = matrix
        return value

    def can_merge_last_row(self, column, value):
        last_row = GRID_LENGTH - 1
        return self._matrix[last_row][column] == value

    def add_to_column(self, value, column):
        index = 0
        while True:
            if index == GRID_LENGTH:
                if self.can_merge_last_row(column, value):
                    self._matrix[GRID_LENGTH - 1][column] *= 2
                    self._score += self._matrix[GRID_LENGTH - 1][column]
                    while self.merge_column(column):
                        self._matrix = rearrange(self._matrix ,column)
                    return True
                else:
                    print("Column is already full")
                    return False

            if self._matrix[index][column] == 0:
                self._matrix[index][column] = value
                while self.merge_column(column):
                    self._matrix = rearrange(self._matrix)
                break
            else:
                index += 1

        for i in range(GRID_WIDTH):
            while self.merge_column(i):
                self._matrix = rearrange(self._matrix)

        print_matrix(self._matrix)
        return True

    def merge_column(self, column=-1):
        if column == -1:
            for i in range(GRID_LENGTH):
                for j in range(GRID_WIDTH):
                    value = self._matrix[j][i]
                    if value == 0:
                        continue
                    if self.merging_values(j, i, value):
                        return True
        else:
            for j in range(GRID_WIDTH):
                value = self._matrix[j][column]
                if value == 0:
                    continue
                if self.merging_values(j, column, value):
                    return True
        return False
    
    def merging_values(self, row, column, value):
        indexes = [
            (-1, 0),
            (0, -1),
            (1,  0),
            (0,  1)
        ]
        count = 0
        visited = set()

        for (i, j) in indexes:
            new_row = row+i
            new_column = column+j
            if 0 <= new_row < GRID_LENGTH and 0 <= new_column < GRID_WIDTH:
                if ((new_row, new_column)) not in visited:
                    visited.add((new_row, new_column))
                    if self._matrix[new_row][new_column] == value:
                        print("EXIST", new_row, new_column)
                        print()
                        self._matrix[new_row][new_column] = 0
                        count += 1
                        for (i, j) in indexes:
                            sec_new_row = new_row+i
                            sec_new_column = new_column+j
                            if 0 <= sec_new_row < GRID_LENGTH and 0 <= sec_new_column < GRID_WIDTH:
                                if ((sec_new_row, sec_new_column)) not in visited:
                                    visited.add((sec_new_row, sec_new_column))
                                    if self._matrix[sec_new_row][sec_new_column] == value:
                                        self._matrix[sec_new_row][sec_new_column] = 0
                                        print("EXIST", sec_new_row, sec_new_column)
                                        print()
                                        count += 1

        if count == 2:
            value *= 2 
            self._matrix[row][column] = value
            self._score += value
        elif count == 3:
            value *= 4 
            self._matrix[row][column] = value
            self._score += value
        elif count == 4:
            value *= 8 
            self._matrix[row][column] = value
            self._score += value
        else:
            return False

        print("Count", count)
        print("Merged", value, "at", row, column)
        return True
