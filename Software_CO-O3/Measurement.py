#!/usr/bin/env python2
##################################################
# Control measurement class
##################################################
from Receiver import *
from Analyze import *
from Finalize import *
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
from astropy.io import fits

class Measurement:
	
	#Constructor
	def __init__(self, fftSize, samp_rate, measureTime, gain, c_freq, config, user):
		
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
		
		#Initate GnuRadio flowgraph
		self.receiver = Receiver(self.fftSize, self.samp_rate, self.gain, self.c_freq)
		
		#Creates usrp object from receiver
		self.usrp = self.receiver.uhd_usrp_source_0
		
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
	def meas_adjust(self):
		histData = []
		print "Adjusting gain"
		self.config.set('CTRL','state','adjusting')
		with open(self.configfil, 'wb') as configfile:
			self.config.write(configfile)
		self.receiver.start()
		timedat = 1 #Read samples for 1 second on current gain
		gain = 18 #Gain start value
		self.set_gain(gain)
		while gain < 31 and gain != -1:
			print gain
			L = []
			L1 = []
			L2 = []
			end = time.time() + timedat
			while time.time() <= end:
				time.sleep(10 / (self.samp_rate))
				L.append(self.receiver.get_probe_var())
			for i in L:
				if i > 0.5:
					L1.append(i)
				else:
					L2.append(i)
			hundra = len(L)
			print (len(L1)/float(hundra))
			if (len(L1)/float(hundra)) < 0.05: #As long as the samples above the value 0.5 are under 5% of all collected samples continue to increase gain
				gain += 1
				self.set_gain(gain)
				print self.usrp.get_gain(0)
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
		print "Final gain: "
		print self.usrp.get_gain(0)
		self.receiver.stop()
		self.receiver.wait()
		self.config.set('USRP','gain', str(self.usrp.get_gain(0)))
		self.config.set('CTRL','state','ready')
		with open(self.configfil, 'wb') as configfile:
			self.config.write(configfile)
		np.save('/home/' + user + '/Documents/sampleDist.npy', histData)
		
	#Start measurement
	def measure_start(self):
		if self.adjust == 1: #Adjust gain?
			self.meas_adjust()
		else:
			self.receiver.start() 
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
				if self.switched == 1:
					self.measure_switch_in()
				else:
					self.loops = 1
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
				td = Finalize(index, self.fftSize, self.c_freq, self.samp_rate, edit, self.sig_time, self.ref_time, self.switched, self.totpowTime, self.user)
			self.receiver.stop()
			self.receiver.wait()
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
		#If dumpfile exists remove it
		try:
			os.remove('/tmp/ramdisk/dump1')
			os.remove('/tmp/ramdisk/dump2')
		except OSError:
			pass
		
		self.receiver.lock()
		self.receiver.signal_file_sink_1.open("/tmp/ramdisk/totPow")
		self.receiver.unlock()
		print self.measureTimeTotPow
		t_end = time.time() + self.measureTimeTotPow
		start = time.time()
		while time.time() <= t_end:
			if int(self.config.get('CTRL','abort')) == 1:
				break
			self.receiver.blks2_selector_0.set_output_index(1) #Stream to signal sink
		end = time.time()
		self.totpowTime += end-start
		self.receiver.blks2_selector_0.set_output_index(0) #Null sink, shouldnt be necessary but just in case
		self.receiver.lock()
		self.receiver.signal_file_sink_1.close()
		self.receiver.unlock()
		
	#Measure and collect FFT files, Dicke-switched
	def measure_switch_in(self):
		#If dumpfile exists remove it
		try:
			os.remove('/tmp/ramdisk/dump1')
			os.remove('/tmp/ramdisk/dump2')
		except OSError:
			pass
				
		#SR pin logic, observe that pin logic might vary with with FPGA image
		S = int('00011',2)
		R = int('00010',2)
		#DV pin logic
		SN = int('00001',2)
		RN = int('00000',2)
		
		self.sigCount = 1
		self.refCount = 1
		#First sig/ref file sink
		self.receiver.lock()
		self.receiver.signal_file_sink_1.open("/tmp/ramdisk/sig0" + self.index)
		self.receiver.signal_file_sink_2.open("/tmp/ramdisk/ref0" + self.index)
		self.receiver.unlock()
		countTwo = 0
		while countTwo == 0:
			if self.usrp.get_gpio_attr("FP0", "READBACK", 0) == S: #Stream to sig sink if datavalid = 1 and SR = 1
				countTwo = 1
				t_end = time.time() + self.measureTime
				while time.time() <= t_end:
					if int(self.config.get('CTRL','abort')) == 1:
						break
					elif self.usrp.get_gpio_attr("FP0", "READBACK", 0) == S:
						time.sleep(1e-3) #Blanking for GnuRadio delay
						start1 = time.time()
						self.receiver.blks2_selector_0.set_output_index(1) #Stream to signal sink
						while self.usrp.get_gpio_attr("FP0", "READBACK", 0) == S: #File sink closes if Datavalid = 0
							continue
						stop1 = time.time()
						self.sig_time += stop1-start1
						print 'sig'
						self.receiver.blks2_selector_0.set_output_index(0) #Null sink, shouldnt be necessary but just in case
						self.receiver.lock()
						self.receiver.signal_file_sink_1.close()
						self.receiver.signal_file_sink_1.open("/tmp/ramdisk/sig" + str(self.sigCount) + self.index)
						self.receiver.unlock()
						self.sigCount += 1
						while self.usrp.get_gpio_attr("FP0", "READBACK", 0) == SN or self.usrp.get_gpio_attr("FP0", "READBACK") == RN:
							continue
					elif self.usrp.get_gpio_attr("FP0", "READBACK") == R:
						time.sleep(1e-3)
						start2 = time.time()
						self.receiver.blks2_selector_0.set_output_index(2) # Stream to reference sink
						while self.usrp.get_gpio_attr("FP0", "READBACK", 0) == R: #Close file sink datavalid = 0
							continue
						stop2 = time.time()
						self.ref_time += stop2-start2
						print 'ref'
						self.receiver.blks2_selector_0.set_output_index(0) #Null sink
						self.receiver.lock()
						self.receiver.signal_file_sink_2.close()
						self.receiver.signal_file_sink_2.open("/tmp/ramdisk/ref" + str(self.refCount) + self.index)
						self.receiver.unlock()
						self.refCount += 1
						while self.usrp.get_gpio_attr("FP0", "READBACK", 0) == RN or self.usrp.get_gpio_attr("FP0", "READBACK") == SN:
							continue

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
	def set_gain(self, gain):
		self.gain = int(gain)
		self.usrp.set_gain(self.gain)
		
	#Set the number of FFT channels
	def set_channels(self, channels):
		self.fftSize = int(channels)
		
	#Set USRP center frequency
	def set_c_freq(self, c_freq):
		self.c_freq = float(c_freq)*1e6
		self.usrp.set_center_freq(self.c_freq)
		
	#Set the sampling frequency equivalent to bandwidth since I/Q samples, however aliasing might occur for high/low freq
	def set_samp_rate(self, samp_rate):
		self.samp_rate = float(samp_rate)*1e6
		self.usrp.set_samp_rate(self.samp_rate)
	def set_index(self, count):
		self.index = str(count)

