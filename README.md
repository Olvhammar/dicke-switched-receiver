# GNURadio-FFTS
This repository contains code, Software_CO-O3, developed for a microwave receiver measuring trace gases, i.e. Carbon monoxide and Ozone, in the atmosphere at Onsala Space Observatory, Sweden.
You will find a fully functional spectrometer implementation using Python and Gnuradio for usage in both total power measurements as well as switched measurements.
Software_HRC is a modified version of Software_CO-O3 for usage as back-end spectrometer for the 25 and 20 m antenna at the observatory. The main difference is that Software_HRC can be used for two channel measurements.

Basic overview:
- Server.py: A socket server for controlling and handling data from the receiver
- Measurement.py: Controls the Gnuradio flowgraph i.e. Receiver.py and handles all measurements.
- Analyze.py: Stacks and averages FFT spectrums
- Finalize.py: Finalizes the averaging procedure and creates e.g. FITS-files
- Receiver.py: Gnuradio flowgraph, performs FFT computions as well as real time averaging and saves it to relevant file sinks
- USRP_start.sh:  GNU Radio optimization script including RAM Disk initialization/PCIe init.

The documentation is generated using sphinx and is published at http://gnuradio-ffts.readthedocs.io/

Simon Olvhammar
