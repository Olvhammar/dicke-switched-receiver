#!/usr/bin/env python2
##################################################
# Analyze, stack and average spectrums
##################################################
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
from astropy.io import fits
from multiprocessing.pool import ThreadPool as Pool

class Analyze():
	def __init__(self, sigCount, refCount, index, fftSize, c_freq, samp_rate, switched, user):
		self.user = user
		self.sigCount = sigCount-1
		self.refCount = refCount-1 #Minus one since counter in Measurement.py increase after last spectrum
		self.index = str(index)
		self.index_count=int(index)
		self.fftSize = fftSize
		self.c_freq = c_freq
		self.samp_rate = samp_rate
		self.switched = switched
		self.error = 0
		if self.switched == 1:
			if self.sigCount == 0:
				print "test"
				self.analyze_TotPow()
			else:
				self.analyze()
		else:
			self.analyze_TotPow()

	#Analyze data
	def analyze(self):
		self.sigList0 = []
		self.refList0 = []
		
		self.sigList1 = []
		self.refList1 = []

		for i in range(self.sigCount):
			item1 = "/tmp/ramdisk/sig0_" + str(i) + self.index
			item2 = "/tmp/ramdisk/sig1_" + str(i) + self.index
			self.sigList0.append(item1)
			self.sigList1.append(item2)
			
		for i in range(self.refCount):
			item1 = "/tmp/ramdisk/ref0_" + str(i) + self.index
			item2 = "/tmp/ramdisk/ref1_" + str(i) + self.index
			self.refList0.append(item1)
			self.refList1.append(item2)
		
		#If first file to small (the loop sometimes enter at late switch state) remove it
		if os.path.getsize('/tmp/ramdisk/sig0_0' + self.index) == 0:
			self.sigList0.remove('/tmp/ramdisk/sig0_0' + self.index)
			self.refList0.remove('/tmp/ramdisk/ref0_0' + self.index)
			self.sigList1.remove('/tmp/ramdisk/sig1_0' + self.index)
			self.refList1.remove('/tmp/ramdisk/ref1_0' + self.index)
		
		#Stack all the data
		self.sig_spec_0 = self.stack_all_data(self.sigList0)
		self.ref_spec_0 = self.stack_all_data(self.refList0)
		
		self.sig_spec_1 = self.stack_all_data(self.sigList1)
		self.ref_spec_1 = self.stack_all_data(self.refList1)
		
		#Calculates mean value for all signal and reference data
		self.SIG_data_0 = self.mean(self.sig_spec_0)
		self.REF_data_0 = self.mean(self.ref_spec_0)
		self.SIG_data_1 = self.mean(self.sig_spec_1)
		self.REF_data_1 = self.mean(self.ref_spec_1)
		
		#Performs (Signal-Reference)
		self.SRR_data_0 = (self.SIG_data_0-self.REF_data_0)/(self.REF_data_0)
		self.SR_data_0 = self.SIG_data_0 - self.REF_data_0
		
		self.SRR_data_1 = (self.SIG_data_1-self.REF_data_1)/(self.REF_data_1)
		self.SR_data_1 = self.SIG_data_1 - self.REF_data_1

		self.tex1 = '/home/' + self.user + '/Documents/SR0_' + self.index + '.npy'
		self.tex2 = '/home/' + self.user + '/Documents/SRR0_' + self.index + '.npy'
		self.tex3 = '/home/' + self.user + '/Documents/SIG0_' + self.index + '.npy'
		self.tex4 = '/home/' + self.user + '/Documents/REF0_' + self.index + '.npy'
		
		self.tex5 = '/home/' + self.user + '/Documents/SR1_' + self.index + '.npy'
		self.tex6 = '/home/' + self.user + '/Documents/SRR1_' + self.index + '.npy'
		self.tex7 = '/home/' + self.user + '/Documents/SIG1_' + self.index + '.npy'
		self.tex8 = '/home/' + self.user + '/Documents/REF1_' + self.index + '.npy'
		
		np.save(self.tex1, self.SR_data_0)
		np.save(self.tex2, self.SRR_data_0)
		np.save(self.tex3, self.SIG_data_0)
		np.save(self.tex4, self.REF_data_0)
		
		np.save(self.tex5, self.SR_data_1)
		np.save(self.tex6, self.SRR_data_1)
		np.save(self.tex7, self.SIG_data_1)
		np.save(self.tex8, self.REF_data_1)
		#Clear temporary files
		files = glob.glob('/tmp/ramdisk/*')
		for f in files:
			if f.endswith(self.index):
				os.remove(f)
			else:
				continue
				
	def analyze_TotPow(self):
		
		#Average totalpower spectrum
		self.totPow_spec_0 = self.stack_FFT_file("/tmp/ramdisk/sig0_0"+self.index)
		self.totPow_spec_1 = self.stack_FFT_file("/tmp/ramdisk/sig1_0"+self.index)
		self.tex_0 = '/home/' + self.user + '/Documents/totPow0' +self.index+ '.npy'
		self.tex_1 = '/home/' + self.user + '/Documents/totPow1' +self.index+ '.npy'
		np.save(self.tex_0, self.totPow_spec_0)
		np.save(self.tex_1, self.totPow_spec_1)
		
		#Clear temporary files
		files = glob.glob('/tmp/ramdisk/*')
		for f in files:
			os.remove(f)
			
	#Stack all the data
	def stack_all_data(self, files):
		pool = Pool(processes=4)
		spectra = pool.map(self.stack_FFT_file, files)
		pool.terminate()
		return spectra
		
	#Function to stack the data from gnuradio
	#Reference https://github.com/varenius/salsa/tree/master/USRP/usrp_gnuradio_dev
	def stack_FFT_file(self, infile):
		signal = np.memmap(infile, mode = 'r', dtype = np.float32)
		num_spec = int(signal.size/self.fftSize) #The number of spectra contained in the file
		length = num_spec*self.fftSize 
		signal = signal[0:length] #Convert the array to an even number of spectras
		spec = signal.reshape((num_spec, self.fftSize)) #Reshape the array with FFT:s so it can be easily stacked
		spec = spec.sum(axis=0) #Stack the FFT:s
		spec = spec/(1.0*num_spec) #Average Spectrum
		del signal
		return spec

	#Meanvalue of stacked spectrums
	def mean(self, spectra):
		sum_spec = np.sum(spectra, axis=0, dtype = np.float32)
		try:
			return sum_spec/float(len(spectra))
		except RuntimeWarning:
			return 0
			

		
		
		
		
		
		
		
		
		
		
        

