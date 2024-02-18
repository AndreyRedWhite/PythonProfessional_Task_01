#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import wraps


def disable(func):
    '''
    Disable a decorator by re-assigning the decorator's name
    to this function. For example, to turn off memoization:
    '''
    return func


def decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return result
    return wrapper


def countcalls(func):
    '''Decorator that counts calls made to the function decorated.'''

    @wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.calls += 1
        return func(*args, **kwargs)
    wrapper.calls = 1
    return wrapper


def memo(func):
    '''
    Memoize a function so that it caches all return values for
    faster future lookups.
    '''

    cache = {}

    @wraps(func)
    def wrapper(*args, **kwargs):
        key = args + tuple(sorted(kwargs.items()))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    return wrapper


def n_ary():
    '''
    Given binary function f(x, y), return an n_ary function such
    that f(x, y, z) = f(x, f(y,z)), etc. Also allow f(x) = x.
    '''
    return


def trace(prefix=''):
    def inner(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            wrapper.depth += 1
            args_repr = [repr(a) for a in args]
            kwargs_repr = [f"{k}={v}" for k, v in kwargs.items()]
            signature = ", ".join(args_repr + kwargs_repr)
            print(f"{prefix * (wrapper.depth - 1)}{prefix} --> {func.__name__}({signature})")
            result = func(*args, **kwargs)
            print(f"{prefix * (wrapper.depth - 1)}{prefix} <-- {func.__name__} == {result}")
            wrapper.depth -= 1
            return result
        wrapper.depth = 0
        return wrapper
    return inner


@memo
@countcalls
# @n_ary
def foo(a, b):
    return a + b


@countcalls
@memo
# @n_ary
def bar(a, b):
    return a * b


@countcalls
@trace("####")
@memo
def fib(n):
    """Some doc"""
    return 1 if n <= 1 else fib(n-1) + fib(n-2)


def main():
    print(foo(4, 3))
    # print(foo(4, 3, 2))
    print(foo(4, 3))
    print("foo was called", foo.calls, "times")

    print(bar(4, 3))
    # print(bar(4, 3, 2))
    # print(bar(4, 3, 2, 1))
    print("bar was called", bar.calls, "times")

    print(fib.__doc__)
    fib(3)
    print(fib.calls, 'calls made')


if __name__ == '__main__':
    main()