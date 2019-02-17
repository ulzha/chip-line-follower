#!/usr/bin/env python3
""" Remotely control the robot's onboard software over SSH and plot a live technical visualization of its state. """

# TODO livestream imagery too?

from datetime import datetime, timedelta
import glob
import os
import re
import sys
from time import sleep

import cv2
import matplotlib.pyplot as plt
import numpy as np

from calc_angle import find_line_norm

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
    time_indicator = fig.text(.01, .01, '', alpha=.7, horizontalalignment='left')
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


control_buffer = []
controller_state = {
    'drive': False
}


def live_sequence(socket):
    """ TODO forward stuff from control_buffer to robot and receive data samples back """
    pass


def throttle_press():
    controller_state['drive'] = not controller_state['drive']
    print('Start' if controller_state['drive'] else 'Stop')
    control_buffer.append(('drive', controller_state['drive']))


def connect_event_handlers(fig, throttle_handler):
    key_indicator = fig.text(.5, .01, '', alpha=.7, horizontalalignment='center')
    # deduplicate key press events. Crazy that we have to do this
    # https://stackoverflow.com/questions/27215326/tkinter-keypress-keyrelease-events/27215461
    # FIXME processing is seriously lagging behind when a key is held
    event_buffer = []

    def debounced_key_press(event):
        """ Also called if the set of pressed keys changes """
        # print('Debounced press', repr(event.key))
        key_indicator.set_text(event.key)
        if event.key == ' ':
            throttle_handler()
        fig.canvas.draw()

    def key_press(event):
        # print('Press', repr(event.key))
        if len(event_buffer) > 0 and event_buffer[-1][0] == 'release' and event_buffer[-1][1].key == event.key:
            # consider this a repeat and ignore both events
            event_buffer.clear()
        else:
            # pass through
            event_buffer.clear()
            debounced_key_press(event)

    def debounced_key_release(event):
        """ Called 0.1 s after a key is released """
        # print('Debounced release', repr(event.key))
        key_indicator.set_text('')
        fig.canvas.draw()

    def key_release(event):
        # print('Release', repr(event.key))
        event_buffer.append(('release', event))

        def maybe_release(event):
            # print('Maybe release', repr(event.key), repr(event_buffer))
            if len(event_buffer) > 0 and event_buffer[-1] == ('release', event):
                event_buffer.clear()
                debounced_key_release(event)

        timer = fig.canvas.new_timer(interval=100, callbacks=[(maybe_release, [event], {})])
        timer.single_shot = True
        timer.start()

    fig.canvas.mpl_connect('key_press_event', key_press)
    fig.canvas.mpl_connect('key_release_event', key_release)


fig.canvas.draw()
fig.canvas.flush_events()
connect_event_handlers(fig, throttle_press)
sleep(1)
vf2.add_patch(plt.Polygon([(35, 15), (-35, 15), (-35, -15), (35, -15)], alpha=.1))
animate_quiver(fig, vf2, replay_sequence(sys.argv[1]))
vf2.text(0, -10, 'press any key', alpha=.7, horizontalalignment='center')
fig.waitforbuttonpress()
