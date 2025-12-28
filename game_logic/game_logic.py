from config.constants import GRID_LENGTH, GRID_WIDTH
import random
from queue import Queue


class GameLogic:
    def __init__(self):
        self._matrix = [[0] * GRID_LENGTH for i in range(GRID_WIDTH)]
        self._score = 0

    def random_value(self):
        max_value = 2

        for i in range(GRID_LENGTH):
            for j in range(GRID_WIDTH):
                if self._matrix[i][j] != 0:
                    max_value = max(max_value, self._matrix[i][j])

        if max_value == 2:
            return random.choice([2, 4])

        min_value = 2
        random_choice = set()
        while True:
            if min_value > max_value:
                break
            random_choice.add(min_value)
            min_value *= 2
        random_choice = sorted(list(random_choice))

        options = list(random_choice)
        if random.random() < 0.9:
            options = options[:-1]
        return random.choice(options)

    def print_matrix(self):
        for row in self._matrix:
            print(row)
        print()

    def rearrange(self, column=None):
        if column is None:
            for col_index in range(GRID_WIDTH):
                self.rearrange(col_index)
            return

        index = 0
        total_non_zero_values = 0

        queue = Queue()
        while index < GRID_LENGTH:
            if self._matrix[index][column] != 0:
                queue.put(self._matrix[index][column])
                total_non_zero_values += 1
            index += 1

        index = 0
        preserve_total_non_zero_values = total_non_zero_values
        while total_non_zero_values > 0:
            self._matrix[index][column] = queue.get()
            total_non_zero_values -= 1
            index += 1

        index = preserve_total_non_zero_values
        while index < GRID_LENGTH:
            self._matrix[index][column] = 0
            index += 1
        return

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
                        self.rearrange(column)
                    return True
                else:
                    print("Column is already full")
                    return False

            if self._matrix[index][column] == 0:
                self._matrix[index][column] = value
                while self.merge_column(column):
                    self.rearrange(column)
                break
            else:
                index += 1
        self.rearrange()
        self.merge_column(column)
        self.rearrange()
        self.print_matrix()
        return True

    def merge_column(self, col_index, value=None):
        merged_any = False

        while True:
            merged_this_pass = False

            for row_index in range(GRID_LENGTH):
                current_value = self._matrix[row_index][col_index]
                if current_value == 0:
                    continue

                for delta_row in [-1, 1]:
                    neighbor_row = row_index + delta_row
                    if (
                        0 <= neighbor_row < GRID_LENGTH
                        and
                        self._matrix[neighbor_row][col_index] == current_value
                    ):
                        self._matrix[row_index][col_index] *= 2
                        self._score += self._matrix[row_index][col_index]
                        self._matrix[neighbor_row][col_index] = 0
                        merged_this_pass = True

                for delta_col in [-1, 1]:
                    neighbor_col = col_index + delta_col
                    if (
                        0 <= neighbor_col < GRID_WIDTH
                        and
                        self._matrix[row_index][neighbor_col] == current_value
                    ):
                        self._matrix[row_index][col_index] *= 2
                        self._score += self._matrix[row_index][col_index]
                        self._matrix[row_index][neighbor_col] = 0
                        merged_this_pass = True

            self.rearrange(col_index)

            if not merged_this_pass:
                break
            merged_any = True

        return merged_any

    def get_score(self):
        return self._score

    def game_over(self, value):
        for i in range(GRID_WIDTH):
            for j in range(GRID_LENGTH):
                if self._matrix[j][i] == 0:
                    return False

        for i in range(GRID_LENGTH):
            if self._matrix[(GRID_WIDTH - 1)][i] == value:
                return False

        return True
