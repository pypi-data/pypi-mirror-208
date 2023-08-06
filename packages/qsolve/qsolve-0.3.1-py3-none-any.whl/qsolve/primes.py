import numpy as np


def get_prime_factors_list(number):

    prime_factors = []

    while number % 2 == 0:
        prime_factors.append(2)
        number = number / 2

    # After the above while loop, when number has been
    # divided by all the 2's - so the number must be odd at this point
    # Otherwise it would be perfectly divisible by 2 another time
    # so now that its odd I can skip 2 ( i = i + 2) for each increment
    for i in range(3, int(np.sqrt(number)) + 1, 2):
        while number % i == 0:
            prime_factors.append(int(i))
            number = number / i

    if number > 2:
        prime_factors.append(int(number))

    return prime_factors


def get_prime_factors(number):

    prime_factors_list = get_prime_factors_list(number)

    prime_factors = np.array(prime_factors_list)

    return prime_factors
