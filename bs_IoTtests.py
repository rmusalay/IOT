from pydantic import root_validator, ValidationError
import pytest
import yaml
import argparse
import requests
from pydantic import BaseModel, Field
from typing import Optional
import logging

from final_iot import IOTmodel

# Parameterized sensor test data and expected error messages
@pytest.mark.parametrize(
    "data, error",
    [
        (
            {
                "action": "report",
                "sensor_serial": "C81C1AF7",
                "event": "trigger",
                "data": {"limit": "low", "temperature": 19.8},
                "sensor_type": "humidity",
            },
            "sensor type is unknown",
        ),
        (
            {
                "action": "report",
                "sensor_serial": "C81C1AF7",
                "event": "trigger",
                "data": {"limit": "low", "temperature": "ab"},
                "sensor_type": "freeze",
            },
            "unsupported operand type(s)",
        ),
        (
            {"action": "report", "sensor_serial": "8DD9BF4B", "sensor_type": "water"},
            "event must be trigger",
        ),
        (
            {
                "action": "report",
                "sensor_serial": "0DCB5A3B",
                "event": "high",
                "sensor_type": "entry",
            },
            "event must be open or close",
        ),
        (
            {
                "action": "report",
                "sensor_serial": "ABF93182",
                "event": "trigger",
                "sensor_type": "key_fob",
            },
            "event must be off, home or away",
        ),
        (
            {
                "action": "report",
                "sensor_serial": "05FBBF75",
                "event": "high",
                "sensor_type": "water",
            },
            "event must be trigger",
        ),
        (
            {
                "action": "report",
                "sensor_serial": "167756ED",
                "event": "low",
                "sensor_type": "panic",
            },
            "event must be trigger",
        ),
        (
            {
                "action": "report",
                "sensor_serial": "E0DECC5C",
                "event": "trigger",
                "data": {"limit": "heat", "temperature": 14.3},
                "sensor_type": "freeze",
            },
            "limit must be high or low",
        ),
        (
            {
                "action": "report",
                "sensor_serial": "E0DECC5C",
                "event": "trigger",
                "data": {"limit": "low"},
                "sensor_type": "freeze",
            },
            "temperature is needed in data",
        ),
        (
            {
                "action": "report",
                "sensor_serial": "EF69F697",
                "event": "triggered",
                "sensor_type": "glassbreak",
            },
            "event must be detected",
        ),
        (
            {
                "action": "report",
                "sensor_serial": "ABFD3182",
                "event": "trigger",
                "data": {"condition": "old"},
                "sensor_type": "smoke",
            },
            "condition must be of type heat, cold or smoke",
        ),
        (
            {
                "action": "report",
                "sensor_serial": "EF69F697",
                "event": "triggered",
                "sensor_type": "glassbreak",
            },
            "event must be detected",
        ),
    ],
)
# pytest driver function to test the parametized data and assert it with the expected error messages
def test_report_data(data, error):
    with pytest.raises(ValidationError) as errinfo:
        IOTmodel(**data)
    logging.error(str(errinfo.value))
    assert error in str(errinfo.value)
