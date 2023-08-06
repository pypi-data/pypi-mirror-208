# here I will put numpy tips
import matplotlib.pyplot as plt
import numpy as np

def get_value_from_nd_coords(img, nd_coords):
    return img[convert_nd_coords_to_numpy_format(nd_coords)]

def convert_nd_coords_to_numpy_format(nd_coords):
    return tuple(nd_coords.T)

def set_coords_to_value(img, nd_coords, value):
    img[convert_nd_coords_to_numpy_format(nd_coords)]=value

def convert_numpy_bbox_to_coord_pairs(bbox):
    '''
    returns coords pairs from a linear bbox (1,2,3,200,600,150) -->
    [[  1 200]
    [  2 600]
    [  3 150]]
    :param bbox: typically a region.bbox from regionprops
    :return: coord pairs
    '''
    if not isinstance(bbox, np.ndarray):
        bbox = np.asarray(bbox)
    return np.reshape(bbox, (2, int(bbox.size / 2))).T


def get_image_bounds(original_image):
    bounds = []
    for dim in range(len(original_image.shape)):
        bounds.append(0)
        bounds.append(original_image.shape[dim])

    # bounds = convert_numpy_bbox_to_coord_pairs(bounds)
    bounds = np.asarray(bounds).reshape(-1, 2)
    return bounds


def filter_nan_rows(coords):
    if coords.size == 0:
        print('empty array --> retruning array')
        return coords
    return coords[~np.isnan(coords).any(axis=1)]

if __name__ == '__main__':
    test = np.zeros(shape=(32,32))
    coords = np.asarray([[0,0],[16,16],[20,20]])
    set_coords_to_value(test, coords, 255) # --> same as test[coords[:,0],coords[:,1]] # and what is great is that infinite nb of dims are supported --> can write generic code for 2D and 3D --> really cool --> replace everywhere in my code
    plt.imshow(test)
    plt.show()

