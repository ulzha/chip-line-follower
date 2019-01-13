#!/usr/bin/env python
""" Remotely control the robot's onboard software over SSH and plot a live technical visualization of its state. """

# TODO livestream imagery too?

from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
import numpy.linalg
from time import sleep
from calc_angle import find_line
import cv2
import glob
import os
import re
import sys

# x = np.linspace(0, 6*np.pi, 100)
# y = np.sin(x)

plt.ion()

fig = plt.figure()

# vf = fig.add_subplot(131)
#


def sleep_until(target_time):
    timeout = target_time - datetime.now()
    if timeout > timedelta():
        timeout_seconds = timeout.seconds + 1E-6 * timeout.microseconds
        sleep(timeout_seconds)


def animate_quiver(fig, subplot, sequence):
    X = np.array([])
    Y = np.array([])
    U = np.array([])
    V = np.array([])
    start_time = datetime.now()
    for frame_capture_time, line in sequence:
        frame_draw_time = start_time + (frame_capture_time - sequence[0][0])
        sleep_until(frame_draw_time)
        X = np.append(X, line[0][0])
        Y = np.append(Y, line[0][1])
        U = np.append(U, line[1][0])
        V = np.append(V, line[1][1])
        # q = subplot.quiver(X, Y, U, V, scale=1)
        q = subplot.quiver(X, Y, U, V)
        fig.canvas.draw()
        fig.canvas.flush_events()


def norm_line(line, img_width, img_height):
    """ Accepts a line as a pair of pixel coordinates.
    Returns a pair of vectors - the line's closest point to origin placed in the center of the image, and the line's direction. """
    a = np.array([line[0][1] + .5 - img_width * .5, -(line[0][0] + .5 - img_height * .5)])
    b = np.array([line[1][1] - line[0][1], -(line[1][0] - line[0][0])])
    a1 = np.multiply(b, np.dot(a, b) / np.dot(b, b))
    return np.subtract(a, a1), np.divide(b, numpy.linalg.norm(b))


# vf2 = fig.add_subplot(132)
vf2 = fig.add_subplot(111)
# vf2.axis([-40, 40, -20, 20])
# vf2.axvline()
# vf2.axhline()
# animate_quiver(fig, vf2, [(1, 1, .5, 1), (-1, 1, -.5, 1), (-1, -1, -.5, 1), (1, -1, .5, 1)])

# ax = fig.add_subplot(133)
# line1, = ax.plot(x, y, 'r-') # Returns a tuple of line objects, thus the comma
#
# for phase in np.linspace(0, 10*np.pi, 500):
#     line1.set_ydata(np.sin(x + phase))
#     fig.canvas.draw()
#     fig.canvas.flush_events()


def parse_time(f):
    FMT_RE = re.compile(r'-(\d{17})-[^/]*$')
    m = re.search(FMT_RE, f)
    if m:
        return datetime.strptime(m.group(1), '%Y%m%d%H%M%S%f')


def parse_line(f):
    img = cv2.imread(f, cv2.IMREAD_GRAYSCALE)
    b = find_line(f, img)
    l = b and norm_line(b, img.shape[1], img.shape[0])
    return l


sequence = [(parse_time(f), parse_line(f)) for f in sorted(glob.glob(os.path.join(sys.argv[1], '????-*.jpg'))) if 'edges' in f]
valid_sequence = [i for i in sequence if i[0] is not None and i[1] is not None]

fig.canvas.draw()
fig.canvas.flush_events()
sleep(1)
vf2.add_patch(plt.Polygon([(35, 15), (-35, 15), (-35, -15), (35, -15)], alpha=.1))
animate_quiver(fig, vf2, valid_sequence)
fig.waitforbuttonpress()
