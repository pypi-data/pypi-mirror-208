# rtcmdecoder

## Assignment

This package was made as a final project for the course SE426 given by Professor Alain Muls. This package gives the user the ability to decode MSM7 and Ephemeris messages from all major GNSS:

* GPS
* GLONASS
* Galileo
* Beidou
* SBAS
* QZSS

This package pardes the proprietary GPS/GNSS differential correction messages designed by the Radio Technical Commission for Maritime Services. The datafields used in this package are described extensively in [the RTCM standard.](https://rtcm.myshopify.com/collections/differential-global-navigation-satellite-dgnss-standards/products/rtcm-10403-3-differential-gnss-global-navigation-satellite-systems-services-version-3-amendment-2-may-20-2021)


## Installation

Installation of the package can be done through the PyPi service through your terminal:

```console
pip install rtcmdecoder
```

Or installation can be done in a virtual environment:

```console
python3 -m pip install --user --upgrade virtualenv
python3 -m virtualenv venv 
source venv/bin/activate
(env) python3 -m pip install rtcmdecoder
```

If you wish to use the tools for personal development, the repository can be cloned in its entirety:

```console
git clone https://github.com/P3tzl/Project-SE426.git
```

## Input

We have implemented three different types of inputs that can be parsed by this package. The input parsing heavily relies on the [pyrtcm package by semuconsulting.](https://github.com/semuconsulting/pyrtcm) For every type of input, you need to specify:

* The output directory
* The mode (decode MSM7, ephemeris or both)

Depending on the selected mode, the output directory will contain files for MSM7 data, ephemeris or both. These will be clearly labeled and categorized by GNSS.

### File
The most straightforward way to decode your data is to store it as raw bytes in a txt file (as output from another NTRIP client). An example of how to decode all the saved MSM7 and ephemeris messages:

```python
rtcmdecoder -it file -i <input_file> -m both -o <my_output_directory> 
```


### Stream
You can also connect your favorite receiver to your computer via USB and decode the data directly from a serial port. Note that during tests, we have only used the mosaic X5. Our program will identify the port you have connected your receiver to (if you have a succesful connection of course). The only thing you need to configure is the baudrate to make it correspond to the outgoing data from the receiver. 

```python
rtcmdecoder -it stream -m <MSM7/ephemeris/both> -o <my_output_directory> -bd <baudrate_receiver>
```

Connecting to the stream may sometimes not be as plug and play, depending on the receiver. Enable debugging mode by adding *-d* if you encounter any problems.

### Server
The final option is connecting directly to a NTRIP server of your choice:

```python
rtcmdecoder -it server -m both -o <my_output_directory> -s <server_address> -p <server_port> -u <username> -pw <password> -mp <mountpoint> -lt <listening_time> -fs <max_filesize>
```

We have implemented a circular buffer mechanism here that will overwrite existing data as well. The maximum size of the files is given with the flag *-fs* in MB. 
