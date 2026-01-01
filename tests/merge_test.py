from queue import Queue


class GameLogic:
    def __init__(self):
        self._matrix = [
          [4, 8, 0, 0],
          [2, 0, 4, 4],
          [2, 0, 4, 0],
          [8, 0, 0, 0],
        ]

    def print_matrix(self):
        for i in self._matrix:
            print(i)

    def rearrange(self, column=None):
        if column is None:
            for i in range(4):
                queue = Queue()
                non_zero_value = 0

                for j in range(4):
                    if self._matrix[j][i] == 0:
                        continue
                    else:
                        queue.put(self._matrix[j][i])

                for j in range(4):
                    self._matrix[j][i] = 0

                non_zero_value = queue.qsize()
                for j in range(non_zero_value):
                    value = queue.get()
                    if value > 0:
                        self._matrix[j][i] = value
        else:
            queue = Queue()
            non_zero_value = 0

            for i in range(4):
                if self._matrix[i][column] == 0:
                    continue
                else:
                    queue.put(self._matrix[i][column])

            for i in range(4):
                self._matrix[i][column] = 0

            non_zero_value = queue.qsize()
            for i in range(non_zero_value):
                value = queue.get()
                if value > 0:
                    self._matrix[i][column] = value
        return

    def merge(self, column=-1):
        if column == -1:
            for i in range(4):
                for j in range(4):
                    value = self._matrix[j][i]
                    if value == 0:
                        continue
                    if self.check_value(j, i, value):
                        return True
        else:
            for j in range(4):
                value = self._matrix[j][column]
                if value == 0:
                    continue
                if self.check_value(j, column, value):
                    return True
        return False

    def check_value(self, row, column, value):
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
            if 0 <= new_row < 4 and 0 <= new_column < 4:
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
                            if 0 <= sec_new_row < 4 and 0 <= sec_new_column < 4:
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
        elif count > 2:
            value *= 4 
            self._matrix[row][column] = value
        else:
            return False

        print("Count", count)
        print("Merged", value, "at", row, column)
        return True


game = GameLogic()
print("Before :")
game.print_matrix()
print()

print("Merged :")
while game.merge():
    array = game.rearrange()
    game.print_matrix()
    print()
