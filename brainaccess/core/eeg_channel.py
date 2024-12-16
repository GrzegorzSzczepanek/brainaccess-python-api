"""Starting addresses of channels in the chunk

Attributes
-----------
SAMPLE_NUMBER
    The number of the sample starting from 0 at stream start
ELECTRODE_MEASUREMENT
    EEG electrode measurement value (uV)
ELECTRODE_CONTACT
    Whether or not the electrode is making contact with the skin
DIGITAL_INPUT
    Digital IO pin
ACCELEROMETER
    Accelerometer values

Examples
---------
To get ACCELEROMETER x y and z index in the chunk

- x: get_channel_index(ACCELEROMETER + 0)
- y: get_channel_index(ACCELEROMETER + 1)
- z: get_channel_index(ACCELEROMETER + 2)

"""
SAMPLE_NUMBER = 0
ELECTRODE_MEASUREMENT = 1
ELECTRODE_CONTACT = 1025
DIGITAL_INPUT = 2049
ACCELEROMETER = 2561
ELECTRODE_CONTACT_P = 513
ELECTRODE_CONTACT_N = 1537
GYROSCOPE = 2497
