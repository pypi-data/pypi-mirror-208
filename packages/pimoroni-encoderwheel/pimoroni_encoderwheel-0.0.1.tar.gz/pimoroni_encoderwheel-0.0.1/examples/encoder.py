from encoderwheel import EncoderWheel

print("""
A demonstration of reading the rotary dial of the Encoder Wheel breakout.

Press Ctrl+C to stop the program.
""")

# Create a new EncoderWheel
wheel = EncoderWheel()

# Variables
position = 0
hue = 0.0

# Set the first LED
wheel.clear()
wheel.set_hsv(position, hue, 1.0, 1.0)
wheel.show()

# Loop forever
while True:

    # Has the dial been turned since the last time we checked?
    change = wheel.delta()
    if change != 0:
        # Print out the direction the dial was turned, and the count
        if change > 0:
            print("Clockwise, Count =", wheel.count())
        else:
            print("Counter Clockwise, Count =", wheel.count())

        # Record the new position (from 0 to 23)
        position = wheel.step()

        # Record a colour hue from 0.0 to 1.0
        hue = wheel.revolutions() % 1.0

        # Set the LED at the new position to the new hue
        wheel.clear()
        wheel.set_hsv(position, hue, 1.0, 1.0)
        wheel.show()
