# will contain all tools for partial
from functools import partial

def get_method_name(partial_func):
    return partial_func.func.__name__

def is_partial(func):
    return isinstance(func, partial)

def are_function_names_matching(func1, func2):
    if is_partial(func1):
        func1 = get_method_name(func1)
    else:
        func1 = func1.__name__
    if is_partial(func2):
        func2 = get_method_name(func2)
    else:
        func2 = func2.__name__
    return func1 == func2

if __name__ == '__main__':
    def dummy():
        print('test')
    tst = partial(dummy)

    def dummy2():
        print('test2')

    print('is partial',is_partial(tst))

    print(get_method_name(tst))
    print(are_function_names_matching(dummy, dummy2))
    print(are_function_names_matching(dummy, dummy))
    print(are_function_names_matching(tst, dummy))