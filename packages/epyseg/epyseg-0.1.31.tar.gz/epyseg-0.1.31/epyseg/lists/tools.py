# contains a set of useful methods for list and list operations
import itertools


def get_list_combinatorial(lst, repack_all_to_lists_if_not_lists=True, return_list=True):
    """
    creates all combinatorial possible for the content of a list. eg: ['D', ['1P', 'hinge_undefined'], '1P'] -->  [('D', '1P', '1P'), ('D', 'hinge_undefined', '1P')]
    :param lst:
    :param repack_all_to_lists_if_not_lists: if True converts every element that is not a list to a list --> avoid that string are being used as list and combinations are made using some of the letters of the string
    :return:
    """
    optimized_list = lst
    if repack_all_to_lists_if_not_lists:
        optimized_list = [[item] if not isinstance(item, list) else item for item in lst]

    tmp = list(itertools.product(*optimized_list))
    if return_list:
        tmp = [list(el) for el in tmp]

    return tmp


def list_contains_sublist(lst):
    """
    returns True if a list contains lists
    :param lst:
    :return:
    """
    for el in lst:
        if isinstance(el, list):
            return True
    return False


if __name__ == '__main__':
    test = ['D', ['1P', 'hinge_undefined'], '1P']
    print(list_contains_sublist(test))  # True
    combi = get_list_combinatorial(test)
    print(combi)  # [['D', '1P', '1P'], ['D', 'hinge_undefined', '1P']]
    print(list_contains_sublist(combi[0]))  # False
