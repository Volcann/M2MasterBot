import random
from queue import Queue

from config.constants import GRID_LENGTH, GRID_WIDTH


def _spawn_weighted_choice(choices):
    if not choices:
        choices = [2, 4]

    if set(choices) == {2, 4} or choices == [2, 4]:
        return random.choices(choices, weights=[90, 10], k=1)[0]

    weights = []
    for value in choices:
        if value == 2:
            weight = 100
        elif value == 4:
            weight = 50
        else:
            weight = max(1, int(200 / value))
        weights.append(weight)

    return random.choices(choices, weights=weights, k=1)[0]


def _get_remove_values(max_value):
    if max_value < 1024:
        return 0

    removed = 2

    while max_value > 1024:
        max_value //= 2
        removed *= 2

    if removed > 8:
        removed //= 2
        if removed > 16:
            removed //= 2
            if removed > 32:
                removed //= 2
                if removed > 64:
                    removed //= 2

    return removed


def initial_random_choices(max_value):
    if max_value < 2:
        return [2, 4]

    if max_value == 256:
        max_value = 128
    if max_value == 512:
        max_value = 128

    random_choice = set()
    if max_value > 2:
        max_value = max_value // 2
        random_choice.add(max_value)

    while True:
        if max_value < 2:
            break
        max_value = max_value // 2
        if max_value < 2:
            break
        random_choice.add(max_value)

    random_choices = sorted(list(random_choice))
    return random_choices


def dynamic_random_choices(max_value):
    random_choice = set()
    if max_value > 4:
        max_value = max_value // 2 // 2 // 2
        random_choice.add(max_value)

        if max_value >= 8192:
            max_value = max_value // 2
            random_choice.add(max_value)
            if max_value >= 16384:
                max_value = max_value // 2
                random_choice.add(max_value)
                if max_value >= 32768:
                    max_value = max_value // 2
                    random_choice.add(max_value)
                    if max_value >= 65536:
                        max_value = max_value // 2
                        random_choice.add(max_value)

    if max_value < 2:
        return [2, 4]

    count = 0
    while True:
        if max_value < 2:
            break
        if count >= 5:
            break
        max_value = max_value // 2
        if max_value < 2:
            break
        random_choice.add(max_value)
        count += 1

    random_choices = sorted(list(random_choice))
    return random_choices


def random_value(matrix, score):
    max_value = 0
    for i in range(GRID_LENGTH):
        for j in range(GRID_WIDTH):
            if matrix[i][j] != 0:
                max_value = max(max_value, matrix[i][j])

    if max_value == 0:
        random_choices = [2, 4]
        print(random_choices)
        return _spawn_weighted_choice(random_choices), matrix
    elif max_value >= 1024:
        random_choices = dynamic_random_choices(max_value)
        remove_value = _get_remove_values(max_value)
        random_choices, matrix = remove_redundant(matrix, random_choices, remove_value)
        remove_value = random_choices[0]
        print("---------------")
        print(remove_value)
        print("---------------")
        remove_value //= 2
        _, matrix = remove_redundant(matrix, random_choices, remove_value)
        print(random_choices)
        return _spawn_weighted_choice(random_choices), matrix
    else:
        random_choices = initial_random_choices(max_value)
        if not random_choices:
            random_choices = [2, 4]
        print(random_choices)
        return _spawn_weighted_choice(random_choices), matrix

    
def remove_redundant(matrix, random_choices=None, remove_values=None):
    remove_value_list = []
    if random_choices is None:
        random_choices = [2, 4]

    if remove_values is None:
        return [2, 4], matrix

    while True:
        if remove_values < 2:
            break
        remove_value_list.append(remove_values)
        remove_values = remove_values // 2

    for value in remove_value_list:
        if value in random_choices:
            random_choices.remove(value)

        for i in range(GRID_LENGTH):
            for j in range(GRID_WIDTH):
                if matrix[i][j] == value:
                    matrix[i][j] = 0

    return random_choices, matrix


def print_matrix(matrix):
    for row in matrix:
        print(row)
    print()


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


def game_over(matrix, value):
    for i in range(GRID_WIDTH):
        for j in range(GRID_LENGTH):
            if matrix[j][i] == 0:
                return False

    for i in range(GRID_WIDTH):
        if matrix[(GRID_WIDTH - 1)][i] == value:
            return False

    return True


def merging_values(matrix, score, row, column, value):
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
                if matrix[new_row][new_column] == value:
                    matrix[new_row][new_column] = 0
                    count += 1
                    for (i, j) in indexes:
                        sec_new_row = new_row+i
                        sec_new_column = new_column+j
                        if 0 <= sec_new_row < GRID_LENGTH and 0 <= sec_new_column < GRID_WIDTH:
                            if ((sec_new_row, sec_new_column)) not in visited:
                                visited.add((sec_new_row, sec_new_column))
                                if matrix[sec_new_row][sec_new_column] == value:
                                    matrix[sec_new_row][sec_new_column] = 0
                                    count += 1

    if count == 2:
        value *= 2 
        matrix[row][column] = value
        score += value
    elif count == 3:
        value *= 4 
        matrix[row][column] = value
        score += value
    elif count == 4:
        value *= 8
        matrix[row][column] = value
        score += value
    else:
        return False, matrix, score, count


    return True, matrix, score, count


def merge_column(matrix, score, column=-1):
    count = 0
    if column == -1:
        for i in range(GRID_WIDTH):
            for j in range(GRID_LENGTH):
                value = matrix[j][i]
                if value == 0:
                    continue
                merged, matrix, score, count = merging_values(matrix, score, j, i, value)
                if merged:
                    return True, matrix, score, count
    else:
        for j in range(GRID_LENGTH):
            value = matrix[j][column]
            if value == 0:
                continue
            merged, matrix, score, count = merging_values(matrix, score, j, column, value)
            if merged:
                return True, matrix, score, count

    return False, matrix, score, count
