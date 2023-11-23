from functools import reduce


def compose2(f, g):
    return lambda *a, **kw: f(g(*a, **kw))


def pipe2(f, g):
    return lambda *a, **kw: g(f(*a, **kw))


def compose(*fs):
    return reduce(compose2, fs)


def pipe(*fs):
    return reduce(pipe2, fs)
