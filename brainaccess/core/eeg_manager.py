import enum
import ctypes
import asyncio
import threading
import copy

from multimethod import multimethod

from brainaccess.core import _dll
from brainaccess.core.battery_info import BatteryInfo
from brainaccess.core.full_battery_info import FullBatteryInfo
from brainaccess.core.device_info import DeviceInfo
from brainaccess.core.gain_mode import GainMode
from brainaccess.core.impedance_measurement_mode import ImpedanceMeasurementMode
from brainaccess.core.annotation import Annotation
from brainaccess.core.polarity import Polarity


# ctypes
# new_eeg_manager
_dll.ba_eeg_manager_new.argtypes = []
_dll.ba_eeg_manager_new.restype = ctypes.c_void_p
# destructor
_dll.ba_eeg_manager_free.argtypes = [ctypes.c_void_p]
_dll.ba_eeg_manager_free.restype = None
# connect(port)
_dll.ba_eeg_manager_connect.argtypes = [
    ctypes.c_void_p,
    ctypes.c_char_p,
    ctypes.CFUNCTYPE(None, ctypes.c_bool, ctypes.c_void_p),
    ctypes.c_void_p,
]
_dll.ba_eeg_manager_connect.restype = None
# is_connected()
_dll.ba_eeg_manager_is_connected.argtypes = [ctypes.c_void_p]
_dll.ba_eeg_manager_is_connected.restype = ctypes.c_bool
# disconnect()
_dll.ba_eeg_manager_disconnect.argtypes = [ctypes.c_void_p]
_dll.ba_eeg_manager_disconnect.restype = None
# start_stream()
_dll.ba_eeg_manager_start_stream.argtypes = [
    ctypes.c_void_p,
    ctypes.CFUNCTYPE(None, ctypes.c_void_p),
    ctypes.c_void_p,
]
_dll.ba_eeg_manager_start_stream.restype = ctypes.c_uint8
# stop_stream()
_dll.ba_eeg_manager_stop_stream.argtypes = [
    ctypes.c_void_p,
    ctypes.CFUNCTYPE(None, ctypes.c_void_p),
    ctypes.c_void_p,
]
_dll.ba_eeg_manager_stop_stream.restype = ctypes.c_uint8
# is_streaming()
_dll.ba_eeg_manager_is_streaming.argtypes = [ctypes.c_void_p]
_dll.ba_eeg_manager_is_streaming.restype = ctypes.c_bool
# set_io()
_dll.ba_eeg_manager_set_io.argtypes = [
    ctypes.c_void_p,
    ctypes.c_uint8,
    ctypes.c_bool,
    ctypes.CFUNCTYPE(None, ctypes.c_void_p),
    ctypes.c_void_p,
]
_dll.ba_eeg_manager_set_io.restype = ctypes.c_uint8
# get_battery_info()
_dll.ba_eeg_manager_get_battery_info.argtypes = [
    ctypes.c_void_p,
]
_dll.ba_eeg_manager_get_battery_info.restype = BatteryInfo
# get_full_battery_info()
_dll.ba_eeg_manager_get_full_battery_info.argtypes = [
    ctypes.c_void_p,
    ctypes.CFUNCTYPE(None, ctypes.POINTER(FullBatteryInfo), ctypes.c_void_p),
    ctypes.c_void_p,
]
_dll.ba_eeg_manager_get_full_battery_info.restype = ctypes.c_uint8
# get_latency()
_dll.ba_eeg_manager_get_latency.argtypes = [
    ctypes.c_void_p,
    ctypes.CFUNCTYPE(None, ctypes.c_float, ctypes.c_void_p),
    ctypes.c_void_p,
]
_dll.ba_eeg_manager_get_latency.restype = ctypes.c_uint8
# set_channel_enabled()
_dll.ba_eeg_manager_set_channel_enabled.argtypes = [
    ctypes.c_void_p,
    ctypes.c_uint16,
    ctypes.c_bool,
]
_dll.ba_eeg_manager_set_channel_enabled.restype = None
# set_channel_gain()
_dll.ba_eeg_manager_set_channel_gain.argtypes = [
    ctypes.c_void_p,
    ctypes.c_uint16,
    ctypes.c_uint8,
]
_dll.ba_eeg_manager_set_channel_gain.restype = None
# set_channel_bias()
_dll.ba_eeg_manager_set_channel_bias.argtypes = [
    ctypes.c_void_p,
    ctypes.c_uint16,
    ctypes.c_uint8,
]
_dll.ba_eeg_manager_set_channel_bias.restype = None
# set_impedance_mode()
_dll.ba_eeg_manager_set_impedance_mode.argtypes = [
    ctypes.c_void_p,
    ctypes.c_uint8,
]
_dll.ba_eeg_manager_set_impedance_mode.restype = None
# get_device_info()
_dll.ba_eeg_manager_get_device_info.argtypes = [ctypes.c_void_p]
_dll.ba_eeg_manager_get_device_info.restype = ctypes.POINTER(DeviceInfo)
# get_channel_index()
_dll.ba_eeg_manager_get_channel_index.argtypes = [ctypes.c_void_p, ctypes.c_uint16]
_dll.ba_eeg_manager_get_channel_index.restype = ctypes.c_size_t
# get_sample_frequency()
_dll.ba_eeg_manager_get_sample_frequency.argtypes = [ctypes.c_void_p]
_dll.ba_eeg_manager_get_sample_frequency.restype = ctypes.c_uint16
# set_callback_chunk()
_dll.ba_eeg_manager_set_callback_chunk.argtypes = [
    ctypes.c_void_p,
    ctypes.CFUNCTYPE(
        None,
        ctypes.POINTER(ctypes.c_void_p),
        ctypes.c_size_t,
        ctypes.c_void_p,
    ),
    ctypes.c_void_p,
]
_dll.ba_eeg_manager_set_callback_chunk.restype = None
# set_callback_battery()
_dll.ba_eeg_manager_set_callback_battery.argtypes = [
    ctypes.c_void_p,
    ctypes.CFUNCTYPE(None, ctypes.POINTER(BatteryInfo), ctypes.c_void_p),
    ctypes.c_void_p,
]
_dll.ba_eeg_manager_set_callback_battery.restype = None
# set_callback_disconnect()
_dll.ba_eeg_manager_set_callback_disconnect.argtypes = [
    ctypes.c_void_p,
    ctypes.CFUNCTYPE(None, ctypes.c_void_p),
    ctypes.c_void_p,
]
_dll.ba_eeg_manager_set_callback_disconnect.restype = None
# annotate()
_dll.ba_eeg_manager_annotate.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
_dll.ba_eeg_manager_annotate.restype = None
# get_annotations()
_dll.ba_eeg_manager_get_annotations.argtypes = [
    ctypes.c_void_p,
    ctypes.POINTER(ctypes.POINTER(Annotation)),
    ctypes.POINTER(ctypes.c_size_t),
]
_dll.ba_eeg_manager_get_annotations.restype = None
# clear_annotations()
_dll.ba_eeg_manager_clear_annotations.argtypes = [ctypes.c_void_p]
_dll.ba_eeg_manager_clear_annotations.restype = None

# Stream size type info super secret function thingy
_dll.ba_eeg_manager_get_stream_channel_data_types.argtypes = [
    ctypes.c_void_p,
    ctypes.POINTER(ctypes.POINTER(ctypes.c_uint8)),
    ctypes.POINTER(ctypes.c_size_t),
]
_dll.ba_eeg_manager_get_stream_channel_data_types.restype = None


_managers_mtx = threading.Lock()
_managers: dict = dict()

_types_map = [
    ctypes.POINTER(ctypes.c_float),  # 0
    ctypes.POINTER(ctypes.c_bool),   # 1
    ctypes.POINTER(ctypes.c_size_t), # 2
    ctypes.POINTER(ctypes.c_double), # 3
]

# TODO: look into the possibility of moving callbacks to async loop with call_soon_threadsafe()


@ctypes.CFUNCTYPE(
    None, ctypes.POINTER(ctypes.c_void_p), ctypes.c_size_t, ctypes.c_void_p
)
def _callback_chunk(chunk_data, chunk_size, data):
    with _managers_mtx:
        mgr = _managers.get(data)
        if mgr != None:
            with mgr._callback_chunk_mtx:
                cbk = mgr._callback_chunk
                if cbk != None:
                    # Get channel sizes and type information
                    types_ptr = ctypes.POINTER(ctypes.c_uint8)()
                    types_size = ctypes.c_size_t()
                    _dll.ba_eeg_manager_get_stream_channel_data_types(
                        data, ctypes.pointer(types_ptr), ctypes.pointer(types_size)
                    )
                    types = [_types_map[types_ptr[i]] for i in range(types_size.value)]
                    # Convert chunk data to Python list and pass to manager
                    chunk_list = [
                        [
                            ctypes.cast(chunk_data[i], types[i])[j]
                            for j in range(chunk_size)
                        ]
                        for i in range(len(types))
                    ]
                    cbk(chunk_list, chunk_size)


@ctypes.CFUNCTYPE(None, ctypes.POINTER(BatteryInfo), ctypes.c_void_p)
def _callback_battery(b_info, data):
    with _managers_mtx:
        mgr = _managers.get(data)
        if mgr != None:
            with mgr._callback_battery_mtx:
                cbk = mgr._callback_battery
                if cbk != None:
                    cbk(copy.copy(b_info[0]))


@ctypes.CFUNCTYPE(None, ctypes.c_void_p)
def _callback_disconnect(data):
    with _managers_mtx:
        mgr = _managers.get(data)
        if mgr != None:
            with mgr._future_map_mtx:
                mgr._future_index = 0
                del_list = []
                for k, v in mgr._future_map.items():
                    _, loop, future = v
                    loop.call_soon_threadsafe(
                        future.set_exception, RuntimeError("Disconnected")
                    )
                    del_list.append(k)
                for item in del_list:
                    del mgr._future_map[item]
            with mgr._callback_disconnect_mtx:
                cbk = mgr._callback_disconnect
                if cbk != None:
                    cbk()


class _FutureStruct(ctypes.Structure):
    _fields_ = [("manager_ptr", ctypes.c_void_p), ("future_index", ctypes.c_size_t)]


def _handle_future(data, arg):
    my_data = ctypes.cast(data, ctypes.POINTER(_FutureStruct))[0]
    with _managers_mtx:
        mgr = _managers.get(my_data.manager_ptr)
        if mgr != None:
            with mgr._future_map_mtx:
                future_obj = mgr._future_map.get(my_data.future_index)
                if future_obj != None:
                    _, loop, future = future_obj
                    del mgr._future_map[my_data.future_index]
                    loop.call_soon_threadsafe(future.set_result, arg)


@ctypes.CFUNCTYPE(None, ctypes.c_void_p)
def _future_callback_void(data):
    _handle_future(data, None)


@ctypes.CFUNCTYPE(None, ctypes.c_bool, ctypes.c_void_p)
def _future_callback_bool(val, data):
    _handle_future(data, val)


@ctypes.CFUNCTYPE(None, ctypes.c_float, ctypes.c_void_p)
def _future_callback_float(val, data):
    _handle_future(data, val)


@ctypes.CFUNCTYPE(None, ctypes.POINTER(FullBatteryInfo), ctypes.c_void_p)
def _future_callback_full_battery_info(val, data):
    _handle_future(data, copy.copy(val[0]))


class _Error(enum.Enum):
    OK = 0
    CONNECTION = 1
    UNSUPPORTED_DEVICE = 2
    UNKNOWN = 0xFF


def _get_error(val):
    try:
        return _Error(val)
    except ValueError:
        return _Error.UNKNOWN


def _handle_error(val):
    err = _get_error(val)
    if err == _Error.OK:
        return
    elif err == _Error.CONNECTION:
        raise RuntimeError("Connection error")
    elif err == _Error.UNSUPPORTED_DEVICE:
        raise RuntimeError("Unsupported device")
    else:
        raise RuntimeError("Unknown error")


class EEGManager:
    """ The EEG manager is the primary tool for communicating with the BrainAccess device.
    Note that the EEG manager is not thread-safe.
    """

    def __init__(self):
        """Creates an EEG Manager.

        Warning
        ---------
        Make sure the core library has been initialized first!
        """
        self._manager = _dll.ba_eeg_manager_new()
        self._callback_chunk_mtx = threading.Lock()
        self._callback_battery_mtx = threading.Lock()
        self._callback_disconnect_mtx = threading.Lock()
        self._future_map_mtx = threading.Lock()
        self._future_map = {}
        self._future_index = 0
        with _managers_mtx:
            _managers[self._manager] = self

        self._callback_disconnect = None
        _dll.ba_eeg_manager_set_callback_disconnect(
            self._manager, _callback_disconnect, self._manager
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.destroy()

    def destroy(self):
        """Destroys an EEG manager instance.

        Warning
        ---------
        Must be called exactly once, after the manager is no longer needed
        """
        self.disconnect()  # prevent callback deadlock by disconnecting first.
        with _managers_mtx:
            _dll.ba_eeg_manager_free(self._manager)
            del _managers[self._manager]

    def _create_future(self):
        loop = asyncio.get_running_loop()
        future = loop.create_future()

        with self._future_map_mtx:
            index = self._future_index
            struct = _FutureStruct()
            struct.manager_ptr = self._manager
            struct.future_index = index
            self._future_map[index] = (struct, loop, future)
            self._future_index = (self._future_index + 1) % (
                ctypes.c_size_t(-1).value + 1
            )

        return future, ctypes.pointer(struct)

    def connect(self, port: str):
        """Connects to a device via COM port and attempts to initialize it.

        Note
        -----
        This function runs asynchronously.

        Parameters
        ----------
        port: str
            `COMx` on Windows and `/dev/rfcommX` on Linux decided upon connecting device to Bluetooth

        Returns
        -------
        future: asyncio.Future
            await future to complete connecting
        """
        future, struct_ptr = self._create_future()

        _dll.ba_eeg_manager_connect(
            self._manager,
            port.encode("ascii"),
            _future_callback_bool,
            struct_ptr,
        )
        return future

    def is_connected(self):
        """Checks if the EEGManager is currently connected to an EEG device

        Returns
        -------
        bool
            True if connected, False otherwise

        """
        return _dll.ba_eeg_manager_is_connected(self._manager)

    def disconnect(self):
        """Disconnects the EEGManager from the EEG device, if connected"""
        _dll.ba_eeg_manager_disconnect(self._manager)

    def start_stream(self):
        """Starts streaming data from the device

        Note
        -----
        This function runs asynchronously.

        Warning
        --------
        You must not call this function twice without stopping the stream in between.

        Returns
        -------
        future: asyncio.Future
            awaiting future starts stream
        """
        future, struct_ptr = self._create_future()

        _handle_error(
            _dll.ba_eeg_manager_start_stream(
                self._manager,
                _future_callback_void,
                struct_ptr,
            )
        )

        return future

    def stop_stream(self):
        """Stops streaming data from the device

        Note
        -----
        This function runs asynchronously.

        Warning
        -------
        You must not call this function twice without starting the stream in between.
        You must not call this function while the stream is not running.
        Calling this function resets all stream settings. If you want to stream again
        afterwards, you must re-enable all the channels, biases, gains, and impedance
        measurement mode that you set previously.

        Returns
        -------
        future: asyncio.Future
            awaiting future stops stream
        """
        future, struct_ptr = self._create_future()

        _handle_error(
            _dll.ba_eeg_manager_stop_stream(
                self._manager,
                _future_callback_void,
                struct_ptr,
            )
        )

        return future

    def is_streaming(self):
        """Checks if the device is streaming

        Returns
        -------
        bool
            True if the stream is active, False otherwise

        """
        return _dll.ba_eeg_manager_is_streaming(self._manager)

    def set_io(self, pin: int, state: bool):
        """Digital pin control
        The digital input pin, which by default is pulled high but can be
        pulled low by an external sensor, can also be pulled low by the
        device itself. By default, upon powering up or connecting/disconnecting
        the device, the digital input pin is pulled high.

        This can be useful, for example, in case you want to synchronize
        devices: connect device A and B's digital inputs, start both streams,
        then set A's digital input to pull low, which also pulls B's input
        with it. The falling edge can be recorded from both streams, and the
        data can then be aligned accordingly.

        This can also be used for low-speed communication with external
        devices, controlling LEDs via a mosfet, etc.

        Note
        -----
        This function runs asynchronously.

        Parameters
        ----------
        pin: int
            Number of digital input pin of the EEG device to set the IO state of (starting from 0)
        state: bool
            True to pull high, False to pull to ground

        Returns
        -------
        future: asyncio.Future
            awaiting future sets digital pin state
        """
        future, struct_ptr = self._create_future()

        _handle_error(
            _dll.ba_eeg_manager_set_io(
                self._manager,
                ctypes.c_uint8(pin),
                ctypes.c_bool(state),
                _future_callback_void,
                struct_ptr,
            )
        )

        return future

    def get_battery_info(self):
        """Returns a structure containing standard battery information from the device

        Returns
        -------
        BatteryInfo
            Battery information from the EEG device
        """
        return _dll.ba_eeg_manager_get_battery_info(self._manager)

    def get_full_battery_info(self):
        """ Returns a structure containing extended battery info from the device

        Note
        -----
        This function runs asynchronously.

        Returns
        -------
        future: asyncio.Future
           awaiting future returns FullBatteryInfo

        """
        future, struct_ptr = self._create_future()

        _handle_error(
            _dll.ba_eeg_manager_get_full_battery_info(
                self._manager,
                _future_callback_full_battery_info,
                struct_ptr,
            )
        )

        return future

    def get_latency(self):
        """Measure approximate communication latency with the device

        Note
        -----
        This function runs asynchronously.

        Returns
        -------
        future: asyncio.Future
            awaiting future returns number of seconds (float)

        """
        future, struct_ptr = self._create_future()

        _handle_error(
            _dll.ba_eeg_manager_get_latency(
                self._manager,
                _future_callback_float,
                struct_ptr,
            )
        )

        return future

    def set_channel_enabled(self, channel: int, state: bool):
        """ Enables or disables the channel on the device

        Warning
        ---------
        Enabled channels are reset by stream stop.
        Must be called with the appropriate arguments before every stream start

        Parameters
        -------------
        channel: int
            Channel ID (brainaccess.core.eeg_channel) to enable/disable.
        state: bool
            True to enable channel, False to disable.

        """
        _dll.ba_eeg_manager_set_channel_enabled(
            self._manager, ctypes.c_uint16(channel), ctypes.c_bool(state)
        )

    def set_channel_gain(self, channel: int, gain: GainMode):
        """ Changes gain mode for a channel on the device.
        Setting gain values to lower will increase the measured voltage range,
        but would decrease the amplitude resolution, 12 is the optimum in most cases.

        Warning
        ------
        This function takes effect on stream start, and its effects are
        reset by stream stop. Therefore, it must be called with the appropriate
        arguments before every stream start.
        This only affects channels that support it. For example, it affects the
        electrode measurement channels but not sample number or digital input.

        Parameters
        -----------
        channel: int
            Channel ID (brainaccess.core.eeg_channel) whose gain to modify.
        gain: GainMode
            Gain mode. Default X12

        """
        _dll.ba_eeg_manager_set_channel_gain(
            self._manager, ctypes.c_uint16(channel), ctypes.c_uint8(gain.value)
        )

    @multimethod
    def set_channel_bias(self, channel: int, bias: bool):
        """
        DEPRECATED: use the version with Polarity instead.

        Set an electrode channel as a bias electrode
        Essentially the signals of these channels are inverted and injected
        into the bias channel/electrode. This helps in reducing common mode
        noise such as noise coming from the mains.
        Only select channels for bias feedback that have good contact with a skin.
        Typically one channel is sufficient for bias feedback to work effectively.

        Warning
        --------
        This function takes effect on stream start, and its effects are
        reset by stream stop. Therefore, it must be called with the appropriate
        arguments before every stream start.

        Parameters
        ------------
        channel: int
            Channel ID (brainaccess.core.eeg_channel) to set/unset as bias channel
        bias: bool
            True to enable channel, False to disable.

        """
        return self.set_channel_bias(channel, Polarity.BOTH if bias else Polarity.NONE)

    @multimethod
    def set_channel_bias(self, channel: int, p: Polarity):
        """Set an electrode channel as a bias electrode
        Essentially the signals of these channels are inverted and injected
        into the bias channel/electrode. This helps in reducing common mode
        noise such as noise coming from the mains.
        Only select channels for bias feedback that have good contact with a skin.
        Typically one channel is sufficient for bias feedback to work effectively.

        Warning
        --------
        This function takes effect on stream start, and its effects are
        reset by stream stop. Therefore, it must be called with the appropriate
        arguments before every stream start.

        Parameters
        ------------
        channel: int
            Channel ID (brainaccess.core.eeg_channel) to set/unset as bias channel
        p: Polarity
            Which side of the electrode to use (if device is not bipolar, use
            BOTH)

        """
        _dll.ba_eeg_manager_set_channel_bias(
            self._manager, ctypes.c_uint16(channel), ctypes.c_uint8(p.value)
        )

    def set_impedance_mode(self, mode: ImpedanceMeasurementMode):
        """Sets impedance measurement mode
        This function setups device for electrode impedance measurement.
        It injects a 7nA certain frequency current through the bias electrodes
        to measurement electrodes. Voltage recordings from each channel can
        then be used to calculate the impedance for each electrode:
        Impedance = Vpp/7nA

        Warning
        ---------
        This function takes effect on stream start, and its effects are
        reset by stream stop. Therefore, it must be called with the appropriate
        arguments before every stream start.

        Parameters
        -----------
        mode: ImpedanceMeasurementMode
            Impedance mode to set

        """
        _dll.ba_eeg_manager_set_impedance_mode(
            self._manager, ctypes.c_uint8(mode.value)
        )

    def get_device_info(self):
        """Get device information

        Warning
        ----------
        Must not be called unless device connection is successful

        Returns
        -------
        DeviceInfo
            device model, version, firmware version and buffer size
        """
        return _dll.ba_eeg_manager_get_device_info(self._manager)

    def get_channel_index(self, channel: int):
        """Gets the index of a channel's data into the chunk

        Get the index into the array provided by the chunk callback that contains
        the data of the channel number specified

        Parameters
        ------------
        channel: int
            The number of the channel whose index to get

        Returns
        ---------
        int
            Index into chunk representing a channel
        """
        val = _dll.ba_eeg_manager_get_channel_index(
            self._manager, ctypes.c_uint16(channel)
        )
        if val == ctypes.c_size_t(-1).value:
            raise IndexError("Channel does not exist or is not currently streaming")
        return val

    def get_sample_frequency(self):
        """Get device sampling frequency

        Returns
        -------
        int
            Sample frequency (Hz)

        """
        return _dll.ba_eeg_manager_get_sample_frequency(self._manager)

    def set_callback_chunk(self, f):
        """Sets a callback to be called every time a chunk is available

        Warning
        -------
        The callback may or may not run in the reader thread, and as such,
        synchronization must be used to avoid race conditions, and the callback
        itself must be as short as possible to avoid blocking communication
        with the device.

        Parameters
        ------------
        f
            callback Function to be called every time a chunk is available
            Set to null to disable.
        """
        with self._callback_chunk_mtx:
            self._callback_chunk = f
            _dll.ba_eeg_manager_set_callback_chunk(
                self._manager, _callback_chunk if f != None else None, self._manager
            )

    def set_callback_battery(self, f):
        """Sets a callback to be called every time the battery status is updated

        Warning
        ---------
        The callback may or may not run in the reader thread, and as such,
        synchronization must be used to avoid race conditions, and the callback
        itself must be as short as possible to avoid blocking communication
        with the device.

        Parameters
        ----------
        f
            pass callback Function to be called every time a battery update is available
            Set to null to disable.
        """
        with self._callback_battery_mtx:
            self._callback_battery = f
            _dll.ba_eeg_manager_set_callback_battery(
                self._manager, _callback_battery if f != None else None, self._manager
            )

    def set_callback_disconnect(self, f):
        """ Sets a callback to be called every time the device disconnects

        Warning
        ---------
        The callback may or may not run in the reader thread, and as such,
        synchronization must be used to avoid race conditions, and the callback
        itself must be as short as possible to avoid blocking communication
        with the device.


        Parameters
        ----------
        f
            callback Function to be called every time the device disconnects. Set to null to disable.
        """
        with self._callback_disconnect_mtx:
            self._callback_disconnect = f
            """_dll.ba_eeg_manager_set_callback_disconnect(
                self._manager, _callback_disconnect if f != None else None, self._manager
            )"""

    def annotate(self, annotation: str):
        """ Adds an annotation at the current time

        Warning
        ---------
        Annotations are cleared on disconnect

        Parameters
        ----------
        annotation: str
            annotation text
        """
        _dll.ba_eeg_manager_annotate(
            self._manager, ctypes.c_char_p(annotation.encode("ascii"))
        )

    def get_annotations(self):
        """Retrieve all the accumulated annotations

        Warning
        ---------
        Annotations are cleared on disconnect

        Returns
        -------
        list
            list of annotations
        """
        ae = ctypes.POINTER(Annotation)()
        size = ctypes.c_size_t()
        _dll.ba_eeg_manager_get_annotations(
            self._manager, ctypes.pointer(ae), ctypes.pointer(size)
        )
        return [ae[i] for i in range(size.value)]

    def clear_annotations(self):
        """Clears annotations"""
        _dll.ba_eeg_manager_clear_annotations(self._manager)
