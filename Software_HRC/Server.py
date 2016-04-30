#!/usr/bin/env python2
##################################################
# Socket Server for communication and controlling measurements
##################################################
import socket
import sys
import subprocess
import ConfigParser
import os
import ephem
from thread import *
from Measurement import *
from Analyze import *
from threading import Thread
from multiprocessing import Process
from Finalize import *
from PyQt4 import QtCore
#stackoverflow.com/questions/380870/python-single-instance-of-program
from tendo import singleton
me = singleton.SingleInstance() #Makes sure only one instance is running

#Change HOST to desired IP
HOST = 'localhost'
PORT = 8081
user = "olvhammar" #Define username
configfil = "/home/" + user + "/GNURadio-FFTS/FFTS.config"
config = ConfigParser.ConfigParser()
config.read(configfil)
buffSize = 8192

#Client commands
measure_start = 'meas:init'
conf_bandwidth = 'conf:usrp:bw'
conf_channels = 'conf:fft:channels'
conf_gain = 'conf:usrp:gain'
conf_c_freq = 'conf:usrp:cfreq'
conf_obs_time = 'conf:time:obs'
read_ref = 'meas:read:ref?'
read_sig = 'meas:read:sig?'
read_sig_ref_ref = 'meas:read:srr?'
read_sig_ref = 'meas:read:sr?'

#Create socket server and bind to local host and port
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
print 'Socket created'
try:
	s.bind((HOST, PORT))
except socket.error as msg:
	print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
	sys.exit()
print 'Socket bind complete'
#Start listening on socket
s.listen(1)
print 'Socket now listening'

#Default values
config.set('CTRL','state','ready') #Set FFTS state ready
with open(configfil, 'wb') as configfile:
	config.write(configfile)
fftSize = int(config.get('USRP','channels'))
samp_rate = float(config.get('USRP','bw'))*1e6
interval = 5	#Default interval for switched measurements
gain = float(config.get('USRP','gain'))
c_freq = float(config.get('USRP','cfreq'))*1e6
window = config.get('USRP', 'fft_window')
#Initialize USRP device
tb =  Measurement(fftSize, samp_rate, interval, gain, c_freq, config, user, window)

class Worker(Thread):
	def __init__(self):
		Thread.__init__(self)
	def run(self):
		#Start measurement
		tb.measure_start()
		#Reinit thread so it can be called several times (TODO: Find a better way)
		Thread.__init__(self)

thread = Worker()
thread.daemon = True

def clientthread(conn):
	while True:
		#Receiving from client
		data = conn.recv(buffSize)
		newdata = data.strip().lower()
		i = newdata.find(' ') #Command syntax:: command value
		if i == -1:
			command = newdata.strip().rstrip()
			value = -2
		else:
			command = newdata[:i].strip().rstrip()
			value = newdata[i:].strip().rstrip()
		#############Read data from server#################
		###################################################
		if command == read_sig:
			#Channel 0
			dat = open('/home/' + user + '/GNURadio-FFTS/Spectrums/Signal_ch0.fits')
			size = os.path.getsize('/home/' + user + '/GNURadio-FFTS/Spectrums/Signal_ch0.fits')
			digits = len(str(size))
			conn.sendall('#' + str(digits) + str(size) + dat.read() +'/n')
			#Channel 1
			dat1 = open('/home/' + user + '/GNURadio-FFTS/Spectrums/Signal_ch1.fits')
			size1 = os.path.getsize('/home/' + user + '/GNURadio-FFTS/Spectrums/Signal_ch1.fits')
			digits1 = len(str(size1))
			conn.sendall('#' + str(digits1) + str(size1) + dat1.read() +'/n') #Format According to SCPI definition for OSO-FFTS systems
		elif command == read_ref:
			#Channel 0
			dat = open('/home/' + user + '/GNURadio-FFTS/Spectrums/Reference_ch0.fits')
			size = os.path.getsize('/home/' + user + '/GNURadio-FFTS/Spectrums/Reference_ch0.fits')
			digits = len(str(size))
			conn.sendall('#' + str(digits) + str(size) + dat.read() +'/n')
			#Channel 1
			dat1 = open('/home/' + user + '/GNURadio-FFTS/Spectrums/Reference_ch1.fits')
			size1 = os.path.getsize('/home/' + user + '/GNURadio-FFTS/Spectrums/Reference_ch1.fits')
			digits1 = len(str(size1))
			conn.sendall('#' + str(digits1) + str(size1) + dat1.read() +'/n') #Format According to SCPI definition for OSO-FFTS systems
		elif command == read_sig_ref_ref or command == 'meas:read:srr':
			#Channel 0
			dat = open('/home/' + user + '/GNURadio-FFTS/Spectrums/SRR_ch0.fits')
			size = os.path.getsize('/home/' + user + '/GNURadio-FFTS/Spectrums/SRR_ch0.fits')
			digits = len(str(size))
			conn.sendall('#' + str(digits) + str(size) + dat.read() +'/n')
			#Channel 1
			dat1 = open('/home/' + user + '/GNURadio-FFTS/Spectrums/SRR_ch1.fits')
			size1 = os.path.getsize('/home/' + user + '/GNURadio-FFTS/Spectrums/SRR_ch1.fits')
			digits1 = len(str(size1))
			conn.sendall('#' + str(digits1) + str(size1) + dat1.read() +'/n') #Format According to SCPI definition for OSO-FFTS systems
		elif command == read_sig_ref:
			#Channel 0
			dat = open('/home/' + user + '/GNURadio-FFTS/Spectrums/SR_ch0.fits')
			size = os.path.getsize('/home/' + user + '/GNURadio-FFTS/Spectrums/SR_ch0.fits')
			digits = len(str(size))
			conn.sendall('#' + str(digits) + str(size) + dat.read() +'/n')
			#Channel 1
			dat1 = open('/home/' + user + '/GNURadio-FFTS/Spectrums/SR_ch1.fits')
			size1 = os.path.getsize('/home/' + user + '/GNURadio-FFTS/Spectrums/SR_ch1.fits')
			digits1 = len(str(size1))
			conn.sendall('#' + str(digits1) + str(size1) + dat1.read() +'/n') #Format According to SCPI definition for OSO-FFTS systems
		elif command == 'meas:read:hist?':
			#Channel 0
			dat = open('/home/' + user + '/Documents/sampleDist_ch0.npy')
			size = os.path.getsize('/home/' + user + '/Documents/sampleDist_ch0.npy')
			digits = len(str(size))
			conn.sendall('#' + str(digits) + str(size) + dat.read() +'/n')
			#Channel 1
			dat1 = open('/home/' + user + '/Documents/sampleDist_ch1.npy')
			size1 = os.path.getsize('/home/' + user + '/Documents/sampleDist_ch1.npy')
			digits1 = len(str(size1))
			conn.sendall('#' + str(digits1) + str(size1) + dat1.read() +'/n') #Format According to SCPI definition for OSO-FFTS systems
		elif command == 'meas:read:totpow?':
			#Channel 0
			dat = open('/home/' + user + '/GNURadio-FFTS/Spectrums/TotPow0.fits')
			size = os.path.getsize('/home/' + user + '/GNURadio-FFTS/Spectrums/TotPow0.fits')
			digits = len(str(size))
			conn.sendall('#' + str(digits) + str(size) + dat.read() +'/n')
			#Channel 1
			dat1 = open('/home/' + user + '/GNURadio-FFTS/Spectrums/TotPow1.fits')
			size1 = os.path.getsize('/home/' + user + '/GNURadio-FFTS/Spectrums/TotPow1.fits')
			digits1 = len(str(size1))
			conn.sendall('#' + str(digits1) + str(size1) + dat1.read() +'/n') #Format According to SCPI definition for OSO-FFTS systems
		#Start measurement
		elif command == measure_start:
			tb.set_adjust(0)
			if config.get('CTRL','state').strip() == 'ready':
				conn.send('OK - meas:init\n')
				thread.start()
			else:
				conn.send('ERROR State - integrating - meas:init ' + '\n')
			continue
		#Adjust gain
		elif command == 'meas:adjust':
			conn.send('OK - meas:adjust\n')
			tb.set_adjust(1)
			thread.start()
		#Set switched mode
		elif command == 'set:mode:switched':
			tb.set_switched(1)
			config.set('USRP','mode', 'Switched')
			with open(configfil, 'wb') as configfile:
				config.write(configfile)
			conn.send('OK - set:mode:switched ' + 'True\n')
		#Set total power mode
		elif command == 'set:mode:totpow':
			tb.set_switched(0)
			config.set('USRP','mode', 'TotalPow')
			with open(configfil, 'wb') as configfile:
				config.write(configfile)
			conn.send('OK - set:mode:totpow ' + 'True\n')
			
		#########Configuration commands###########
		##########################################
		
		elif command == conf_obs_time and value != -2:
			obs_time = int(value)
			if obs_time > 1000 and int(obs_time)%60 == 0:
				lp = 60
				tb.set_int_time(lp)
				tb.set_time_totPow(lp)
				loops = int(obs_time/(1*lp))
				tb.set_loops(loops)
				print "Number of loops"
				print loops
				config.set('CTRL','obs_time', str(int(obs_time)))
				with open(configfil, 'wb') as configfile:
					config.write(configfile)
				conn.send('OK - {0} {1}\n'.format(command, obs_time))
			elif obs_time <= 1000:
				tb.set_loops(1)
				tb.set_int_time(obs_time)
				tb.set_time_totPow(obs_time)
				config.set('CTRL','obs_time', str(int(obs_time)))
				with open(configfil, 'wb') as configfile:
					config.write(configfile)
				conn.send('OK - {0} {1}\n'.format(command, obs_time))
			else:
				conn.send('ERROR Bad integration time - conf:time:obs ' + str(obs_time) + '\n')
				
		elif command == conf_bandwidth and value != -2:
			samp_rate = value
			if int(samp_rate) <= 50:
				tb.set_samp_rate(samp_rate)
				config.set('USRP','bw', str(tb.usrp.get_samp_rate()*1e-6))
				with open(configfil, 'wb') as configfile:
					config.write(configfile)
				conn.send('OK - conf:usrp:bw ' + str(tb.usrp.get_samp_rate()*1e-6) + ' [MHz]\n')
			else:
				conn.send('ERROR Bad bandwidth - conf:usrp:bw ' + samp_rate + '\n')
		elif command == conf_channels and value != -2:
			channels = value
			if int(channels) == 8192 or int(channels) == 4096  or int(channels) == 2048 or int(channels) == 1024 or int(channels) == 512 or int(channels) == 256 or int(channels) == 128:
				tb.set_channels(channels)
				config.set('USRP','channels', channels)
				with open(configfil, 'wb') as configfile:
					config.write(configfile)
				conn.send('OK - conf:fft:channels ' + channels + '\n')
			else:
				conn.send('ERROR Bad number of channels - conf:fft:channels ' +channels + '\n')
		elif command == conf_c_freq and value != -2:
			c_freq = value
			if float(c_freq) >= 400 and float(c_freq) <= 4400: #Change value for UBX, specified are for SBX
				tb.set_c_freq(c_freq)
				config.set('USRP','cfreq', str(tb.usrp.get_center_freq(0)*1e-6))
				with open(configfil, 'wb') as configfile:
					config.write(configfile)
				conn.send('OK - conf:usrp:cfreq ' + str(tb.usrp.get_center_freq(0)*1e-6) + ' [MHz]\n')
			else:
				conn.send('ERROR Bad center frequency - conf:usrp:cfreq ' + c_freq + ' [MHz]\n')
		#Set manual gain
		elif command == 'conf:usrp:gain' and value != -2:
			gain = value
			tb.set_gain(gain)
			config.set('USRP','gain', gain)
			with open(configfil, 'wb') as configfile:
				config.write(configfile)
			conn.send('OK - conf:usrp:gain ' + str(tb.usrp.get_gain(0)))
			
		elif command == 'conf:fft:window':
			window = value
			if window == 'blackman-harris' or window == 'hanning' or window == 'rectangular':
				tb.receiver.select_window = value
				config.set('USRP','fft_window',value)
				with open(configfil, 'wb') as configfile:
					config.write(configfile)
				conn.send('OK - conf:fft:window ' + window + '\n')
			else:
				conn.send('ERROR Bad FFT Window - conf:fft:window ' + window + '\n')

		#Questions to server
		elif command == 'state?':
			state = config.get('CTRL','state').strip()
			conn.send(state + ' - state?\n')
		elif command == 'conf:usrp:bw?':
			bw = str(tb.usrp.get_samp_rate()*1e-6)
			conn.send(bw + ' [MHz]' + ' - conf:usrp:bw?\n')
		elif command == 'conf:usrp:gain?':
			gain = str(tb.usrp.get_gain(0))
			gain1 = str(tb.usrp.get_gain(1))
			conn.send('Ch0: ' + gain + ' [dB]' + 'Ch1: ' + gain1 + ' [dB]' + ' - conf:usrp:gain?\n')
		elif command == 'conf:usrp:cfreq?':
			c = str(tb.usrp.get_center_freq(0)*1e-6)
			conn.send(c + ' [MHz] - conf:usrp:cfreq?\n')
		elif command == 'conf:fft:channels?':
			channels = config.get('USRP', 'channels')
			conn.send(channels + ' - conf:fft:channels?\n')
		elif command == 'conf:time:obs?':
			i_time = config.get('CTRL', 'obs_time')
			conn.send(i_time + ' - conf:time:obs?\n')
			
		elif command == 'conf:fft:window?':
			window = config.get('USRP', 'fft_window')
			conn.send(window + ' - conf:fft:window?\n')
			
		## Read all settings ##
		elif command == 'read:settings?':
			conn.send("""
	GNURadio-FFTS state and config
	----------------------------------------
	State			| {state}
	Bandwidth		| {bandwidth} [MHz]
	Center frequency	| {cfreq} [MHz]
	Number of channels	| {channels} #
	Resolution		| {resolution} [kHz]
	Window			| {window}
	USRP Gain Ch0		| {gain} dB
	USRP Gain Ch1		| {gain1} dB
	Switch frequency	| {switch_freq} [Hz] (Approx CO-O3)
	Master clock rate	| {clock_rate} MHz
	I/Q rate		| {samp_rate} MHz
	Clock source		| {clock_source}
	Time source		| {time_source}
	Port			| {port}
	----------------------------------------
		""".format(
				state = config.get('CTRL','state').strip(),
				bandwidth = str(tb.usrp.get_samp_rate()*1e-6),
				cfreq = str(tb.usrp.get_center_freq(0)*1e-6),
				channels = tb.fftSize,
				resolution = str((tb.usrp.get_samp_rate()/tb.fftSize)*1e-3),
				window = 'Blackman-Harris',
				gain = str(tb.usrp.get_gain(0)),
				gain1 = str(tb.usrp.get_gain(1)),
				switch_freq = 1/float(1.1),
				clock_rate = tb.usrp.get_clock_rate(0)/1e6,
				samp_rate = str(tb.usrp.get_samp_rate()*1e-6),
				clock_source = tb.usrp.get_clock_source(0),
				time_source = tb.usrp.get_time_source(0),
				port = 8081,
			))

		#Aborting measurement
		elif command == 'meas:stop' or command == 'stop':
			conn.send('OK - meas:stop\n')
			config.set('CTRL','abort','1')
			with open(configfil, 'wb') as configfile:
				config.write(configfile)
			print 'Aborting measurement...'
		elif command == 'exit':
			break
		else:
			conn.send('ERROR invalid command\n')

	conn.close()
 
#now keep talking with the client
while 1:
    #wait to accept a connection - blocking call
	conn, addr = s.accept()
	print 'Connected with ' + addr[0] + ':' + str(addr[1])     
    #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
	start_new_thread(clientthread ,(conn,))
s.close()
