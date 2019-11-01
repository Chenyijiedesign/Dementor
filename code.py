import adafruit_hcsr04
import array
import audiobusio
import audioio
import board
import math
import neopixel
import time
from adafruit_crickit import crickit
from digitalio import DigitalInOut, Direction
from varspeed import Vspeed

status = False

crickit.servo_1.set_pulse_width_range(min_pulse=500, max_pulse=2500)
servo_1 = crickit.servo_1
last_time_1 = time.monotonic()
angle_1 = 0
increment_1 = 2
#servo1_position = Vspeed(False) # get decimal values for the servo

last_time_2 = time.monotonic()
crickit.continuous_servo_2.throttle = -0.05
counter_1 = 0
counter_2 = 0
overrun = 0

sonar = adafruit_hcsr04.HCSR04(trigger_pin=board.A2, echo_pin=board.A3)
last_time_3 = time.monotonic()
current_distance = 0
last_distance = 0
counter_3 = 0
motionstatus = False

last_time_4 = time.monotonic()
color = 255
increment_4 = -10
counter_4 = 0
lightstatus = False
NUM_PIXELS = 10
NUM_SAMPLES = 160

color_2 = 0
increment_2 = 10
lightstatus_2 = True

# Remove DC bias before computing RMS.
def normalized_rms(values):
    minbuf = int(mean(values))
    samples_sum = sum(
        float(sample - minbuf) * (sample - minbuf)
        for sample in values
    )

    return math.sqrt(samples_sum / len(values))


def mean(values):
    return sum(values) / len(values)

# Main program

# Set up NeoPixels and turn them all off.
pixels = neopixel.NeoPixel(board.NEOPIXEL, NUM_PIXELS, brightness=0.1, auto_write=False)
pixels.fill(0)
pixels.show()

mic = audiobusio.PDMIn(board.MICROPHONE_CLOCK, board.MICROPHONE_DATA,
                       sample_rate=16000, bit_depth=16)

# Record an initial sample to calibrate. Assume it's quiet when we start.
samples = array.array('H', [0] * NUM_SAMPLES)
mic.record(samples, len(samples))

# enable the speaker
spkrenable = DigitalInOut(board.SPEAKER_ENABLE)
spkrenable.direction = Direction.OUTPUT
spkrenable.value = True

status_2 = False
audiofiles = ["DementorSound.wav"]
a = audioio.AudioOut(board.A0)
bpm = 120  # beats per minute, change this to suit your tempo


f = open(audiofiles[0], "rb")
wave = audioio.WaveFile(f)

while True:
    # the functions - move, loop, sequence are the same as before, but now return three items
    if crickit.touch_1.value == False:
        if lightstatus_2 == True:
            color_2 += increment_2
            #print(color_2)
            if color_2 >= 250:
                color = 255
                increment_2 = -10
            if color_2 <= 0:
                color_2 = 0
                increment_2 = 10
            for j in range(NUM_PIXELS):
                pixels[j] = (0, 0, color_2)
                pixels.show()


    if crickit.touch_1.value:
        #print("WakeUp")
        status = True
        status_2 = True
        lightstatus_2 = False
        for j in range(NUM_PIXELS):
                pixels[j] = (0, 0, 0)
                pixels.show()
        crickit.continuous_servo_2.throttle = 0.05
        time.sleep(1.5)

    if status == True:

        if time.monotonic() - last_time_1 > 0.05:
            if motionstatus:
                servo_1.angle = 120
                last_time_1 = time.monotonic()
            else:
                angle_1 += increment_1
                if angle_1 > 180:
                    angle_1 = 180
                    increment_1 = -5
                if angle_1 < 0:
                    angle_1 = 0
                    increment_1 = 2
                servo_1.angle = angle_1
                last_time_1 = time.monotonic()

        if time.monotonic() - last_time_2 > 0.05:
            if motionstatus:
                if counter_1 <= 6:
                    crickit.continuous_servo_2.throttle = -0.1
                    counter_1 += 1
                else:
                    crickit.continuous_servo_2.throttle = 0.03
                    counter_1 += 1
                    if counter_1 >= 14:
                        counter_1 = 0
                last_time_2 = time.monotonic()
            else:
                if counter_2 <= 13:
                    crickit.continuous_servo_2.throttle = -0.09
                    #print(counter_2)
                    counter_2 += 1
                else:
                    crickit.continuous_servo_2.throttle = 0.02
                    #print(counter_2)
                    counter_2 += 1
                    if counter_2 >=24:
                        counter_2 = 0
                        overrun += 1
                        print(overrun)
                    if overrun == 4:
                        crickit.continuous_servo_2.throttle = -0.09
                        print("hi")
                        time.sleep(0.3)
                        overrun = 0
                last_time_2 = time.monotonic()

        try:
            if time.monotonic() - last_time_3 > 0.05:
                last_distance = current_distance
                current_distance = sonar.distance
                print(current_distance)
                #print(counter_3)
                #print(motionstatus)
                if current_distance - last_distance >= 1:
                    counter_3 += 1
                if current_distance >= 40:
                    counter_3 += 1
                if counter_3 >= 10:
                    motionstatus = False
                    counter_3 = 0
                if current_distance >= 10 and current_distance <= 30:
                    motionstatus = True
                    counter_3 = 0
                last_time_3 = time.monotonic()

        except RuntimeError:
            counter_3 += 1
            print("Retrying!")
        time.sleep(0.1)

    mic.record(samples, len(samples))
    magnitude = normalized_rms(samples)
#        You might want to print this to see the values.
    if time.monotonic() - last_time_4 > 0.05 and status_2 == True:
        #print(magnitude)
        if magnitude >= 1000:
            print("playing file " + audiofiles[0])
            a.play(wave)
            while time.monotonic() - last_time_4 < 2:
                pass
            a.pause()
            lightstatus = True
            status = False
        if lightstatus == True:
            color += increment_4
            print(color)
            if color <= 0:
                color = 0
                increment_4 = 0
            for j in range(NUM_PIXELS):
                pixels[j] = (color, color, color)
                pixels.show()
            last_time_4 = time.monotonic()

            if counter_4 <= 15:
                crickit.continuous_servo_2.throttle = -0.1
                counter_4 += 1
            else:
                crickit.continuous_servo_2.throttle = 0
                counter_4 = 0
                color = 255
                increment_4 = -10
                lightstatus = False
                status_2 = False
                lightstatus_2 = True
