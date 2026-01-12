
import copy
import math
from config.constants import GRID_WIDTH, GRID_LENGTH
from game_logic.utils.utils import rearrange, merge_column, remove_redundant

class GameBot:
    def __init__(self):
        # Weights for the heuristic function
        self.W_SCORE = 20.0
        self.W_EMPTY = 1500.0  # Empty space is critical
        self.W_MERGE_CHAIN = 50.0 # Reward cascading merges
        self.W_MONOTONICITY = 50.0 # Order matters
        self.W_SMOOTHNESS = 5.0    # Neighbor compatibility
        self.W_CORNER = 1000.0     # Keep max tile in corner

    def solve(self, matrix, next_value):
        """
        Determines the best column to drop the next_value.
        Returns the column index (0 to GRID_WIDTH-1).
        """
        best_score = -float('inf')
        best_column = 0
        
        # Lookahead depth (1 for now to keep it fast, can increase if optimized)
        # For a simple game like this, depth 1 with good heuristics is usually enough.
        
        for col in range(GRID_WIDTH):
            temp_matrix = copy.deepcopy(matrix)
            score_gain, distinct_merges = self.simulate_move(temp_matrix, col, next_value)
            
            if score_gain == -1: # Invalid move
                continue

            heuristic_score = self.evaluate_board(temp_matrix, score_gain, distinct_merges)
            
            if heuristic_score > best_score:
                best_score = heuristic_score
                best_column = col

        return best_column

    def evaluate_board(self, matrix, move_score, merge_count):
        """
        Calculates a heuristic score for the board state.
        """
        score = 0
        
        # 1. Immediate score gained from the move
        score += move_score * self.W_SCORE
        
        # 2. Number of empty cells (Crucial for survival)
        empty_count = self.count_empty_cells(matrix)
        score += empty_count * self.W_EMPTY
        
        # 3. Chains (Distinct merges count > 1 means a chain occurred)
        if merge_count > 1:
            score += merge_count * self.W_MERGE_CHAIN

        # 4. Monotonicity (Encourage decreasing values along rows/cols)
        score += self.calculate_monotonicity(matrix) * self.W_MONOTONICITY
        
        # 5. Smoothness (Encourage small differences between neighbors)
        score -= self.calculate_smoothness(matrix) * self.W_SMOOTHNESS
        
        # 6. Corner Strategy (Keep Max Tile at Top-Left (0,0))
        max_val = 0
        max_pos = (0,0)
        for r in range(GRID_LENGTH):
            for c in range(GRID_WIDTH):
                if matrix[r][c] > max_val:
                    max_val = matrix[r][c]
                    max_pos = (r, c)
        
        if max_pos == (0, 0):
            score += self.W_CORNER
        
        return score

    def calculate_monotonicity(self, matrix):
        """
        Rewards board states where values increase/decrease monotonically.
        Since gravity pulls to Row 0, we want higher values at Row 0.
        We also want left-to-right monotonicity on Row 0.
        """
        score = 0
        
        # Vertical Monotonicity (Should decrease as index increases: 0 -> 4)
        for c in range(GRID_WIDTH):
            for r in range(GRID_LENGTH - 1):
                current = matrix[r][c]
                next_val = matrix[r+1][c]
                if current >= next_val:
                    score += 1
                else:
                     # Penalize if a larger block is blocked by a smaller one (if checking bottom-up)
                     # But here larger index = "below" in stack, but visually "lower" on screen?
                     # Gravity pulls to 0. So 0 is the "floor" of the stack in terms of accumulation?
                     # Yes, 0 is mostly filled.
                     # We want big blocks at 0. So 0 >= 1 >= 2...
                     score -= (math.log2(next_val) - math.log2(current)) if current > 0 and next_val > 0 else 0

        # Horizontal Monotonicity (Prefer decreasing left-to-right or right-to-left)
        # We'll check both directions and pick the best one to allow flexibility
        left_to_right = 0
        right_to_left = 0
        
        for r in range(GRID_LENGTH):
            for c in range(GRID_WIDTH - 1):
                curr = matrix[r][c]
                nxt = matrix[r][c+1]
                if curr >= nxt:
                    left_to_right += 1
                if curr <= nxt:
                    right_to_left += 1
        
        score += max(left_to_right, right_to_left)
        return score

    def calculate_smoothness(self, matrix):
        """
        Penalizes large value differences between adjacent cells.
        Uses log2 to make it linear with respect to power of 2.
        """
        smoothness = 0
        for r in range(GRID_LENGTH):
            for c in range(GRID_WIDTH):
                if matrix[r][c] > 0:
                    val = math.log2(matrix[r][c])
                    # Check Right
                    if c + 1 < GRID_WIDTH and matrix[r][c+1] > 0:
                        neighbor = math.log2(matrix[r][c+1])
                        smoothness += abs(val - neighbor)
                    # Check Down
                    if r + 1 < GRID_LENGTH and matrix[r+1][c] > 0:
                        neighbor = math.log2(matrix[r+1][c])
                        smoothness += abs(val - neighbor)
        return smoothness

    def count_empty_cells(self, matrix):
        count = 0
        for i in range(GRID_LENGTH):
            for j in range(GRID_WIDTH):
                if matrix[i][j] == 0:
                    count += 1
        return count

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
