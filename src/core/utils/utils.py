import random
from queue import Queue

from config.constants import GRID_LENGTH, GRID_WIDTH


def _spawn_choice(choices):
    if not choices:
        choices = [2, 4]

    return random.choices(choices)[0]


def _get_remove_values(max_value):
    if max_value < 1024:
        return 0

    removed = 2
    while max_value > 1024:
        max_value //= 2
        removed *= 2

    thresholds = [
        8, 32, 64, 128, 256,
        512, 1024, 2048, 4096,
        8192, 16384, 32768, 65536,
        131072, 262144, 524288,
        1048576, 2097152, 4194304,
        8388608, 16777216, 33554432,
        67108864, 134217728, 268435456,
        536870912, 1073741824, 2147483648,
        4294967296, 8589934592, 17179869184,
        34359738368, 68719476736, 137438953472,
        274877906944, 549755813888, 1099511627776,
        2199023255552, 4398046511104, 8796093022208,
        17592186044416, 35184372088832, 70368744177664,
        140737488355328, 281474976710656, 562949953421312,
        1125899906842624, 2251799813685248, 4503599627370496,
        9007199254740992, 18014398509481984, 36028797018963968,
    ]

    for t in thresholds:
        if removed > t:
            removed //= 2
        else:
            break

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
    if max_value < 2:
        return [2, 4]

    random_choice = set()
    removed_value = _get_remove_values(max_value)

    count = 0
    while True:
        if count == 6:
            break
        removed_value *= 2
        max_value = removed_value
        count += 1

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


def random_value(matrix):
    max_value = 0
    for i in range(GRID_LENGTH):
        for j in range(GRID_WIDTH):
            if matrix[i][j] != 0:
                max_value = max(max_value, matrix[i][j])

    if max_value == 0:
        random_choices = [2, 4]
        return _spawn_choice(random_choices), matrix
    elif max_value >= 1024:
        random_choices = dynamic_random_choices(max_value)
        remove_value = _get_remove_values(max_value)

        random_choices, matrix = remove_redundant(
            matrix=matrix,
            random_choices=random_choices,
            remove_values=remove_value
        )
        return _spawn_choice(random_choices), matrix
    else:
        random_choices = initial_random_choices(max_value)
        if not random_choices:
            random_choices = [2, 4]
        return _spawn_choice(random_choices), matrix


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
        if matrix[GRID_LENGTH - 1][i] == value:
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
