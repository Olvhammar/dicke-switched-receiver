# dicke-switched-receiver
This repository contains code developed for a microwave receiver measuring trace gases in the atmosphere at Onsala Space Observatory, Sweden.
You will find a fully functional spectrometer implementation using Python and Gnuradio for usage in both total power measurements as well as switched measurements.

Basic overview:
- Server.py: A socket server for controlling and handling data from the receiver
- Measurement.py: Controls the Gnuradio flowgraph i.e. Receiver.py and handles all measurements.
- Analyze.py: Stacks and averages FFT spectrums
- Finalize.py: Finalizes the averaging procedure and creates e.g. FITS-files
- Receiver.py: Gnuradio flowgraph, performs FFT computions as well as real time averaging and saves it to relevant file sinks
- USRP_start.sh:  GNU radio optimization script including RAM Disk initialization.

For more information please refer to the documention sub repository.
