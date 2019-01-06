from CHIP_IO import GPIO
from time import sleep
import cv2
from datetime import datetime, timedelta
import math
import glob
import os

GPIO.setup("LCD-D12", GPIO.IN)
GPIO.setup("LCD-D14", GPIO.IN)
GPIO.setup("LCD-D18", GPIO.OUT)
GPIO.setup("LCD-D20", GPIO.OUT)
GPIO.setup("LCD-D22", GPIO.OUT)
GPIO.setup("LCD-CLK", GPIO.OUT)
GPIO.setup("LCD-VSYNC", GPIO.OUT)

GPIO.input("LCD-D12")
GPIO.input("LCD-D14")


def drive(speed, direction=0):
    print "Driving", speed, direction
    if speed > 0:
        GPIO.output("LCD-D20", GPIO.LOW)
        GPIO.output("LCD-D22", GPIO.HIGH if direction > 0 else GPIO.LOW)
        GPIO.output("LCD-CLK", GPIO.LOW if direction < 0 else GPIO.HIGH)
        GPIO.output("LCD-VSYNC", GPIO.HIGH)
        GPIO.output("LCD-D18", GPIO.HIGH)
    elif speed < 0:
        GPIO.output("LCD-D20", GPIO.LOW if direction > 0 else GPIO.HIGH)
        GPIO.output("LCD-D22", GPIO.HIGH)
        GPIO.output("LCD-CLK", GPIO.LOW)
        GPIO.output("LCD-VSYNC", GPIO.HIGH if direction < 0 else GPIO.LOW)
        GPIO.output("LCD-D18", GPIO.HIGH)
    else: # brake
        GPIO.output("LCD-D20", GPIO.LOW)
        GPIO.output("LCD-D22", GPIO.HIGH)
        GPIO.output("LCD-CLK", GPIO.LOW)
        GPIO.output("LCD-VSYNC", GPIO.HIGH)
        GPIO.output("LCD-D18", GPIO.HIGH)


def coast():
    print "Putting motor controller to sleep"
    GPIO.output("LCD-D18", GPIO.LOW)


def find_line(img):
    """ Simpleton logic - assume the line crosses the bottom row, so find the white pixels of the bottom row and take their midpoint. """
    r = img.shape[0] - 1
    leftmost = None
    rightmost = None
    for c in range(0, img.shape[1]):
        if img.item(r, c) > 0:
            if leftmost is None:
                leftmost = c
            rightmost = c
    return None if leftmost is None or rightmost is None else (leftmost + rightmost) / 2


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


def turn_smooth(direction, amount):
    assert amount >= 0
    assert amount <= 1
    duration = 0.05
    n_pulses = 5
    for i in range(n_pulses):
    # for i in range(int(n_pulses * max((1 - amount), 0.2))):  # if need to turn a lot, then slow down in general, but don't stop
        drive(1, direction)
        sleep(duration / n_pulses * amount)
        drive(1)
        sleep(duration / n_pulses * (1 - amount))
    coast()


def follow_fast(err):
    if err < 0:
        turn_smooth(1, abs(err))
    else:
        turn_smooth(-1, abs(err))


try:
    print "Removing old images"
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

            c_line = find_line(img_edges)
            print frame_start_time_str, c_line

            if c_line is None:
                n_missed += 1
                if n_missed == 10:
                    print "Lost the line"
                    break
            else:
                n_missed = 0
                err = 2. * c_line / img_edges.shape[1] - 1
                print "Calculated error {:.2f}".format(err)
                # follow(err)  # loses the line often
                # follow_slow(err)  # yay, this works, but sometimes oversteers anyway
                follow_fast(err)
        else:
            print "Capture error"
            break
        if datetime.now() - start_time > timedelta(seconds=20):
            print "Time is up"
            break
        i_frame += 1
finally:
    coast()
    GPIO.cleanup()
