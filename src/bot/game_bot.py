import copy
import math

from config.constants import GRID_WIDTH, GRID_LENGTH
from core.utils.utils import rearrange, merge_column


class GameBot:
    def __init__(self):
        self.W_SCORE = 20.0
        self.W_EMPTY = 1000.0          # Empty space is critical
        self.W_MERGE_CHAIN = 100.0    # Reward cascading merges
        self.W_MONOTONICITY = 300.0  # Order matters
        self.W_SMOOTHNESS = 200.0   # Neighbor compatibility
        self.W_CORNER = 400.0      # Keep max tile in corner

    def solve(self, matrix, next_value):
        best_score = -float('inf')
        best_column = 0

        for column in range(GRID_WIDTH):
            temp_matrix = copy.deepcopy(matrix)
            score_gain, distinct_merges = self.simulate_move(temp_matrix, column, next_value)

            if score_gain == -1:
                continue

            heuristic_score = self.evaluate_board(column, temp_matrix, score_gain, distinct_merges)
            if heuristic_score > best_score:
                best_score = heuristic_score
                best_column = column

        return best_column

    def evaluate_board(self, column, matrix, move_score, merge_count):
        score = 0
        score += move_score * self.W_SCORE

        if merge_count > 1:
            score += merge_count * self.W_MERGE_CHAIN

        score += self.count_empty_cells(matrix) * self.W_EMPTY
        score += self.calculate_monotonicity(matrix) * self.W_MONOTONICITY
        score -= self.calculate_smoothness(matrix) * self.W_SMOOTHNESS
        score += self.corner_bonus(column, matrix)
        score += self.column_stack_penalty(matrix)

        return score

    def column_stack_penalty(self, matrix):
        penalty = 0
        threshold = 1

        for column in range(GRID_WIDTH):
            empty_count = sum(1 for row in range(GRID_LENGTH) if matrix[row][column] == 0)
            if empty_count <= threshold:
                penalty -= 100
        # TODO: check if this column can merge values if no then its dangours
        return penalty

    def corner_bonus(self, column, matrix):
        max_value = 0
        max_position = (0, 0)
        score = 0

        for row in range(GRID_LENGTH):
            if matrix[row][column] > max_value:
                max_value = matrix[row][column]
                max_position = (row, column)

        if max_position == (0, column):
            score += self.W_CORNER * 2
        elif max_position == (1, column):
            score += self.W_CORNER
        elif max_position == (2, column):
            score -= self.W_CORNER
        elif max_position == (3, column):
            score -= self.W_CORNER * 2

        return score

    def count_empty_cells(self, matrix):
        count_zero = 0

        for row in range(GRID_LENGTH):
            for column in range(GRID_WIDTH):
                if matrix[row][column] == 0:
                    count_zero += 1

        return count_zero

    def calculate_monotonicity(self, matrix):
        score = 0

        for column in range(GRID_WIDTH):
            for row in range(GRID_LENGTH - 1):
                current_value = matrix[row][column]
                next_value = matrix[row+1][column]

                if current_value >= next_value:
                    score += 1
                else:
                    score -= (math.log2(next_value) - math.log2(current_value)) if current_value > 0 and next_value > 0 else 0

        return score

    def calculate_smoothness(self, matrix):
        smoothness = 0

        for row in range(GRID_LENGTH):
            for column in range(GRID_WIDTH):
                if matrix[row][column] > 0:
                    value = math.log2(matrix[row][column])

                    if column + 1 < GRID_WIDTH and matrix[row][column+1] > 0:
                        neighbor = math.log2(matrix[row][column + 1])
                        smoothness += abs(value - neighbor)

                    if row + 1 < GRID_LENGTH and matrix[row + 1][column] > 0:
                        neighbor = math.log2(matrix[row + 1][column])
                        smoothness += abs(value - neighbor)

        return smoothness

    def simulate_move(self, matrix, column, value):
        index = 0
        score_gained = 0
        distinct_merges = 0

        while True:
            if index == GRID_LENGTH:
                last_row = GRID_LENGTH - 1
                if matrix[last_row][column] == value:
                    matrix[last_row][column] *= 2
                    score_gained += matrix[last_row][column]
                    distinct_merges += 1

                    while True:
                        merged, _, score_delta, count = merge_column(matrix, 0, column)
                        score_gained += score_delta
                        if not merged:
                            break
                        distinct_merges += 1
                        matrix = rearrange(matrix, column)
                    return score_gained, distinct_merges
                else:
                    return -1, -1

            if matrix[index][column] == 0:
                matrix[index][column] = value
                while True:
                    merged, _, score_delta, count = merge_column(matrix, 0, column)
                    score_gained += score_delta
                    if not merged:
                        break
                    distinct_merges += 1
                    matrix = rearrange(matrix)
                break
            else:
                index += 1

        for row in range(GRID_WIDTH):
            while True:
                merged, _, score_delta, count = merge_column(matrix, 0, row)
                score_gained += score_delta

                if not merged:
                    break
                distinct_merges += 1
                matrix = rearrange(matrix)

        return score_gained, distinct_merges





















# import random

# weight_sets = [
#     {'W_SCORE': 20, 'W_EMPTY': 1000, 'W_MERGE_CHAIN': 100, 'W_MONOTONICITY': 300, 'W_SMOOTHNESS': 200, 'W_CORNER': 500},
#     {'W_SCORE': 15, 'W_EMPTY': 1500, 'W_MERGE_CHAIN': 120, 'W_MONOTONICITY': 250, 'W_SMOOTHNESS': 180, 'W_CORNER': 600},
#     # ...generate many random variants
# ]

# results = []

# for weights in weight_sets:
#     bot = GameBot()
#     # set custom weights
#     for k, v in weights.items():
#         setattr(bot, k, v)

#     # simulate N games
#     game_over_count = 0
#     for _ in range(50):  # 50 games per set
#         matrix = [[0]*GRID_WIDTH for _ in range(GRID_LENGTH)]
#         # simulate simplified moves here or with your GameLogic
#         # increase game_over_count if bot dies

#     results.append((weights, game_over_count))

# # sort by lowest game_over_count
# results.sort(key=lambda x: x[1])
# print("Best weight set:", results[0])
