import time
from colorsys import hsv_to_rgb

from ioexpander import IN_PU, IOE
from ioexpander.encoder import Encoder

from encoderwheel import is31fl3731

__version__ = '0.0.1'

DEFAULT_IOE_I2C_ADDR = 0x13
DEFAULT_LED_I2C_ADDR = 0x77
ALTERNATE_LED_I2C_ADDR = 0x74
NUM_LEDS = 24
NUM_BUTTONS = 5
NUM_GPIOS = 3

UP = 0
DOWN = 1
LEFT = 2
RIGHT = 3
CENTRE = 4

GP7 = 7
GP8 = 8
GP9 = 9
GPIOS = (GP7, GP8, GP9)


class EncoderWheel():
    ENC_CHANNEL = 1
    ENC_TERMS = (3, 12)

    SW_UP = 13
    SW_DOWN = 4
    SW_LEFT = 11
    SW_RIGHT = 2
    SW_CENTRE = 1

    PWM_MODULE = 0  # Small Nuvoton only has a single PWM module

    def __init__(self, ioe_address=DEFAULT_IOE_I2C_ADDR, led_address=DEFAULT_LED_I2C_ADDR, interrupt_timeout=1.0, interrupt_pin=None, skip_chip_id_check=False):
        self.ioe = IOE(i2c_addr=ioe_address,
                       interrupt_timeout=interrupt_timeout,
                       interrupt_pin=interrupt_pin,
                       gpio=None,
                       skip_chip_id_check=skip_chip_id_check,
                       perform_reset=True
                       )

        self.encoder = Encoder(self.ioe, self.ENC_CHANNEL, self.ENC_TERMS, count_microsteps=True, count_divider=2)
        if interrupt_pin is not None:
            self.ioe.enable_interrupt_out(pin_swap=True)

        self.ioe.set_mode(self.SW_UP, IN_PU)
        self.ioe.set_mode(self.SW_DOWN, IN_PU)
        self.ioe.set_mode(self.SW_LEFT, IN_PU)
        self.ioe.set_mode(self.SW_RIGHT, IN_PU)
        self.ioe.set_mode(self.SW_CENTRE, IN_PU)

        self.ioe.set_pin_interrupt(self.SW_UP, True)
        self.ioe.set_pin_interrupt(self.SW_DOWN, True)
        self.ioe.set_pin_interrupt(self.SW_LEFT, True)
        self.ioe.set_pin_interrupt(self.SW_RIGHT, True)
        self.ioe.set_pin_interrupt(self.SW_CENTRE, True)

        self.button_map = {
            UP: self.SW_UP,
            RIGHT: self.SW_RIGHT,
            DOWN: self.SW_DOWN,
            LEFT: self.SW_LEFT,
            CENTRE: self.SW_CENTRE
        }

        self.is31fl3731 = is31fl3731.RGBRing(None, address=led_address, gamma_table=is31fl3731.LED_GAMMA)
        self.is31fl3731.clear()
        self.is31fl3731.show()

    def set_ioe_address(self, address):
        self.ioe.set_address(address)

    def get_interrupt_flag(self):
        return self.ioe.get_interrupt()

    def clear_interrupt_flag(self):
        self.ioe.clear_interrupt()

    def pressed(self, button):
        if button < 0 or button >= NUM_BUTTONS:
            raise ValueError(f"button out of range. Expected 0 to {NUM_BUTTONS - 1}")

        return self.ioe.input(self.button_map[button]) == 0

    def count(self):
        return self.encoder.count()

    def delta(self):
        return self.encoder.delta()

    def step(self):
        return self.encoder.step()

    def turn(self):
        return self.encoder.turn()

    def zero(self):
        self.encoder.zero()

    def revolutions(self):
        return self.encoder.revolutions()

    def degrees(self):
        return self.encoder.degrees()

    def radians(self):
        return self.encoder.radians()

    def direction(self, direction=None):
        return self.encoder.direction(direction)

    def set_rgb(self, index, r, g, b):
        if index < 0 or index >= NUM_LEDS:
            raise ValueError(f"index out of range. Expected 0 to {NUM_LEDS - 1}")

        self.is31fl3731.set_pixel(index, r, g, b)

    def set_hsv(self, index, h, s=1.0, v=1.0):
        if index < 0 or index >= NUM_LEDS:
            raise ValueError(f"index out of range. Expected 0 to {NUM_LEDS - 1}")

        r, g, b = [int(c * 255) for c in hsv_to_rgb(h, s, v)]
        self.is31fl3731.set_pixel(index, r, g, b)

    def clear(self):
        self.is31fl3731.clear()

    def show(self):
        self.is31fl3731.show()

    def gpio_pin_mode(self, gpio, mode=None):
        if gpio < 7 or gpio > 9:
            raise ValueError("gpio out of range. Expected GP7 (7), GP8 (8), or GP9 (9)")

        if mode is None:
            return self.ioe.get_mode(gpio)
        else:
            self.ioe.set_mode(gpio, mode)

    def gpio_pin_value(self, gpio, value=None, load=True, wait_for_load=False):
        if gpio < 7 or gpio > 9:
            raise ValueError("gpio out of range. Expected GP7 (7), GP8 (8), or GP9 (9)")

        if value is None:
            return self.ioe.input(gpio)
        else:
            self.ioe.output(gpio, value, load=load, wait_for_load=wait_for_load)

    def gpio_pwm_load(self, wait_for_load=True):
        self.ioe.pwm_load(self.PWM_MODULE, wait_for_load)

    def gpio_pwm_frequency(self, frequency, load=True, wait_for_load=True):
        return self.ioe.set_pwm_frequency(frequency, self.PWM_MODULE, load=load, wait_for_load=wait_for_load)


if __name__ == "__main__":
    wheel = EncoderWheel()

    last_update_time = time.monotonic()
    led_index = 0
    led_sequence = 0
    last_count = 0

    last_pressed = {
        UP: False,
        DOWN: False,
        LEFT: False,
        RIGHT: False,
        CENTRE: False,
    }

    while True:

        current_time = time.monotonic()
        if current_time >= last_update_time + 0.1:
            if led_sequence == 0:
                wheel.set_rgb(led_index, 255, 0, 0)

            if led_sequence == 1:
                wheel.set_rgb(led_index, 0, 255, 0)

            if led_sequence == 2:
                wheel.set_rgb(led_index, 0, 0, 255)

            if led_sequence == 3:
                wheel.set_rgb(led_index, 255, 255, 255)

            if led_sequence == 4:
                wheel.set_rgb(led_index, 0, 0, 0)

            led_index += 1
            if led_index >= NUM_LEDS:
                led_index = 0
                led_sequence += 1
                if led_sequence >= 5:
                    led_sequence = 0

            last_update_time = current_time
            wheel.show()

        count = wheel.count()
        if count != last_count:
            if count - last_count > 0:
                print("Clockwise, Count =", count)
            else:
                print("Counter Clockwise, Count =", count)
            last_count = count

        pressed = wheel.pressed(UP)
        if pressed != last_pressed[UP]:
            if pressed:
                print("Up Pressed")
            else:
                print("Up Released")
            last_pressed[UP] = pressed

        pressed = wheel.pressed(DOWN)
        if pressed != last_pressed[DOWN]:
            if pressed:
                print("Down Pressed")
            else:
                print("Down Released")
            last_pressed[DOWN] = pressed

        pressed = wheel.pressed(LEFT)
        if pressed != last_pressed[LEFT]:
            if pressed:
                print("Left Pressed")
            else:
                print("Left Released")
            last_pressed[LEFT] = pressed

        pressed = wheel.pressed(RIGHT)
        if pressed != last_pressed[RIGHT]:
            if pressed:
                print("Right Pressed")
            else:
                print("Right Released")
            last_pressed[RIGHT] = pressed

        pressed = wheel.pressed(CENTRE)
        if pressed != last_pressed[CENTRE]:
            if pressed:
                print("Centre Pressed")
            else:
                print("Centre Released")
            last_pressed[CENTRE] = pressed
