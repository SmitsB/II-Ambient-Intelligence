import sys
import time
from neopixel import *


# LED strip configuration:
LED_COUNT      = 12      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT = False # True to invert the signal (when using NPN transistor level shift)

if __name__ == '__main__':
	# Create NeoPixel object with appropriate configuration.
	strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
	# Intialize the library (must be called once before other functions).
	strip.begin()

#	print sys.argv[1]
	
	color = Color(0,0,0)

	if sys.argv[1] == "70069549":
		print "Abdil"
		color = Color(255,0,0)
	elif sys.argv[1] == "79938499":
		print "Mats"
		color = Color(0,255,0)
	elif sys.argv[1] == "67306243":
		print "Michiel"
		color = Color(0,0,255)
        elif sys.argv[1] == "68161552":
                print "Bernd"
                color = Color(0,255,255)
        elif sys.argv[1] == "78885811":
                print "Dennis"
                color = Color(255,0,255)

	for i in range(strip.numPixels()):
		strip.setPixelColor(i, color)
		strip.show()
                time.sleep(0.5)

	strip._cleanup()
