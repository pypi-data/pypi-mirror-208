def prime_factors(n: int) -> dict:
    """Inefficient use sieve instead."""
    if n < 2:
        return dict()

    prime_factors = dict()
    while n % 2 == 0:
        prime_factors[2] = prime_factors.get(2, 0) + 1
        n //= 2

    for factor in range(3, n + 1, 2):
        while n % factor == 0:
            prime_factors[factor] = prime_factors.get(factor, 0) + 1
            n //= factor
    return prime_factors
