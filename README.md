# sciospecgui
Graphical user interface for operating ScioSpecEIT devices.

___
# Error Handling

## USB-Connection Problems

If you can´t establish a connection to the USB-FS or USB-HS port on `Linux`, make shure you have the permission to to this

For USB-HS:

    sudo chmod a+rw /dev/ttyUSB0

For USB-FS:

    sudo chmod a+rw /dev/ttyACM0

Furthermore you have to install a [FTDI driver](https://ftdichip.com/drivers/d2xx-drivers/). 
