from collections import defaultdict
from dataclasses import dataclass
import typing_extensions
import urllib3
from urllib3._collections import HTTPHeaderDict

from datetime import date, datetime, timedelta  # noqa: F401
from dateutil.relativedelta import relativedelta
import decimal  # noqa: F401
import functools  # noqa: F401
import io  # noqa: F401
import re  # noqa: F401
import typing  # noqa: F401
import typing_extensions  # noqa: F401
import uuid  # noqa: F401
from pandas import DataFrame, concat
from typing import List
from pydantic import parse_raw_as
from varname import nameof


from climify_api.apis.PathBase import PathBase  # noqa: F401

from climify_api.exceptions import ApiValueError, ClimifyApiException
from climify_api.api_client import ClimifyApiResponse, ClimifyApiResponseWithoutDeserialization
from climify_api.models import SensorDataExtDto

PATH = 'locations/{id}/sensor-values'

def convert_values_to_dataFrame(data: List[SensorDataExtDto]) -> DataFrame:
    """Converts the sensor values to pandas DataFrames inplace.

    :param data: List of sensor data DTOs with sensor data as list of Data models
    :type data: List[SensorDataExtDto]
    :return: The list of sensor data with the updated data values
    :rtype: DataFrame
    """
    if len(data) == 0:
        return data
    
    for sensor in data:
        variables = list(sensor.data[0].values.keys())
        columns = [nameof(sensor.data[0].time)] + variables
        values = [[row.time] + [row.values[col] for col in variables] for row in sensor.data]
        sensor.data = DataFrame(values, columns = columns)

    return data

class GetLocationSensorValuesById(PathBase):
    def get_location_sensor_values_by_id(
        self,
        locationId: int,
        deviceId: str = None,
        fromDatetime: datetime = None,
        toDatetime: datetime = None,
        asDataFrame: bool = False,
        stream: bool = False,
        timeout: typing.Optional[typing.Union[int, typing.Tuple]] = None,
        skip_deserialization: bool = False,
    ) -> ClimifyApiResponse[List[SensorDataExtDto]]:
        """Returns sensor values from devices associated with the given location.

        fromDatetime and toDatetime:
            The default time period of the data is 3 months. 
            Thus the sensor period is always the last 3 months unless *both* time period variables are specified.
            The storage time is 3 years for the data, fromDatetime must therefore be later than this point.

        :param locationId: Location identifier
        :type locationId: int
        :param deviceId: Device identifier
        :type deviceId: int
        :param fromDatetime: Start time for wanted sensor data period
        :type fromDatetime: datetime
        :param toDatetime: End time for wanted sensor data period
        :type toDatetime: datetime
        :param asDataFrame: If True, will convert the data of the devices to pandas DataFrames, defaults to False.
        :type asDataFrame: bool, optional
        :type stream: bool, optional
        :param timeout: How long to wait for a request in seconds, defaults to None
        :type timeout: typing.Optional[typing.Union[int, typing.Tuple]], optional
        :param skip_deserialization: Toggles whether or not to skip deserialize of the byte response, defaults to False
        :type skip_deserialization: bool, optional

        :raises ApiValueError: Will be raised if invalid inputs are provided
        :raises ClimifyApiException: Will be raised if an error occurred while calling the API

        :return: A response with a body containing the list of devices with their data
        :rtype: ClimifyApiResponse[List[SensorDataExtDto]]
        """
        # Validate input
        if locationId is None:
            raise ApiValueError("Location id was given as None. A valid location id must be provided.")

        if fromDatetime > toDatetime:
            raise ApiValueError(f'Given {nameof(fromDatetime)} was later than the given {nameof(toDatetime)}. Please provide a valid time period.')

        if fromDatetime < datetime.today() - relativedelta(years=3):
            raise ApiValueError(f'The given value of {nameof(fromDatetime)} is longer than 3 years ago. Data storage limit is 3 years, please provide a value within this limit.')

        # Make rest request
        usedPath = PATH.replace('{id}',str(locationId))

        requests = []
        subRequestToTime = toDatetime
        subRequestFromTime = max(subRequestToTime - relativedelta(months=3), fromDatetime)

        while subRequestFromTime >= fromDatetime:
            query_parameters = []
            for name, value in (
                ('devId', deviceId),
                ('dateTimeFrom', subRequestFromTime.isoformat()+'Z' if subRequestFromTime else None),
                ('dateTimeTo', subRequestToTime.isoformat()+'Z' if subRequestToTime else None)
            ):
                if value:
                    query_parameters.append(f"{name}={value}")

            if len(query_parameters) > 0:
                requests.append("?" + "&".join(query_parameters))

            if subRequestFromTime == fromDatetime:
                break

            subRequestToTime = subRequestFromTime - relativedelta(seconds=1)
            subRequestFromTime = max(subRequestToTime - relativedelta(months=3), fromDatetime)
            
        bodies = []
        for request in requests:
            requestPath = usedPath+request
            response = self.api_client.call_api(
                resource_path=requestPath,
                method='GET',
                stream=stream,
                timeout=timeout
            )

            # Format response
            if not 200 <= response.status <= 299:
                raise ClimifyApiException(
                    status=response.status,
                    reason=response.reason,
                    api_response=response
                )
        
            if skip_deserialization:
                bodies.append(response.data)
                continue
            
            deserialized_body = parse_raw_as(List[SensorDataExtDto],response.data) if response.data\
                                else []
            
            # Sort observations on time
            for sensor in deserialized_body:
                sensor.data = sorted(sensor.data, key=lambda x: x.time, reverse=True)

            if asDataFrame:
                deserialized_body = convert_values_to_dataFrame(deserialized_body)
            
            bodies.append(deserialized_body)

        if skip_deserialization:
            response.data = bodies
            return ClimifyApiResponseWithoutDeserialization(response=response)

        sensors = {}
        for body in bodies:
            for sensor in body:
                if sensor.devId not in sensors:
                    sensors[sensor.devId] = sensor
                    continue

                sensor_data = sensors[sensor.devId]
                if asDataFrame:
                    sensor_data.data = concat([sensor_data.data, sensor.data], ignore_index=True)
                else:
                    sensor_data.data += sensor.data

        deserialized_body = list(sensors.values())

        return ClimifyApiResponse[List[SensorDataExtDto]](
            response=response,
            body=deserialized_body,
            headers=response.headers
        )