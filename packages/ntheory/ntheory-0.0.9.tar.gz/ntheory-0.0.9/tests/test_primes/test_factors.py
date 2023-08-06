from ntheory.primes import prime_factors


def test_prime_factors():
    assert prime_factors(-10) == {}
    assert prime_factors(1) == {}
    assert prime_factors(2) == {2: 1}
    assert prime_factors(8) == {2: 3}
    assert prime_factors(8) == {2: 3}
