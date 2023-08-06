def digits(num):
    return list(map(int, str(num)))


def sumprod(a, b):
    r = 1
    for x, y in zip(a, b):
        r += x * y
    return r


def eulers_totient(num: int, *, pf: Dict[int, int] = None) -> int:
    phi = num
    for f in pf or prime_factors(num):
        phi *= (1 - 1/f)
    return int(round(phi))


def congruent(a, b, modulo) -> bool:
    return (a % modulo) == (b % modulo)


def chinese_remainder_theorem(remainders: list, moduli: list):
    """Solve a system of congruences, such as:
    x = 3   (mod 5)
    x = 1   (mod 7)
    x = 6   (mod 8)
    => find all values for x that satisfy this system
    """
    N = prod(moduli)
    nums = N // moduli
    inverses = [modular_inverse(num, modulo)
                for num, modulo in zip(nums, moduli)]
    x = sum(r*n*i for r, n, i in zip(remainders, nums, inverses)) % N
    return x, N
