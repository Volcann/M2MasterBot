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
        elif max_value >= 1024:
            min_value = 4
            return self.random_choices(max_value, min_value)
        elif max_value >= 2048:
            min_value = 8
            return self.random_choices(max_value, min_value)
        elif max_value >= 4096:
            min_value = 16
            return self.random_choices(max_value, min_value)
        elif max_value >= 8192:
            min_value = 32
            return self.random_choices(max_value, min_value)
        elif max_value >= 16384:
            min_value = 64
            return self.random_choices(max_value, min_value)
        else:
            min_value = 2
            return self.random_choices(max_value, min_value)

    def random_choices(self, max_value, min_value):
        random_choice = set()
        while True:
            if min_value > max_value:
                break
            random_choice.add(min_value)
            min_value *= 2
        
        random_choice = sorted(list(random_choice))
        options = list(random_choice)
        if random.random() < 0.95:
            options = options[:-1]
        value = random.choice(options)
        print("Random value:", value)
        return value

    def print_matrix(self):
        for row in self._matrix:
            print(row)
        print()

    def rearrange(self, column=None):
        if column is None:
            for i in range(GRID_LENGTH):
                queue = Queue()
                non_zero_value = 0

                for j in range(GRID_WIDTH):
                    if self._matrix[j][i] == 0:
                        continue
                    else:
                        queue.put(self._matrix[j][i])

                for j in range(GRID_WIDTH):
                    self._matrix[j][i] = 0

                non_zero_value = queue.qsize()
                for j in range(non_zero_value):
                    value = queue.get()
                    if value > 0:
                        self._matrix[j][i] = value
        else:
            queue = Queue()
            non_zero_value = 0

            for i in range(GRID_LENGTH):
                if self._matrix[i][column] == 0:
                    continue
                else:
                    queue.put(self._matrix[i][column])

            for i in range(GRID_LENGTH):
                self._matrix[i][column] = 0

            non_zero_value = queue.qsize()
            for i in range(non_zero_value):
                value = queue.get()
                if value > 0:
                    self._matrix[i][column] = value
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
                    self.rearrange()
                break
            else:
                index += 1
        for i in range(GRID_WIDTH):
            while self.merge_column(i):
                self.rearrange()
        self.print_matrix()
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
        elif count > 2:
            value *= 4 
            self._matrix[row][column] = value
            self._score += value
        else:
            return False

        print("Count", count)
        print("Merged", value, "at", row, column)
        return True

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
