# will contain a series of tools to better handle dicts

import numpy as np
import json

def string_to_dict(string):
    """
    converts a string representation of a dict back to a real dict
    :param string:
    :return:
    """
    if string is None:
        return None
    return json.loads(string.replace("'", '"').replace('None', 'null'))

def invert_keys_and_values(input_dict, warn_on_dupes=True):
    """
    swaps keys and values of a dict
    :param input_dict:
    :param warn_on_dupes:
    :return:
    """
    output_dict = {value:key for key, value in input_dict.items()}
    if warn_on_dupes:
        if len(output_dict)!=len(input_dict):
            print('Warning: some values in the dict are duplicated, keys and values cannot be inverted safely')
    return output_dict

def dict_to_numpy(input_dict):
    """
    converts a dict to a numpy array
    :param input_dict:
    :return:
    """
    # TODO add controls and report if dupe entries for example (I could get len of dict and len of the array first dim to see if all is ok
    return np.array(list(input_dict.items()))

def get_values_in_dict_matching_a_search_list(input_dict, search_list, ignore_not_found=True, value_for_not_found_if_not_ignored=None):
    """
    can be used to find all the values that match a search in a dict, can be used for retromapping for example
    :param input_dict:
    :param search_list:
    :param ignore_not_found:
    :param value_for_not_found_if_not_ignored:
    :return:
    """
    if ignore_not_found:
        output = [input_dict[search] for search in search_list if search in input_dict.keys()] # do I need to specify keys ????
    else:
        output = [input_dict[search] if search in input_dict.keys() else value_for_not_found_if_not_ignored for search in
                  search_list]  # do I need to specify keys ????
    return output

# convert smthg that is not a dict but has two values to a dict --> TODO add controls
def _to_dict(input):
    dct = {}
    for k,v in input:
        dct[k]=v
    return dct