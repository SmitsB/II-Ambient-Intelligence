# Installation process for the Raspberry Pi 3

1) Install OpenHAB 2:
follow the instructions on the website: http://docs.openhab.org/installation/linux.html

2) Install MQTT:
We used Mosquitto

3) Install a MQTT Library:
Follow the instructions: https://eclipse.org/paho/clients/c/

4) Copy the files:
Copy our files to your machine, you'll need to change the path in some scripts to make them work. Make sure to check everything!

5) Setup cron
setup a cron task to start the camera script and the sensor script using the files from autoLaunch
(sensor script can be called every minute or started once, depending on your preferences)

```bash
@reboot sh /home/pi/autoLaunch/launchCameraScript.sh
@reboot sh /home/pi/autoLaunch/launchSensorScript.sh
*/1 * * * * /home/pi/autoLaunch/launchSensorScript.sh
```

6) Rebuild project:
Building the source again can be done using the command:
```C
gcc -o test test.c rpi_3_sensor_shield.h rpi_3_sensor_shield.c -l bcm2835 -lpython2.7 -lm -L/usr/lib/python2.7/confi -lpaho-mqtt3c
```