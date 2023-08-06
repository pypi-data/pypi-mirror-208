from capabilities import llm
from pydantic import BaseModel
from typing import List


def test_tutorial1():
    class PrimeFactor(BaseModel):
        prime: int
        exponent: int

    class PrimeFactorization(BaseModel):
        factors: List[PrimeFactor]

    @llm
    def factor_primes(number: int) -> PrimeFactorization:
        """
        Return a prime factorization of the `number` as a list of pairs of a `prime`s and `exponent`s.
        """
        ...

    def check_result(number: int, fac: PrimeFactorization):
        product = 1

        for prime_factor in fac.factors:
            product *= prime_factor.prime**prime_factor.exponent

        return number == product

    n = 85
    result = factor_primes(n)
    print(result, check_result(n, result))
    assert check_result(n, result)
    # factors=[PrimeFactor(prime=5, exponent=1), PrimeFactor(prime=17, exponent=1)] True


if __name__ == "__main__":
    test_tutorial1()
