#!/usr/bin/env python3

from time import sleep
import cv2
from datetime import datetime, timedelta
import logging
import glob
import os
import sys

from calc_angle import find_line_col, find_line_norm
from drive import drive, coast, turn_smooth

logging.basicConfig(filename='all.log', level=logging.DEBUG)
log = logging.getLogger(__name__)


def follow_slow(err):
    if err < 0:
        drive(1, 1)
        # it turns very fast, so let's turn in very short pulses
        sleep(.02)
        coast()
    else:
        drive(1, -1)
        sleep(.02)
        coast()


def follow_fast(err):
    if err < 0:
        turn_smooth(1, abs(err))
    else:
        turn_smooth(-1, abs(err))


try:
    log.info("Removing old images")
    for f in glob.glob('????-*.jpg'):
        os.remove(f)

    cap = cv2.VideoCapture(0)
    n_missed = 0
    start_time = datetime.now()
    i_frame = 0
    while True:
        frame_start_time = datetime.now()
        frame_start_time_str = frame_start_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        frame_filename_suffix = frame_start_time_str.translate(None, '- :.')
        s, img = cap.read()
        if s:
            img_cropped = img[120:360, 40:600]
            img_shrunk = cv2.resize(img_cropped, (70, 30))
            img_edges = cv2.Canny(img_shrunk, 100, 200)

            filename_prefix = '{:04d}-{}-'.format(i_frame, frame_filename_suffix)
            cv2.imwrite(filename_prefix + 'shrunk.jpg', img_shrunk)
            cv2.imwrite(filename_prefix + 'edges.jpg', img_edges)

            c_line = find_line_col(img_edges)

            if c_line is None:
                data_sample = (frame_start_time_str, None)
                log.info(repr(data_sample))
                print(repr(data_sample))
                n_missed += 1
                # TODO drive somewhere?
                if n_missed == 10:
                    log.info("Lost the line")
                    break
            else:
                n_missed = 0
                l = find_line_norm(img_edges)
                err = 2. * c_line / img_edges.shape[1] - 1
                data_sample = (frame_start_time_str, l)
                log.info(repr(data_sample))
                print(repr(data_sample))
                # follow(err)  # loses the line often
                # follow_slow(err)  # yay, this works, but sometimes oversteers anyway
                follow_fast(err)
        else:
            log.error("Capture error: %s", s)
            sys.exit(1)
        if datetime.now() - start_time > timedelta(seconds=20):
            log.info("Time is up")
            break
        i_frame += 1
finally:
    coast()
    GPIO.cleanup()
