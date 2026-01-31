def _get_remove_values(max_value):
    if max_value < 1024:
        return 0, 0

    removed = 2
    reduction_count = 0
    while max_value > 1024:
        max_value //= 2
        reduction_count += 1
        removed *= 2

    thresholds = [
        8, 32, 64, 128, 256,
        512, 1024, 2048, 4096,
        8192, 16384, 32768, 65536,
        131072, 262144, 524288,
        1048576, 2097152, 4194304,
        8388608, 16777216, 33554432,
        67108864, 134217728, 268435456,
        536870912, 1073741824, 2147483648,
        4294967296, 8589934592, 17179869184,
        34359738368, 68719476736, 137438953472,
        274877906944, 549755813888, 1099511627776,
        2199023255552, 4398046511104, 8796093022208,
        17592186044416, 35184372088832, 70368744177664,
        140737488355328, 281474976710656, 562949953421312,
        1125899906842624, 2251799813685248, 4503599627370496,
        9007199254740992, 18014398509481984, 36028797018963968,
    ]

    for t in thresholds:
        if removed > t:
            removed //= 2
            reduction_count += 1
        else:
            break

    return removed, reduction_count


powers_of_two = [2**i for i in range(1, 64)]
print(f"{'Max Value':<15} | {'Removed':<10} | {'Reductions'}")
print("-" * 40)

for value in powers_of_two:
    result, count = _get_remove_values(value)
    if result > 0:
        print(f"{value:<15} | {result:<10} | {count}")
