import ctypes


class FullBatteryInfo(ctypes.Structure):
    """Object containing extended battery information
    Attributes
    ----------
    is_charging
        True if battery is charging
    is_charging
        True if charger is connected to the device
    level
        Battery charge percentage, 0-100
    health
        Battery health percentage, 0-100
    voltage
        Battery voltage in volts
    current
        Current flow in amps (negative means discharge)
    """
    _fields_ = [
        ("is_charging", ctypes.c_bool),
        ("is_charger_connected", ctypes.c_bool),
        ("level", ctypes.c_uint8),
        ("health", ctypes.c_float),
        ("voltage", ctypes.c_float),
        ("current", ctypes.c_float),
    ]
