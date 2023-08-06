import os
from pathlib import Path
import math
from math import *
import numpy as np



def arcCenter(C, iH, oH, iLA, oLA, diff_radius=None):
    inner_radius = (np.sqrt(np.square(iH.x - C.x) + np.square(iH.y - C.y)) +
                    np.sqrt(np.square(iLA.x - C.x) + np.square(iLA.y - C.y))) / 2
    if diff_radius:
        outer_radius = inner_radius + diff_radius
    else:
        outer_radius = (np.sqrt(np.square(oH.x - C.x) + np.square(oH.y - C.y)) +
                        np.sqrt(np.square(oLA.x - C.x) + np.square(oLA.y - C.y))) / 2
    d_inner = [0.5 * abs((iLA.x - iH.x)), 0.5 * abs((iH.y - iLA.y))]
    d_outer = [0.5 * abs((oLA.x - oH.x)), 0.5 * abs((oH.y - oLA.y))]
    aa = [np.sqrt(np.square(d_inner[0]) + np.square(d_inner[1])),
          np.sqrt(np.square(d_outer[0]) + np.square(d_outer[1]))]
    bb = [np.sqrt(np.square(inner_radius) - np.square(aa[0])), np.sqrt(np.square(outer_radius) - np.square(aa[1]))]
    if iLA.y < iH.y:
        M_inner = [iH.x + d_inner[0], iLA.y + d_inner[1]]
        M_outer = [oH.x + d_outer[0], oLA.y + d_outer[1]]
        if iLA.y >= 0.:
            sign = [-1, -1]
        else:
            sign = [1, 1]
    else:
        M_inner = [iH.x + d_inner[0], iH.y + d_inner[1]]
        M_outer = [oH.x + d_outer[0], oH.y + d_outer[1]]
        if iLA.y >= 0.:
            sign = [1, -1]
        else:
            sign = [-1, 1]
    inner = [M_inner[0] + sign[0] * bb[0] * d_inner[1] / aa[0], M_inner[1] + sign[1] * bb[0] * d_inner[0] / aa[0]]
    outer = [M_outer[0] + sign[0] * bb[1] * d_outer[1] / aa[1], M_outer[1] + sign[1] * bb[1] * d_outer[0] / aa[1]]
    return inner, outer

