#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <bcm2835.h>
#include <unistd.h>
#include <python2.7/Python.h>
#include "rpi_3_sensor_shield.h"
#include "MQTTClient.h"
#include <signal.h>
#define PIN RPI_GPIO_P1_15

#define ADDRESS     "tcp://localhost:1883"
#define CLIENTID    "gateway"
#define QOS         1
#define TIMEOUT     10000L

static volatile int keepRunning = 1;

void intHandler(int dummy) {
	keepRunning = 0;
}

void readAirQuality(uint16_t* CO21) {
	if(bcm2835_gpio_lev(PIN)==0){
		uint32_t data;
		uint16_t tVOC1;
		getData_CCS811(&data);
		parseResult_CCS811(&data,CO21,&tVOC1);
	}
}

void main() {

//	signal(SIGINT, intHandler);
//	signal(SIGTSTP, intHandler);

	bcm2835_init();
	bcm2835_i2c_setClockDivider(25000); //10kHz
	configure_CCS811(1);
	enableInterrupts_CCS811();
	bcm2835_gpio_fsel(PIN, BCM2835_GPIO_FSEL_INPT);
	sleep(1);
	int i;
	char str[80];
	uint16_t lastCO21;
	uint16_t CO21;
	double humidity;
	double temperatureSI;
	double temperatureMPL;
	double pressure;
	double altitude;

	Py_Initialize();
	PyObject* main_module = PyImport_AddModule("__main__");
	// Get the main module's dictionary
      	// and make a copy of it.
      	PyObject* main_dict = PyModule_GetDict(main_module);
      	PyObject* main_dict_copy = PyDict_Copy(main_dict);
	char pythonvar[80];

	MQTTClient client;
	MQTTClient_connectOptions conn_opts = MQTTClient_connectOptions_initializer;
	MQTTClient_message pubmsg = MQTTClient_message_initializer;
	MQTTClient_deliveryToken token;
	int rc;

//	while(keepRunning)
//	{
		MQTTClient_create(&client, ADDRESS, CLIENTID,
	        MQTTCLIENT_PERSISTENCE_NONE, NULL);
		conn_opts.keepAliveInterval = 20;
		conn_opts.cleansession = 1;

		if ((rc = MQTTClient_connect(client, &conn_opts)) != MQTTCLIENT_SUCCESS){
	        	printf("Failed to connect, return code %d\n", rc);
        		exit(-1);
    		}

		if(CO21 > 0 && CO21 < 8192){
			lastCO21 = CO21;
		}
		readAirQuality(&CO21);
		char buffer[50];
		char buffer2[50];
		char buffer3[50];

		if(CO21 > 0 && CO21 < 8192){
			sprintf(str, "%d", CO21);
			printf("CO2: %s\n",str);

			sprintf(pythonvar,"CO21=%ld",CO21);
      			PyRun_SimpleString(pythonvar);
//			snprintf(buffer,sizeof(buffer),"mosquitto_pub -d -t rpi/airquality -m  %s\n",str);
//			system(buffer);

			pubmsg.payload = str;
			pubmsg.payloadlen = strlen(str);
			pubmsg.qos = QOS;
			pubmsg.retained = 0;
			MQTTClient_publishMessage(client, "rpi/airquality", &pubmsg, &token);
			printf("Waiting for up to %d seconds for publication of %s\n"
		 		"on topic %s for client with ClientID: %s\n",
				(int)(TIMEOUT/1000), str, "rpi/airquality", CLIENTID);
			rc = MQTTClient_waitForCompletion(client, token, TIMEOUT);
			printf("Message with delivery token %d delivered\n", token);
		}else{
			sprintf(pythonvar,"CO21=%ld",lastCO21);
                        PyRun_SimpleString(pythonvar);

		}

		humidity = readHumidity();
		printf("hum: %f\n",humidity);
//              snprintf(buffer, sizeof(buffer), "mosquitto_pub -d -t rpi/humidity -m %f\n",humidity);
//		system(buffer);
		snprintf(str, 80, "%f", humidity);
                pubmsg.payload = str;
                pubmsg.payloadlen = strlen(str);
                pubmsg.qos = QOS;
                pubmsg.retained = 0;
                MQTTClient_publishMessage(client, "rpi/humidity", &pubmsg, &token);
                printf("Waiting for up to %d seconds for publication of %s\n"
	                "on topic %s for client with ClientID: %s\n",
        		(int)(TIMEOUT/1000), str, "rpi/humidity", CLIENTID);
                rc = MQTTClient_waitForCompletion(client, token, TIMEOUT);
                printf("Message with delivery token %d delivered\n", token);


		temperatureSI = readTemperatureSI();
		temperatureMPL = readTemperatureMPL();

		if(temperatureSI > 0 || temperatureMPL > 0){
			printf("tempSI %f\n",temperatureSI);
			printf("tempMPL %f\n", temperatureMPL);

			sprintf(pythonvar,"temp=%f",(temperatureSI+temperatureMPL)/2);
	              	PyRun_SimpleString(pythonvar);
//        		snprintf(buffer, sizeof(buffer), "mosquitto_pub -d -t rpi/temperature -m %f\n",(temperatureSI+temperatureMPL)/2);
//			system(buffer);
			snprintf(str, 80, "%f", (temperatureSI+temperatureMPL)/2);
        	        pubmsg.payload = str;
              		pubmsg.payloadlen = strlen(str);
             		pubmsg.qos = QOS;
                	pubmsg.retained = 0;
       	         	MQTTClient_publishMessage(client, "rpi/temperature", &pubmsg, &token);
    	            	printf("Waiting for up to %d seconds for publication of %s\n"
  	                	"on topic %s for client with ClientID: %s\n",
      	                	(int)(TIMEOUT/1000), str, "rpi/temperature", CLIENTID);
	                rc = MQTTClient_waitForCompletion(client, token, TIMEOUT);
	                printf("Message with delivery token %d delivered\n", token);
		}

		pressure = readPressure();
		printf("pressure %f\n", pressure);
//              snprintf(buffer3, sizeof(buffer3), "mosquitto_pub -d -t rpi/pressure -m %f\n",pressure);
//              system(buffer3);
		snprintf(str, 80, "%f", pressure);
                pubmsg.payload = str;
                pubmsg.payloadlen = strlen(str);
                pubmsg.qos = QOS;
                pubmsg.retained = 0;
                MQTTClient_publishMessage(client, "rpi/pressure", &pubmsg, &token);
                printf("Waiting for up to %d seconds for publication of %s\n"
                        "on topic %s for client with ClientID: %s\n",
                        (int)(TIMEOUT/1000), str, "rpi/pressure", CLIENTID);
                rc = MQTTClient_waitForCompletion(client, token, TIMEOUT);
                printf("Message with delivery token %d delivered\n", token);


		MQTTClient_disconnect(client, 10000);
		MQTTClient_destroy(&client);
//		return rc;

		FILE* file_1 = fopen("showVal.py", "r");
	        PyRun_File(file_1, "sudo showVal.py", Py_file_input, main_dict, main_dict);
		fclose(file_1);

//	}
//	FILE* file_2 = fopen("stopcolors.py","r");
//	PyRun_File(file_2, "sudo stopcolors.py", Py_file_input, main_dict, main_dict);
}
