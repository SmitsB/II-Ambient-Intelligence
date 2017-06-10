#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <bcm2835.h>
#include <linux/i2c-dev.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <fcntl.h>
#include <math.h>
#include "rpi_3_sensor_shield.h"
#define PIN RPI_GPIO_P1_15

double altitudeOffset = 60.3;

double readHumidity(void)
{
	// Create I2C bus
	int file;
	char *bus = "/dev/i2c-1";
	if((file = open(bus, O_RDWR)) < 0) 
	{
		printf("Failed to open the bus. \n");
		exit(1);
	}
	// Get I2C device, SI7021 I2C address is 0x40(64)
	ioctl(file, I2C_SLAVE, SI7021_ADDRESS);

	// Send humidity measurement command(0xF5)
	char config[1] = {0xF5};
	write(file, config, 1);
	sleep(1);

	// Read 2 bytes of humidity data
	// humidity msb, humidity lsb
	char data[2] = {0};
	if(read(file, data, 2) != 2)
	{
		printf("Error : Input/output Error \n");
	}
	else
	{
                short a = 0;
                a = (data[0]<<8) | (data[1]);

//		printf("raw: %s, %c \n",data[0], data[0]);
		// Convert the data
//		float humidity = (((data[0] * 256 + data[1]) * 125.0) / 65536.0) - 6;
		float humidity = ((a * 125.0) / 65536.0) - 6;

		return humidity;
	}
	return 0;
}

double readTemperatureSI(void) {
	// Create I2C bus
        int file;
        char *bus = "/dev/i2c-1";
        if((file = open(bus, O_RDWR)) < 0) 
        {
                printf("Failed to open the bus. \n");
                exit(1);
        }
        // Get I2C device, SI7021 I2C address is 0x40(64)
        ioctl(file, I2C_SLAVE, SI7021_ADDRESS);

	// Send temperature measurement command(0xF3)
	char config[1] = {0xF3};
	write(file, config, 1);
	sleep(1);

	// Read 2 bytes of temperature data
	// temp msb, temp lsb
	char data[2] = {0};
	if(read(file, data, 2) != 2)
	{
		printf("Error : Input/output Error \n");
	}
	else
	{
		// Convert the data
		float cTemp = (((data[0] * 256 + data[1]) * 175.72) / 65536.0) - 46.85 - 8.0;
		return cTemp;
	}
	return 0;
}

double readAltitude() {
	// Create I2C bus
        int file;
        char *bus = "/dev/i2c-1";
        if((file = open(bus, O_RDWR)) < 0)
        {
                printf("Failed to open the bus. \n");
                exit(1);
        }
        // Get I2C device, TSL2561 I2C address is 0x60(96)
        ioctl(file, I2C_SLAVE, MPL3115A2_ADDRESS);

        char config[2] = {0};
        char reg[1] = {0x00};

        // Select control register(0x26)
        // Active mode, OSR = 128, barometer mode(0x39)
        config[0] = MPL3115A2_CTRL_REG1;
        config[1] = 0x39;
        write(file, config, 2);
        sleep(1);

        // Read 4 bytes of data from register(0x00)
        // status, pres msb1, pres msb, pres lsb
        reg[0] = MPL3115A2_STATUS;
        write(file, reg, 1);
        char data[4] = {0};
        read(file, data, 4);

        // Convert the data to 20-bits
        int pres = ((data[1] * 65536) + (data[2] * 256 + (data[3] & 0xF0))) / 16;
        double pressure = (pres / 4.0) / 1000.0;
	printf("press: %f\n",pressure);
	double altitude = 44330.77 * (1-(pow((pressure/101.326),0.1902632))) + altitudeOffset;
        return altitude;
}
double readTemperatureMPL() {
	// Create I2C bus
        int file;
        char *bus = "/dev/i2c-1";
        if((file = open(bus, O_RDWR)) < 0) 
        {
                printf("Failed to open the bus. \n");
                exit(1);
        }
        // Get I2C device, TSL2561 I2C address is 0x60(96)
        ioctl(file, I2C_SLAVE, MPL3115A2_ADDRESS);

	// Select control register(0x26)
        // Active mode, OSR = 128, altimeter mode(0xB9)
        char config[2] = {0};
        config[0] = MPL3115A2_CTRL_REG1;
        config[1] = 0xB9;
        write(file, config, 2);
        // Select data configuration register(0x13)
        // Data ready event enabled for altitude, pressure, temperature(0x07)
        config[0] = MPL3115A2_PT_DATA_CFG;
        config[1] = 0x07;
        write(file, config, 2);
        // Select control register(0x26)
        // Active mode, OSR = 128, altimeter mode(0xB9)
        config[0] = MPL3115A2_CTRL_REG1;
        config[1] = 0xB9;
        write(file, config, 2);
        sleep(1);

	// Read 6 bytes of data from address 0x00(00)
        // status, tHeight msb1, tHeight msb, tHeight lsb, temp msb, temp lsb
        char reg[1] = {0x00};
        write(file, reg, 1);
        char data[6] = {0};
        if(read(file, data, 6) != 6)
        {
                printf("Error : Input/Output error \n");
                exit(1);
        }

        int temp = ((data[4] * 256) + (data[5] & 0xF0)) / 16;
        double cTemp = (temp / 16.0)-8.0;
	return cTemp;
}

double readPressure() {
	// Create I2C bus
        int file;
        char *bus = "/dev/i2c-1";
        if((file = open(bus, O_RDWR)) < 0)
        {
                printf("Failed to open the bus. \n");
                exit(1);
        }
        // Get I2C device, TSL2561 I2C address is 0x60(96)
        ioctl(file, I2C_SLAVE, MPL3115A2_ADDRESS);

        char config[2] = {0};
	char reg[1] = {0x00};

	// Select control register(0x26)
        // Active mode, OSR = 128, barometer mode(0x39)
        config[0] = MPL3115A2_CTRL_REG1;
        config[1] = 0x39;
        write(file, config, 2);
        sleep(1);

        // Read 4 bytes of data from register(0x00)
        // status, pres msb1, pres msb, pres lsb
        reg[0] = MPL3115A2_STATUS;
        write(file, reg, 1);
	char data[4] = {0};
        read(file, data, 4);

        // Convert the data to 20-bits
        int pres = ((data[1] * 65536) + (data[2] * 256 + (data[3] & 0xF0))) / 16;
        double pressure = (pres / 4.0) / 1000.0;
	return pressure;
}

void WRITE_REGISTER_CCS811(char pData[],uint8_t length)
{
	bcm2835_i2c_setSlaveAddress(CCS811_ADDR);
	bcm2835_i2c_write(pData, length);
	return;
}
void READ_REGISTER_CCS811(char buf[],char reg,uint8_t length)
{
	char regaddr = reg;
	bcm2835_i2c_setSlaveAddress(CCS811_ADDR);
	bcm2835_i2c_write(&regaddr, length);	//First write to indicate the register address
	bcm2835_i2c_read(buf, length);		//Then read data at address
	return;
}

void getData_CCS811(uint32_t *data)
{
	char buf[4];
	READ_REGISTER_CCS811(buf,CSS811_ALG_RESULT_DATA,4);
	uint32_t requiredData= buf[0]<<24 | buf[1]<<16|buf[2]<<8|buf[3];
	*data=requiredData;
	return;
}

void parseResult_CCS811(uint32_t *data,uint16_t *CO2,uint16_t *tVOC)
{
	  *CO2 = *data>>16;
	  *tVOC = *data;
}

void setMode_CCS811(uint8_t mode)
{
  if (mode > 4) mode = 4; //Error correction
  char setting[1];
  READ_REGISTER_CCS811(setting,CSS811_MEAS_MODE,1);
  setting[0] &= ~(0b00000111 << 4); //Clear DRIVE_MODE bits
  setting[0] |= (mode << 4); //Mask in mode
  char writeData[2]={CSS811_MEAS_MODE, setting[0]};
  WRITE_REGISTER_CCS811(writeData,2);
}

uint8_t configure_CCS811(uint8_t mode)
{
	uint8_t state=0;
	char hwID[1];
	READ_REGISTER_CCS811(hwID,CSS811_HW_ID,1);

	if (hwID[0] == 0x81)
	{
		char ready[1];
		READ_REGISTER_CCS811(ready,CSS811_STATUS,1);
		if(ready[0] & 1 << 4)
		{
			char data[1];
			data[0]=CSS811_APP_START;
			WRITE_REGISTER_CCS811(data,1);
			setMode_CCS811(mode);
			state=1;
		}
		else
		{
			state=0;
			getError_CCS811();
		}
	}
	else
	{
		state=0;
		getError_CCS811();
	}
	return state;
}
uint8_t getError_CCS811()
{
	char error[1];
	READ_REGISTER_CCS811(error,CSS811_ERROR_ID,1);

	if (error[0] & 1 << 5)
		return HEATER_SUPPLY;
	else if (error[0] & 1 << 4)
		return HEATER_FAULT;
	else if (error[0] & 1 << 3)
		return MAX_RESISTANCE;
	else if (error[0] & 1 << 2)
		return MEASMODE_INVALID;
	else if (error[0] & 1 << 1)
		return READ_REG_INVALID;
	else if (error[0] & 1 << 0)
		return WRITE_REG_INVALID;
	else
		return NO_ERROR;
}

uint8_t dataAvailable_CCS811()
{
	char value[1];
	READ_REGISTER_CCS811(value,CSS811_STATUS,1);

	if(value[0] & 1 << 3)
		return (1);
	else
		return 0;
}
uint8_t checkForError_CCS811()
{
	char value[1];
	READ_REGISTER_CCS811(value,CSS811_STATUS,1);
	return (value[0] & 1 << 0);
}
uint16_t getBaseline_CCS811()
{
	char baselineElements[2];
	uint16_t  baseline;
	READ_REGISTER_CCS811(baselineElements,CSS811_BASELINE,2);
	baseline= baselineElements[0]<<8|baselineElements[1];
	return baseline;
}

uint8_t appValid_CCS811()
{
	char value[1];
	READ_REGISTER_CCS811(value,CSS811_STATUS,1);
	return (value[0] & 1 << 4);
}

void enableInterrupts_CCS811()
{
	char setting[1];
	READ_REGISTER_CCS811(setting,CSS811_MEAS_MODE,1);
	setting[0] |= (1 << 3); //Set INTERRUPT bit
	char writeData[2]={CSS811_MEAS_MODE, setting[0]};
	WRITE_REGISTER_CCS811(writeData,2);
}

void disableInterrupts_CCS811()
{
	char setting[1];
	READ_REGISTER_CCS811(setting,CSS811_MEAS_MODE,1);
	setting[0] &= ~(1 << 3); //Clear INTERRUPT bit
	char writeData[2]={CSS811_MEAS_MODE, setting[0]};
	WRITE_REGISTER_CCS811(writeData,2);
}
