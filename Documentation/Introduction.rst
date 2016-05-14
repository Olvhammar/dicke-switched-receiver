Introduction
============

Software defined radio (SDR) was initially introduced by
J.Mitola in 1995 [1]. It can be described as a radio that
can change it’s physical equivalance through modifications
in software. Since the work of Mitola SDRs has
obtained a key role in the development of new radio systems
[2] which is in part motivated by the high flexibility
and cost effectiveness that a digital solution yields [3].
The main supplier for SDRs today is the Ettus Research
and National Instruments company (NI) providing the
Universal Software Radio Peripheral (USRP) as the SDR
product line [4]. The SDR platform essentially provides
a front-end for discretization of the signal as well as a
Digital Down Donverter (DDC) chain through the usage
of a Field-Programmable Gate Array (FPGA) [5]. The
strength and flexibility of the USRP is exposed when
combined with software interfaces such as GNU Radio
and NI-LabView, providing digital domain signal processing
[6].

Studies of microwave spectral emission from different
kinds of molecules is fundamental in the fields of Astronomy
and Aeronomy. Hydrogen is the most common
substance in the Universe thus making the transition at
21 cm of central interest to astronomers, e.g. for studies
of galactic spiral arms. Microwave radiation
is also abundant from different gases in the atmosphere,
both CO, O2, H2O and O3 exhibit rotational transitions
below 150 GHz thus providing a way to study the concentration
and distribution of these gases in the atmosphere
[7]. The technique most commonly used, for these kinds
of studies and observations is Dicke-switching, first introduced
by physicist Robert H. Dicke. Dicke-switching
is a method that eliminates gain variations in receiver systems
by rapidly comparing signals, often labelled signal
and reference. The reference can be a source of known
temperature, another part of the sky or by defining a reference
through mixer tuning. The techniques are referred
to as load, sky and frequency-switching respectively [8].

This documentation briefly explains how a general purpose Dicke-switched Fast Fourier Transform Spectrometer (FFTS) can be achieved using Software Defined Radio (SDR)
platforms, i.e. the Ettus USRP x310 interfaced with the signal processing toolkit GNU Radio. However the main function of this documentation
is to act as a informational source and usage manual for employees at Onsala Space Observatory (OSO) using the two GNURadio-FFTSs on the site.
For that purpose it is mainly the section "Manual" and "USRP and GNURadio" that is relevant.

Acknowledgements
----------------
First of all I would like to thank Gunnar Elgered for making this project possible.
I would also like to thank Lars Petersson and Peter Forkman for supervising the project and providing me with wonderful insights and supporting me at all times.
The SALSA system has been a inspirational source throughout this project and I have Eskil Varenius to thank for that.
Mikael Lerner has played a fundemental role in integrating the spectrometer in existing systems and it's now continous usage would not have happend without him.
The spectrometer is fully integrated in his software package BIFROST, providing a truly great interface for Radiometers in
Sweden and around the world.

Personal background
-------------------
I am a bachelor student at Chalmers University of Technology in Sweden and have been, part time, developing a new spectrometer
solution for Radio Astronomy and Aeronomy. I am currently pursuing a degree in Master of Wireless and Space Engineering and eventually a Phd.
