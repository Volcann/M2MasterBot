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
