# IOT
SimpliSafe-CodeExercise



IOT BASE STATION 

This program simulates a real world IOT base station by reading the sensor data from a TestData.yaml file and then processing it before sending as HTTP web post requests for monitoring and logging purpose

USAGE
	Install the python dependencies by running pip -r install requirements.txt

	usage: bs_iot.py [-h] -env ENV -system_serial SYSTEM_SERIAL -password
                    PASSWORD [-script_path SCRIPT_PATH]
           
           To run the pytest unit test 
	Usage: pytest  bsIOT_test.py
         
To view the sensor-date in the request bin web console replace the BASE_URL in the script to your own url generated by requestbin. The publically shared request bin project does not show sensor data
	
IMPLEMENTATION

Below are the features implemented in the project using python.

Command line options:  
The python program takes input command line parameters from the user using the python argparse library. The program requires the user to input password, environment and serial number. The password is sent as a bearer token for authentication. The system environment needs to be set to either Production, QA or Staging. A serial number also needs to be set along with the environment. Both the environment and serial number is sent in the request bin request URL.


Script parsing: 
The program supports both automatic driving of sensor data from an external TestData.yaml file and also a command-line read-eval-print loop (REPL) mode that allows manual sending of sensor events. The TestData.yaml script needs to be provided from the command-line interface for automated sensor data parsing. When the script path is not provided the program enters in to REPL mode and accepts manual inputs for the sensor data from the user

I have used a third party python yaml parsing library called pyyaml to parse the sensor data from the TestData.yaml file.

Sensor data validation: After parsing the sensor data, we validate the data based on the sensor data rules defined in the problem statement before sending it as a json post data request. I have used a python library called Pydantic to validate the input data. Pydantic provides user-friendly validation errors when the input data fields are invalid.

API request :
The python requests library is used to make the API web requests. The sensor data is sent in the api request only if it passes the validation, if the validation fails we log the validation error. If the sensor data passes the validation, we look for the value of action in the sensor data. If the value of action is  “report”  sensor data is sent in the post request  in the json format. The post request URL is constructed using the cmd line input parameters in the format https://requestbin-fake-url/v1/basestation/{env}/{serial}/event. If the action in the sensor data is set to delay, the program just logs the time delay to indicate the time delay and proceeds further.


The post request can be viewed in the requestbin web console. The sensor data is sent in the body and the password is present the as a bearer token in the authentication header

TESTING

The base station python program was tested with different sets of input sensor data for the TestData.yml file. The validata_data function has the rules defined for the sensor data and it effectively validates the input sensor data before sending it as json for the requests.


To check if the validate_date function is working as expected, I have used a TestValidate.yaml file to drive the program with wrong sensor values to see if the correct validation errors are reported. Both assertion errors and value errors are reported

Example assertion errors

ERROR - Validation error for {'action': 'report', 'sensor_serial': '281D69C9', 'event': None, 'sensor_type': 'panic'}
Traceback (most recent call last):
  File "/Users/rakeshmusalay/Downloads/bsIOT.py", line 68, in report_data
    IOTmodel(**iot)
  File "pydantic/main.py", line 406, in pydantic.main.BaseModel.__init__
pydantic.error_wrappers.ValidationError: 1 validation error for IOTmodel
__root__
  event must be trigger (type=assertion_error)

ERROR - Validation error for {'action': 'report', 'sensor_serial': '0DCB5A3B', 'event': 'close1', 'sensor_type': 'entry'}
Traceback (most recent call last):
  File "pydantic/main.py", line 406, in pydantic.main.BaseModel.__init__
pydantic.error_wrappers.ValidationError: 1 validation error for IOTmodel
__root__
  event must be open or close (type=assertion_error)

	
 ERROR - Validation error for {'action': 'report', 'sensor_serial': 'EF69F697', 'event': 'detected', 'sensor_type': 'glass'}
Traceback (most recent call last):
  File "pydantic/main.py", line 406, in pydantic.main.BaseModel.__init__
pydantic.error_wrappers.ValidationError: 1 validation error for IOTmodel
__root__
  sensor type is unknown (type=value_error)

Pytest Unit Test

The BaseStation_IOT.py is written to validate the different validation errors by sending the sensor data with wrong info. The unit test uses a parameterized set of sensor data and passes it to the IOTModel class to assert the validation errors generated by the validate_data function. This is to make sure that we are sending the correct json data to the python post request.

