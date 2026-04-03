from Crypto.Util.number import bytes_to_long, getStrongPrime

n = getStrongPrime(2048)
e = 2**16 + 1

flag = bytes_to_long(open("flag.txt", "rb").read())
c = pow(flag, e, n)

print(f"{n = }")
print(f"{e = }")
print(f"{c = }")
