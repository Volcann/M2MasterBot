import copy
import math

from config.constants import GRID_WIDTH, GRID_LENGTH
from core.utils.utils import rearrange, merge_column


class HeuristicBot:
    def __init__(self):
        self.weights = {
            "score": 0.15,
            "empty": 0.30,
            "merge": 0.10,
            "mono": 0.15,
            "smooth": 0.15,
            "corner": 0.15,
        }
        self.learning_rate = 0.05

    def evaluate_board(self, column, matrix, move_score, merge_count):
        features = self.compute_features(column, matrix, move_score, merge_count)
        total = 0

        for key, value in features.items():
            total += self.weights[key] * value

        return total

    def norm_score(self, score):
        if score <= 0:
            return 0.0
        return self.soft_norm(math.log2(score + 1), scale=6.0)

    def soft_norm(self, x, scale):
        return x / (x + scale)

    def norm_empty(self, matrix):
        empties = sum(
            1 for r in range(GRID_LENGTH)
            for c in range(GRID_WIDTH)
            if matrix[r][c] == 0
        )
        return self.soft_norm(empties, scale=GRID_WIDTH)

    def norm_merge(self, merges):
        return self.soft_norm(merges, scale=2.0)

    def norm_monotonicity(self, matrix):
        raw = self.calculate_monotonicity(matrix)
        return 0.5 + 0.5 * math.tanh(raw)

    def norm_smoothness(self, matrix):
        raw = self.calculate_smoothness(matrix)
        return 1.0 - self.soft_norm(raw, scale=2.0)

    def compute_features(self, column, matrix, move_score, merge_count):
        return {
            "score": self.norm_score(move_score),
            "empty": self.norm_empty(matrix),
            "merge": self.norm_merge(merge_count),
            "mono": self.norm_monotonicity(matrix),
            "smooth": self.norm_smoothness(matrix),
            "corner": self.corner_bonus(column, matrix),
        }

    def update_weights(self, features, reward):
        if reward <= 0:
            return

        for key in self.weights:
            self.weights[key] += self.learning_rate * reward * features[key]

        total = sum(self.weights.values())
        for key in self.weights:
            self.weights[key] /= total

    def solve(self, matrix, next_value, debugger=None):
        best_score = -float('inf')
        best_column = 0
        move_summaries = []
        for column in range(GRID_WIDTH):
            temp_matrix = copy.deepcopy(matrix)
            score_gain, distinct_merges = self.simulate_move(temp_matrix, column, next_value)

            if score_gain == -1:
                continue

            features = self.compute_features(column, temp_matrix, score_gain, distinct_merges)
            heuristic_score = sum(self.weights[k] * features[k] for k in self.weights)
            self.update_weights(features, self.norm_score(score_gain))
            move_summaries.append({
                "col": column,
                "score": score_gain,
                "h_score": heuristic_score,
                "merges": distinct_merges
            })
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
            empty_count = sum(1 for row in range(GRID_LENGTH) if matrix[row][column] == 0)
            if empty_count <= threshold:
                penalty -= 100

        return penalty

    def corner_bonus(self, column, matrix):
        max_val = 0
        max_pos = (0, 0)
        for row in range(GRID_LENGTH):
            for column in range(GRID_WIDTH):
                value = matrix[row][column]
                if value > max_val:
                    max_val = value
                    max_pos = (row, column)

        row, column = max_pos
        if (row, column) == (0, 0):
            return 1.0
        if row == 0:
            return 0.7
        return 0.0

    def count_empty_cells(self, matrix):
        count_zero = 0

        for row in range(GRID_LENGTH):
            for column in range(GRID_WIDTH):
                if matrix[row][column] == 0:
                    count_zero += 1

        return count_zero

    def calculate_monotonicity(self, matrix):
        score = 0
        comparisons = 0
        for column in range(GRID_WIDTH):
            for row in range(GRID_LENGTH - 1):
                current_value = matrix[row][column]
                next_value = matrix[row+1][column]

                if current_value >= next_value:
                    score += 1
                else:
                    score -= (math.log2(next_value) - math.log2(current_value)) if current_value > 0 and next_value > 0 else 0
                comparisons += 1

        if comparisons == 0:
            return 0.0

        return score / comparisons

    def calculate_smoothness(self, matrix):
        smoothness = 0
        comparisons = 0
        for row in range(GRID_LENGTH):
            for column in range(GRID_WIDTH):
                if matrix[row][column] > 0:
                    value = math.log2(matrix[row][column])

                    if column + 1 < GRID_WIDTH and matrix[row][column+1] > 0:
                        neighbor = math.log2(matrix[row][column + 1])
                        smoothness += abs(value - neighbor)
                        comparisons += 1

                    if row + 1 < GRID_LENGTH and matrix[row + 1][column] > 0:
                        neighbor = math.log2(matrix[row + 1][column])
                        smoothness += abs(value - neighbor)
                        comparisons += 1
                else:
                    continue

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
