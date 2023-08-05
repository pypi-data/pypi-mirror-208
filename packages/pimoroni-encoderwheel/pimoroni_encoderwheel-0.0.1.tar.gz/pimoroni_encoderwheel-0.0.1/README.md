# RGB Encoder Wheel Breakout

[![Build Status](https://img.shields.io/github/actions/workflow/status/pimoroni/encoderwheel-python/test.yml?branch=main)](https://github.com/pimoroni/encoderwheel-python/actions/workflows/test.yml)
[![Coverage Status](https://coveralls.io/repos/github/pimoroni/encoderwheel-python/badge.svg?branch=main)](https://coveralls.io/github/pimoroni/encoderwheel-python?branch=main)
[![PyPi Package](https://img.shields.io/pypi/v/pimoroni-encoderwheel.svg)](https://pypi.python.org/pypi/pimoroni-encoderwheel)
[![Python Versions](https://img.shields.io/pypi/pyversions/pimoroni-encoderwheel.svg)](https://pypi.python.org/pypi/pimoroni-encoderwheel)

RGB Encoder Wheel is a breakout for the ANO directional navigation and scroll wheel rotary encoder. It uses a Nuvoton MS51 microcontroller to read the encoder and direction buttons via I2C, and features a IS31FL3731 LED driver to control a ring of 24 RGB LEDs that surround the encoder.

**Buy it from:** https://shop.pimoroni.com/products/rgb-encoder-wheel-breakout


 Getting the Library

**Stable library only (no examples) from PyPi:**

* Just run `python3 -m pip install pimoroni-encoderwheel`

In some cases you may need to install pip with: `sudo apt install python3-pip`

**Stable library, with latest examples from GitHub:**

* `git clone https://github.com/pimoroni/encoderwheel-python`
* `cd encoderwheel-python`
* `./install.sh`

**Latest/development library and examples from GitHub:**

* `git clone https://github.com/pimoroni/encoderwheel-python`
* `cd encoderwheel-python`
* `./install.sh --unstable`


# Configuring your Raspberry Pi

## Enable I2C

In order to use the Encoder Wheel, you need to enable the I2C interface of your Raspberry Pi. This can be done in the terminal by running:

* `sudo raspi-config nonint do_i2c 0`

Alternatively, you can enable the I2C interface by:
* running `sudo raspi-config` and enabling the option under **Interfacing Options**.
* opening the graphical **Raspberry Pi Configuration** application from the **Preferences** menu.

You may need to reboot after enabling I2C for the change to take effect.


# Examples and Usage

There are various examples to get you started with your Encoder Wheel. With the library installed on your Raspberry Pi, these can be found in the `~/Pimoroni/pimoroni-encoderwheel/examples` directory.

To take Encoder Wheel further, the full API is described in the [library reference](/REFERENCE.md).


# Removing the Library

To uninstall the library only (keeping all examples):

* Just run `python3 -m pip uninstall pimoroni-encoderwheel`

Or if you have grabbed the library from Github:

* `cd encoderwheel-python`
* `./uninstall.sh`
