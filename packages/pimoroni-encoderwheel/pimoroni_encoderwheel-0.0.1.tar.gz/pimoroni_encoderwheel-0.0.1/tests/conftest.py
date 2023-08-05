import sys

import mock
import pytest


@pytest.fixture(scope='function', autouse=False)
def smbus2():
    """Mock smbus2 module."""

    smbus2 = mock.MagicMock()
    smbus2.i2c_msg.read().__iter__.return_value = [0b00000000]
    sys.modules['smbus2'] = smbus2
    yield smbus2
    del sys.modules['smbus2']


@pytest.fixture(scope='function', autouse=False)
def ioexpander():
    """Mock ioexpander module."""
    io_expander = mock.MagicMock()
    sys.modules['ioexpander'] = io_expander
    sys.modules['ioexpander.motor'] = io_expander.motor
    sys.modules['ioexpander.servo'] = io_expander.servo
    sys.modules['ioexpander.encoder'] = io_expander.encoder
    sys.modules['ioexpander.common'] = io_expander.common
    yield io_expander
    del sys.modules['ioexpander']
