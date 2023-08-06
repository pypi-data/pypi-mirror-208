import functools  # noqa: F401
import io  # noqa: F401
import re  # noqa: F401
import typing  # noqa: F401
import typing_extensions  # noqa: F401
import uuid  # noqa: F401
from typing import List
from pydantic import parse_raw_as


from climify_api.apis.PathBase import PathBase  # noqa: F401

from climify_api.exceptions import ClimifyApiException
from climify_api.api_client import ClimifyApiResponse, ClimifyApiResponseWithoutDeserialization
from climify_api.models import ResourceDto

PATH = 'resources'

class GetAllUserResources(PathBase):
    def get_user_resources(
        self,
        stream: bool = False,
        timeout: typing.Optional[typing.Union[int, typing.Tuple]] = None,
        skip_deserialization: bool = False,
    ) -> ClimifyApiResponse[List[ResourceDto]]:
        """Returns all organisations the user has access.

        :param stream: Toggles streaming. Defaults to False.
        :type stream: bool, optional
        :param timeout: How long to wait for a request in seconds. Defaults to None.
        :type timeout: typing.Optional[typing.Union[int, typing.Tuple]], optional
        :param skip_deserialization: Toggles whether or not to skip deserialize of the byte response. Defaults to False.
        :type skip_deserialization: bool, optional

        :raises ClimifyApiException: Will be raised if an error occurred while calling the API

        :return: A response with a body containing a list of organisation models including id and name
        :rtype: ClimifyApiResponse[List[ResourceDto]]
        """

        # Make rest request
        used_path = PATH

        response = self.api_client.call_api(
            resource_path=used_path,
            method='GET',
            stream=stream,
            timeout=timeout,
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
            # Deserialize response
            deserialized_body = parse_raw_as(List[ResourceDto],response.data)
            api_response = ClimifyApiResponse[List[ResourceDto]](
                response=response,
                body=deserialized_body,
                headers=response.headers
            )


        return api_response