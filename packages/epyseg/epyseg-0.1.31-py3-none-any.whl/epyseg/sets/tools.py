# just a small class to do various sets operations
# could easily do it for any given size of sets

def difference(set1, set2):
    """
    returns the elements of set 1 that are not in set 2
    :param set1:
    :param set2:
    :return:
    """
    if not isinstance(set1, set):
        set1 = set(set1)
    return set1.difference(set2)

def differences(set1, set2):
    """
    returns the elements of set 1 and set 2 that are not present in the other set
    :param set1:
    :param set2:
    :return:
    """
    dif1 = difference(set1,set2)
    dif2 = difference(set2,set1)
    return dif1.union(dif2)

def intersection(set1, set2):
    if not isinstance(set1, set):
        set1 = set(set1)
    return set1.intersection(set2)

def union_no_dupes(*sets):
    output_set = set(sets[0])
    for st in sets[1:]:
        output_set = output_set.union(st)
    return output_set



if __name__ == '__main__':
    set1 = ['toto', 'tutu', 'tata']
    set2 = ['tete', 'tutu', 'titi']

    print(intersection(set1, set2))
    print(union_no_dupes(set1,set2))
    print(differences(set1, set2))
    print(difference(set1, set2))
