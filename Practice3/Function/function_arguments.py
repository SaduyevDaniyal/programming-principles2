def f1(a, b):
    print(a, b)

f1(1, 2)


def f2(a, b):
    print(a, b)

f2(b=4, a=3)


def f3(a, b=2):
    return a ** b

print(f3(5))
print(f3(5, 3))


def f4(*a):
    s = 0
    for i in a:
        s += i
    return s

print(f4(1, 2, 3))
print(f4(4, 5, 6, 7))


def f5(**a):
    for k in a:
        print(k, a[k])

f5(a=1, b=2, c=3)


