# test LocalImportsNotAllowed class


def compute(n):
    for i in range(1, n):
        print(i * "*")
    from json import load

    load(...)
