# prime-faster - Faster Prime Number Generator
# Author: Takahashi Akari <akaritakahashioss@gmail.com>
# License: MIT License Copyright (c) 2022 Takahashi Akari <akaritakahashioss@gmail.com>
# Version: 0.0.9
# Date: 2022-08-08
# Python: 3.10.6
# Description: prime-faster - Faster Prime Number Generator

from numpy import sqrt
import numpy

def is_prime(n):
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True

def get_prime(n):
    if n < 2:
        return []
    if n == 2:
        return [2]
    if n == 3:
        return [2, 3]
    n += 1
    sieve = numpy.ones(n // 3 + (n % 6 == 2), dtype=bool)
    for i in range(1, int(sqrt(n)) // 3 + 1):
        if sieve[i]:
            k = 3 * i + 1 | 1
            sieve[k * k // 3 :: 2 * k] = False
            sieve[k * ( k - 2 * (i & 1 ) + 4) // 3 :: 2 * k] = False
    np = numpy.r_[2, 3, ((3 * numpy.nonzero(sieve)[0][1:] + 1)|1)]
    # return array
    return np.tolist()
