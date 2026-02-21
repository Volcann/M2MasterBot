from queue import Queue

GRID_ROWS = 7
GRID_COLS = 5


def rearrange(matrix, column=None):
    if column is None:
        for i in range(GRID_COLS):
            queue = Queue()
            non_zero_value = 0

            for j in range(GRID_ROWS):
                if matrix[j][i] == 0:
                    continue
                else:
                    queue.put(matrix[j][i])

            for j in range(GRID_ROWS):
                matrix[j][i] = 0

            non_zero_value = queue.qsize()
            for j in range(non_zero_value):
                value = queue.get()
                if value > 0:
                    matrix[j][i] = value
    else:
        queue = Queue()
        non_zero_value = 0

        for i in range(GRID_ROWS):
            if matrix[i][column] == 0:
                continue
            else:
                queue.put(matrix[i][column])

        for i in range(GRID_ROWS):
            matrix[i][column] = 0

        non_zero_value = queue.qsize()
        for i in range(non_zero_value):
            value = queue.get()
            if value > 0:
                matrix[i][column] = value

    return matrix


def remove_redundant_values(matrix, available_values=None, target_value=None):
    values_to_remove = []

    if available_values is None:
        available_values = [2, 4]

    if target_value is None:
        return [2, 4], matrix

    current_value = target_value
    while current_value >= 2:
        values_to_remove.append(current_value)
        current_value //= 2

    for value in values_to_remove:
        if value in available_values:
            available_values.remove(value)

        for row_index in range(GRID_ROWS):
            for col_index in range(GRID_COLS):
                if (
                    row_index < len(matrix)
                    and col_index < len(matrix[row_index])
                    and matrix[row_index][col_index] == value
                ):
                    matrix[row_index][col_index] = 0

    return available_values, matrix


def display_matrix(matrix, heading="Matrix"):
    print(f"\n{heading}")
    print("-" * 30)
    for row in matrix:
        print(row)
    print("-" * 30)


def run_tests():
    matrix_one = [
        [2, 4, 8, 16, 32],
        [2, 4, 8, 16, 32],
        [0, 8, 0, 0, 0],
        [0, 16, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
    ]

    choices_one = [2, 4, 8, 16, 32]
    remove_value_one = 8
    remove_value_one //= 2
    print("\n========= TEST CASE 1 =========")
    print("Initial available values:", choices_one)
    display_matrix(matrix_one, "Before")

    updated_choices, updated_matrix = remove_redundant_values(
        matrix=matrix_one,
        available_values=choices_one,
        target_value=remove_value_one,
    )

    print("Returned available values:", updated_choices)
    rearrange(updated_matrix)
    display_matrix(updated_matrix, "After")


if __name__ == "__main__":
    run_tests()
