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
		self.fftSize = fftSize
		self.c_freq = c_freq
		self.samp_rate = samp_rate
		self.switched = switched
		self.error = 0
		if self.switched == 1:
			self.analyze()
		else:
			self.analyze_TotPow()

	#Analyze data
	def analyze(self):
		self.sigList = []
		self.refList = []

		for i in range(self.sigCount):
			item = "/tmp/ramdisk/sig" + str(i) + self.index
			self.sigList.append(item)
		for i in range(self.refCount):
			item = "/tmp/ramdisk/ref" + str(i) + self.index
			self.refList.append(item)
		
		#If first file to small (the loop sometimes enter at late switch state) remove it
		if os.path.getsize('/tmp/ramdisk/sig0' + self.index) == 0:
			self.sigList.remove('/tmp/ramdisk/sig0' + self.index)
			self.refList.remove('/tmp/ramdisk/ref0' + self.index)
		
		#Stack all the data
		self.sig_spec = self.stack_all_data(self.sigList)
		self.ref_spec = self.stack_all_data(self.refList)
		
		#Calculates mean value for all signal and reference data
		self.SIG_data = self.mean(self.sig_spec)
		self.REF_data = self.mean(self.ref_spec)
		
		#Performs (Signal-Reference)
		self.SRR_data = (self.SIG_data-self.REF_data)/(self.REF_data)
		self.SR_data = self.SIG_data - self.REF_data

		self.tex1 = '/home/' + self.user + '/Documents/SR' + self.index + '.npy'
		self.tex2 = '/home/' + self.user + '/Documents/SRR' + self.index + '.npy'
		self.tex3 = '/home/' + self.user + '/Documents/SIG' + self.index + '.npy'
		self.tex4 = '/home/' + self.user + '/Documents/REF' + self.index + '.npy'
		
		np.save(self.tex1, self.SR_data)
		np.save(self.tex2, self.SRR_data)
		np.save(self.tex3, self.SIG_data)
		np.save(self.tex4, self.REF_data)
		#Clear temporary files
		files = glob.glob('/tmp/ramdisk/*')
		for f in files:
			if f.endswith(self.index):
				os.remove(f)
			else:
				continue
				
	def analyze_TotPow(self):
		
		#Average totalpower spectrum
		self.totPow_spec_0 = self.stack_FFT_file("/tmp/ramdisk/totPow0")
		self.totPow_spec_1 = self.stack_FFT_file("/tmp/ramdisk/totPow1")
		self.tex_0 = '/home/' + self.user + '/Documents/totPow0' + '.npy'
		self.tex_1 = '/home/' + self.user + '/Documents/totPow1' + '.npy'
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
		return sum_spec/float(len(spectra))

		
		
		
		
		
		
		
		
		
		
        

