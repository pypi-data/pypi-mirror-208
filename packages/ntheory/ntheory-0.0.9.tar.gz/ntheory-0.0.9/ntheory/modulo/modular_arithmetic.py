from ..binary import binary_digits


def modular_sum(*args, mod):
    """Compute (a+b)%modulo"""
    r = 0
    for x in args:
        r = (r + x) % mod
    return r


def modular_prod(*args, mod):
    """Compute (a+b)%modulo"""
    r = 1
    for x in args:
        r = (r*x) % mod
    return r


def modular_pow(a, b, *, mod):
    """ Modular exponentiation a^b
    5 ** 117 = 5 ** (1 + 4 + 16 + 32 + 64)
    """
    factors = []
    for bit in binary_digits(b)[::-1]:
        if bit:
            factors.append(a)
        a = modular_prod(a, a, mod=mod)

    return modular_prod(*factors, mod=mod)


def gcd_extended(a, b):
    """Implement the extended euclidian algorithm
    a*x + b*y = gcd(a, b)
    """
    if b > a:
        gcd, x, y = gcd_extended(b, a)
        return gcd, y, x
        # a, b = b, a

    chart = []
    while b > 0:
        chart.insert(0, (a, a//b))
        a, b = b, a % b
    gcd = a

    a, x, b, y = 0, 1, 0, 0
    for p, s in chart:
        a, x, b, y = p, y, a, x - y*s
    return gcd, x, y


def modular_inverse(num, modulo):
    g, x, y = gcd_extended(num, modulo)
    if g != 1:
        raise ValueError('No inverse exists!')
    return x % modulo
