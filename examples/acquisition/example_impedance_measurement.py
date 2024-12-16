""" Impedance measurement example
Example how to get impedance measurements using acquisition
class from brainaccess.utils

Change Bluetooth port according to your device
"""

import time
from sys import platform

from brainaccess.utils import acquisition
from brainaccess.core.eeg_manager import EEGManager

eeg = acquisition.EEG()

cap: dict = {
  0: "Fp1",
  1: "Fp2",
  2: "O1",
  3: "O2",
}

with EEGManager() as mgr:
    # Set correct Bluetooth port for windows or linux
    if platform == "linux" or platform == "linux2":
        eeg.setup(mgr, port='/dev/rfcomm0', cap=cap, gain=4)
    else:
        eeg.setup(mgr, port='COM4', cap=cap, gain=4)
    # Start measuring impedance
    eeg.start_impedance_measurement()
    # Print impedances
    start_time = time.time()
    while time.time()-start_time < 20:
        time.sleep(1)
        imp = eeg.calc_impedances()
        print(imp)

    # Stop measuring impedance
    eeg.stop_impedance_measurement()
    mgr.disconnect()

eeg.close()
