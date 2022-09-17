#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 2016 Marc Lieser

import argparse
import cv2
import AppKit
import numpy as np


def generate_pattern_screen(pattern_type, n_cols, n_rows, grid_size, shape_size, screen_width, screen_height, screen_size):
    """Generate and return a device-specific calibration pattern."""

    print('screen_size [inch]', screen_size)
    dp = np.sqrt(screen_width**2 + screen_height**2)  # diagonal number of pixels
    print('dp', dp)
    ppi = dp / screen_size  # pixels per inch (ppi)
    print('ppi', ppi)

    screen_width_mm = int(round(ppi*25.4/screen_width))
    screen_height_mm = int(round(ppi*25.4/screen_height))
    print('screen w x h [px]', screen_width, screen_height)
    print('screen w x h [mm]', screen_width_mm, screen_height_mm)

    d = int(round(ppi/25.4*grid_size))  # distance between grid points
    r = int(round(ppi/25.4*shape_size*0.5))  # radius in pixels in case of circles grid
    print('grid distance [px]', d)
    print('radius [px]', d)

    _n_cols = n_cols+1 if pattern_type == 'chessboard' else n_cols
    _n_rows = n_rows+1 if pattern_type == 'chessboard' else n_rows

    w = d * n_cols  # pattern width in pixels
    h = d * n_rows  # pattern height in pixels

    ox = int(round((screen_width - w) / 2.))  # x offset to center pattern
    oy = int(round((screen_height - h) / 2.))  # y offset to center pattern

    pattern = np.ones((screen_height, screen_width)) * 255  # white image in screen size

    for i in range(_n_cols):
        for j in range(_n_rows):
            if pattern_type == 'chessboard':
                if (i*n_cols+j) % 2 == 0:  # draw every second shape
                    d2 = d//2
                    a = ((ox-d2)+i*d, (oy-d2)+j*d)  # first point
                    dw = d2*2
                    dw += d % dw
                    b = (a[0]+dw, a[1]+dw)  # second point
                    cv2.rectangle(pattern, a, np.subtract(b, (1, 1)), 0, -1)  # draw
            else:
                cx = ox + r + i * d  # x coordinate
                cy = int(round(oy/2)) + r + (2*j+i % 2)*d  # y coordinate
                cv2.circle(pattern, (cx, cy), r, 0, -1)  # draw

    return pattern


if __name__ == "__main__":

    # generate command line argument parser
    parser = argparse.ArgumentParser(description='Create a device-dependent calibration pattern.')

    # setup arguments
    parser.add_argument('-p', '--pattern_type', help='Calibration pattern type (chessboard or asymcirclegrid).', nargs='?', const=1, type=str, default='chessboard')
    parser.add_argument('-c', '--cols', help='Number of columns of the calibration pattern.', nargs='?', const=1, type=int, default=9)
    parser.add_argument('-r', '--rows', help='Number of rows of the calibration pattern.', nargs='?', const=1, type=int, default=6)
    parser.add_argument('-g', '--grid_size', help='Grid size in millimeters.', nargs='?', const=1, type=float, default=5.)
    parser.add_argument('-s', '--shape_size', help='Circle diameter in millimeters.', nargs='?', const=1, type=float, default=5.)
    parser.add_argument('-dw', '--screen_width', help='Display width in pixels.', nargs='?', const=1, type=int, default=1920)
    parser.add_argument('-dh', '--screen_height', help='Display height in pixels.', nargs='?', const=1, type=int, default=1080)
    parser.add_argument('-d', '--screen_size', help='Diagonal screen size in inches.', nargs='?', const=1, type=float, default=5.)
    parser.add_argument('--show', help='Displays the generated pattern.', nargs='?', const=1, type=bool, default=False)

    # parse arguments
    args = parser.parse_args()

    # generate pattern
    pattern = generate_pattern_screen(args.pattern_type, args.cols, args.rows, args.grid_size, args.shape_size, args.screen_width, args.screen_height, args.screen_size)

    # name it
    name = "{}_{}x{}-{}_{}x{}-{}".format(args.pattern_type, args.cols, args.rows, args.grid_size, args.shape_size, args.screen_width, args.screen_height, args.screen_size)

    # save it
    cv2.imwrite(name + ".png", pattern)

    # show it
    if args.show:
        cv2.namedWindow(name, cv2.WINDOW_KEEPRATIO)
        cv2.moveWindow(name, 0, 0)
        cv2.imshow(name, pattern)
        AppKit.NSApplication.sharedApplication().activateIgnoringOtherApps_(1)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
