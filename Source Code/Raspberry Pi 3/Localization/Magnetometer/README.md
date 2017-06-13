# Info magnetometer localization

## Scripts

### magneto_loc/checkNode.py
This script shows the received data by DASH7.

### magneto_loc/localization.py
This script executes the kNN-algorithm for localization and makes the data available for openHab.

### magneto_loc/mapping.py
This script can be used to fingerprint a room.

### magneto_loc/pymongoAmbient.py
This is just a test-script.

## How to use
The scrips have to be executed from this directory by following command:
```bash
$ PYTHONPATH=. python magneto_loc/scriptName.py
```
