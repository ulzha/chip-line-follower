#!/usr/bin/env python3
""" Remotely control the robot's onboard software over SSH and plot a live technical visualization of its state. """

# TODO livestream imagery too?

from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
from time import sleep
from calc_angle import find_line_norm
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


def animate_quiver(fig, subplot, iter):
    X = np.array([])
    Y = np.array([])
    U = np.array([])
    V = np.array([])
    time_indicator = fig.text(0, 0, '', alpha=.7, horizontalalignment='left')
    for frame_time, line in iter:
        time_indicator.set_text(str(frame_time))
        if line:
            X = np.append(X, line[0][0])
            Y = np.append(Y, line[0][1])
            U = np.append(U, line[1][0])
            V = np.append(V, line[1][1])
            # q = subplot.quiver(X, Y, U, V, scale=1)
            q = subplot.quiver(X, Y, U, V)
        fig.canvas.draw()
        fig.canvas.flush_events()


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
    return find_line_norm(img)


class DataSample(object):
    """ TODO """
    def __str__(self):
        pass


def replay_sequence(images_path):
    """ Iterates with pauses between frames as they originally occurred. """
    sequence = [(parse_time(f), parse_line(f)) for f in sorted(glob.glob(os.path.join(images_path, '????-*.jpg'))) if 'edges' in f]
    start_time = datetime.now()
    for frame_time, line in sequence:
        frame_time_str = frame_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        data_sample = (frame_time_str, line)
        frame_draw_time = start_time + (frame_time - sequence[0][0])
        sleep_until(frame_draw_time)
        print(repr(data_sample))
        yield frame_time, line


def live_sequence(socket):
    """ TODO """
    pass


fig.canvas.draw()
fig.canvas.flush_events()
sleep(1)
vf2.add_patch(plt.Polygon([(35, 15), (-35, 15), (-35, -15), (35, -15)], alpha=.1))
animate_quiver(fig, vf2, replay_sequence(sys.argv[1]))
vf2.text(0, -10, 'press any key', alpha=.7, horizontalalignment='center')
fig.waitforbuttonpress()
