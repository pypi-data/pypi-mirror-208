# this will contain a set of binary tools
from skimage.measure import label, regionprops
from skimage.draw import ellipse

# should also work for 3D even though the 3D version is not super elegant
def ellipsoidify_dots(binary_dots):
    """
    replaces all 2D dots detected by an equivalent ellipse using bbox radius to draw the dot
    :param binary_dots: an image that contains dots (typically obtained through binarization of an image)
    :return:
    """
    # try replace all spots by a circle of the same size centered on the centroid

    # if image is 3D --> loop over all images
    if len(binary_dots.shape) == 3:
        # image is 3D --> do this for every channel (not ideal ideally should draw a 3D ellipsoid but all is ok for now)
        for iii,img_2D in enumerate(binary_dots):
            binary_dots[iii] = ellipsoidify_dots(img_2D)
        return binary_dots

    lab_dots = label(binary_dots,connectivity=None, background=0)
    rps_dots = regionprops(lab_dots)

    for region in rps_dots:
        centroid = region.centroid
        bbox = region.bbox
        # draw a circle that fits that
        rr, cc = ellipse(centroid[0], centroid[1], r_radius=abs(bbox[0]-bbox[2])/2, c_radius=abs(bbox[1]-bbox[3])/2, shape=binary_dots.shape)
        binary_dots[rr, cc] = binary_dots.max()
    return binary_dots

if __name__ == '__main__':
    pass