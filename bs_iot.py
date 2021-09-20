from pydantic import root_validator, ValidationError
import pytest
import yaml
import argparse
import requests
from pydantic import BaseModel, Field
from typing import Optional
import logging
import time


class IOTmodel(BaseModel):
    action: str
    sensor_serial: Optional[str]
    event: Optional[str]
    sensor_type: Optional[str]
    data: Optional[dict]

    @root_validator
    def validate_data(cls, values):
        sensor_type, event, action, data = (
            values.get("sensor_type"),
            values.get("event"),
            values.get("action"),
            values.get("data"),
        )

        if sensor_type == "entry":
            assert event in ["open", "close"], "event must be open or close"
            assert data is None

        elif sensor_type == "motion":
            assert event == "motion_detected", "event must be motion_detected"
            assert data is None

        elif sensor_type == "glassbreak":
            assert event == "detected", "event must be detected"
            assert data is None

        elif sensor_type == "freeze":
            assert event == "trigger"
            assert "limit" in data, "limit is nedded in data"
            assert data["limit"] in ["high", "low"], "limit must be high or low"
            assert "temperature" in data, "temperature is needed in data"
            assert isinstance(
                data["temperature"] / 1.0, float
            ), "temperature should be a number"

        elif sensor_type == "water":
            assert event == "trigger", "event must be trigger"
            assert data is None

        elif sensor_type == "panic":
            assert event == "trigger", "event must be trigger"
            assert data is None

        elif sensor_type == "key_fob":
            assert event in ["off", "home", "away"], "event must be off, home or away"
            assert data is None

        elif sensor_type == "smoke":
            assert event == "trigger", "event must be trigger"
            assert "condition" in data, "data must have condition"
            assert data["condition"] in [
                "heat",
                "cold",
                "smole",
            ], "condition must be of type heat, cold or smoke"

        elif action == "delay":
            assert data is None
            assert sensor_type is None
            assert event is None
        else:
            raise ValueError("sensor type is unknown")

        return values


def report_data(iot, args):

    try:
        IOTmodel(**iot)
    except Exception as e:
        logger.error("Validation error for {data}".format(data=iot), exc_info=True)
        return

    base_url = "https://enrzbui2ev9f1t9.m.pipedream.net"
    base_path = "/v1/basestation/{env}/{serial}/event"

    bearer = "Bearer {password}".format(password=args.password)

    format_path = base_path.format(env=args.env, serial=args.system_serial)

    headers = {"Authorization": bearer}

    if iot["action"] == "delay":
        secs = sum(int(x) * 60 ** i for i, x in enumerate(reversed(iot["time"].split(':'))))
        time.sleep(secs)
        logger.info("Delay logged for {time} ".format(time=secs)
        
    else:
        try:
            response = requests.post(base_url + format_path, json=iot, headers=headers)
            logger.info(
                "Sensor data reported for sensor_serial {sensor_serial}".format(
                    sensor_serial=iot["sensor_serial"]
                )
            )
            if response.status_code != 200:
                logger.error("Error in reporting,bad status code ")
        except requests.exceptions.HTTPError as err:
            logger.error("Http error" + repr(err))
        except requests.exceptions.ConnectionError as errc:
            logger.error("Error Connecting to the API:" + repr(errc))
        except Exception as err:
            logger.error("Error while reporting data")


def parseargs():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-env", help="Specify Env like production, QA, staging", required=True
    )
    parser.add_argument("-system_serial", help="System Serial", required=True)
    parser.add_argument("-password", help="Bearer Password", required=True)
    parser.add_argument("-script_path", help="Script Path")
    args = parser.parse_args()
    return args


def main():

    args = parseargs()
    if args.script_path is None:
        logging.info("Entering Interactive shell")
        while True:
            packet = {}
            packet["action"] = input("Enter Action: ")

            if packet["action"] == "report":
                packet["sensor_serial"] = input("Enter Sensor Serial: ")
                packet["event"] = input("Enter Event: ")
                packet["sensor_type"] = input("Sensor Type: ")
                if packet["sensor_type"] == "freeze":
                    data = {}
                    data["limit"] = input("Enter Freeze limit: ")
                    data["temperature"] = float(input("Enter Temperature: "))
                    packet["data"] = data
                elif packet["sensor_type"] == "smoke":
                    data = {}
                    data["condition"] = input("Enter Condition: ")
                    packet["data"] = data

            else:
                logger.error("Invalid Action type: {}".format(packet["action"]))
                continue

            report_data(packet, args)

    with open(args.script_path, "r") as stream:
        try:
            datalist = yaml.safe_load(stream)
            for data in datalist:
                report_data(data, args)
        except yaml.YAMLError as exc:
            logger.exception(exc)


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=logging.INFO,
        handlers=[logging.FileHandler("debug.log"), logging.StreamHandler()],
    )

    logger = logging.getLogger(__name__)
    main()
