# test LocalImportsNotAllowed class


def TestFunc(n):
    for i in range(1, n):
        print(i * "*")
    from json import load

    load(...)
