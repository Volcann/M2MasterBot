GRID_LENGTH = 7
GRID_WIDTH = 5


def game_over(matrix, value):
    for i in range(GRID_WIDTH):
        for j in range(GRID_LENGTH):
            if matrix[j][i] == 0:
                return False

    for i in range(GRID_WIDTH):
        if matrix[GRID_LENGTH - 1][i] == value:
            return False

    return True


def run_tests():
    matrix1 = [
        [2, 4, 8, 16, 32],
        [32, 64, 128, 256, 512],
        [512, 1024, 2048, 4096, 8192],
        [0, 0, 0, 0, 0],
        [2, 4, 8, 16, 32],
        [64, 128, 256, 512, 1024],
        [2048, 4096, 8192, 16384, 32768],
    ]
    assert game_over(matrix1, 4096) is False
    print("Test 1 passed")

    matrix2 = [
        [2, 4, 8, 16, 32],
        [32, 64, 128, 256, 512],
        [512, 1024, 2048, 4096, 8192],
        [2, 4, 8, 16, 32],
        [64, 128, 256, 512, 1024],
        [2048, 4096, 8192, 16384, 32768],
        [2, 4, 8, 4096, 32],
    ]
    assert game_over(matrix2, 4096) is False
    print("Test 2 passed")

    matrix3 = [
        [2, 4, 8, 16, 32],
        [32, 64, 128, 256, 512],
        [512, 1024, 2048, 4096, 8192],
        [2, 4, 8, 16, 32],
        [64, 128, 256, 512, 1024],
        [2048, 4096, 8192, 16384, 32768],
        [2, 4, 8, 16, 32],
    ]
    assert game_over(matrix3, 4096) is True
    print("Test 3 passed")

    matrix4 = [[0]*5 for _ in range(7)]
    assert game_over(matrix4, 4096) is False
    print("Test 4 passed")

    print("All tests passed!")


if __name__ == "__main__":
    run_tests()
