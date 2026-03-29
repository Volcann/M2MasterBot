def _get_remove_values(max_value):
    if max_value < 1024:
        return 0

    removed = 2

    while max_value > 1024:
        max_value //= 2
        removed *= 2

    if removed > 8:
        removed //= 2
        if removed > 16:
            removed //= 2
            if removed > 32:
                removed //= 2
                if removed > 64:
                    removed //= 2

    return removed


powers_of_two = [2**i for i in range(1, 64)]
print(f"{'Max Value':<15} | {'Removed':<10} | {'Reductions'}")
print("-" * 40)

for value in powers_of_two:
    result = _get_remove_values(value)
    if result > 0:
        print(f"{value:<15} | {result:<10}")
