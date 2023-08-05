from encoderwheel import CENTRE, DOWN, LEFT, NUM_BUTTONS, NUM_LEDS, RIGHT, UP, EncoderWheel

print("""
A demonstration of reading the 5 buttons on Encoder Wheel.

Press Ctrl+C to stop the program.
""")

# Constants
BUTTON_NAMES = ["Up", "Down", "Left", "Right", "Centre"]
UPDATES = 50        # How many times the buttons will be checked and LEDs updated, per second
UPDATE_RATE = 1 / UPDATES

# Create a new EncoderWheel
wheel = EncoderWheel()

# Variables
last_pressed = [False] * NUM_BUTTONS
pressed = [False] * NUM_BUTTONS

# Loop forever
while True:

    # Read all of the encoder wheel's buttons
    for b in range(NUM_BUTTONS):
        pressed[b] = wheel.pressed(b)
        if pressed[b] != last_pressed[b]:
            print(BUTTON_NAMES[b], "Pressed" if pressed[b] else "Released")
        last_pressed[b] = pressed[b]

    # Clear the LED ring
    wheel.clear()

    for i in range(NUM_LEDS):
        if i % 6 == 3:
            wheel.set_rgb(i, 64, 64, 64)

    # If up is pressed, set the top LEDs to yellow
    if pressed[UP]:
        mid = NUM_LEDS
        for i in range(mid - 2, mid + 3):
            wheel.set_rgb(i % NUM_LEDS, 255, 255, 0)

    # If right is pressed, set the right LEDs to red
    if pressed[RIGHT]:
        mid = NUM_LEDS // 4
        for i in range(mid - 2, mid + 3):
            wheel.set_rgb(i % NUM_LEDS, 255, 0, 0)

    # If down is pressed, set the bottom LEDs to green
    if pressed[DOWN]:
        mid = NUM_LEDS // 2
        for i in range(mid - 2, mid + 3):
            wheel.set_rgb(i % NUM_LEDS, 0, 255, 0)

    # If left is pressed, set the left LEDs to blue
    if pressed[LEFT]:
        mid = (NUM_LEDS * 3) // 4
        for i in range(mid - 2, mid + 3):
            wheel.set_rgb(i % NUM_LEDS, 0, 0, 255)

    # If centre is pressed, set the diagonal LEDs to half white
    if pressed[CENTRE]:
        for i in range(NUM_LEDS):
            if i % 6 >= 2 and i % 6 <= 4:
                wheel.set_rgb(i, 128, 128, 128)
    wheel.show()
