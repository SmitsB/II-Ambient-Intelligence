import time
from neopixel import *


# LED strip configuration:
LED_COUNT      = 12      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 100     # Set to 0 for darkest and 255 for brightest
LED_INVERT = False # True to invert the signal (when using NPN transistor level shift)
#max = 8192
max =1400
min = 400
#tempMin = 0
#tempMax = 47
tempMin = 19.0
tempMax = 35.0 

if __name__ == '__main__':
        # Create NeoPixel object with appropriate configuration.
        strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
        # Intialize the library (must be called once before other functions).
        strip.begin()

	#nmax = max-min
        #nval = CO21-min
        #step = nmax/12
        #tmap = int(round(nval/step,0))

	#colorR = int(((temp-tempMin)/(tempMax-tempMin))*255)
	#colorB = int((1-((temp-tempMin)/(tempMax-tempMin)))*255)

	tempNewMax = tempMax-tempMin
        nTemp = temp-tempMin
        step = tempNewMax/12
	unrounded = nTemp/step
        tmap = int(round(unrounded,0))

        colorR = int(((CO21-min)/(max-min))*255)
        colorG = int((1-((CO21-min)/(max-min)))*255)
	
	if colorR > 255:
		colorR = 255
	if colorR < 0:
		colorR = 0
	if colorG > 255:
		colorG = 255
	if colorG < 0:
		colorG = 0

	for i in range(LED_COUNT):
                        if i <= tmap:
                                #strip.setPixelColor(i, Color(0,colorR,colorB))
				strip.setPixelColor(i, Color(colorG,colorR,0))
                        else:
				strip.setPixelColor(i,Color(0,0,0))
                        strip.show()
	strip._cleanup()
