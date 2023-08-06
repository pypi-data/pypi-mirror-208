import math
from random import gauss

import matplotlib.pyplot as plt
import numpy as np
import qtpy
from numpy.ma.testutils import assert_array_equal

from epyseg.img import Img,  pop
from epyseg.settings.global_settings import print_default_qtpy_UI_really_in_use
from epyseg.utils.loadlist import loadlist
import random


# do that for all GUIs --> TODO

if __name__ == '__main__':
    if True:
        # incroyable ça marche ici mais pas en unittest ... --> comprend rien

        # KEEP ALL ça marche
        # tst_pyqt5()
        # tst_pyside2()
        # tst_pyside6()
        # there are weird bugs but globally ok


        import sys
        sys.exit(0)

    if True:
        img = Img('/E/Sample_images/sample_images_FIJI/150707_WTstack.lsm')
        # auto_scale(img)
        pop(img)

        img = Img('/E/Sample_images/sample_images_FIJI/AuPbSn40.jpg')
        pop(img)
        # ok but then where is the bug???

        import sys
        sys.exit(0)
