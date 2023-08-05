from shared import binw, bitconfigs, bin_bitmask


# def positions_via_bin(n, w):
#     return [i for i, b in enumerate(binw(n, w)) if b == '1']

def positions_via_bin(n, w):
    return [i for i, b in enumerate(bin(n)[2:].rjust(w, '0')) if b == '1']


lookup = [positions_via_bin(i, 8) for i in range(256)]

def positions_via_bytes(n, w):
    return [i + rpos
            for i, b in zip(range(0, w, 8), n.to_bytes(w//8, "big", signed=False))
            for rpos in lookup[b]]

k = 240349839028904802576018347923479561957

print(binw(k, 128))
assert positions_via_bin(k, 128) == positions_via_bytes(k, 128)

import timeit
from math import log2,ceil


N = 3**100_000
# Nb = ceil(log2(N) + 1)


def fcn1():
    s = N
    one_bit_indexes = []
    index = 0
    while s: # returns true if sum is non-zero
        if s & 1: # returns true if right-most bit is 1
            one_bit_indexes.append(index)
        s >>= 1 # discard the right-most bit
        index += 1
    return one_bit_indexes


def fcn2():
    bits = []
    for i, c in enumerate(bin(N)[:1:-1], 1):
        if c == '1':
            bits.append(i)
    return bits


def fcn3():
    return [i for i in range(N.bit_length()) if N & (1<<i)]




def fcn4():
    nbits = N.bit_length()
    nbytes = nbits//8 + 1
    unsigned_big = N.to_bytes(nbytes, "big", signed=False)
    return [i + rpos
            for i, b in zip(range(0, nbits, 8), unsigned_big)
            for rpos in lookup[b]]


print(timeit.timeit(fcn1, number=1))
print(timeit.timeit(fcn2, number=1))
print(timeit.timeit(fcn3, number=1))
print(timeit.timeit(fcn4, number=1))


"""


3**100K
0.6382
0.0116
0.2926
0.0052

3**1M
62.4622
0.1276
31.8356
0.0582

"""