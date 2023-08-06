import typing
from climify_api import ApiClient, Configuration
from climify_api.apis.v1.paths import (
    # GET
    GetAllUserResources,
    GetOrganisationById,
    GetOrganisationDevicesById,
    GetBuildingById,
    GetBuildingDevicesById,
    GetMapById,
    GetMapDevicesById,
    GetLocationById,
    GetLocationDevicesById,
    GetLocationSensorValuesById,
    GetFormResponsesFromLocationById,

    # POST
    SetLocationTemperatureById
)

class ApiController(
    # GET
    GetAllUserResources,
    GetOrganisationById,
    GetOrganisationDevicesById,
    GetBuildingById,
    GetBuildingDevicesById,
    GetMapById,
    GetMapDevicesById,
    GetLocationById,
    GetLocationDevicesById,
    GetLocationSensorValuesById,
    GetFormResponsesFromLocationById,
    
    # POST
    SetLocationTemperatureById
):
    def __init__(self, api_client: typing.Optional[ApiClient] = None, configuration: typing.Optional[Configuration] = None):
        if api_client:
            api_client.api_version = 'v1'

        api_client = api_client if api_client is not None\
                     else ApiClient(configuration=configuration, api_version = 'v1')
        
        super().__init__(api_client)