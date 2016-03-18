#!/usr/bin/env python2
##################################################
# GNU Radio Python Flow Graph
# Title: Calculates FFT, in stream averaging, probes and storage
##################################################

from gnuradio import analog
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import fft
from gnuradio import uhd
from gnuradio.eng_option import eng_option
from grc_gnuradio import blks2 as grc_blks2
from gnuradio.fft import window
from gnuradio.filter import firdes
from gnuradio import filter
from optparse import OptionParser
import timeit
import time
import threading

##########RECEIVER###########
class Receiver(gr.top_block):
    
    def __init__(self, fftsize, samp_rate, gain, c_freq, windows):
		gr.top_block.__init__(self, "CalculateFFT")
        
		#Class variables
		self.samp_rate = samp_rate
		self.gain = gain
		self.fftsize = fftsize
		self.c_freq = c_freq
		self.dump1 = "/tmp/ramdisk/dump1" #View as null sinks
		self.dump2 = "/tmp/ramdisk/dump2"
		self.dump3 = "/tmp/ramdisk/dump3"
		self.dump4 = "/tmp/ramdisk/dump4"
		self.alpha = 0.01 #Integrate 100 FFTS 0.01
		self.N = 100 #100
		self.probe_var = probe_var = 0
		self.probe_var_1 = probe_var_1 = 0
		
		blackman_harris = window.blackmanharris(self.fftsize)
		hanning = window.hanning(self.fftsize)
		rectangular = window.rectangular(self.fftsize)
		self.window = blackman_harris #Default window
		self.select_window = windows
		
		###Selectable FFT Windows###
		if self.select_window == "blackman-harris":
			self.window = blackman_harris
		elif self.select_window == "hanning":
			self.window = hanning
		elif self.select_window == "rectangular":
			self.window = rectangular
			
		########## GNURADIO BLOCKS #########
		####################################
		self.uhd_usrp_source_0 = uhd.usrp_source(
			",".join(("", "")), #Set the master_clock_rate, default = 200 MHz, alt 184.32 MHz and 120 MHz (Set)
			uhd.stream_args(
				cpu_format="fc32",
				channels=range(2),
			),
        )
        #Configure USRP channel 0
		self.uhd_usrp_source_0.set_antenna("RX2", 0)
		self.uhd_usrp_source_0.set_samp_rate(self.samp_rate)
		self.uhd_usrp_source_0.set_center_freq(self.c_freq, 0)
		self.uhd_usrp_source_0.set_gain(self.gain, 0)
		self.uhd_usrp_source_0.set_bandwidth(self.samp_rate, 0)
		#self.uhd_usrp_source_0.set_clock_source('internal', 0)
		
		#Configure USRP channel 1
		self.uhd_usrp_source_0.set_antenna("RX2", 1)
		self.uhd_usrp_source_0.set_samp_rate(self.samp_rate)
		self.uhd_usrp_source_0.set_center_freq(self.c_freq, 1)
		self.uhd_usrp_source_0.set_gain(self.gain, 1)
		self.uhd_usrp_source_0.set_bandwidth(self.samp_rate, 1)
		#self.uhd_usrp_source_0.set_clock_source('internal', 1)
		
		
		#Signal and reference file sinks channel 0
		self.signal_file_sink_1 = blocks.file_sink(gr.sizeof_float*1, self.dump1, False)
		self.signal_file_sink_1.set_unbuffered(False)
		self.signal_file_sink_2 = blocks.file_sink(gr.sizeof_float*1, self.dump2, False)
		self.signal_file_sink_2.set_unbuffered(False)
		
		#Signal and reference file sinks channel 1
		self.signal_file_sink_3 = blocks.file_sink(gr.sizeof_float*1, self.dump3, False)
		self.signal_file_sink_3.set_unbuffered(False)
		self.signal_file_sink_4 = blocks.file_sink(gr.sizeof_float*1, self.dump4, False)
		self.signal_file_sink_4.set_unbuffered(False)
		
	
		#Selector for GPIO switch channel 0
		self.blks2_selector_0 = grc_blks2.selector(
			item_size=gr.sizeof_float*1,
			num_inputs=1,
			num_outputs=2+1, #+1 for the null sink
			input_index=0,
			output_index=0,
		)
        
        #Selector for GPIO switch channel 1
		self.blks2_selector_1 = grc_blks2.selector(
			item_size=gr.sizeof_float*1,
			num_inputs=1,
			num_outputs=2+1, #+1 for the null sink
			input_index=0,
			output_index=0,
		)
        
        #Div blocks channel 0
		self.blocks_null_sink = blocks.null_sink(gr.sizeof_float*1)
		self.single_pole_iir_filter_xx_0 = filter.single_pole_iir_filter_ff(self.alpha, self.fftsize)
		self.fft_vxx_0 = fft.fft_vcc(self.fftsize, True, (self.window), True, 1)
		self.blocks_vector_to_stream_0 = blocks.vector_to_stream(gr.sizeof_float*1, self.fftsize)
		self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, self.fftsize)
		self.blocks_keep_one_in_n_0 = blocks.keep_one_in_n(gr.sizeof_float*self.fftsize, self.N)
		self.blocks_complex_to_mag_squared_0 = blocks.complex_to_mag_squared(self.fftsize)
		
		#Div blocks channel 1
		self.blocks_null_sink_1 = blocks.null_sink(gr.sizeof_float*1)
		self.single_pole_iir_filter_xx_1 = filter.single_pole_iir_filter_ff(self.alpha, self.fftsize)
		self.fft_vxx_1 = fft.fft_vcc(self.fftsize, True, (self.window), True, 1)
		self.blocks_vector_to_stream_1 = blocks.vector_to_stream(gr.sizeof_float*1, self.fftsize)
		self.blocks_stream_to_vector_1 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, self.fftsize)
		self.blocks_keep_one_in_n_1 = blocks.keep_one_in_n(gr.sizeof_float*self.fftsize, self.N)
		self.blocks_complex_to_mag_squared_1 = blocks.complex_to_mag_squared(self.fftsize)
	
		#Block connections channel 0
		self.connect((self.uhd_usrp_source_0, 0), (self.blocks_stream_to_vector_0, 0))
		self.connect((self.blocks_stream_to_vector_0, 0), (self.fft_vxx_0, 0))
		self.connect((self.fft_vxx_0, 0), (self.blocks_complex_to_mag_squared_0, 0))
		self.connect((self.blocks_complex_to_mag_squared_0, 0), (self.single_pole_iir_filter_xx_0, 0))
		self.connect((self.single_pole_iir_filter_xx_0, 0), (self.blocks_keep_one_in_n_0, 0))
		self.connect((self.blocks_keep_one_in_n_0, 0), (self.blocks_vector_to_stream_0, 0))
		self.connect((self.blocks_vector_to_stream_0, 0), (self.blks2_selector_0, 0))
		
		#Block connections channel 1
		self.connect((self.uhd_usrp_source_0, 1), (self.blocks_stream_to_vector_1, 0))
		self.connect((self.blocks_stream_to_vector_1, 0), (self.fft_vxx_1, 0))
		self.connect((self.fft_vxx_1, 0), (self.blocks_complex_to_mag_squared_1, 0))
		self.connect((self.blocks_complex_to_mag_squared_1, 0), (self.single_pole_iir_filter_xx_1, 0))
		self.connect((self.single_pole_iir_filter_xx_1, 0), (self.blocks_keep_one_in_n_1, 0))
		self.connect((self.blocks_keep_one_in_n_1, 0), (self.blocks_vector_to_stream_1, 0))
		self.connect((self.blocks_vector_to_stream_1, 0), (self.blks2_selector_1, 0))
		
		#Selector connections channel 0
		self.connect((self.blks2_selector_0, 1), (self.signal_file_sink_1, 0))
		self.connect((self.blks2_selector_0, 2), (self.signal_file_sink_2, 0))
		
		#Selector connections channel 1
		self.connect((self.blks2_selector_1, 1), (self.signal_file_sink_3, 0))
		self.connect((self.blks2_selector_1, 2), (self.signal_file_sink_4, 0))
		
		#Null sink connection channel 0
		self.connect((self.blks2_selector_0, 0), (self.blocks_null_sink, 0))
		
		#Null sink connection channel 1
		self.connect((self.blks2_selector_1, 0), (self.blocks_null_sink_1, 0))
		
		#########PROBE SAMPLES channel 0##########
		self.probe_signal = blocks.probe_signal_f()
		self.blocks_complex_to_mag_0 = blocks.complex_to_mag(1)
		
		self.connect((self.blocks_complex_to_mag_0, 0), (self.probe_signal, 0))    
		self.connect((self.uhd_usrp_source_0, 0), (self.blocks_complex_to_mag_0, 0))
		
		#Probe update rate
		def _probe_var_probe():
			while True:
				val = self.probe_signal.level()
				try:
					self.set_probe_var(val)
				except AttributeError:
					pass
				time.sleep(10 / (self.samp_rate)) #Update probe variabel every 10/samp_rate seconds

		_probe_var_thread = threading.Thread(target=_probe_var_probe)
		_probe_var_thread.daemon = True
		_probe_var_thread.start()
		
		#########PROBE SAMPLES channel 1##########
		self.probe_signal_1 = blocks.probe_signal_f()
		self.blocks_complex_to_mag_1 = blocks.complex_to_mag(1)
		
		self.connect((self.blocks_complex_to_mag_1, 0), (self.probe_signal_1, 0))    
		self.connect((self.uhd_usrp_source_0, 1), (self.blocks_complex_to_mag_1, 0))
		
		#Probe update rate
		def _probe_var_probe_1():
			while True:
				val = self.probe_signal_1.level()
				try:
					self.set_probe_var_1(val)
				except AttributeError:
					pass
				time.sleep(10 / (self.samp_rate)) #Update probe variabel every 10/samp_rate seconds

		_probe_var_thread_1 = threading.Thread(target=_probe_var_probe_1)
		_probe_var_thread_1.daemon = True
		_probe_var_thread_1.start()
		
		
    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        analog_sig_source.set_sampling_freq(self.samp_rate)
        throttle_0.set_sample_rate(self.samp_rate)

    def get_int_time(self):
        return self.int_time

    def set_int_time(self, int_time):
        self.int_time = int_time
        blocks_head_0.set_length(int(self.int_time*self.samp_rate))

    def get_gain(self):
        return self.gain

    def set_gain(self, gain):
        self.gain = gain

    def get_fftsize(self):
        return self.fftsize

    def set_fftsize(self, fftsize):
        self.fftsize = fftsize
    
    def get_c_freq(self):
        return self.c_freq

    def set_c_freq(self, c_freq):
        self.c_freq = c_freq
        self.uhd_usrp_source_0.set_center_freq(self.c_freq, 0)
        
    def get_probe_var(self):
        return self.probe_var

    def set_probe_var(self, probe_var):
        self.probe_var = probe_var

