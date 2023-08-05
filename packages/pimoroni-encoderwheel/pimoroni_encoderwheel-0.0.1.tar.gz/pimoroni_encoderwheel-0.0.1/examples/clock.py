import time
from datetime import datetime

from encoderwheel import NUM_LEDS, EncoderWheel

print("""
Displays a 12 hour clock on Encoder Wheel's LED ring, getting time from the system.

Press Ctrl+C to stop the program.
""")

# Constants
BRIGHTNESS = 1.0    # The brightness of the LEDs
UPDATES = 50        # How many times the LEDs will be updated per second
UPDATE_RATE = 1 / UPDATES

# Handy values for the number of milliseconds
MILLIS_PER_SECOND = 1000
MILLIS_PER_MINUTE = MILLIS_PER_SECOND * 60
MILLIS_PER_HOUR = MILLIS_PER_MINUTE * 60
MILLIS_PER_HALF_DAY = MILLIS_PER_HOUR * 12

# Create a new EncoderWheel
wheel = EncoderWheel()


# Sleep until a specific time in the future. Use this instead of time.sleep() to correct for
# inconsistent timings when dealing with complex operations or external communication
def sleep_until(end_time):
    time_to_sleep = end_time - time.monotonic()
    if time_to_sleep > 0.0:
        time.sleep(time_to_sleep)


# Simple function to clamp a value between a minimum and maximum
def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))


# Calculates the brightness of an LED based on its index and a position along the LED ring
def led_brightness_at(led, position, half_width=1, span=1):
    brightness = 0.0
    upper = position + half_width
    lower = position - half_width
    if led > position:
        brightness = clamp((upper - led) / span, 0.0, 1.0)
    else:
        brightness = clamp((led - lower) / span, 0.0, 1.0)

    # Handle the LEDs being in a circle
    if upper >= NUM_LEDS:
        brightness = clamp(((upper - NUM_LEDS) - led) / span, brightness, 1.0)
    elif lower < 0.0:
        brightness = clamp((led - (lower + NUM_LEDS)) / span, brightness, 1.0)

    return brightness * BRIGHTNESS * 255


# Make rainbows
while True:

    # Record the start time of this loop
    start_time = time.monotonic()

    # Get the current system time
    now = datetime.now()

    # Convert the seconds, minutes, and hours into milliseconds (this is done to give a smoother animation, particularly for the seconds hand)
    sec_as_millis = (now.second * MILLIS_PER_SECOND) + (now.microsecond // MILLIS_PER_SECOND)
    min_as_millis = (now.minute * MILLIS_PER_MINUTE) + sec_as_millis
    hour_as_millis = ((now.hour % 12) * MILLIS_PER_HOUR) + min_as_millis

    # Calculate the position on the LED ring that the, second, minute, and hour hands should be
    sec_pos = min(sec_as_millis / MILLIS_PER_MINUTE, 1.0) * NUM_LEDS
    min_pos = min(min_as_millis / MILLIS_PER_HOUR, 1.0) * NUM_LEDS
    hour_pos = min(hour_as_millis / MILLIS_PER_HALF_DAY, 1.0) * NUM_LEDS

    for i in range(NUM_LEDS):
        # Turn on the LEDs close to the position of the current second, minute, and hour
        r = led_brightness_at(i, sec_pos)
        g = led_brightness_at(i, min_pos)
        b = led_brightness_at(i, hour_pos)
        wheel.set_rgb(i, r, g, b)
    wheel.show()

    # Sleep until the next update, accounting for how long the above operations took to perform
    sleep_until(start_time + UPDATE_RATE)
