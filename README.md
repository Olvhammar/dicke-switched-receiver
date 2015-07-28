# dicke-switched-receiver
This repository contains code developed for a microwave receiver measuring trace gases in the atmosphere at Onsala Space Observatory, Sweden.
You will find a fully functional Dicke-switching radiometer implementation using Python and Gnuradio.

Basic overview:
- Server.py: A socket server for controlling and handling data from the receiver
- Measurement.py: Handles the Gnuradio flowgraph
- Analyze.py: 
- Finalize.py: 
- Receiver.py: Gnuradio flowgraph, performs FFT computions and saves it to relevant file sinks
- read_data.c: A script created by Lars Pettersson for reading data from the socket server

For more information please refer to the documention sub repository
