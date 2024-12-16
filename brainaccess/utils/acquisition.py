import asyncio
import typing
import time
import brainaccess.core as bacore
import brainaccess.core.eeg_channel as eeg_channel
from brainaccess.core.gain_mode import GainMode, multiplier_to_gain_mode
from brainaccess.core.eeg_manager import EEGManager
from brainaccess.core.impedance_measurement_mode import ImpedanceMeasurementMode
import threading
import numpy as np
import mne  # type: ignore
import pathlib

IMPEDANCE_DRIVE_AMPS = 6.0e-9  # 6 nA
BOARD_RESISTOR_OHMS = 2 * 4.7e3  # 4.7 kOhm


class EEG:
    """EEG acquisition class. Gathers data from brainaccess core and converts to MNE structure."""

    def __init__(
        self,
        mode: str = "accumulate",
    ) -> None:
        """Creates EEG object and initializes device with default parameters.

        Parameters
        -------------
        mode: str
            Data storage modes accumulate (all data is accumulated in array) or roll (only last x seconds preserved)

        """
        self.directory = pathlib.Path.cwd()
        self.wait_max: int = 2
        self.time_step: float = 0.5
        self.impedances: dict = {}
        self.eeg_channels: dict = {}
        self.bias_channels: typing.Optional[list] = None
        self.mode: str = mode
        self.gain: GainMode = GainMode.X8
        bacore.init(bacore.Version(2, 0, 0))

    async def _connect(self, port: str = "COM4"):
        self.conn_error = await self.mgr.connect(port)

    def setup(
        self,
        mgr: EEGManager,
        cap: dict = {
            0: "F3",
            1: "F4",
            2: "C3",
            3: "C4",
            4: "P3",
            5: "P4",
            6: "O1",
            7: "O2",
        },
        port: str = "COM4",
        zeros_at_start: int = 0,
        bias: typing.Optional[list] = None,
        gain: int = 8,
    ) -> None:
        """Connects to device and sets channels

        Parameters
        ------------
        mgr: EEGManager
        port: str (Default value = 'COM4')

        """
        self.mgr = mgr
        self.zeros_at_start = zeros_at_start
        if bias:
            self.bias_channels = bias
        else:
            self.bias_channels = []
        if gain in [1, 2, 4, 6, 8, 12, 24]:
            self.gain = multiplier_to_gain_mode(gain)
        else:
            print("Provided gain not supported. Using default 8")
        start_time = time.time()
        while time.time() < (start_time + self.wait_max):
            try:
                asyncio.run(self._connect(port))
                if self.conn_error:
                    break
                else:
                    print("could not connect")
            except Exception as e:
                raise e
        else:
            self._error("Could not connect to Client.")
        self.eeg_channels = {}
        self.channels_indexes = {}
        for electrode, name in cap.items():
            self.eeg_channels[eeg_channel.ELECTRODE_MEASUREMENT + electrode] = name
            self.channels_indexes[eeg_channel.ELECTRODE_MEASUREMENT + electrode] = 0
        self.eeg_channels[eeg_channel.ACCELEROMETER + 0] = "Accel_x"
        self.eeg_channels[eeg_channel.ACCELEROMETER + 1] = "Accel_y"
        self.eeg_channels[eeg_channel.ACCELEROMETER + 2] = "Accel_z"
        self.eeg_channels[eeg_channel.DIGITAL_INPUT] = "Digital"
        self.eeg_channels[eeg_channel.SAMPLE_NUMBER] = "Sample"
        self.channels_indexes[eeg_channel.ACCELEROMETER + 0] = 0
        self.channels_indexes[eeg_channel.ACCELEROMETER + 1] = 0
        self.channels_indexes[eeg_channel.ACCELEROMETER + 2] = 0
        self.channels_indexes[eeg_channel.DIGITAL_INPUT] = 0
        self.channels_indexes[eeg_channel.SAMPLE_NUMBER] = 0
        eeg_info = self._create_info()
        self.info = eeg_info
        self.chans = len(self.info.ch_names)
        if self.mode == "accumulate":
            self.lock = threading.Lock()
            self.data = EEGData(eeg_info, lock=self.lock, zeros_at_start=zeros_at_start)
        else:
            self.lock = threading.Lock()
            self.data = EEGData_roll(
                eeg_info, lock=self.lock, zeros_at_start=zeros_at_start
            )

    def _set_channels(self):
        for chan in self.eeg_channels.keys():
            self.mgr.set_channel_enabled(chan, True)

    async def _get_battery(self):
        return await self.mgr.get_full_battery_info()

    def get_battery(self):
        """Returns battery level"""
        return asyncio.run(self._get_battery()).level

    def _error(self, extra: str = ""):
        """Raises error with extra text
        Parameters
        ----------
        extra: str  (Default value = '')

        """
        raise RuntimeError(f"{extra}")

    def close(self):
        """Close device"""
        bacore.close()

    async def _start_acquisition(self):
        """Starts streaming and collecting data"""
        self._set_channels()
        for chan in self.bias_channels:
            self.mgr.set_channel_bias(eeg_channel.ELECTRODE_MEASUREMENT + chan, True)
        for idx in list(self.eeg_channels.keys())[:-5]:
            self.mgr.set_channel_gain(idx, self.gain)
        if self.mode == "accumulate":
            self.mgr.set_callback_chunk(self._acq)
        else:
            self.mgr.set_callback_chunk(self._acq_roll)
        try:
            await self.mgr.start_stream()
        except Exception:
            raise Exception
        for key in self.channels_indexes.keys():
            self.channels_indexes[key] = self.mgr.get_channel_index(key)

    def start_acquisition(self):
        """Starts streaming and collecting data"""
        asyncio.run(self._start_acquisition())

    async def _stop_acquisition(self):
        """"""
        await self.mgr.stop_stream()

    def stop_acquisition(self):
        asyncio.run(self._stop_acquisition())

    def get_annotations(self):
        """Returns annotations"""
        self.data.annotations = self.mgr.get_annotations()
        return self.data.annotations

    def annotate(self, msg: str) -> None:
        """
        Parameters
        -----------
        msg: str
            annotation to send

        """
        self.mgr.annotate(msg)

    def get_mne(
        self, tim: float = None, samples: int = None, annotations: bool = True
    ) -> mne.io.BaseRaw:
        """Return MNE structure.
        If tim None returns all data otherwise last tim seconds

        Parameters
        -----------
        tim: float (Default value = None)
            time in seconds

        Returns
        -------
        mne.io.BaseRaw
            Raw MNE EEG data structure

        """
        if annotations:
            self.get_annotations()
        self.data.convert_to_mne(
            tim=tim,
            samples=samples,
            channels_indexes=list(self.channels_indexes.values()),
        )
        return self.data.mne_raw

    def _acq(self, chunk, chunk_size):
        """function to acquire data with callback
        Parameters
        ----------
        chunk
            data chunk from device
        chunk_size: int
            size of the chunk
        """
        self.data.data.append(np.array(chunk))

    def _acq_roll(self, chunk, chunk_size):
        """function to acquire fixed size data with callback
        Parameters
        ----------
        chunk
            data chunk from device
        chunk_size: int
            size of the chunk
        """
        self.data.data = np.roll(self.data.data, -chunk_size, axis=1)
        self.data.data[:, -chunk_size:] = np.array(chunk)

    def _create_info(self):
        """mne info structure creation"""
        sampling_freq = self.mgr.get_sample_frequency()
        ch_names = [x for x in self.eeg_channels.values()]
        ch_types = ["eeg"] * int(len(ch_names) - 5)
        ch_types.extend(["misc"] * 3)
        ch_types.extend(["stim"])
        ch_types.extend(["syst"])
        eeg_info = mne.create_info(ch_names, ch_types=ch_types, sfreq=sampling_freq)
        eeg_info.set_montage("standard_1005")
        return eeg_info

    def calc_impedances(self, tim: float = 4) -> list:
        """Calculate impedance in last tim seconds
        Impedance calculated as in https://openbci.com/community/openbci-measuring-electrode-impedance/

        Parameters
        ----------
        tim: float
            Last x seconds in acquisition to get average impedance from
        Returns
        -------
        list
            Impedances
        """
        data = self.get_mne(tim=tim).filter(20, 40).get_data(picks="eeg")
        data = np.std(data, axis=1)
        self.impedance = (
            (np.sqrt(2.0) * data * 1.0e-6) / IMPEDANCE_DRIVE_AMPS - BOARD_RESISTOR_OHMS
        ) / 1000
        self.impedance[self.impedance < 0] = 0
        return self.impedance

    def start_impedance_measurement(self):
        self.mgr.set_impedance_mode(ImpedanceMeasurementMode.HZ_31_2)
        self.start_acquisition()

    def stop_impedance_measurement(self):
        self.stop_acquisition()
        self.mgr.set_impedance_mode(ImpedanceMeasurementMode.OFF)


class EEGData_roll:
    """Data structure to store rolling EEG data buffer"""

    def __init__(self, info, lock, zeros_at_start: int = 1):
        if not lock:
            raise (Exception("No lock passed"))
        self.eeg_info: mne.Info = info
        self.mne_raw: mne.io.BaseRaw
        self.chans = len(info.ch_names)
        self.zeros_at_start = zeros_at_start
        self.data = np.zeros((self.chans, self.zeros_at_start))
        self.connectivity: list = []
        self.annotations: list = []
        self.lock = lock

    def save(self, fname: str):
        """
        Parameters
        ------------
        fname: str
            filename to save data to
        """
        with self.lock:
            self.mne_raw.save(fname=fname, verbose=False, overwrite=True, fmt="double")

    def load(self, fname: str):
        self.mne_raw = mne.io.read_raw(fname, verbose=False)

    def convert_to_mne(
        self,
        tim: float = None,
        samples: int = None,
        annotations: bool = True,
        channels_indexes: typing.Optional[list] = None,
    ):
        """Convert arrays to MNE.
        If tim None returns all data from acquisition start. Otherwise last tim seconds

        Parameters
        ------------
        tim: float, default value = None
            time in seconds or samples to cut
        samples: int, default value = None
            samples or time to cut
        annotations: bool, default value = True
            should annotations be included

        """
        with self.lock:
            length = len(self.data)
        if length > 0:
            if annotations:
                onset = []
                description = []
                for annotation in self.annotations:
                    description.append(annotation.annotation)
                    onset.append(
                        (annotation.timestamp + self.zeros_at_start)
                        / self.eeg_info["sfreq"]
                    )
                duration = np.repeat(0, len(onset))
            if tim:
                # convert tim to samples
                tim = int(tim * self.eeg_info["sfreq"])
                with self.lock:
                    data = np.array(self.data)  # .reshape(self.chans, -1)
                    data = data[:, -tim:]
                # fix annotations
                if annotations:
                    onset = [x - tim for x in onset]
                    duration = np.repeat(0, len(onset))
            elif samples:
                with self.lock:
                    data = np.array(self.data)  # .reshape(self.chans, -1)
                    data = data[:, -samples:]
                # fix annotations
                if annotations:
                    onset = [x - samples for x in onset]
                    duration = np.repeat(0, len(onset))
            else:
                with self.lock:
                    data = np.array(self.data)  # .reshape(self.chans, -1)
            # select right order channels
            if channels_indexes:
                data = data[channels_indexes]
            self.mne_raw = mne.io.RawArray(
                data,
                self.eeg_info,
                verbose=False,
            )
            if annotations:
                annot = mne.Annotations(onset, duration, description)
                self.mne_raw.set_annotations(annot, verbose=False)
        else:
            print("No data to convert to MNE structure")


class EEGData:
    """Object to store EEG data in accumulation mode"""

    def __init__(self, info, lock, zeros_at_start: int = 2):
        self.eeg_info: mne.Info = info
        self.mne_raw: mne.io.BaseRaw
        self.lock = lock
        chans = len(info.ch_names)
        self.zeros_at_start = zeros_at_start
        self.data: list = [np.zeros((chans, self.zeros_at_start))]
        self.connectivity: list = []
        self.annotations: list = []

    def save(self, fname: str):
        """
        Parameters
        ------------
        fname: str
            filename to save data to
        """
        with self.lock:
            self.mne_raw.save(fname=fname, verbose=False, overwrite=True, fmt="double")

    def load(self, fname: str):
        self.mne_raw = mne.io.read_raw(fname, verbose=False)

    def convert_to_mne(
        self,
        tim: float = None,
        samples: int = None,
        annotations: bool = True,
        channels_indexes: typing.Optional[list] = None,
    ):
        """Convert arrays to MNE.
        If tim None returns all data from acquisition start. Otherwise last tim seconds

        Parameters
        ------------
        tim: float, default value = None
            time in seconds till the end to include in the output
        samples: int, default value = None
            time in samples till the end to include in the output
        annotations: bool, default value = True
            should annotations be included

        """
        with self.lock:
            _length = len(self.data)
        if _length > 0:
            if annotations:
                onset = []
                description = []
                for annotation in self.annotations:
                    description.append(annotation.annotation)
                    onset.append(
                        (annotation.timestamp + self.zeros_at_start)
                        / self.eeg_info["sfreq"]
                    )
                duration = np.repeat(0, len(onset))
            if tim:
                # convert tim to samples
                tim = int(tim * self.eeg_info["sfreq"])
                data = self._concat_data()
                data = data[:, -tim:]
                # fix annotations
                if annotations:
                    onset = [x - tim for x in onset]
                    duration = np.repeat(0, len(onset))
            elif samples:
                data = self._concat_data()
                data = data[:, -samples:]
                # fix annotations
                if annotations:
                    onset = [x - samples for x in onset]
                    duration = np.repeat(0, len(onset))
            else:
                data = self._concat_data()
            # select right order channels
            if channels_indexes:
                data = data[channels_indexes]
            self.mne_raw = mne.io.RawArray(
                data,
                self.eeg_info,
                verbose=False,
            )
            if annotations:
                annot = mne.Annotations(onset, duration, description)
                self.mne_raw.set_annotations(annot, verbose=False)
        else:
            print("No data to convert to MNE structure")

    def _concat_data(self):
        with self.lock:
            data = np.block(self.data)
        return data
