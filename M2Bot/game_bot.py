import copy
import math

from config.constants import GRID_WIDTH, GRID_LENGTH
from game_logic.utils.utils import rearrange, merge_column


class GameBot:
    def __init__(self):
        self.W_SCORE = 20.0
        self.W_EMPTY = 1500.0  # Empty space is critical
        self.W_MERGE_CHAIN = 50.0  # Reward cascading merges
        self.W_MONOTONICITY = 50.0  # Order matters
        self.W_SMOOTHNESS = 5.0    # Neighbor compatibility
        self.W_CORNER = 1000.0     # Keep max tile in corner

    def solve(self, matrix, next_value):
        best_score = -float('inf')
        best_column = 0

        for col in range(GRID_WIDTH):
            temp_matrix = copy.deepcopy(matrix)
            score_gain, distinct_merges = self.simulate_move(temp_matrix, col, next_value)

            if score_gain == -1:
                continue

            heuristic_score = self.evaluate_board(temp_matrix, score_gain, distinct_merges)
            if heuristic_score > best_score:
                best_score = heuristic_score
                best_column = col

        return best_column

    def evaluate_board(self, matrix, move_score, merge_count):
        score = 0
        score += move_score * self.W_SCORE
        if merge_count > 1:
            score += merge_count * self.W_MERGE_CHAIN

        score += self.count_empty_cells(matrix) * self.W_EMPTY
        score += self.calculate_monotonicity(matrix) * self.W_MONOTONICITY
        score -= self.calculate_smoothness(matrix) * self.W_SMOOTHNESS

        max_value = 0
        max_position = (0, 0)
        for row in range(GRID_LENGTH):
            for colomn in range(GRID_WIDTH):
                if matrix[row][colomn] > max_value:
                    max_value = matrix[row][colomn]
                    max_position = (row, colomn)

        if max_position == (0, 0):
            score += self.W_CORNER

        return score

    def count_empty_cells(self, matrix):
        count_zero = 0

        for i in range(GRID_LENGTH):
            for j in range(GRID_WIDTH):
                if matrix[i][j] == 0:
                    count_zero += 1

        return count_zero

    def calculate_monotonicity(self, matrix):
        score = 0

        for colomn in range(GRID_WIDTH):
            for row in range(GRID_LENGTH - 1):
                current_value = matrix[row][colomn]
                next_value = matrix[row+1][colomn]

                if current_value >= next_value:
                    score += 1
                else:
                    score -= (math.log2(next_value) - math.log2(current_value)) if current_value > 0 and next_value > 0 else 0

        return score

    def calculate_smoothness(self, matrix):
        smoothness = 0

        for row in range(GRID_LENGTH):
            for colomn in range(GRID_WIDTH):
                if matrix[row][colomn] > 0:
                    value = math.log2(matrix[row][colomn])

                    if colomn + 1 < GRID_WIDTH and matrix[row][colomn+1] > 0:
                        neighbor = math.log2(matrix[row][colomn + 1])
                        smoothness += abs(value - neighbor)

                    if row + 1 < GRID_LENGTH and matrix[row + 1][colomn] > 0:
                        neighbor = math.log2(matrix[row + 1][colomn])
                        smoothness += abs(value - neighbor)

        return smoothness

    def simulate_move(self, matrix, column, value):
        """
        Simulates adding a value to a column.
        Returns (score_gain, distinct_merge_count).
        Returns (-1, -1) if the move is invalid (column full).
        """
        
        index = 0
        score_gained = 0
        distinct_merges = 0
        
        while True:
            if index == GRID_LENGTH:
                # Column is visibly full
                last_row = GRID_LENGTH - 1
                if matrix[last_row][column] == value:
                     matrix[last_row][column] *= 2
                     score_gained += matrix[last_row][column]
                     distinct_merges += 1
                     
                     # Cascading merges
                     while True:
                         merged, _, score_delta, count = merge_column(matrix, 0, column)
                         score_gained += score_delta
                         if not merged:
                             break
                         distinct_merges += 1
                         matrix = rearrange(matrix, column)
                     return score_gained, distinct_merges
                else:
                    return -1, -1 # Column full and no merge possible

            if matrix[index][column] == 0:
                matrix[index][column] = value
                
                # Cascading merges
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
        
        return score_gained, distinct_merges
