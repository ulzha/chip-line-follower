log = logging.getLogger(__name__)

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
    log.debug("Driving %s %s".format(speed, direction))
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
    log.debug("Putting motor controller to sleep")
    GPIO.output("LCD-D18", GPIO.LOW)


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
