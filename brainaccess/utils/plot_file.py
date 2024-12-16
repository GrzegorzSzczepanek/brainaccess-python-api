import pathlib
import sys
import mne
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use("TKAgg", force=True)

try:
    path = pathlib.Path(sys.argv[1])
    raw = mne.io.read_raw_fif(path, preload=True).filter(1, None)
    raw.pick('eeg').plot(scalings="auto", show=True)
    plt.show()
except Exception:
    print(Exception)
