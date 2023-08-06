from dataclasses import dataclass
import json
import typing_extensions
import urllib3
from urllib3._collections import HTTPHeaderDict

from climify_api import api_client, exceptions
from datetime import date, datetime  # noqa: F401
import decimal  # noqa: F401
import functools  # noqa: F401
import io  # noqa: F401
import re  # noqa: F401
import typing  # noqa: F401
import typing_extensions  # noqa: F401
import uuid  # noqa: F401
from typing import List
from pydantic import parse_raw_as


from climify_api.apis.PathBase import PathBase  # noqa: F401

from climify_api.exceptions import ApiValueError, ClimifyApiException
from climify_api.api_client import ClimifyApiResponse, ClimifyApiResponseWithoutDeserialization

PATH = 'locations/{id}/change-temperature'

class SetLocationTemperatureById(PathBase):
    def set_location_temperature_by_id(
        self,
        location_id: int,
        device_EUI: str,
        temperature: float,
        stream: bool = False,
        timeout: typing.Optional[typing.Union[int, typing.Tuple]] = None,
        skip_deserialization: bool = False,
    ) -> ClimifyApiResponse[str]:
        """Sets the temperature of the smart thermostat in the provided location

        :param location_id: Location identifier
        :type location_id: int
        :param device_EUI: Identifier of smart thermostat
        :type device_EUI: str
        :param temperature: Temperature in Celsius
        :type temperature: float
        :param stream: Toggles streaming, defaults to False
        :type stream: bool, optional
        :param timeout: How long to wait for a request in seconds, defaults to None
        :type timeout: typing.Optional[typing.Union[int, typing.Tuple]], optional
        :param skip_deserialization: Toggles whether or not to skip deserialize of the byte response, defaults to False
        :type skip_deserialization: bool, optional

        :raises ApiValueError: Will be raised if invalid inputs are provided
        :raises ClimifyApiException: Will be raised if an error occurred while calling the API

        :return: A response with the status of the request
        :rtype: ClimifyApiResponse[str]
        """
        # Validate input
        if location_id is None:
            raise ApiValueError("Location id was given as None. A valid location id must be provided.")

        # Prepare body
        body = {
            "temperature": temperature,
            "devEUI": device_EUI
        }

        # Make rest request
        used_path = PATH.replace('{id}',str(location_id))

        headers = HTTPHeaderDict({'Content-Type':'application/json'})

        response = self.api_client.call_api(
            resource_path=used_path,
            method='POST',
            stream=stream,
            timeout=timeout,
            headers=headers,
            body=json.dumps(body)
        )

        if not 200 <= response.status <= 299:
            raise ClimifyApiException(
                status=response.status,
                reason=response.reason,
                api_response=response
            )
        
        if skip_deserialization:
            api_response = ClimifyApiResponseWithoutDeserialization(response=response)
        else:
            deserialized_body = response.data.decode()
            api_response = ClimifyApiResponse[str](
                response=response,
                body=deserialized_body,
                headers=response.headers
            )


        return api_response