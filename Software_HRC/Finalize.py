#!/usr/bin/env python2
##################################################
# Finalize spectrums
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
import sys
from astropy.io import fits
import shutil

class Finalize():
	def __init__(self, index, fftSize, c_freq, samp_rate, edit, sig_time, ref_time, switched, powTime, user, date):
		self.user = user
		self.index = index
		self.fftSize = fftSize
		self.c_freq = c_freq
		self.samp_rate = samp_rate
		self.bandwidth = samp_rate
		self.edit = edit
		self.sig_time = sig_time
		self.ref_time = ref_time
		self.obs_time = sig_time + ref_time
		self.switched = switched
		self.totPowTime = powTime
		self.date = date
		
		print "sigTime: "
		print self.sig_time
		print "refTime: "
		print self.ref_time
		
		if self.switched == 1:
			#Arrays to be filled
			self.SR_data_0 = np.zeros(fftSize, dtype = np.float32)
			self.SRR_data_0 = np.zeros(fftSize, dtype = np.float32)
			self.SIG_data_0 = np.zeros(fftSize, dtype = np.float32)
			self.REF_data_0 = np.zeros(fftSize, dtype = np.float32)
			
			self.SR_data_1 = np.zeros(fftSize, dtype = np.float32)
			self.SRR_data_1 = np.zeros(fftSize, dtype = np.float32)
			self.SIG_data_1 = np.zeros(fftSize, dtype = np.float32)
			self.REF_data_1 = np.zeros(fftSize, dtype = np.float32)
			
			#Perform final averaging channel 0
			for i in range(self.index):
				self.SR_data_0 += np.load('/home/' + self.user + '/Dokument/SR0_' + str(i) + '.npy')/float(self.index)
				self.SRR_data_0 += np.load('/home/' + self.user + '/Dokument/SRR0_' + str(i) + '.npy')/float(self.index)
				self.SIG_data_0 += np.load('/home/' + self.user + '/Dokument/SIG0_' + str(i) + '.npy')/float(self.index)
				self.REF_data_0 += np.load('/home/' + self.user + '/Dokument/REF0_' + str(i) + '.npy')/float(self.index)
				os.remove('/home/' + self.user + '/Dokument/SR0_' + str(i) + '.npy')
				os.remove('/home/' + self.user + '/Dokument/SRR0_' + str(i) + '.npy')
				os.remove('/home/' + self.user + '/Dokument/SIG0_' + str(i) + '.npy')
				os.remove('/home/' + self.user + '/Dokument/REF0_' + str(i) + '.npy')
			#Perform final averaging channel 1
			for i in range(self.index):
				self.SR_data_1 += np.load('/home/' + self.user + '/Dokument/SR1_' + str(i) + '.npy')/float(self.index)
				self.SRR_data_1 += np.load('/home/' + self.user + '/Dokument/SRR1_' + str(i) + '.npy')/float(self.index)
				self.SIG_data_1 += np.load('/home/' + self.user + '/Dokument/SIG1_' + str(i) + '.npy')/float(self.index)
				self.REF_data_1 += np.load('/home/' + self.user + '/Dokument/REF1_' + str(i) + '.npy')/float(self.index)
				os.remove('/home/' + self.user + '/Dokument/SR1_' + str(i) + '.npy')
				os.remove('/home/' + self.user + '/Dokument/SRR1_' + str(i) + '.npy')
				os.remove('/home/' + self.user + '/Dokument/SIG1_' + str(i) + '.npy')
				os.remove('/home/' + self.user + '/Dokument/REF1_' + str(i) + '.npy')
				
			#Creates fits files channel 0
			self.create_fits_file(self.SIG_data_0, "Signal_ch0", self.sig_time)
			self.create_fits_file(self.REF_data_0, "Reference_ch0", self.ref_time)
			self.create_fits_file(self.SRR_data_0, "SRR_ch0", self.obs_time)
			self.create_fits_file(self.SR_data_0, "SR_ch0", self.obs_time)
			
			#Creates fits files channel 1
			self.create_fits_file(self.SIG_data_1, "Signal_ch1", self.sig_time)
			self.create_fits_file(self.REF_data_1, "Reference_ch1", self.ref_time)
			self.create_fits_file(self.SRR_data_1, "SRR_ch1", self.obs_time)
			self.create_fits_file(self.SR_data_1, "SR_ch1", self.obs_time)
		
			#To make sure same data not read twice channel 0
			shutil.copy('/home/' + self.user + '/Dokument/Signal_ch0.fits', '/home/' + self.user + '/GNURadio-FFTS/Spectrums/Signal_ch0.fits')
			shutil.copy('/home/' + self.user + '/Dokument/Reference_ch0.fits', '/home/' + self.user + '/GNURadio-FFTS/Spectrums/Reference_ch0.fits')
			shutil.copy('/home/' + self.user + '/Dokument/SRR_ch0.fits', '/home/' + self.user + '/GNURadio-FFTS/Spectrums/SRR_ch0.fits')
			shutil.copy('/home/' + self.user + '/Dokument/SR_ch0.fits', '/home/' + self.user + '/GNURadio-FFTS/Spectrums/SR_ch0.fits')
			os.remove('/home/' + self.user + '/Dokument/Signal_ch0.fits')
			os.remove('/home/' + self.user + '/Dokument/Reference_ch0.fits')
			os.remove('/home/' + self.user + '/Dokument/SRR_ch0.fits')
			os.remove('/home/' + self.user + '/Dokument/SR_ch0.fits')
			
			#To make sure same data not read twice channel 1
			shutil.copy('/home/' + self.user + '/Dokument/Signal_ch1.fits', '/home/' + self.user + '/GNURadio-FFTS/Spectrums/Signal_ch1.fits')
			shutil.copy('/home/' + self.user + '/Dokument/Reference_ch1.fits', '/home/' + self.user + '/GNURadio-FFTS/Spectrums/Reference_ch1.fits')
			shutil.copy('/home/' + self.user + '/Dokument/SRR_ch1.fits', '/home/' + self.user + '/GNURadio-FFTS/Spectrums/SRR_ch1.fits')
			shutil.copy('/home/' + self.user + '/Dokument/SR_ch1.fits', '/home/' + self.user + '/GNURadio-FFTS/Spectrums/SR_ch1.fits')
			os.remove('/home/' + self.user + '/Dokument/Signal_ch1.fits')
			os.remove('/home/' + self.user + '/Dokument/Reference_ch1.fits')
			os.remove('/home/' + self.user + '/Dokument/SRR_ch1.fits')
			os.remove('/home/' + self.user + '/Dokument/SR_ch1.fits')
		
			print "Done\n"
		else:
			self.totPow0_data = np.zeros(self.fftSize, dtype = np.float32)
			self.totPow1_data = np.zeros(self.fftSize, dtype = np.float32)
			for i in range(self.index):
				self.totPow0_data += np.load('/home/' + self.user + '/Dokument/totPow0' +str(i)+ '.npy')/float(self.index)
				self.totPow1_data += np.load('/home/' + self.user + '/Dokument/totPow1' +str(i)+ '.npy')/float(self.index)
				os.remove('/home/' + self.user + '/Dokument/totPow0' +str(i)+'.npy')
				os.remove('/home/' + self.user + '/Dokument/totPow1' +str(i)+'.npy')

			self.create_fits_file(self.totPow0_data, "TotPow0", self.totPowTime)
			self.create_fits_file(self.totPow1_data, "TotPow1", self.totPowTime)
			
			shutil.copy('/home/' + self.user + '/Dokument/TotPow0.fits', '/home/' + self.user + '/GNURadio-FFTS/Spectrums/TotPow0.fits')
			os.remove('/home/' + self.user + '/Dokument/TotPow0.fits')
			
			shutil.copy('/home/' + self.user + '/Dokument/TotPow1.fits', '/home/' + self.user + '/GNURadio-FFTS/Spectrums/TotPow1.fits')
			os.remove('/home/' + self.user + '/Dokument/TotPow1.fits')
			
			print "Total Power Measurement Done \n"
				
	#Remove center spike, other RFI components can be inserted in known_RFI , not used
	#Reference https://github.com/varenius/salsa/blob/master/Control_program/spectrum.py
	def auto_edit_bad_data(self, spec):
		
		freq_res = self.bandwidth/float(self.fftSize) # Hz
		# List known RFI as center-frequency in MHz, and width in hz
		known_RFI = [self.c_freq, 0.05]

		RFI_freq = known_RFI[0]
		RFI_width = known_RFI[1]*1e6
		ch0_freq = self.c_freq - 0.5*self.bandwidth
		ind_low = int(np.floor((RFI_freq-0.5*RFI_width - ch0_freq)/freq_res))
		ind_high = int(np.ceil((RFI_freq+0.5*RFI_width - ch0_freq)/freq_res))
      
		margin = min(ind_high-ind_low, ind_low, self.fftSize-ind_high)
		RFI_part = spec[ind_low-margin:ind_high+margin]
		xdata = np.arange(len(RFI_part))
		weights = np.ones_like(RFI_part)
		weights[margin:-margin] = 0.0 # Ignore RFI when fitting
		pf = np.polyfit(xdata, RFI_part, deg=1, w=weights)
		interpdata = np.polyval(pf, xdata)
		spec[ind_low:ind_high] = interpdata[margin:-margin]

	def create_fits_file(self, spec_data, dataType, obs_time):
		hdu = fits.PrimaryHDU()
		hdu.data = spec_data

		#Header definitions http://heasarc.gsfc.nasa.gov/docs/fcg/standard_dict.html
		#hdu.header['BUNIT']  = 'K'
		#hdu.header['CTYPE1'] = 'Freq'
		hdu.header['CRPIX1'] = self.fftSize/float(2) #Reference pixel (center)
		hdu.header['CRVAL1'] = self.c_freq #Center, USRP, frequency
		hdu.header['CDELT1'] = self.samp_rate/(1*self.fftSize) #Channel width
		#hdu.header['CUNIT1'] = 'Hz'
		
		hdu.header['TELESCOP'] = 'GNURadio-FFTS'
		hdu.header['OBJECT'] = 'CO-O3'
		hdu.header['OBSERVER'] = 'Olvhammar'
		hdu.header['ORIGIN'] = 'Onsala Space Observatory, SWEDEN'
		
		year = str(self.date[0]); month=str(self.date[1]); day=str(self.date[2]); hour = str(self.date[3]); minute =str(self.date[4]); sec = str(round(self.date[5]))
		hdu.header['DATE-OBS'] = year.zfill(4) + '-' + month.zfill(2)+'-'+ day.zfill(2)
		hdu.header['UTC'] = hour.zfill(2)+':'+ minute.zfill(2) +':' + sec.zfill(4)
		hdu.header['OBSTIME'] = obs_time
	
		#Write to disk, clobber indicates that overwrite is true
		hdu.writeto('/home/' + self.user + '/Dokument/' + dataType +'.fits', clobber=True)
		print " saved to home folder"
			
	def calc_power(self, data):
		# Calculate total power
		channels = self.fftSize
		total_power = np.sum(data[0.2*channels:0.8*channels]) / (0.5*channels)
		print 10*math.log10(total_power*1000)
