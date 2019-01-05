from CHIP_IO import GPIO
from time import sleep
import cv2
from datetime import datetime, timedelta
import math

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


def follow(err):
    if err < -0.2:
        drive(1, 1)
        # it turns very fast, so let's turn in very short pulses
        sleep(.05)
        coast()
    elif err > 0.2:
        drive(1, -1)
        sleep(.05)
        coast()
    else:
        drive(1)


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


# def turn_smooth(direction, amount):
#     n_pulses = 5
#     n_turn_pulses = max(int(n_pulses * amount), 1)
#     n_straight_pulses = n_pulses - n_turn_pulses
#     for i in range(n_turn_pulses):
#         drive(1, direction)
#         sleep(.005)
#         drive(1)
#         sleep(.005)
#     sleep(0.01 * n_straight_pulses)
#     coast()


def turn_smooth(direction, amount):
    assert amount >= 0
    assert amount <= 1
    duration = 0.05
    n_pulses = 8
    # for i in range(n_pulses):
    for i in range(int(n_pulses * max((1 - amount), 0.2))):  # if need to turn a lot, then slow down in general, but don't stop
        drive(1, direction)
        sleep(duration / n_pulses * amount)
        drive(1)
        sleep(duration / n_pulses * (1 - amount))
    coast()


# def turn_smooth(direction, amount):
#     assert amount >= 0
#     assert amount <= 1
#     duration = 0.05
#     n_pulses = 5
#     for i in range(n_pulses):
#         drive(1, direction)
#         sleep(duration / n_pulses * 0.3)
#         drive(1)
#         sleep(duration / n_pulses * 0.7 * (1 - amount))
#         coast()
#         sleep(duration / n_pulses * 0.7 * amount)


def follow_fast(err):
    if err < 0:
        turn_smooth(1, abs(err))
    else:
        turn_smooth(-1, abs(err))


try:
    cap = cv2.VideoCapture(0)
    n_missed = 0
    start_time = datetime.now()
    while True:
        frame_start_time = datetime.now()
        s, img = cap.read()
        if s:
            img_cropped = img[120:360, 40:600]
            img_shrunk = cv2.resize(img_cropped, (70, 30))
            edges = cv2.Canny(img_shrunk, 100, 200)

            # cv2.imwrite("cv2_test_edges.jpg", edges)
            c_line = find_line(edges)
            frame_end_time = datetime.now()
            print frame_end_time - frame_start_time, c_line

            if c_line is None:
                n_missed += 1
                if n_missed == 10:
                    print "Lost the line"
                    break
            else:
                n_missed = 0
                err = 2. * c_line / edges.shape[1] - 1
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
finally:
    coast()
    GPIO.cleanup()
