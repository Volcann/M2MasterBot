from config.constants import GRID_LENGTH, GRID_WIDTH
from core.utils.utils import (
    rearrange,
    merge_column,
    random_value
)


class GameLogic:
    def __init__(self):
        self._matrix = [[0] * GRID_WIDTH for i in range(GRID_LENGTH)]
        self._score = 0

    def _reset(self):
        self._matrix = [[0] * GRID_WIDTH for i in range(GRID_LENGTH)]
        self._score = 0

    def reset(self):
        self._reset()

    def get_matrix(self):
        return self._matrix

    def set_matrix(self, matrix):
        self._matrix = matrix

    def step(self, column: int):
        value = self.get_random_value()
        success, merge_count = self.add_to_column(value, column)
        reward = merge_count
        done = not success
        return reward, done

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
        count_merge = []
        while True:
            if index == GRID_LENGTH:
                if self.can_merge_last_row(column, value):
                    self._matrix[GRID_LENGTH - 1][column] *= 2
                    self._score += self._matrix[GRID_LENGTH - 1][column]
                    while True:
                        merged, count = self.merge_column(column)
                        if not merged:
                            break
                        count_merge.append(count)
                        self._matrix = rearrange(self._matrix, column)
                    merge_count = max(count_merge) if count_merge else count
                    return True, merge_count
                else:
                    pass
                    return False, 0

            if self._matrix[index][column] == 0:
                self._matrix[index][column] = value
                while True:
                    merged, count = self.merge_column(column)
                    if not merged:
                        break
                    count_merge.append(count)
                    self._matrix = rearrange(self._matrix, column)
                break
            else:
                index += 1

        for i in range(GRID_WIDTH):
            while True:
                merged, count = self.merge_column(i)
                if not merged:
                    break
                count_merge.append(count)
                self._matrix = rearrange(self._matrix)

        count_merge.sort()
        merge_count = count_merge[-1] if count_merge else 0

        return True, merge_count

    def merge_column(self, column=-1):
        merged, self._matrix, self._score, count = merge_column(self._matrix, self._score, column)
        return merged, count
