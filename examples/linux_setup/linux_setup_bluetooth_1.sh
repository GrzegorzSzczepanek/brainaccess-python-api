# # Find the device address
# Open terminal
# From command line enter Bluetooth then power it on and scan for devices (can be done from GUI)
bluetoothctl
power on
scan on

# Example:
# Device B8:F0:09:AA:30:CE BrainAccess MINI

# Using the address connect and trust Bluetooth
connect B8:F0:09:AA:30:CE 
trust B8:F0:09:AA:30:CE 

# close terminal
