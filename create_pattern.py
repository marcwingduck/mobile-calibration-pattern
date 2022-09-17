#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 2016 Marc Lieser

import argparse
import cv2
import AppKit
import numpy as np


def convert_for_print(sheet_width_mm, sheet_height_mm):
    '''calculate image size in pixels from physical sheet size in millimeters and default dpi'''

    dpi = 300.
    sheet_with_px = int(round(sheet_width_mm/25.4*dpi))
    sheet_height_px = int(round(sheet_height_mm/25.4*dpi))
    return sheet_with_px, sheet_height_px, dpi


def convert_for_screen(screen_width_px, screen_height_px, screen_diagonal_inch):
    '''calculate ppi from screen resolution and diagonal screen size'''

    dp = np.sqrt(screen_width_px**2 + screen_height_px**2)  # diagonal number of pixels
    ppi = dp / screen_diagonal_inch  # pixels per inch (ppi)
    return screen_width_px, screen_height_px, ppi

    # debug check metric screen size
    #screen_width_mm = int(round(ppi*25.4/screen_width_px))
    #screen_height_mm = int(round(ppi*25.4/screen_height_px))


def generate_pattern(pattern_type, n_cols, n_rows, grid_size, shape_size, width_px, height_px, ppi):
    """Generate and return a device-specific calibration pattern."""

    d = int(round(ppi/25.4*grid_size))  # distance between grid points
    r = int(round(ppi/25.4*shape_size*0.5))  # radius in pixels in case of circles grid

    if pattern_type == 'chessboard':
        n_cols += 1
        n_rows += 1

    w = d * n_cols  # pattern width in pixels
    h = d * n_rows  # pattern height in pixels

    if pattern_type == 'asymcirclegrid':
        h = h*2

    ox = int(round((width_px - w) / 2.))  # x offset to center pattern
    oy = int(round((height_px - h) / 2.))  # y offset to center pattern

    pattern = np.ones((height_px, width_px)) * 255  # white image in screen size
    cv2.rectangle(pattern, (ox, oy), (ox+w, oy+h), 0, 1)

    for i in range(n_cols):
        for j in range(n_rows):
            if pattern_type == 'chessboard':
                if (i*(n_cols-1)+j) % 2 == 0:  # draw every second shape
                    a = (ox+i*d, oy+j*d)  # first point
                    b = (a[0]+d, a[1]+d)  # second point
                    cv2.rectangle(pattern, a, np.subtract(b, (1, 1)), 0, -1)  # draw
            else:
                cx = ox+r + i * d  # x coordinate
                cy = oy+r + (2*j+i % 2)*d  # y coordinate
                cv2.circle(pattern, (cx, cy), r, 0, -1)  # draw

    return pattern


if __name__ == "__main__":

    # generate command line argument parser
    parser = argparse.ArgumentParser(description='Create a print or device-dependent calibration pattern.')

    # setup arguments
    parser.add_argument('-m', '--medium', help='Screen or print.', nargs='?', const=1, type=str, default='screen')
    parser.add_argument('-p', '--pattern_type', help='Calibration pattern type (chessboard or asymcirclegrid).', nargs='?', const=1, type=str, default='chessboard')
    parser.add_argument('-c', '--cols', help='Number of columns of the calibration pattern.', nargs='?', const=1, type=int, default=9)
    parser.add_argument('-r', '--rows', help='Number of rows of the calibration pattern.', nargs='?', const=1, type=int, default=6)
    parser.add_argument('-g', '--grid_size', help='Grid size in millimeters.', nargs='?', const=1, type=float, default=5.)
    parser.add_argument('-s', '--shape_size', help='Circle diameter in millimeters.', nargs='?', const=1, type=float, default=5.)
    parser.add_argument('-mw', '--width', help='Display or paper width in pixels or mm.', nargs='?', const=1, type=int, default=1920)
    parser.add_argument('-mh', '--height', help='Display or sheet height in pixels or mm.', nargs='?', const=1, type=int, default=1080)
    parser.add_argument('-d', '--screen_size', help='Diagonal screen size in inches.', nargs='?', const=1, type=float, default=5.)
    parser.add_argument('--show', help='Displays the generated pattern.', nargs='?', const=1, type=bool, default=True)

    # parse arguments
    args = parser.parse_args()

    # generate pattern
    params = convert_for_print(args.width, args.height) if args.medium == 'print' else convert_for_screen(args.width, args.height, args.screen_size)
    pattern = generate_pattern(args.pattern_type, args.cols, args.rows, args.grid_size, args.shape_size, *params)

    # diss
    #pattern = generate_pattern('chessboard', 9, 6, 8, 100000, *convert_for_print(105,72))
    #cv2.imwrite('chessboard.png', pattern)
    #pattern = generate_pattern('asymcirclegrid', 11, 4, 7, 7, *convert_for_print(105,72))
    #cv2.imwrite('asymcirclegrid.png', pattern)
    # exit(0)

    # name it
    name = f'{args.pattern_type}_{args.cols}x{args.rows}_{args.medium}_{args.width}_{args.height}'

    # save it
    cv2.imwrite(name + '.png', pattern)

    # show it
    if args.show:
        cv2.namedWindow(name, cv2.WINDOW_KEEPRATIO)
        cv2.moveWindow(name, 0, 0)
        cv2.imshow(name, pattern)
        AppKit.NSApplication.sharedApplication().activateIgnoringOtherApps_(1)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
