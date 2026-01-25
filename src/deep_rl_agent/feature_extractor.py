import math
from typing import Dict, Tuple
from config.constants import GRID_WIDTH, GRID_LENGTH
from core.utils.utils import rearrange, merge_column


class FeatureExtractor:
    def __init__(self):
        self.grid_width = GRID_WIDTH
        self.grid_length = GRID_LENGTH

    def clamp(self, value: float, low: float = 0.0, high: float = 1.0) -> float:
        return max(low, min(high, value))

    def norm_empty(self, matrix) -> float:
        total = self.grid_width * self.grid_length
        empties = sum(
            1 for r in range(self.grid_length) for c in range(self.grid_width)
            if matrix[r][c] == 0
        )
        return self.clamp(empties / total)

    def norm_score(self, score: int) -> float:
        if score <= 0:
            return 0.0
        return self.clamp(math.log2(score + 1) / 12)

    def norm_merge(self, merges: int) -> float:
        return self.clamp(merges / 4.0)

    def calculate_monotonicity(self, matrix) -> float:
        score = 0.0
        comparisons = 0
        for col in range(self.grid_width):
            for row in range(self.grid_length - 1):
                current_value = matrix[row][col]
                next_value = matrix[row + 1][col]
                if current_value >= next_value:
                    score += 1
                else:
                    if current_value > 0 and next_value > 0:
                        score -= math.log2(next_value) - math.log2(current_value)
                comparisons += 1
        if comparisons == 0:
            return 0.0
        return score / comparisons

    def calculate_smoothness(self, matrix) -> float:
        smoothness = 0.0
        comparisons = 0
        for row in range(self.grid_length):
            for col in range(self.grid_width):
                if matrix[row][col] > 0:
                    value = math.log2(matrix[row][col])
                    if col + 1 < self.grid_width and matrix[row][col + 1] > 0:
                        neighbor = math.log2(matrix[row][col + 1])
                        smoothness += abs(value - neighbor)
                        comparisons += 1
                    if row + 1 < self.grid_length and matrix[row + 1][col] > 0:
                        neighbor = math.log2(matrix[row + 1][col])
                        smoothness += abs(value - neighbor)
                        comparisons += 1
        if comparisons == 0:
            return 0.0
        return smoothness / comparisons

    def corner_bonus(self, matrix) -> float:
        max_val = 0
        max_pos = (0, 0)
        for row in range(self.grid_length):
            for col in range(self.grid_width):
                value = matrix[row][col]
                if value > max_val:
                    max_val = value
                    max_pos = (row, col)
        row, col = max_pos
        if (row, col) == (0, 0):
            return 1.0
        if row == 0:
            return 0.7
        return 0.0

    def compute_features(
        self, column: int, matrix, move_score: int, merge_count: int
    ) -> Dict[str, float]:
        mono_raw = self.calculate_monotonicity(matrix)
        smooth_raw = self.calculate_smoothness(matrix)
        features = {
            "score": self.norm_score(move_score),
            "empty": self.norm_empty(matrix),
            "merge": self.norm_merge(merge_count),
            "mono": self.clamp((mono_raw + 1) / 2),
            "smooth": self.clamp(1 - smooth_raw / 6.0),
            "corner": self.corner_bonus(matrix),
        }
        return features

    def simulate_move(self, matrix, column: int, value: int) -> Tuple[int, int, object]:
        temp = [row[:] for row in matrix]
        index = 0
        score_gained = 0
        distinct_merges = 0
        while True:
            if index == self.grid_length:
                last_row = self.grid_length - 1
                if temp[last_row][column] == value:
                    temp[last_row][column] *= 2
                    score_gained += temp[last_row][column]
                    distinct_merges += 1
                    while True:
                        merged, _, score_delta, _ = merge_column(temp, 0, column)
                        score_gained += score_delta
                        if not merged:
                            break
                        distinct_merges += 1
                        temp = rearrange(temp, column)
                    return score_gained, distinct_merges, temp
                return -1, -1, temp
            if temp[index][column] == 0:
                temp[index][column] = value
                while True:
                    merged, _, score_delta, _ = merge_column(temp, 0, column)
                    score_gained += score_delta
                    if not merged:
                        break
                    distinct_merges += 1
                    temp = rearrange(temp, column)
                break
            index += 1
        for row in range(self.grid_width):
            while True:
                merged, _, score_delta, _ = merge_column(temp, 0, row)
                score_gained += score_delta
                if not merged:
                    break
                distinct_merges += 1
                temp = rearrange(temp, row)
        return score_gained, distinct_merges, temp
