from time import sleep
from picamera import PiCamera
import os

camera = PiCamera()
camera.resolution = (1024, 768)
camera.start_preview()
# Camera warm-up time
sleep(2)

counter = 0

while 1:
	# camera.capture('/etc/openhab2/html/pictures/picture' + str(counter) + '.jpg')
	camera.capture('/etc/openhab2/html/picture.jpg')
	counter = counter + 1
	sleep(3)
	# os.remove('/etc/openhab2/html/pictures/picture0.jpg')


