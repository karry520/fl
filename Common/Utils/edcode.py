def encode(indx_sign):
    length = len(indx_sign)
    n = length % 32
    if n != 0:
        length += 32 - n
        add = [0 for i in range(32 - n)]
        indx_sign += add
    tmp = []
    for j in range(0, length, 32):
        res = 0
        for t in range(32):
            res += indx_sign[j + t] * (2 ** (31 - t))
        tmp.append(res)

    return tmp


def decode(bf):
    indx_sign = []
    for a in bf:
        tmp = []
        for t in range(32):
            tmp.append(a // (2 ** (31 - t)))
            a %= (2 ** (31 - t))
        indx_sign.extend(tmp)

    return indx_sign


# import numpy as np
#
# if __name__ == "__main__":
#     a = np.random.randint(2, size=10)
#     print(a)
#     b = np.nonzero(a)[0]
#     c = a[b]=[2 for _ in b]
#     print(c)
