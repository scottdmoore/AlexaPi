# NeoPixel library strandtest example
# Author: Tony DiCola (tony@tonydicola.com)
#
# Direct port of the Arduino NeoPixel library strandtest example.  Showcases
# various animations on a strip of NeoPixels.
import time
import logging
import threading
import socket
from collections import deque
from neopixel import *


# LED strip configuration:
LED_COUNT      = 120      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)


# Define functions which animate LEDs in various ways.
def colorWipe(strip, color, wait_ms=50):
	"""Wipe color across display a pixel at a time."""
	for i in range(strip.numPixels()):
		strip.setPixelColor(i, color)
		strip.show()
		time.sleep(wait_ms/1000.0)

def theaterChase(strip, color, wait_ms=50, iterations=10):
	"""Movie theater light style chaser animation."""
	for j in range(iterations):
		for q in range(3):
			for i in range(0, strip.numPixels(), 3):
				strip.setPixelColor(i+q, color)
			strip.show()
			time.sleep(wait_ms/1000.0)
			for i in range(0, strip.numPixels(), 3):
				strip.setPixelColor(i+q, 0)

def wheel(pos):
	"""Generate rainbow colors across 0-255 positions."""
	if pos < 85:
		return Color(pos * 3, 255 - pos * 3, 0)
	elif pos < 170:
		pos -= 85
		return Color(255 - pos * 3, 0, pos * 3)
	else:
		pos -= 170
		return Color(0, pos * 3, 255 - pos * 3)

def rainbow(strip, wait_ms=20, iterations=1):
	"""Draw rainbow that fades across all pixels at once."""
	for j in range(256*iterations):
		for i in range(strip.numPixels()):
			strip.setPixelColor(i, wheel((i+j) & 255))
		strip.show()
		time.sleep(wait_ms/1000.0)

def rainbowCycle(strip, wait_ms=20, iterations=5):
	"""Draw rainbow that uniformly distributes itself across all pixels."""
	for j in range(256*iterations):
		for i in range(strip.numPixels()):
			strip.setPixelColor(i, wheel((int(i * 256 / strip.numPixels()) + j) & 255))
		strip.show()
		time.sleep(wait_ms/1000.0)

def theaterChaseRainbow(strip, wait_ms=50):
	"""Rainbow movie theater light style chaser animation."""
	for j in range(256):
		for q in range(3):
			for i in range(0, strip.numPixels(), 3):
				strip.setPixelColor(i+q, wheel((i+j) % 255))
			strip.show()
			time.sleep(wait_ms/1000.0)
			for i in range(0, strip.numPixels(), 3):
				strip.setPixelColor(i+q, 0)

def sunrise(strip, total_time, stop_event):
    """WOOO"""

    print "Starting sunrise over:"+ str(total_time) + " seconds"
    r = 0
    g = 0
    b = 0
    resolution = 255
    queue = deque()
    for m in range(strip.numPixels()/2):
    	queue.append({'r':0.0,'g':0.0,'b':0.0})
    for j in range(resolution):
            for i in range(strip.numPixels()/2):
                color = Color(int(queue[len(queue)-i-1]['g']),int(queue[len(queue)-i-1]['r']),int(queue[len(queue)-i-1]['b']))
                strip.setPixelColor(i, color) 
                strip.setPixelColor(strip.numPixels()-i-1, color)
            strip.show()
            divisor = resolution / 5.0
            rinc = 0
            ginc = 0
            binc = 0
            if j < divisor:
              rinc = (0.0 - 0)/ divisor
              ginc = (0.0 - 0)/ divisor
              binc = (50.0 - 0)/ divisor
            elif j < divisor *2:
              binc = 0.0
              ginc = 0.0
              rinc = ((50.0-0.0)/ divisor)
            elif j < divisor * 3:
              binc = 0.0
              rinc = (200.0 - 50.0) / divisor
              binc = (50.0 - 0) / divisor * -1
            elif j < divisor * 4:
              rinc = (200.0-200.0)/ divisor
              ginc = (200.0 - 0) / divisor
              binc = 0
            elif j < divisor * 5:
              rinc = 0.0
              ginc = (200.0 - 200) / divisor
              binc = (170.0 - 0) / divisor
            else:
              rinc = (200.0 - 180) / divisor * -1
              ginc = 0.0
              binc = 0.0
              
            newcolor = {}
            newcolor['r'] = queue[len(queue)-1]['r'] + rinc
            newcolor['g'] = queue[len(queue)-1]['g'] + ginc
            newcolor['b'] = queue[len(queue)-1]['b'] + binc
            queue.append(newcolor)
            queue.popleft()
            #logging.warning("R G B "+ str(newcolor))
            time.sleep(total_time * 1.0 / resolution)
            if stop_event.is_set():
                return


def doSunrise(total_time, stop_event):
	# Create NeoPixel object with appropriate configuration.
	strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
	# Intialize the library (must be called once before other functions).
	strip.begin()
        sunrise(strip, total_time, stop_event)

def doDarkness():
	# Create NeoPixel object with appropriate configuration.
	strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
	# Intialize the library (must be called once before other functions).
	strip.begin()
        colorWipe(strip, Color(0, 0, 0))  # Green wipe



# Main program logic follows:
if __name__ == '__main__':
	# Create NeoPixel object with appropriate configuration.
	strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
	# Intialize the library (must be called once before other functions).
	strip.begin()

	print ('Press Ctrl-C to quit.')
	# Color wipe animations.
	#colorWipe(strip, Color(255, 0, 0))  # Red wipe
	#colorWipe(strip, Color(0, 255, 0))  # Blue wipe
	#colorWipe(strip, Color(0, 0, 255))  # Green wipe
	# Theater chase animations.
	#theaterChase(strip, Color(127, 127, 127))  # White theater chase
	#theaterChase(strip, Color(127,   0,   0))  # Red theater chase
	#theaterChase(strip, Color(  0,   0, 127))  # Blue theater chase
	# Rainbow animations.
	#rainbow(strip)
	#rainbowCycle(strip)
	#theaterChaseRainbow(strip)
	#colorWipe(strip, Color(0, 0, 0))  # Green wipe
        t1_stop= threading.Event()
        UDP_IP="127.0.0.1"
        UDP_PORT=5005
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((UDP_IP, UDP_PORT))
        while True:
            data, addr = sock.recvfrom(1024)
            print "received message:", data
            command = data.split(':')[0]
            if command == "start":
                atime = int(data.split(':')[1])
                thread = threading.Thread(target = sunrise, args= (strip, atime, t1_stop))
                thread.start()
            elif command == "stop":
                print "Stopping"
                t1_stop.set()
                doDarkness()
        socket.close()
