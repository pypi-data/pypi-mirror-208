# TODO also make a code that gets only one position of a multiposition aoutput so that I can use pipes with things that are not pipeable...
# this should be part of the pipeable pipeline

# TODO I could also make a repacker that creates a dict with defined values from an input to pass it to another function!
import random

import matplotlib.pyplot as plt

from epyseg.img import apply_2D_gradient, create_random_intensity_graded_perturbation, Img


def GuidedDataRecoverer(input_data, indices_to_recover, auto_unpack_if_single=True):
    if input_data is None:
        return None
    # if indices_to_recover
    # shall I allow negative indices
    # check if input_data is iterable otherwise

    assert isinstance(input_data, (list, tuple)), "input_data should be a list or a tuple"

    # create a list/tuple with all the values
    if isinstance(indices_to_recover, int):
        indices_to_recover = [indices_to_recover]

    for val in indices_to_recover:
        assert isinstance(val, int), 'indices must be integers'

    data_to_be_recovered = [input_data[idx] for idx in indices_to_recover]
    if auto_unpack_if_single and len(indices_to_recover) == 1:
        return data_to_be_recovered[0]
    else:
        return data_to_be_recovered


# just for a test
def graded_intensity_modification(orig, parameters, is_mask):
    out = orig
    if not is_mask:
        out = apply_2D_gradient(orig,create_random_intensity_graded_perturbation(orig, off_centered=True))
    return [], out

if __name__ == '__main__':
    # this is a test

    input_data = ['crap', 'important', 'crap2']
    assert GuidedDataRecoverer(input_data, 1) == 'important'
    assert GuidedDataRecoverer(input_data, -2) == 'important'
    assert GuidedDataRecoverer(input_data, -2, auto_unpack_if_single=False) == ['important']
    assert GuidedDataRecoverer(input_data, [0, 1]) == ['crap', 'important']

    # try pipes to get the stuff done
    # so easy with random to apply the same the only difficulty is that the nb of random calls should be the same --> inportant to keep in mind when doing this

    from datetime import datetime
    seed = datetime.now()
    random.seed(seed)

    orig = Img('/E/Sample_images/sample_images_PA/trash_test_mem/mini/focused_Series012.png')[...,1]
    out = GuidedDataRecoverer(graded_intensity_modification(orig, None,False),-1)
    plt.imshow(out)
    plt.show()

    random.seed(seed)
    random.randint(0,12)# any extra random call messes it up but that makes sense

    # whatever happens the nb of random calls should be the same --> could add a fake option that calls random the exact same nb of times --> TODO
    # if I have that parameters become useless --> ok most likely

    orig = Img('/E/Sample_images/sample_images_PA/trash_test_mem/mini/focused_Series012.png')[..., 1]
    out = GuidedDataRecoverer(graded_intensity_modification(orig, None, False), -1)
    plt.imshow(out)
    plt.show()



