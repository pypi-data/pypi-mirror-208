from ntheory.modulo import modular_sum, modular_prod, modular_pow, gcd_extended, modular_inverse


def test_modular_sum():
    assert modular_sum(14, 17, mod=5) == 1


def test_modular_prod():
    assert modular_prod(4, 7, mod=6) == 4


def test_modular_pow():
    assert modular_pow(5, 117, mod=19) == 1


def test_gcd_extended():
    assert gcd_extended(888, 54) == (6, -2, 33)
    assert gcd_extended(1180, 482) == (2, -29, 71)
    assert gcd_extended(482, 1180) == (2, 71, -29)


def test_modular_inverse():
    assert modular_inverse(5, modulo=56) == 45
    assert modular_inverse(56, modulo=5) == 1
    assert modular_inverse(40, modulo=7) == 3
    assert modular_inverse(35, modulo=8) == 3
    assert modular_inverse(197, modulo=3000) == 533
