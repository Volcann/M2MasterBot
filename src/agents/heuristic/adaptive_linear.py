import copy
import math
from config.constants import GRID_WIDTH, GRID_LENGTH
from core.utils.core_utils import rearrange, merge_column


class AdaptiveLinearBot:
    def __init__(self):
        self.weights = {
            "score": 1.0 / 7.0,
            "empty_cells": 1.0 / 7.0,
            "merges": 1.0 / 7.0,
            "monotonicity": 1.0 / 7.0,
            "smoothness": 1.0 / 7.0,
            "corner_bonus": 1.0 / 7.0,
            "stack": 1.0 / 7.0,
        }
        self.learning_rate = 0.05

    def evaluate_board(self, column, matrix, move_score, merge_count):
        features = self.compute_features(column, matrix, move_score, merge_count)
        total_heuristic = 0.0
        for key, value in features.items():
            total_heuristic += self.weights[key] * value
        return total_heuristic

    def compute_features(self, column, matrix, move_score, merge_count):
        return {
            "score": float(move_score),
            "empty_cells": float(self.count_empty_cells(matrix)),
            "merges": float(merge_count),
            "monotonicity": float(self.calculate_monotonicity(matrix)),
            "smoothness": float(self.calculate_smoothness(matrix)),
            "corner_bonus": float(self.corner_bonus(column, matrix)),
            "stack": float(self.norm_stack(matrix)),
        }

    def norm_stack(self, matrix):
        raw = self.column_stack_penalty(matrix)
        return max(-1.0, raw / (100.0 * GRID_WIDTH))

    def update_weights(self, features, reward):
        if reward <= 0:
            return
        for key in self.weights:
            self.weights[key] += self.learning_rate * reward * features[key]
        total = sum(self.weights.values())
        if total != 0:
            for key in self.weights:
                self.weights[key] /= total

    def solve(self, matrix, next_value, debugger=None):
        best_score = -float("inf")
        best_column = 0
        move_summaries = []
        for column in range(GRID_WIDTH):
            temp_matrix = copy.deepcopy(matrix)
            score_gain, distinct_merges = self.simulate_move(
                temp_matrix, column, next_value
            )
            if score_gain == -1:
                continue
            features = self.compute_features(
                column, temp_matrix, score_gain, distinct_merges
            )
            heuristic_score = sum((self.weights[k] * features[k] for k in self.weights))
            self.update_weights(features, score_gain)
            move_summaries.append(
                {
                    "col": column,
                    "score": score_gain,
                    "h_score": heuristic_score,
                    "merges": distinct_merges,
                }
            )
            if debugger:
                impact = {k: self.weights[k] * features[k] for k in self.weights}
                debugger.update(column, impact, heuristic_score)
            if heuristic_score > best_score:
                best_score = heuristic_score
                best_column = column
        if debugger:
            debugger.draw_summary(move_summaries, best_column)
        return best_column

    def column_stack_penalty(self, matrix):
        penalty = 0
        threshold = 1
        for column in range(GRID_WIDTH):
            empty_count = sum(
                (1 for row in range(GRID_LENGTH) if matrix[row][column] == 0)
            )
            if empty_count <= threshold:
                penalty -= 100
        return penalty

    def corner_bonus(self, _column, matrix):
        max_val, max_pos = 0, (0, 0)
        for r in range(GRID_LENGTH):
            for c in range(GRID_WIDTH):
                if matrix[r][c] > max_val:
                    max_val = matrix[r][c]
                    max_pos = (r, c)
        row, col = max_pos
        max_dist = (GRID_LENGTH - 1) + (GRID_WIDTH - 1)
        dist = row + col
        return 1.0 - (dist / max_dist)

    def count_empty_cells(self, matrix):
        count_zero = 0
        for row in range(GRID_LENGTH):
            for column in range(GRID_WIDTH):
                if matrix[row][column] == 0:
                    count_zero += 1
        return count_zero

    def calculate_monotonicity(self, matrix):
        return (self._mono_vertical(matrix) + self._mono_horizontal(matrix)) / 2.0

    def _mono_vertical(self, matrix):
        score, comparisons = 0, 0
        for col in range(GRID_WIDTH):
            for row in range(GRID_LENGTH - 1):
                cur, nxt = matrix[row][col], matrix[row + 1][col]
                if cur >= nxt:
                    score += 1
                elif cur > 0 and nxt > 0:
                    score -= math.log2(nxt) - math.log2(cur)
                comparisons += 1
        return score / comparisons if comparisons else 0.0

    def _mono_horizontal(self, matrix):
        score, comparisons = 0, 0
        for row in range(GRID_LENGTH):
            for col in range(GRID_WIDTH - 1):
                cur, nxt = matrix[row][col], matrix[row][col + 1]
                if cur >= nxt:
                    score += 1
                elif cur > 0 and nxt > 0:
                    score -= math.log2(nxt) - math.log2(cur)
                comparisons += 1
        return score / comparisons if comparisons else 0.0

    def calculate_smoothness(self, matrix):
        smoothness = 0
        comparisons = 0
        for row in range(GRID_LENGTH):
            for column in range(GRID_WIDTH):
                if matrix[row][column] > 0:
                    value = math.log2(matrix[row][column])
                    if column + 1 < GRID_WIDTH and matrix[row][column + 1] > 0:
                        neighbor = math.log2(matrix[row][column + 1])
                        smoothness += abs(value - neighbor)
                        comparisons += 1
                    if row + 1 < GRID_LENGTH and matrix[row + 1][column] > 0:
                        neighbor = math.log2(matrix[row + 1][column])
                        smoothness += abs(value - neighbor)
                        comparisons += 1
        if comparisons == 0:
            return 0.0
        return smoothness / comparisons

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
                    return (score_gained, distinct_merges)
                else:
                    return (-1, -1)
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
        return (score_gained, distinct_merges)
