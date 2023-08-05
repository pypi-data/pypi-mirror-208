# test UnconventionalFunctionNamesNotAllowed class


def TestFunc(n):
    for i in range(1, n):
        print(i * "*")
    from json import load

    load(...)


def testFunc(n):
    for i in range(1, n):
        print(i * "*")


def test_func(n):
    hamsters = ["nom nom", "paper bean"]
    hamster = ["nom nom", "paper bean", "maple"]
    print(hamsters)
    print(hamster)
    for i in range(1, n):
        print(i * "*")
