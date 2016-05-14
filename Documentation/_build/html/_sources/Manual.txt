Spectrometer Manual
===================

Here I will provide a usage manual for the spectrometer. For now this only applies to employees at Onsala Space Observatory (OSO). 
Making the spectrometer publically available might be something to consider for the future. Until then I encourage you to try out OSO:s
`Small Radio Telescopes.  <http://vale.oso.chalmers.se/salsa/>`_

USRP, Computer and Server initialization
----------------------------------------
**The USRP device has to be started before the computer in order for the PCIe communication to function properly.**
After bootup the PCIe drivers for the device has to be turned on. This can be accomplished by the following commands in the terminal::

	cd /bin/niusrprio-installer
	sudo ./niusrprio_pcie start
	
If the device needs to be turned off issue::

	sudo ./niusrprio_pcie stop
	
Before turning it off.
The radiometer software is located in the home directory under GNURadio-FFTS (Software_HRC for two channel version else Software_COO3) and the socket server is turned on by issuing the following command::

	python Server.py
	
This will also initialize the USRP and the system is now ready.
**The listed actions as well as several optimization parameters (including setting up RAM-disk) have been summarized in the script
USRP_start.sh located in the home folder. Always initiate this script on system reboot.**

The computer can either be controlled locally or remotely. For remote control please generate ssh-keys using ssh-keygen and then issue:: 

	ssh-copy-id user@remoteHost
	
The server can now be accessed through ssh or vnc. The installed vnc server is x11vnc, I recommend using ssvnc for the client which utilize ssh-keys.
To install ssvnc issue::

	sudo apt-get install tsvnc

then run::

	ssvnc
	
in your terminal window. SSVNC is also available for Windows systems.

Specifications
--------------
**OS** Ubuntu 15.10 Desktop

**Back-end:** Ettus USRP X310 Motherboard + SBX(120MHz) for COO3 system and dual UBX(160MHz) for HRC replacement system

**Interface:** GNU Radio with UHD version 3.9.1

**IP/PORT**: Se internal docs

**A/D Master Clock Rate** = 120 MHz (COO3) 200 MHz (HRC Replacement) (Configurable at host i.e 184.32 MHz, 200 MHz, 120 MHz)

**FFT Channels:** 8192*2^(-n), where n zero or positive integer.

**Integration time COO3:** Integer multiples of 5 seconds are accepted for integrations <= 30 seconds
Above 30 seconds only integer multiples of 30 seconds is accepted.
Integrations >= 30 seconds is recommended for switched measurements for optimal processing
performance.
Processing time is <= 3% of integration time at 120 MHz. Total power measurements have
significantly lower processing time <0.3%.

**Integration time HRC Replacement:** There are no limitations on integration times <= 1000s, above that only integer multiples of 60 seconds accepted (due to RAM-limitations).
However you can of course make any integration time possible by creating appropriate loops in your control program, i.e. BIFROST.
Processing time may vary depending on whether switched or unswitched measurements are used. Please use the "state?" command to make sure no overlapping occurs between two measurements.
Proccessing time guidelines are however less than 3% for switched measurements and significantly lower for SR=DV=1 measurements.

**Center frequency:** Range 400-4400 MHz SBX-120, 10-6000 MHz UBX-160

**USRP Gain settings:** Range 0-31.5 dB (automatic adjustment recommended)

**Clock source:** External, 10 MHz square wave recommended

**Time source:** Ettus USRP Internal (alt external, GPSDO)

Recommended bandwidths [MHz]
----------------------------
**CO-O3 System:**

.. code-block:: python

	120  60  30  20  15  12  10  7.5  5  2.5  2  1.5  1  0.7  0.5  0.3  0.1
	
**HRC Replacement:**

.. code-block:: python

	50  25  20  10  5  2.5  2  1  0.8  0.5  0.2	
	
Listed bandwidths are confirmed for 8k FFT:s. If other bandwidths are desired possibilities exist.
Note: Switched measurements have confirmed functionality for bandwidths >= 20 MHz. Other bandwidths are possible, make a request to the GNURadio-FFTS and it will answer with closest possible value.
Even decimations of the Master Clock Rate = 200 MHz are however recommended for the best filter characteristics.
The upper limit is 50 MHz for the two channel edition GNURadio-FFTS and 120 MHz for COO3 system. 

List of commands
----------------
Communication with the FFTS is handled by a socket server. Invalid commands will return an error message. The following commands are accepted.::

	command value
	e.g
	conf:fft:channels 8192

**Control:**

.. code-block:: python

	meas:init #initilize measurement
	meas:adjust #set gain automatically, se code explanation for detailed information
	meas:stop #abort measurement
	conf:usrp:bw #configure Ettus USRP bandwidth
	conf:time:obs #integration time
	conf:fft:channels #configure FFT channels
	conf:usrp:cfreq #configure center frequency
	conf:usrp:gain #manual gain setting

**State variables:**

.. code-block:: python

	state? #state of spectrometer i.e. integrating, adjusting, ready
	read:settings? #returns configured settings and general information
	conf:usrp:bw? #return configured bandwidth
	conf:usrp:gain? #return USRP gain
	conf:usrp:cfreq? #return center frequency
	conf:fft:channels? #return FFT channels
	conf:time:obs? #return set integration time

**Read data CO-O3:**

.. code-block:: python

	meas:read:sig? #read signal spectrum
	meas:read:ref? #read reference spectrum
	meas:read:sr? #read signal-reference spectrum
	meas:read:srr? #read (signal-reference)/reference spectrum
	meas:read:hist? #read sample values from latest meas:adjust, plot in a histogram to observe the sample distribution
	
**Read data HRC Replacement: (Replace x with desired channel i.e. 0 or 1)**

.. code-block:: python

	meas:read:sig_chx? #read signal spectrum
	meas:read:ref_chx? #read reference spectrum
	meas:read:sr_chx? #read signal-reference spectrum
	meas:read:srr_chx? #read (signal-reference)/reference spectrum
	meas:read:hist_chx? #read sample values from latest meas:adjust, plot in a histogram to observe the sample distribution
	
Effective bandwidth and offsets
--------------------------------
The figure shows an example of a power spectrum at 120 MHz. Observe the filter roll off at band
edges, implies that effective bandwidth is less than theoretical set bandwidth. In this case a
configured bandwidth of 120 MHz quadrature returns approximately an effective bandwidth of 105
MHz.
Ettus lists an effective bandwidth of approximately 80% of the Nyquist bandwidth which seems to
be in accordance with the experimental results. E.g a set bandwidth of 20 MHz (+-10MHz from
center) will result in an effective bandwidth of approximately 16 MHz (+-8MHz from center).
Raw data may contain a center spike due to DC offset in the A/D converters, as shown in the figure.
Interpolate the spike to obtain a clean spectrum.

..	figure::  images/filterrolloff.png
	:align:	center
	:width:	500px
	:alt:	test
	
Ettus USRP X310 Data sheet
--------------------------
..	figure::  images/x300_x310_Spec_Sheet_Sida_1.png
	:align:	center
	:width:	1000px
	:alt:	test

..	figure::  images/x300_x310_Spec_Sheet_Sida_2.png
	:align:	center
	:width:	1000px
	:alt:	test

UBX-160 Daughterboard Data sheet
--------------------------------
..	figure::  images/UBX_Data_Sheet_Sida_1.png
	:align:	center
	:width:	1000px
	:alt:	test

..	figure::  images/UBX_Data_Sheet_Sida_2.png
	:align:	center
	:width:	1000px
	:alt:	test
