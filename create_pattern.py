#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 2016 Marc Lieser

import argparse
import cv2
import numpy as np


def generate_pattern(pattern_type, n_cols, n_rows, shape_size,
                     screen_width, screen_height, screen_size):
    """Generate and return a device-specific calibration pattern."""

    dp = np.sqrt(screen_width**2 + screen_height**2)  # diagonal number of pixels
    ppi = dp / screen_size  # pixels per inch (ppi)

    size_p = shape_size / 25.4 * ppi  # shape size in pixels

    d = int(round(size_p))  # distance between shapes in pixels
    r = int(round(size_p / 2.))  # radius in pixels in case of circles grid

    w = d * n_cols  # pattern width in pixels
    h = d * n_rows  # pattern height in pixels

    ox = int(round((screen_width - w) / 2.))  # x offset to center pattern
    oy = int(round((screen_height - h) / 2.))  # y offset to center pattern

    pattern = np.ones((screen_height, screen_width)) * 255  # white image in screen size

    for i in range(n_cols):
        for j in range(n_rows):
            if (i * n_cols + j) % 2 == 0:  # draw every second shape
                if pattern_type == 'chessboard':
                    a = (ox + i * d, oy + j * d)  # first point
                    b = (a[0] + d, a[1] + d)  # second point
                    cv2.rectangle(pattern, a, b, 0, -1)  # draw
                else:
                    cx = ox + r + i * d  # x coordinate
                    cy = oy + r + j * d  # y coordinate
                    cv2.circle(pattern, (cx, cy), r, 0, -1)  # draw

    return pattern


if __name__ == "__main__":
    # generate command line argument parser
    parser = argparse.ArgumentParser(description='Create a device-dependent calibration pattern.')

    # setup arguments
    parser.add_argument('-p', '--pattern_type', help='Calibration pattern type (chessboard or asymcirclegrid).',
                        nargs='?', const=1, type=str, default='chessboard')
    parser.add_argument('-c', '--cols', help='Number of columns of the calibration pattern.',
                        nargs='?', const=1, type=int, default=9)
    parser.add_argument('-r', '--rows', help='Number of rows of the calibration pattern.',
                        nargs='?', const=1, type=int, default=6)
    parser.add_argument('-s', '--shape_size', help='Shape size in millimeters.',
                        nargs='?', const=1, type=float, default=9.)
    parser.add_argument('-dw', '--screen_width', help='Display width in pixels.',
                        nargs='?', const=1, type=int, default=1920)
    parser.add_argument('-dh', '--screen_height', help='Display height in pixels.',
                        nargs='?', const=1, type=int, default=1080)
    parser.add_argument('-d', '--screen_size', help='Diagonal screen size in inches.',
                        nargs='?', const=1, type=float, default=5.)
    parser.add_argument('--show', help='Displays the generated pattern.',
                        nargs='?', const=1, type=bool, default=False)

    # parse arguments
    args = parser.parse_args()

    # generate pattern
    pattern = generate_pattern(args.pattern_type, args.cols, args.rows, args.shape_size,
                               args.screen_width, args.screen_height, args.screen_size)

    # name it
    name = "{}_{}x{}-{}_{}x{}-{}".format(args.pattern_type, args.cols, args.rows, args.shape_size,
                                         args.screen_width, args.screen_height, args.screen_size)

    # save it
    cv2.imwrite(name + ".png", pattern)

    # show it
    if args.show:
        cv2.namedWindow(name, cv2.WINDOW_KEEPRATIO)
        cv2.imshow(name, pattern)
        cv2.waitKey(0)

