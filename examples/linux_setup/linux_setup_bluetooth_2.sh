# Using the address from step 1 bind it to rfcomm0 directory
sudo rfcomm bind rfcomm0 B8:F0:09:AA:30:CE
# to unbind sudo rfcomm unbind rfcomm0
sudo chmod a+rwx /dev/rfcomm0
ls /dev/rfcomm0 # check if binding successful and directory is created

