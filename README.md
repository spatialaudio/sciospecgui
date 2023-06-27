# ScioSpecGui
A graphical user interface for operating ScioSpecEIT devices.

# 1. Installation and Run

Clone this repository and navigate to the directory.
Inside the cloned folder just type

    python main.py

and the gui should start.
If packages are missing just install them using e.g. pip or run:

    pip install -r requirements.txt
___
## Error Handling

### USB-Connection Problems

If you can´t establish a connection to the USB-FS or USB-HS port on `Linux`, make shure you have the permission to do this.

For USB-HS:

    sudo chmod a+rw /dev/ttyUSB0

For USB-FS:

    sudo chmod a+rw /dev/ttyACM0

Furthermore you have to install a [FTDI driver](https://ftdichip.com/drivers/d2xx-drivers/). 
