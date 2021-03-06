#!/usr/bin/env python

import math

import numpy

from utilities import Cffi
from utilities import RvizHandler


def skeletonizationCffi(ogm, origin, resolution, ogml):
    skeleton = (ogm < 49).astype("int32")
    skeleton = Cffi.thinning(skeleton, ogml)
    skeleton = Cffi.prune(skeleton, ogml, 10)

    print_viz(skeleton, resolution, origin['x'], origin['y'])
    return skeleton


def skeletonization(self, ogm, origin, resolution, ogml):
    useful_ogm = ogm[ogml['min_x']:ogml['max_x'], ogml['min_y']:ogml['max_y']]
    useful_width = useful_ogm.shape[0]
    useful_height = useful_ogm.shape[1]

    useful_local = numpy.zeros(useful_ogm.shape)

    for i in range(0, useful_width):
        for j in range(0, useful_height):
            if useful_ogm[i][j] < 49:
                useful_local[i][j] = 1

    from skimage.morphology import skeletonize
    skeleton = skeletonize(useful_local)
    skeleton = self.pruning(skeleton, 10)

    # padding
    skeleton_final = numpy.zeros(ogm.shape)
    skeleton_final[ogml['min_x']:ogml['max_x'], ogml['min_y']:ogml['max_y']] = skeleton

    print_viz(skeleton_final, resolution, origin['x'], origin['y'])
    return skeleton_final


def topologicalNodes(ogm, skeleton, coverage, brush):
    nodes = []

    width = ogm.shape[0]
    height = ogm.shape[1]

    for i in range(1, width - 1):
        for j in range(1, height - 1):
            if ogm[i][j] <= 49 and brush[i][j] > 3 and skeleton[i][j] == 1 and coverage[i][j] != 100:
                c = 0
                for ii in range(-1, 2):
                    for jj in range(-1, 2):
                        c = c + skeleton[i + ii][j + jj]

                if c == 2 or c == 4:  # and coverage etc
                    nodes.append([i, j])

    change = True
    while change:
        change = False
        for i in range(0, len(nodes)):
            for j in range(0, len(nodes)):
                if i == j:
                    continue
                n1 = nodes[i]
                n2 = nodes[j]
                if math.pow(n1[0] - n2[0], 2) + math.pow(n1[1] - n2[1], 2) < 25:
                    change = True
                    del nodes[i]
                    break
            if change:
                break

    return nodes


def pruning(img, n):
    for k in range(0, n):
        tmp_img = numpy.copy(img)
        for i in range(0, img.shape[0] - 1):
            for j in range(0, img.shape[1] - 1):
                if img[i][j] == 1:
                    c = 0
                    for ii in range(-1, 2):
                        for jj in range(-1, 2):
                            c = c + img[i + ii][j + jj]
                    if c == 2:
                        tmp_img[i][j] = 0
        img = numpy.copy(tmp_img)
    return img


def print_viz(skeleton, resolution, x, y):
    i, j = numpy.where(skeleton == 1)
    viz = zip(i * resolution + x, j * resolution + y)
    RvizHandler.printMarker(
        viz,
        1,  # Type: Arrow
        0,  # Action: Add
        "map",  # Frame
        "art_skeletonization",  # Namespace
        [0.5, 0, 0, 0.5],  # Color RGBA
        0.05  # Scale
    )
