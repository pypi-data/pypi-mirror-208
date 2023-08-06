def fs(n):
    assert n >= 0, "n > 0"
    if n <= 1:
        return n
    return fs(n - 1) + fs(n - 2)
# 获得斐波那契数列，项数20
for i in range(1, 20):
    print(fs(i), end=' ')


