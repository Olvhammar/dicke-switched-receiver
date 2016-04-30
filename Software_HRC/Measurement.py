#!/usr/bin/env python2
##################################################
# Control measurement class
##################################################
from Receiver import *
from Analyze import *
from Finalize import *
from gnuradio import gr
from gnuradio import blocks
import ephem
import matplotlib.pyplot as plt
import numpy as np
import math
import os
import timeit
import time
import glob
import threading
import astropy
import ConfigParser
import sys
from astropy.io import fits

class Measurement:
	
	#Constructor
	def __init__(self, fftSize, samp_rate, measureTime, gain, c_freq, config, user, window):
		
		self.user = user
		self.fftSize = int(fftSize)
		self.samp_rate = float(samp_rate)
		self.bandwidth = self.samp_rate
		self.measureTime = int(measureTime)
		self.gain = int(gain)
		self.c_freq = float(c_freq)
		self.index = ''
		self.config = config
		self.configfil = "/home/" + self.user + "/GNURadio-FFTS/FFTS.config"
		self.loops = 1
		self.switched = 1
		self.measureTimeTotPow = 5
		self.adjust = 0
		self.window = window
		
		#Initate GnuRadio flowgraph
		self.receiver = Receiver(self.fftSize, self.samp_rate, self.gain, self.c_freq)
		self.receiver.blks2_selector_0.set_output_index(1)
		self.receiver.blks2_selector_1.set_output_index(1)
		#Creates usrp object from receiver
		self.usrp = self.receiver.uhd_usrp_source_0
		self.receiver.start()
		######### GPIO INIT #########
		#############################
		num_bits = 11
		mask = (1 << num_bits) - 1
		#########   Initiate SR and DV pin   ##############
		#Defines whether this pin is controlled automatically by FPGA,1, or manual,0
		self.usrp.set_gpio_attr("FP0", "CTRL", 0x0, mask)
		#Defines whether this pin is an output(1) or input(0)
		self.usrp.set_gpio_attr("FP0", "DDR", 0x0, mask)
		
	def set_loops(self, loops):
		self.loops = loops
		
	#Set optimal gain to utilize full dynamic range of ADC
	def meas_adjust(self, channel):
		histData = []
		print "Adjusting gain"
		self.config.set('CTRL','state','adjusting')
		with open(self.configfil, 'wb') as configfile:
			self.config.write(configfile)
		timedat = 1 #Read samples for 1 second on current gain
		gain = 5 #Gain start value
		self.set_gain(gain, channel)
		while gain < 31 and gain != -1:
			print gain
			L = []
			L1 = []
			L2 = []
			end = time.time() + timedat
			while time.time() <= end:
				time.sleep(10 / (self.samp_rate))
				if channel == 0:
					L.append(self.receiver.get_probe_var())
				else:
					L.append(self.receiver.get_probe_var_1())
			for i in L:
				if i > 0.5:
					L1.append(i)
				else:
					L2.append(i)
			hundra = len(L)
			print (len(L1)/float(hundra))
			if (len(L1)/float(hundra)) < 0.05: #As long as the samples above the value 0.5 are under 5% of all collected samples continue to increase gain
				gain += 1
				self.set_gain(gain, channel)
				print "Set gain on channel" + str(channel) +": "
				print self.usrp.get_gain(channel)
				del L, L1, L2
			elif gain == 30:
				histData = L
				i = -1
				break
			else:
				histData = L
				i = -1
				del L, L1, L2
				break
		print "Final gain channel " + str(channel) +": "
		print self.usrp.get_gain(channel)
		self.config.set('USRP','gain_ch'+str(channel), str(self.usrp.get_gain(channel)))
		self.config.set('CTRL','state','ready')
		with open(self.configfil, 'wb') as configfile:
			self.config.write(configfile)
		np.save('/home/' + self.user + '/Documents/sampleDist_ch' + str(channel) + '.npy', histData)
		
	#Start measurement
	def measure_start(self):
		if self.adjust == 1: #Adjust gain?
			self.meas_adjust(0)
			self.meas_adjust(1)
		else:
			self.date = ephem.now().tuple() #Date for FITS-file
			self.sig_time = 0
			self.ref_time = 0
			self.totpowTime = 0
			self.config.set('CTRL','abort','0')
			self.config.set('CTRL','state','integrating')
			with open(self.configfil, 'wb') as configfile:
				self.config.write(configfile)
			index = 0
			start = time.time()
			while index < self.loops:
				self.set_index(index)
				if self.switched == 1 and int(self.config.get('CTRL','abort')) != 1:
					self.measure_switch_in()
				elif self.switched != 1 and int(self.config.get('CTRL','abort')) != 1:
					self.measure_tot_pow()
					self.counter = 0
					self.sigCount = 0
					self.refCount = 0
				if int(self.config.get('CTRL','abort')) != 1:
					tc = Analyze(self.sigCount, self.refCount, index, self.fftSize, self.c_freq, self.samp_rate, self.switched, self.user)
				index += 1
			stop = time.time()
			print "Total time: "
			print stop - start
			edit = 0
			if int(self.config.get('CTRL','abort')) != 1:
				td = Finalize(index, self.fftSize, self.c_freq, self.samp_rate, edit, self.sig_time, self.ref_time, self.switched, self.totpowTime, self.user, self.date)
			files = glob.glob('/tmp/ramdisk/*')
			for f in files:
				if f.endswith(self.index):
					os.remove(f)
				else:
					continue
			self.config.set('CTRL','state','ready')
			with open(self.configfil, 'wb') as configfile:
				self.config.write(configfile)
				
	def measure_tot_pow(self):
		try:
			os.remove('/tmp/ramdisk/dump1')
			os.remove('/tmp/ramdisk/dump2')
			os.remove('/tmp/ramdisk/dump3')
			os.remove('/tmp/ramdisk/dump4')
		except OSError:
			pass
		
		self.date = ephem.now().tuple()
		self.receiver.signal_file_sink_1.open("/tmp/ramdisk/totPow0" + self.index)
		self.receiver.signal_file_sink_3.open("/tmp/ramdisk/totPow1" + self.index)

		print self.measureTimeTotPow
		t_end = time.time() + self.measureTimeTotPow
		start = time.time()
		self.receiver.blks2_selector_0.set_output_index(1) #Stream to signal sink
		self.receiver.blks2_selector_1.set_output_index(1)
		while time.time() <= t_end:
			if int(self.config.get('CTRL','abort')) == 1:
				break
		self.receiver.signal_file_sink_1.close()
		self.receiver.signal_file_sink_3.close()
		end = time.time()
		self.totpowTime += end-start
		
	#Measure and collect FFT files, Dicke-switched
	def measure_switch_in(self):
		#If dumpfile exists remove it
		try:
			os.remove('/tmp/ramdisk/dump1')
			os.remove('/tmp/ramdisk/dump2')
			os.remove('/tmp/ramdisk/dump3')
			os.remove('/tmp/ramdisk/dump4')
		except OSError:
			pass
		#SR pin logic, observe that pin logic might vary with with FPGA image
		S = int('00011',2) 
		R = int('00010',2)
		#DV pin logic
		SN = int('00001',2)
		RN = int('00000',2)
		self.sigCount = 0
		self.refCount = 0
		countTwo = 0
		while countTwo == 0:
			if self.usrp.get_gpio_attr("FP0", "READBACK") == S: #Stream to sig sink if datavalid = 1 and SR = 1
				countTwo = 1
				t_end = time.time() + self.measureTime
				while time.time() <= t_end:
					if int(self.config.get('CTRL','abort')) == 1:
						break
					elif self.usrp.get_gpio_attr("FP0", "READBACK") == S:
						time.sleep(2e-3) #Blanking for GnuRadio delay
						start1 = time.time()
						self.receiver.signal_file_sink_1.open("/tmp/ramdisk/sig0_" + str(self.sigCount) + self.index)
						self.receiver.signal_file_sink_3.open("/tmp/ramdisk/sig1_" + str(self.sigCount) + self.index)
						while self.usrp.get_gpio_attr("FP0", "READBACK") == S and int(self.config.get('CTRL','abort')) != 1 and time.time() <= t_end: #File sink closes if Datavalid = 0
							continue
						self.receiver.signal_file_sink_1.close()
						self.receiver.signal_file_sink_3.close()
						stop1 = time.time()
						self.sig_time += stop1-start1
						print 'sig'
						self.sigCount += 1
						while self.usrp.get_gpio_attr("FP0", "READBACK") == SN or self.usrp.get_gpio_attr("FP0", "READBACK") == RN:
							continue
					elif self.usrp.get_gpio_attr("FP0", "READBACK") == R:
						time.sleep(2e-3)
						start2 = time.time()
						self.receiver.signal_file_sink_1.open("/tmp/ramdisk/ref0_" + str(self.refCount) + self.index)
						self.receiver.signal_file_sink_3.open("/tmp/ramdisk/ref1_" + str(self.refCount) + self.index)
						while self.usrp.get_gpio_attr("FP0", "READBACK") == R and int(self.config.get('CTRL','abort')) != 1: #Close file sink datavalid = 0
							continue
						self.receiver.signal_file_sink_1.close()
						self.receiver.signal_file_sink_3.close()
						stop2 = time.time()
						self.ref_time += stop2-start2
						print 'ref'
						self.refCount += 1
						while self.usrp.get_gpio_attr("FP0", "READBACK") == RN or self.usrp.get_gpio_attr("FP0", "READBACK") == SN:
							continue
					else:
						break

	#Set integration time
	def set_int_time(self, int_time):
		self.measureTime = int(int_time)
		
	def set_adjust(self, adjust):
		self.adjust = int(adjust)
		
	def set_switched(self, switched):
		self.switched = int(switched)
		
	def set_time_totPow(self, totPowTime):
		self.measureTimeTotPow = int(totPowTime)
		
	#Set USRP gain
	def set_gain(self, gain, channel):
		self.gain = int(gain)
		self.usrp.set_gain(self.gain, channel)
		
	#Set the number of FFT channels
	def set_channels(self, channels):
		self.fftSize = int(channels)
		
	#Set USRP center frequency
	def set_c_freq(self, c_freq):
		self.c_freq = float(c_freq)*1e6
		self.usrp.set_center_freq(self.c_freq, 0)
		self.usrp.set_center_freq(self.c_freq, 1)
		
	#Set the sampling frequency equivalent to bandwidth since I/Q samples, however aliasing might occur for high/low freq
	def set_samp_rate(self, samp_rate):
		self.samp_rate = float(samp_rate)*1e6
		self.usrp.set_samp_rate(self.samp_rate)
		self.usrp.set_bandwidth(self.samp_rate, 0)
		self.usrp.set_bandwidth(self.samp_rate, 1)
		
	def set_index(self, count):
		self.index = str(count)

