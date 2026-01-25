from queue import Queue

GRID_WIDTH = 4
GRID_LENGTH = 4


def rearrange(matrix, column=None):
    if column is None:
        for i in range(GRID_WIDTH):
            queue = Queue()
            non_zero_value = 0

            for j in range(GRID_LENGTH):
                if matrix[j][i] == 0:
                    continue
                else:
                    queue.put(matrix[j][i])

            for j in range(GRID_LENGTH):
                matrix[j][i] = 0

            non_zero_value = queue.qsize()
            for j in range(non_zero_value):
                value = queue.get()
                if value > 0:
                    matrix[j][i] = value
    else:
        queue = Queue()
        non_zero_value = 0

        for i in range(GRID_LENGTH):
            if matrix[i][column] == 0:
                continue
            else:
                queue.put(matrix[i][column])

        for i in range(GRID_LENGTH):
            matrix[i][column] = 0

        non_zero_value = queue.qsize()
        for i in range(non_zero_value):
            value = queue.get()
            if value > 0:
                matrix[i][column] = value

    return matrix


matrix = [
    [2, 0, 2, 0],
    [0, 2, 0, 4],
    [2, 0, 2, 0],
    [0, 4, 0, 4]
]

print("Original matrix:")
for row in matrix:
    print(row)

new_matrix = rearrange(matrix)

print("\nAfter rearrange():")
for row in new_matrix:
    print(row)

new_matrix_col = rearrange(matrix, column=1)
print("\nAfter rearrange(column=1):")
for row in new_matrix_col:
    print(row)
