FPGA implementation using RFNoC
===============================
The current GNURadio-FFTS only uses the Kintex 7 FPGA of the Ettus x310 as a standard DDC.
The Kintex 7 however have a great potential and it would be extremely beneficial to perform e.g. the FFT on the FPGA
instead of the host-computer. Some of the benefits include lowering the CPU stress and data rates.

RFNoC
-----
RFNoC (RF Network on Chip) is a relatively new concept in GNURadio which allows for, in relation to raw VHDL/Verilog, an easy FPGA implementation of several functions.
Such as:: 

	FFT computations up to 2048 channels
	Vector IIR averaging filters, extremely useful for FFT outputs
	Keep one in N function, combined with the IIR filter allows for decimation of the stream and thus data rates

GNURadio-FFTS RFNoC modification
--------------------------------
Code have been develop to implement a RFNoC version of the GNURadio-FFTS described here and 
right now there are mainly two points that prevents a update of the system::

	- Number of FFT-channels, where max for RFNoC is in practice only 2048 with a theoretical max of 4096 (Xilinx coregen based). At OSO we require atleast 8192 channels to achieve the desired resolution.
	- RFNoC, at this time, only fully supports ethernet communication.
	
The ethernet equipment is obviously not the biggest problem since we can aquire that but the FFT is trickier. 
There is basically two things that needs be updated in order for a 8k channel FFT to be implemented in RFNoC. One: the Xilinx coregen based FPGA FFT implementation
needs to be updated to 8k channels. And secondly the GNURadio developers needs to add support for fragmentation of vectors in RFNoC which is why only 2048 channel FFT is possible in RFNoC right now.
I have however spoken to several of them and an update is expected and it is on their todolist. It should also be noted that RFNoC is yet in it's alpha stage of development rendering instability as possible problem as well.
I expect that within one year a 8k FFT in RFNoC is implemented and thus the GNURadio-FFTS can be implemented on the FPGA of the Ettus X310 instead of the host computer.
This is useful for the CO-O3 systems where high bandwidths are desired, for the HRC replacement system the benefits are small. 
