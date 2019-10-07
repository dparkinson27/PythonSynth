import pyaudio
import time
import math
from itertools import count
import numpy as np
import sys
import wave
import struct
import argparse
from itertools import *
import random
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

on = True
C = 2
Cs = 3
D = 4
Ds = 17
E = 27
F = 22
Fs = 10
G = 9
Gs = 11
A = 0
As= 5
B = 6
octaveUp = 15
octaveDown = 24
arpeg = 13
bpmUp = 26
bpmDown = 14
volumeUp = 18
volumeDown = 23
volume = 0.5
tVolume = 0.5
bpm = 0.8
total = 0
past = 0
octaveTracker = 1
effect = 19
toneTracker = False

GPIO.setup(C, GPIO.IN)
GPIO.setup(Cs, GPIO.IN)
GPIO.setup(D, GPIO.IN)
GPIO.setup(Ds, GPIO.IN)
GPIO.setup(E, GPIO.IN)
GPIO.setup(F, GPIO.IN)
GPIO.setup(Fs, GPIO.IN)
GPIO.setup(G, GPIO.IN)
GPIO.setup(Gs, GPIO.IN)
GPIO.setup(A, GPIO.IN)
GPIO.setup(As, GPIO.IN)
GPIO.setup(B, GPIO.IN)
GPIO.setup(octaveUp, GPIO.IN)
GPIO.setup(octaveDown, GPIO.IN)
GPIO.setup(volumeUp, GPIO.IN)
GPIO.setup(volumeDown, GPIO.IN)
GPIO.setup(bpmUp, GPIO.IN)
GPIO.setup(bpmDown, GPIO.IN)
GPIO.setup(arpeg, GPIO.IN)
GPIO.setup(effect, GPIO.IN)

p = pyaudio.PyAudio()
#Creates a 32 float sine wave stored in an array
def sine_wave(frequency=440.0, framerate=48000, amplitude=0.5):
    period = int(framerate / frequency)
    if amplitude > 1.0: amplitude = 1.0
    if amplitude < 0.0: amplitude = 0.0
    lookup_table = [float(amplitude) * math.sin(2.0*math.pi*float(frequency)*(float(i%period)/float(framerate))) for i in xrange(period)]
    return (lookup_table[i%period] for i in count(0))

def square_func(t, amp):
    if(t < (amp / 2)):
	return 0
    if(t > (amp / 2)):
	return amp

def square_wave(frequency=440.0, framerate=48000, amplitude=0.5):
    period = int(framerate / frequency)
    if amplitude > 1.0: amplitude = 1.0
    if amplitude < 0.0: amplitude = 0.0
    lookup_table = [square_func(float(amplitude) * math.sin(2.0*math.pi*float(frequency)*(float(i%period)/float(framerate))), amplitude) for i in xrange(period)]
    return (lookup_table[i%period] for i in count(0))

def white_noise(amplitude=0.5):
    return (float(amplitude) * random.uniform(-1, 1) for _ in count(0))
#Creates a Note which stores a sine wave based off frequency parameter and an on/off state
class Note:
    def __init__(self, freq):
        self.frequency = freq
        self.on = False
	self.tone = False
        self.sine1 = sine_wave(self.frequency, 48000, volume)
    def turnOn(self):
        self.on = True
    def turnOff(self):
        self.on = False
    def octaveUp(self):
        self.frequency = 2 * self.frequency
        if(self.tone):
            self.sine1 = square_wave(self.frequency, 48000, volume)
        else:
            self.sine1 = sine_wave(self.frequency, 48000, volume)
    def octaveDown(self):
        self.frequency = self.frequency / 2
        if(self.tone):
            self.sine1 = square_wave(self.frequency, 48000, volume)
        else:
            self.sine1 = sine_wave(self.frequency, 48000, volume)
    def redeclare(self):
	if(self.tone):
	    self.sine1 = square_wave(self.frequency, 48000, volume)
        else:
	    self.sine1 = sine_wave(self.frequency, 48000, volume)
    def toneOn(self):
	self.tone = True
	self.sine1 = square_wave(self.frequency, 48000, volume)
    def toneOff(self):
	self.tone = False
        self.sine1 = sine_wave(self.frequency, 48000, volume)
#Creates a sine wave to be outputted by adding together the sine waves of turned on Notes
class Output:
    def __init__(self):
        self.outputs = [white_noise(0)]
        self.toBeAdded1 = []

    def callback(self, in_data, frame_count, time_info, status):
        wave = self.outputs[0]
        data = [wave.next()]
        for i in range(frame_count - 1):
            data.append(wave.next())
        ret_array =np.array(data).astype(np.float32).tostring()
        return (ret_array, pyaudio.paContinue)
    
    def computeOutput(self, scale):
        total = 0
        self.toBeAdded1 = []
        for x in range(len(scale)):
            if(scale[x].on):
                total = total + 1
		self.toBeAdded1.append(scale[x].sine1)
        if(total == 0):
            self.outputs = []
            self.outputs.append(white_noise(0))
        else:
            out1 = islice(izip((imap(sum, izip(*self.toBeAdded1)))), None)
            self.outputs = []
            self.outputs.append(out1)

    def computeArpeg(self, scale, index):
        self.outputs = []
	if(index > -1 and index < 12):
            self.outputs.append(scale[x].sine1)
	else:
	    self.outputs.append(white_noise(0))

#scale is an array of all twelve notes in synth scale
scale = [Note(130.81), Note(138.59), Note(146.83), Note(155.56), Note(164.81),
         Note(174.61), Note(185.00), Note(196.00), Note(207.65), Note(220.00),
         Note(233.08), Note(246.94)]

sound = Output()

stream = p.open(format=pyaudio.paFloat32,
                 channels=1,
                 rate=48000,
                 frames_per_buffer=4096,
                 output=True,
                 stream_callback=sound.callback)

#infinte loop where all user operations are performed
stream.start_stream()
while(on):
    #change becomes true if any GPIO state changes during current cycle. Resets at start of each loop
    #refreshs state of each note
    #C
    if GPIO.input(C) == 1 and total < 8:
        scale[0].turnOn()
    if GPIO.input(C) == 0:
        scale[0].turnOff()
    #Csharp
    if GPIO.input(Cs) == 1 and total < 8:
        scale[1].turnOn()
    if GPIO.input(Cs) == 0:
        scale[1].turnOff()
    #D
    if GPIO.input(D) == 1 and total < 8:
        scale[2].turnOn()
    if GPIO.input(D) == 0:
        scale[2].turnOff()
    #Dsharp
    if GPIO.input(Ds) == 1 and total < 8:
        scale[3].turnOn()
    if GPIO.input(Ds) == 0:
        scale[3].turnOff()
    #E
    if GPIO.input(E) == 1 and total < 8:
        scale[4].turnOn()
    if GPIO.input(E) == 0:
        scale[4].turnOff()
    #F
    if GPIO.input(F) == 1 and total < 8:
        scale[5].turnOn()
    if GPIO.input(F) == 0:
        scale[5].turnOff()
    #Fs
    if GPIO.input(Fs) == 1 and total < 8:
        scale[6].turnOn()
    if GPIO.input(Fs) == 0:
        scale[6].turnOff()
    #G
    if GPIO.input(G) == 1 and total < 8:
        scale[7].turnOn()
    if GPIO.input(G) == 0:
        scale[7].turnOff()
    #Gs
    if GPIO.input(Gs) == 1 and total < 8:
        scale[8].turnOn()
    if GPIO.input(Gs) == 0:
        scale[8].turnOff()
    #A
    if GPIO.input(A) == 1 and total < 8:
        scale[9].turnOn()
    if GPIO.input(A) == 0:
        scale[9].turnOff()
    #As
    if GPIO.input(As) == 1 and total < 8:
        scale[10].turnOn()
    if GPIO.input(As) == 0:
        scale[10].turnOff()
    #B
    if GPIO.input(B) == 1 and total < 8:
        scale[11].turnOn()
    if GPIO.input(B) == 0:
        scale[11].turnOff()
    #Octave Shifts
    if GPIO.input(octaveUp) == 1:
	if(octaveTracker < 7):
	    octaveTracker = octaveTracker + 1
            for x in range(len(scale)):
                scale[x].octaveUp()
    if GPIO.input(octaveDown) == 1:
	if(octaveTracker > 0):
	    octaveTracker = octaveTracker - 1
            for x in range(len(scale)):
                scale[x].octaveDown()
    #Bpm increase/decrease
    if GPIO.input(bpmDown) == 1:
        if bpm < 2:
            bpm = bpm + .1
    if GPIO.input(bpmUp) == 1:
        if bpm > .05:
            bpm = bpm - .1
    if GPIO.input(effect) == 1 and not(toneTracker):
        toneTracker = True
	for x in range(len(scale)):
	    scale[x].toneOn()
    if GPIO.input(effect) == 0 and toneTracker:
	toneTracker = False
	for x in range(len(scale)):
            scale[x].toneOff()
    #Continuous mode
    if(GPIO.input(arpeg) == 0):
	#Volume increase/decrease(calculates for chorus playing)
	if GPIO.input(volumeUp) == 1:
            if tVolume < 0.9:
                tVolume = tVolume + 0.1
                total = 0
                for x in range(len(scale)):
                    if(scale[x].on):
                        total = total + 1
                if(total > 0):
                    volume = float(tVolume / total)
                    for x in range(len(scale)):
                        scale[x].redeclare()
        if GPIO.input(volumeDown) == 1:
            if tVolume > 0:
                tVolume = tVolume - 0.1
                total = 0
                for x in range(len(scale)):
                    if(scale[x].on):
                        total = total + 1
                if(total > 0):
                    volume = float(tVolume / total)
                    for x in range(len(scale)):
                        scale[x].redeclare()
        total = 0
        for x in range(len(scale)):
            if(scale[x].on):
                total = total + 1
        if(total > 0 and past != total):
            volume = float(tVolume / total)
            for x in range(len(scale)):
                scale[x].redeclare()
        past = total
        #Computes output sine wave if any thing has changed       
        sound.computeOutput(scale)
        #pause
        time.sleep(.2)
    #arpegiator mode
    if GPIO.input(arpeg) == 1:
	total = 0
	past = 0
        for x in range(len(scale)):
	    #Volume increase/decrease(different for arpeg)
            if GPIO.input(volumeUp) == 1:
                if tVolume < 1:
                    tVolume = tVolume + 0.05
                    volume = tVolume
                    for y in range(len(scale)):
                        scale[y].redeclare()
            if GPIO.input(volumeDown) == 1:
                if tVolume > 0:
                    tVolume = tVolume - 0.05
                    volume = tVolume
                    for y in range(len(scale)):
                        scale[y].redeclare()
	    if GPIO.input(bpmDown) == 1:
                if bpm < 2:
                    bpm = bpm + .1
            if GPIO.input(bpmUp) == 1:
                if bpm > .05:
                    bpm = bpm - .1
	    if(scale[x].on):
		total = total + 1
		sound.computeArpeg(scale, x)
		time.sleep(bpm)
	if(total == 0):
	    sound.computeArpeg(scale, 100)
	    time.sleep(.2)
        if GPIO.input(volumeUp) == 1:
            if tVolume < 1:
                tVolume = tVolume + 0.1
                total = 0
                for x in range(len(scale)):
                    if(scale[x].on):
                        total = total + 1
                if(total > 0):
                    volume = float(tVolume / total)
                    for x in range(len(scale)):
                        scale[x].redeclare()

stream.close()

p.terminate()

