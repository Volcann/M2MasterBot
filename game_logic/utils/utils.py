import random
from queue import Queue

from config.constants import GRID_LENGTH, GRID_WIDTH

def temp_random_choices(score):
    if score < 50:
        random_choices = [2, 4, 8]
    elif score < 100:
        random_choices = [2, 4, 8, 16]
    elif score < 200:
        random_choices = [2, 4, 8, 16, 32]
    elif score < 300:
        random_choices = [2, 4, 8, 16, 32, 64]
    else:
        random_choices = [2, 4, 8, 16, 32, 64]
        
    print(random_choices)
    return random.choices(random_choices)[0]


def dynamic_random_choices(max_value):
    random_choice = set()
    count = 0
    max_value = max_value // 2 // 2
    
    while True:
        if count == 6:
            break
        max_value = max_value // 2
        random_choice.add(max_value)
        count += 1

    random_choices = sorted(list(random_choice))
    return random_choices


def random_value(matrix, score):
    max_value = 2
    for i in range(GRID_LENGTH):
        for j in range(GRID_WIDTH):
            if matrix[i][j] != 0:
                max_value = max(max_value, matrix[i][j])

    if max_value >= 1024:
        print("dynamic")
        random_choices = dynamic_random_choices(max_value)
        max_value = random_choices[0]
        while True:
            if max_value < 2:
                break
            max_value = max_value // 2
            matrix = remove_redundant(matrix, max_value)
        return random.choices(random_choices)[0], matrix
    else:
        print("temp")
        return temp_random_choices(score), matrix


def remove_redundant(matrix, value):
    for i in range(GRID_LENGTH):
        for j in range(GRID_WIDTH):
            if matrix[i][j] == value:
                matrix[i][j] = 0
    return matrix


def print_matrix(matrix):
    for row in matrix:
        print(row)
    print()


def rearrange(matrix, column=None):
    if column is None:
        for i in range(GRID_LENGTH):
            queue = Queue()
            non_zero_value = 0

            for j in range(GRID_WIDTH):
                if matrix[j][i] == 0:
                    continue
                else:
                    queue.put(matrix[j][i])

            for j in range(GRID_WIDTH):
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

    for i in range(GRID_LENGTH):
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
                    print("EXIST", new_row, new_column)
                    print()
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
                                    print("EXIST", sec_new_row, sec_new_column)
                                    print()
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
        return False, matrix, score

    print("Count", count)
    print("Merged", value, "at", row, column)
    return True, matrix, score


def merge_column(matrix, score, column=-1):
    print(score)
    if column == -1:
        for i in range(GRID_LENGTH):
            for j in range(GRID_WIDTH):
                value = matrix[j][i]
                if value == 0:
                    continue
                merged, matrix, score = merging_values(matrix, score, j, i, value)
                if merged:
                    return True, matrix, score
    else:
        for j in range(GRID_WIDTH):
            value = matrix[j][column]
            if value == 0:
                continue
            merged, matrix, score = merging_values(matrix, score, j, column, value)
            if merged:
                return True, matrix, score
    return False, matrix, score
