""" EEG measurement example

Example how to get measurements and save to fif format using acquisition
class from brainaccess.utils

Change Bluetooth port according to your device
"""
import matplotlib.pyplot as plt
import matplotlib
from sys import platform
import time

from brainaccess.utils import acquisition
from brainaccess.core.eeg_manager import EEGManager

matplotlib.use("TKAgg", force=True)

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
        eeg.setup(mgr, port='/dev/rfcomm0', cap=cap)
    else:
        eeg.setup(mgr, port='COM4', cap=cap)
    # Start acquiring data
    eeg.start_acquisition()

    start_time = time.time()
    while time.time()-start_time < 10:
        print('annotating eeg data')
        time.sleep(1)
        # send annotation to the device
        eeg.annotate('1')

    # get all eeg data and stop acquisition
    eeg.get_mne()
    eeg.stop_acquisition()
    mgr.disconnect()

# save EEG data to MNE fif format
eeg.data.save(f'{time.strftime("%Y%m%d_%H%M")}-raw.fif')
# Close brainaccess library
eeg.close()
# Show recorded data
eeg.data.mne_raw.filter(1, 40).plot(scalings='auto', verbose=False)
plt.show()
